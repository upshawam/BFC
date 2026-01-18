#!/usr/bin/env python3
"""Run the EntrantTracker for every configured event.

Ensure the repository root is on sys.path so `from scraper import ...` works
when this script is executed from `scripts/` (this is the behavior in
GitHub Actions and when running `python scripts/run_all.py`).
"""
from pathlib import Path
import sys

# Prepend repo root to sys.path so sibling modules at the repo root can be imported
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scraper import EntrantTracker, EVENTS


def main():
    for key in EVENTS.keys():
        tracker = EntrantTracker(event_key=key)
        print(f"\n=== Running tracker for: {tracker.event_name} (key={key}) ===")
        try:
            tracker.run()
        except Exception as e:
            print(f"Error running tracker for {key}: {e}")


if __name__ == '__main__':
    main()
