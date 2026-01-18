#!/usr/bin/env python3
"""Diagnose per-event data files and compute metrics similar to index.html's analysis."""
import json
import csv
from pathlib import Path
from datetime import datetime

EVENTS = {
    'frozen_head_50k': 'Barkley Fall Classic',
    'other_race_50m': 'Dam Yeti 50 Miler',
    'other_race_55k': 'Dam Yeti 55K'
}
DATA_DIR = Path('data')


def read_changes(key):
    p = DATA_DIR / f'changes_{key}.json'
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def read_history(key):
    p = DATA_DIR / f'history_{key}.csv'
    if not p.exists():
        return []
    rows = []
    with open(p) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def analyze(key):
    name = EVENTS.get(key, key)
    changes = read_changes(key)
    history = read_history(key)

    print('\n---', name, f'({key})', '---')
    if not changes:
        print('No changes data')
        return
    latest = changes[-1]
    total_new = sum(c.get('total_new', 0) for c in changes)
    total_dropped = sum(c.get('total_dropped', 0) for c in changes)

    if history:
        start_ts = history[0].get('Date')
        start_count = int(history[0].get('Total_Entrants') or 0)
    else:
        start_ts = changes[0].get('timestamp')
        start_count = changes[0].get('previous_count') or 0

    days_between = (datetime.fromisoformat(latest['timestamp']) - datetime.fromisoformat(start_ts)).total_seconds() / (86400)
    daily_rate = (total_new / days_between) if days_between > 0 else 0

    print('Snapshots:', len(changes))
    print('Latest count:', latest.get('new_count'))
    print('Total new:', total_new)
    print('Total dropped:', total_dropped)
    print('Start count:', start_count)
    print('Days tracked:', round(days_between, 2))
    print('Average daily growth:', round(daily_rate, 3))
    print('Total change (latest - start):', latest.get('new_count') - start_count)


if __name__ == '__main__':
    for k in EVENTS.keys():
        analyze(k)
