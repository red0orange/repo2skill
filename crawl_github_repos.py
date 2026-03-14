#!/usr/bin/env python3
"""
Crawl all GitHub repositories with stars > 100.
Phase 1: Collect repo metadata via Search API (token-rotated, star-range segmented)
Phase 2: Fetch README via raw.githubusercontent.com (async, high concurrency)
Supports resume from interruption.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

import aiohttp
import requests
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================
load_dotenv()

TOKENS = [t.strip() for t in os.environ.get("GITHUB_TOKENS", "").split(",") if t.strip()]
if not TOKENS:
    print("ERROR: Set GITHUB_TOKENS in .env (comma-separated)")
    sys.exit(1)

DATA_DIR = Path("data")
REPOS_FILE = DATA_DIR / "github_repos.jsonl"
PROGRESS_FILE = DATA_DIR / "search_progress.json"
READMES_DIR = DATA_DIR / "readmes"
README_FAILURES_FILE = DATA_DIR / "readme_failures.jsonl"

MIN_STARS = 100
SEARCH_PER_PAGE = 100
SEARCH_MAX_PAGES = 10  # 10 pages × 100 = 1000 (API hard limit)
README_CONCURRENCY = 50
README_RETRY = 3

# ============================================================
# Token Rotator
# ============================================================
class TokenRotator:
    """Round-robin token rotation with per-token search rate tracking."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        # Search API: 30 req/min/token. Track last request times per token.
        self.search_times = {i: [] for i in range(len(tokens))}

    def next(self):
        token = self.tokens[self.index]
        idx = self.index
        self.index = (self.index + 1) % len(self.tokens)
        return token, idx

    def get_headers(self, token):
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def wait_for_search_rate(self, token_idx):
        """Ensure we don't exceed 30 req/min for this token's search API."""
        now = time.time()
        times = self.search_times[token_idx]
        # Remove entries older than 60s
        self.search_times[token_idx] = [t for t in times if now - t < 60]
        times = self.search_times[token_idx]
        if len(times) >= 29:  # leave 1 margin
            oldest = times[0]
            wait = 60 - (now - oldest) + 0.5
            if wait > 0:
                print(f"    Search rate limit for token {token_idx}, waiting {wait:.1f}s...")
                time.sleep(wait)
        self.search_times[token_idx].append(time.time())


rotator = TokenRotator(TOKENS)

# ============================================================
# Phase 1: Search API
# ============================================================

def load_progress():
    """Load completed star ranges."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed_ranges": [], "known_repos": set()}


def save_progress(progress):
    """Save progress (convert set to list for JSON)."""
    to_save = {
        "completed_ranges": progress["completed_ranges"],
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(to_save, f)


def load_existing_repos():
    """Load already-saved repo full_names for dedup."""
    existing = set()
    if REPOS_FILE.exists():
        with open(REPOS_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        repo = json.loads(line)
                        existing.add(repo["full_name"])
                    except (json.JSONDecodeError, KeyError):
                        pass
    return existing


def search_repos_in_range(star_min, star_max):
    """Search repos in a star range. Returns (repos, total_count)."""
    token, idx = rotator.next()
    rotator.wait_for_search_rate(idx)
    headers = rotator.get_headers(token)

    if star_max is None:
        q = f"stars:>={star_min}"
    else:
        q = f"stars:{star_min}..{star_max}"

    resp = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": q, "sort": "stars", "order": "desc", "per_page": 1, "page": 1},
        headers=headers,
        timeout=30,
    )

    if resp.status_code == 403:
        # Rate limited - wait and retry
        reset_ts = int(resp.headers.get("X-RateLimit-Reset", 0))
        wait = max(reset_ts - time.time(), 0) + 5
        print(f"    Rate limited (403), waiting {wait:.0f}s...")
        time.sleep(wait)
        return search_repos_in_range(star_min, star_max)

    if resp.status_code == 422:
        print(f"    Validation error for range {star_min}..{star_max}, skipping")
        return [], 0

    if resp.status_code != 200:
        print(f"    Error {resp.status_code} for range {star_min}..{star_max}: {resp.text[:200]}")
        time.sleep(5)
        return [], 0

    data = resp.json()
    total_count = data.get("total_count", 0)
    return data.get("items", []), total_count


def fetch_all_pages(star_min, star_max):
    """Fetch all pages for a star range (up to 1000 results)."""
    repos = []
    for page in range(1, SEARCH_MAX_PAGES + 1):
        token, idx = rotator.next()
        rotator.wait_for_search_rate(idx)
        headers = rotator.get_headers(token)

        if star_max is None:
            q = f"stars:>={star_min}"
        else:
            q = f"stars:{star_min}..{star_max}"

        for attempt in range(3):
            try:
                resp = requests.get(
                    "https://api.github.com/search/repositories",
                    params={"q": q, "sort": "stars", "order": "desc",
                            "per_page": SEARCH_PER_PAGE, "page": page},
                    headers=headers,
                    timeout=30,
                )
                break
            except requests.exceptions.RequestException as e:
                print(f"    Request error: {e}, retry {attempt+1}")
                time.sleep(2 ** attempt)
        else:
            break

        if resp.status_code == 403:
            reset_ts = int(resp.headers.get("X-RateLimit-Reset", 0))
            wait = max(reset_ts - time.time(), 0) + 5
            print(f"    Rate limited on page {page}, waiting {wait:.0f}s...")
            time.sleep(wait)
            # Retry this page
            token, idx = rotator.next()
            rotator.wait_for_search_rate(idx)
            headers = rotator.get_headers(token)
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": q, "sort": "stars", "order": "desc",
                        "per_page": SEARCH_PER_PAGE, "page": page},
                headers=headers,
                timeout=30,
            )

        if resp.status_code != 200:
            print(f"    Error {resp.status_code} on page {page}, stopping pagination")
            break

        items = resp.json().get("items", [])
        if not items:
            break

        repos.extend(items)

    return repos


def extract_repo_info(item):
    """Extract relevant fields from a search API result."""
    license_info = item.get("license") or {}
    return {
        "full_name": item["full_name"],
        "description": item.get("description", ""),
        "language": item.get("language", ""),
        "topics": item.get("topics", []),
        "stargazers_count": item.get("stargazers_count", 0),
        "forks_count": item.get("forks_count", 0),
        "open_issues_count": item.get("open_issues_count", 0),
        "created_at": item.get("created_at", ""),
        "updated_at": item.get("updated_at", ""),
        "pushed_at": item.get("pushed_at", ""),
        "license": license_info.get("spdx_id", ""),
        "default_branch": item.get("default_branch", "main"),
        "homepage": item.get("homepage", ""),
        "size": item.get("size", 0),
        "archived": item.get("archived", False),
        "fork": item.get("fork", False),
        "owner": item["owner"]["login"],
        "html_url": item.get("html_url", ""),
    }


def generate_star_ranges():
    """Generate star ranges from high to low, with smaller ranges for dense areas."""
    ranges = []
    # Very high stars: single large ranges
    ranges.append((50000, None))      # 50k+
    ranges.append((20000, 49999))
    ranges.append((10000, 19999))
    ranges.append((5000, 9999))
    ranges.append((3000, 4999))
    ranges.append((2000, 2999))
    ranges.append((1500, 1999))
    ranges.append((1000, 1499))
    # 500-999: denser
    for s in range(900, 499, -100):
        ranges.append((s, s + 99))
    # 100-499: very dense, use smaller ranges
    for s in range(490, 99, -10):
        ranges.append((s, s + 9))
    return ranges


def phase1_collect_repos():
    """Phase 1: Collect all repos with stars > 100 via Search API."""
    print("=" * 60)
    print("Phase 1: Collecting repository metadata via Search API")
    print(f"  Tokens available: {len(TOKENS)}")
    print("=" * 60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load progress
    progress = load_progress()
    completed_ranges = set(tuple(r) for r in progress["completed_ranges"])
    existing_repos = load_existing_repos()
    print(f"  Already saved: {len(existing_repos)} repos")
    print(f"  Completed ranges: {len(completed_ranges)}")

    star_ranges = generate_star_ranges()
    total_new = 0

    with open(REPOS_FILE, "a") as f_out:
        for i, (star_min, star_max) in enumerate(star_ranges):
            range_key = (star_min, star_max)
            if range_key in completed_ranges:
                continue

            range_str = f"{star_min}..{star_max}" if star_max else f">={star_min}"
            print(f"\n[{i+1}/{len(star_ranges)}] Searching stars:{range_str}...")

            # First check total count
            _, total_count = search_repos_in_range(star_min, star_max)
            print(f"  Total count: {total_count}")

            if total_count == 0:
                completed_ranges.add(range_key)
                progress["completed_ranges"].append(list(range_key))
                save_progress(progress)
                continue

            if total_count > 1000:
                # Need to split this range further
                print(f"  Count > 1000, splitting range...")
                sub_ranges = split_range(star_min, star_max, total_count)
                for sub_min, sub_max in sub_ranges:
                    sub_key = (sub_min, sub_max)
                    if sub_key in completed_ranges:
                        continue
                    sub_str = f"{sub_min}..{sub_max}" if sub_max else f">={sub_min}"
                    print(f"  Sub-range stars:{sub_str}...")

                    # Check sub count
                    _, sub_count = search_repos_in_range(sub_min, sub_max)
                    print(f"    Count: {sub_count}")

                    if sub_count > 1000:
                        # Split again
                        print(f"    Still > 1000, splitting further...")
                        sub_sub_ranges = split_range(sub_min, sub_max, sub_count)
                        for ss_min, ss_max in sub_sub_ranges:
                            ss_key = (ss_min, ss_max)
                            if ss_key in completed_ranges:
                                continue
                            ss_str = f"{ss_min}..{ss_max}"
                            _, ss_count = search_repos_in_range(ss_min, ss_max)
                            print(f"      Sub-sub stars:{ss_str} count={ss_count}")
                            if ss_count > 0:
                                items = fetch_all_pages(ss_min, ss_max)
                                new = write_repos(f_out, items, existing_repos)
                                total_new += new
                                print(f"      Fetched {len(items)}, new: {new}")
                            completed_ranges.add(ss_key)
                            progress["completed_ranges"].append(list(ss_key))
                            save_progress(progress)
                    elif sub_count > 0:
                        items = fetch_all_pages(sub_min, sub_max)
                        new = write_repos(f_out, items, existing_repos)
                        total_new += new
                        print(f"    Fetched {len(items)}, new: {new}")

                    completed_ranges.add(sub_key)
                    progress["completed_ranges"].append(list(sub_key))
                    save_progress(progress)
            else:
                items = fetch_all_pages(star_min, star_max)
                new = write_repos(f_out, items, existing_repos)
                total_new += new
                print(f"  Fetched {len(items)}, new: {new}")

            completed_ranges.add(range_key)
            progress["completed_ranges"].append(list(range_key))
            save_progress(progress)

    total_repos = len(existing_repos) + total_new
    print(f"\nPhase 1 complete! Total repos: {total_repos} (new this run: {total_new})")
    return total_repos


def split_range(star_min, star_max, total_count):
    """Split a star range into smaller sub-ranges."""
    if star_max is None:
        star_max = 500000  # arbitrary high cap
    ranges = []
    # Estimate how many splits we need
    n_splits = max(2, (total_count // 800) + 1)
    step = max(1, (star_max - star_min + 1) // n_splits)
    current = star_min
    while current <= star_max:
        end = min(current + step - 1, star_max)
        ranges.append((current, end))
        current = end + 1
    return ranges


def write_repos(f_out, items, existing_repos):
    """Write new repos to JSONL file. Returns count of new repos."""
    new_count = 0
    for item in items:
        full_name = item["full_name"]
        if full_name in existing_repos:
            continue
        repo_info = extract_repo_info(item)
        f_out.write(json.dumps(repo_info, ensure_ascii=False) + "\n")
        existing_repos.add(full_name)
        new_count += 1
    f_out.flush()
    return new_count


# ============================================================
# Phase 2: Fetch READMEs
# ============================================================

async def fetch_readme(session, sem, repo_info, retries=README_RETRY):
    """Fetch README for a single repo via raw.githubusercontent.com."""
    owner = repo_info["owner"]
    repo_name = repo_info["full_name"].split("/", 1)[1]
    branch = repo_info.get("default_branch", "main")

    # Try common README filenames
    filenames = ["README.md", "readme.md", "README.rst", "README.txt", "README",
                 "Readme.md", "readme.rst"]

    async with sem:
        for fname in filenames:
            url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{fname}"
            for attempt in range(retries):
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            content = await resp.text(errors="replace")
                            return content, fname
                        elif resp.status == 404:
                            break  # Try next filename
                        elif resp.status == 429:
                            # Rate limited
                            wait = 2 ** attempt + 1
                            await asyncio.sleep(wait)
                        else:
                            break
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    if attempt < retries - 1:
                        await asyncio.sleep(1)

    return None, None


async def phase2_fetch_readmes():
    """Phase 2: Fetch READMEs for all repos."""
    print("\n" + "=" * 60)
    print("Phase 2: Fetching READMEs via raw.githubusercontent.com")
    print("=" * 60)

    READMES_DIR.mkdir(parents=True, exist_ok=True)

    # Load all repos
    repos = []
    with open(REPOS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    repos.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    print(f"  Total repos: {len(repos)}")

    # Check which READMEs already exist
    existing = set()
    for p in READMES_DIR.iterdir():
        if p.is_file():
            existing.add(p.stem)  # owner__repo

    to_fetch = []
    for repo in repos:
        key = repo["full_name"].replace("/", "__")
        if key not in existing:
            to_fetch.append(repo)

    print(f"  Already downloaded: {len(existing)}")
    print(f"  To fetch: {len(to_fetch)}")

    if not to_fetch:
        print("  Nothing to do!")
        return

    sem = asyncio.Semaphore(README_CONCURRENCY)
    fetched = 0
    failed = 0
    total = len(to_fetch)

    # Open failures file
    f_fail = open(README_FAILURES_FILE, "a")

    connector = aiohttp.TCPConnector(limit=README_CONCURRENCY, limit_per_host=30)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Process in batches
        batch_size = 500
        for batch_start in range(0, total, batch_size):
            batch = to_fetch[batch_start:batch_start + batch_size]
            tasks = [fetch_readme(session, sem, repo) for repo in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for repo, result in zip(batch, results):
                if isinstance(result, Exception):
                    failed += 1
                    f_fail.write(json.dumps({"full_name": repo["full_name"],
                                             "error": str(result)}) + "\n")
                    continue

                content, fname = result
                if content is not None:
                    key = repo["full_name"].replace("/", "__")
                    ext = Path(fname).suffix if fname else ".md"
                    out_path = READMES_DIR / f"{key}{ext}"
                    out_path.write_text(content, encoding="utf-8")
                    fetched += 1
                else:
                    failed += 1
                    f_fail.write(json.dumps({"full_name": repo["full_name"],
                                             "error": "not_found"}) + "\n")

            elapsed_pct = (batch_start + len(batch)) / total * 100
            print(f"  Progress: {batch_start + len(batch)}/{total} ({elapsed_pct:.1f}%) "
                  f"- fetched: {fetched}, failed: {failed}", flush=True)

    f_fail.close()
    print(f"\nPhase 2 complete! Fetched: {fetched}, Failed: {failed}")


# ============================================================
# Main
# ============================================================
def main():
    print(f"GitHub Repos Crawler (stars > {MIN_STARS})")
    print(f"Tokens: {len(TOKENS)}")
    print(f"Data dir: {DATA_DIR}")
    print()

    # Phase 1
    phase1_collect_repos()

    # Phase 2
    asyncio.run(phase2_fetch_readmes())

    print("\n" + "=" * 60)
    print("All done!")
    # Summary
    repo_count = sum(1 for _ in open(REPOS_FILE))
    readme_count = sum(1 for _ in READMES_DIR.iterdir()) if READMES_DIR.exists() else 0
    print(f"  Repos collected: {repo_count}")
    print(f"  READMEs downloaded: {readme_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
