#!/usr/bin/env python3
"""Run the EntrantTracker for every configured event."""
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
