#!/usr/bin/env python3
"""
Scrape detailed skill info from clawhub.ai:
  Round 1: /api/v1/skills/{slug}        → owner + moderation
  Round 2: /api/v1/skills/{slug}/versions/{ver} → files + security
"""

import json
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

API_BASE = "https://clawhub.ai"
INPUT_FILE = "clawhub_all_skills.json"

# Round 1 outputs
DETAIL_OUTPUT = "clawhub_skill_details.json"
DETAIL_PROGRESS = "clawhub_detail_progress.json"

# Round 2 outputs
VERSION_OUTPUT = "clawhub_skill_versions.json"
VERSION_PROGRESS = "clawhub_version_progress.json"

MAX_WORKERS = 30
MAX_RETRIES = 5
SAVE_EVERY = 500  # save progress every N completed


class RateLimiter:
    """Token-bucket style rate limiter that allows bursts."""
    def __init__(self, max_per_second=25):
        self.lock = threading.Lock()
        self.min_interval = 1.0 / max_per_second
        self.last_call = 0
        self.total = 0

    def wait(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_call = time.time()
            self.total += 1


rate_limiter = RateLimiter(max_per_second=25)

# Shared session with connection pooling
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=MAX_WORKERS,
    pool_maxsize=MAX_WORKERS + 5,
    max_retries=0,  # we handle retries ourselves
)
session.mount("https://", adapter)


def api_get(url, timeout=45):
    """GET with retries and rate limiting."""
    for attempt in range(1, MAX_RETRIES + 1):
        rate_limiter.wait()
        try:
            resp = session.get(url, timeout=timeout)
            if resp.status_code == 429:
                wait = min(10 * attempt, 60)
                time.sleep(wait)
                continue
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            wait = min(5 * attempt, 30)
            time.sleep(wait)
    return None


def load_skills():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_progress(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def save_final(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# Round 1: skill detail (owner + moderation)
# ──────────────────────────────────────────────
def fetch_skill_detail(slug):
    url = f"{API_BASE}/api/v1/skills/{requests.utils.quote(slug, safe='')}"
    return api_get(url)


def round1_details(skills):
    print("=" * 60)
    print("Round 1: Fetching owner + moderation for each skill")
    print("=" * 60)

    results = load_progress(DETAIL_PROGRESS)
    done_slugs = set(results.keys())
    todo = [s for s in skills if s["slug"] not in done_slugs]
    total = len(skills)

    print(f"  Total: {total}, Already done: {len(done_slugs)}, Remaining: {len(todo)}")

    completed = len(done_slugs)
    lock = threading.Lock()
    failed = 0

    def process(skill):
        nonlocal completed, failed
        slug = skill["slug"]
        data = fetch_skill_detail(slug)
        with lock:
            if data:
                results[slug] = {
                    "owner": data.get("owner"),
                    "moderation": data.get("moderation"),
                }
            else:
                results[slug] = {"owner": None, "moderation": None, "error": True}
                failed += 1
            completed += 1
            if completed % SAVE_EVERY == 0:
                save_progress(results, DETAIL_PROGRESS)
                print(f"  [{completed}/{total}] saved progress... (failed: {failed}, requests: {rate_limiter.total})")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(process, s): s for s in todo}
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"  Unexpected error: {e}")

    save_progress(results, DETAIL_PROGRESS)
    print(f"  Round 1 complete: {completed}/{total}, failed: {failed}")

    # Save final
    save_final(results, DETAIL_OUTPUT)
    print(f"  Saved to {DETAIL_OUTPUT}")
    return results


# ──────────────────────────────────────────────
# Round 2: version detail (files + security)
# ──────────────────────────────────────────────
def fetch_version_detail(slug, version):
    url = f"{API_BASE}/api/v1/skills/{requests.utils.quote(slug, safe='')}/versions/{requests.utils.quote(version, safe='')}"
    return api_get(url)


def round2_versions(skills):
    print()
    print("=" * 60)
    print("Round 2: Fetching files + security for each skill version")
    print("=" * 60)

    results = load_progress(VERSION_PROGRESS)
    done_slugs = set(results.keys())
    todo = [s for s in skills if s["slug"] not in done_slugs]
    total = len(skills)

    print(f"  Total: {total}, Already done: {len(done_slugs)}, Remaining: {len(todo)}")

    completed = len(done_slugs)
    lock = threading.Lock()
    failed = 0

    def process(skill):
        nonlocal completed, failed
        slug = skill["slug"]
        lv = skill.get("latestVersion")
        version = lv["version"] if isinstance(lv, dict) and "version" in lv else None

        if not version:
            with lock:
                results[slug] = {"error": "no_version"}
                completed += 1
            return

        data = fetch_version_detail(slug, version)
        with lock:
            if data and data.get("version"):
                v = data["version"]
                results[slug] = {
                    "files": v.get("files"),
                    "security": v.get("security"),
                    "changelogSource": v.get("changelogSource"),
                    "license": v.get("license"),
                }
            else:
                results[slug] = {"files": None, "security": None, "error": True}
                failed += 1
            completed += 1
            if completed % SAVE_EVERY == 0:
                save_progress(results, VERSION_PROGRESS)
                print(f"  [{completed}/{total}] saved progress... (failed: {failed}, requests: {rate_limiter.total})")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(process, s): s for s in todo}
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"  Unexpected error: {e}")

    save_progress(results, VERSION_PROGRESS)
    print(f"  Round 2 complete: {completed}/{total}, failed: {failed}")

    save_final(results, VERSION_OUTPUT)
    print(f"  Saved to {VERSION_OUTPUT}")
    return results


# ──────────────────────────────────────────────
# Merge everything into one file
# ──────────────────────────────────────────────
def merge_all(skills, details, versions):
    print()
    print("=" * 60)
    print("Merging all data...")
    print("=" * 60)

    merged = []
    for s in skills:
        slug = s["slug"]
        entry = dict(s)  # copy base fields

        # Add owner + moderation
        d = details.get(slug, {})
        entry["owner"] = d.get("owner")
        entry["moderation"] = d.get("moderation")

        # Add files + security
        v = versions.get(slug, {})
        entry["files"] = v.get("files")
        entry["security"] = v.get("security")
        entry["changelogSource"] = v.get("changelogSource")
        entry["license"] = v.get("license")

        merged.append(entry)

    output = "clawhub_skills_complete.json"
    save_final(merged, output)
    print(f"  Merged {len(merged)} skills → {output}")

    # Stats
    has_owner = sum(1 for m in merged if m.get("owner"))
    has_mod = sum(1 for m in merged if m.get("moderation") is not None)
    has_files = sum(1 for m in merged if m.get("files"))
    has_security = sum(1 for m in merged if m.get("security"))
    suspicious = sum(1 for m in merged if isinstance(m.get("moderation"), dict) and m["moderation"].get("isSuspicious"))
    malware = sum(1 for m in merged if isinstance(m.get("moderation"), dict) and m["moderation"].get("isMalwareBlocked"))

    print(f"\n--- Final Stats ---")
    print(f"  Total skills:       {len(merged)}")
    print(f"  With owner:         {has_owner}")
    print(f"  With moderation:    {has_mod}")
    print(f"  With files:         {has_files}")
    print(f"  With security:      {has_security}")
    print(f"  Flagged suspicious: {suspicious}")
    print(f"  Blocked malware:    {malware}")

    return merged


def main():
    skills = load_skills()
    print(f"Loaded {len(skills)} skills from {INPUT_FILE}\n")

    details = round1_details(skills)
    versions = round2_versions(skills)
    merge_all(skills, details, versions)

    # Cleanup progress files
    for p in [DETAIL_PROGRESS, VERSION_PROGRESS]:
        if os.path.exists(p):
            os.remove(p)

    print(f"\nTotal API requests: {rate_limiter.total}")
    print("Done!")


if __name__ == "__main__":
    main()
