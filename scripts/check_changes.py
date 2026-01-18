#!/usr/bin/env python3
"""Check if any event had meaningful changes (new/dropped entrants)."""
import json
from pathlib import Path
import sys

DATA_DIR = Path('data')
EVENTS = ['frozen_head_50k', 'other_race_50m', 'other_race_55k']

def check_for_changes():
    """Return True if any event has new or dropped entrants in the latest change."""
    has_changes = False
    
    for event_key in EVENTS:
        changes_file = DATA_DIR / f'changes_{event_key}.json'
        if not changes_file.exists():
            continue
            
        with open(changes_file) as f:
            changes = json.load(f)
        
        if not changes:
            continue
            
        latest = changes[-1]
        if latest.get('total_new', 0) > 0 or latest.get('total_dropped', 0) > 0:
            has_changes = True
            break
    
    return has_changes

if __name__ == '__main__':
    if check_for_changes():
        sys.exit(0)  # Has changes
    else:
        sys.exit(1)  # No changes
