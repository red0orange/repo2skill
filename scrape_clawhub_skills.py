#!/usr/bin/env python3
"""Scrape all skills from clawhub.ai using the public REST API with cursor pagination."""

import json
import os
import time
import requests

API_BASE = "https://clawhub.ai"
SKILLS_ENDPOINT = f"{API_BASE}/api/v1/skills"
OUTPUT_FILE = "clawhub_all_skills.json"
PROGRESS_FILE = "clawhub_progress.json"
LIMIT = 200  # max per request
MAX_RETRIES = 5


def load_progress():
    """Resume from saved progress if available."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Resuming from progress: {len(data['skills'])} skills, page {data['page']}")
        return data["skills"], data.get("cursor"), data["page"]
    return [], None, 0


def save_progress(skills, cursor, page):
    """Save progress for resumption."""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"skills": skills, "cursor": cursor, "page": page}, f, ensure_ascii=False)


def fetch_all_skills():
    all_skills, cursor, page = load_progress()

    while True:
        page += 1
        params = {"limit": LIMIT, "sort": "updated"}
        if cursor:
            params["cursor"] = cursor

        print(f"Fetching page {page} (collected {len(all_skills)} so far)...")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.get(SKILLS_ENDPOINT, params=params, timeout=60)
                if resp.status_code == 429:
                    wait = min(10 * attempt, 60)
                    print(f"  Rate limited, waiting {wait}s (attempt {attempt})...")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                break
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                wait = min(5 * attempt, 30)
                print(f"  Network error (attempt {attempt}/{MAX_RETRIES}): {type(e).__name__}, retrying in {wait}s...")
                time.sleep(wait)
        else:
            print(f"  Failed after {MAX_RETRIES} attempts, saving progress and stopping.")
            save_progress(all_skills, cursor, page - 1)
            return all_skills

        data = resp.json()
        items = data.get("items", [])
        next_cursor = data.get("nextCursor")

        all_skills.extend(items)
        print(f"  Got {len(items)} skills, nextCursor={'yes' if next_cursor else 'none'}")

        # Save progress every 5 pages
        if page % 5 == 0:
            save_progress(all_skills, next_cursor, page)

        if not next_cursor or len(items) == 0:
            break

        cursor = next_cursor
        time.sleep(1.5)  # rate limit courtesy

    # Clean up progress file on success
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

    return all_skills


def main():
    print("Starting to collect all skills from clawhub.ai...")
    print(f"API endpoint: {SKILLS_ENDPOINT}")
    print(f"Limit per page: {LIMIT}")
    print()

    skills = fetch_all_skills()
    print(f"\nTotal skills collected: {len(skills)}")

    # Save raw data
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)
    print(f"Saved to {OUTPUT_FILE}")

    # Print summary
    if skills:
        print(f"\nFields per skill entry:")
        for key in skills[0]:
            val = skills[0][key]
            print(f"  {key}: {type(val).__name__} = {json.dumps(val, ensure_ascii=False)[:100]}")

    # Print some stats
    print(f"\n--- Summary ---")
    total_downloads = sum(
        (s.get("stats") or {}).get("downloads", 0) for s in skills if isinstance(s.get("stats"), dict)
    )
    total_installs = sum(
        (s.get("stats") or {}).get("installsAllTime", 0) for s in skills if isinstance(s.get("stats"), dict)
    )
    with_summary = sum(1 for s in skills if s.get("summary"))
    print(f"Total skills: {len(skills)}")
    print(f"With summary: {with_summary}")
    print(f"Total downloads: {total_downloads}")
    print(f"Total installs (all time): {total_installs}")


if __name__ == "__main__":
    main()
