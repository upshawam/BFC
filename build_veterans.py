#!/usr/bin/env python3
"""
Build veterans scout data by cross-referencing 2026 entrants
against historical 50K and Marathon finishers (2015-2025).
"""

import json
from collections import defaultdict
from pathlib import Path

# Load 2026 entrants
with open('data/entrants.json', 'r') as f:
    entrants_data = json.load(f)

entrants = entrants_data['entrants']

# Build a name index for fast lookup
def normalize_name(first, last):
    """Normalize name for matching - lowercase, strip whitespace."""
    return f"{first.strip().lower()} {last.strip().lower()}"

entrant_index = {}
for uid, entrant in entrants.items():
    name = normalize_name(entrant['first_name'], entrant['last_name'])
    entrant_index[name] = {
        'uid': uid,
        'first_name': entrant['first_name'],
        'last_name': entrant['last_name'],
        'city': entrant.get('city', ''),
        'state': entrant.get('location', ''),
        'age': entrant.get('age', ''),
    }

# Load all historical results and cross-reference
veterans = {}  # {normalized_name: {'entrant_info': {...}, '50k': [...], 'marathon': [...], 'dnf': [...]}}

historical_path = Path('data/historical/results')

# Process each year's results
FIRST_YEAR = 2015
LAST_YEAR = 2025

for year in range(FIRST_YEAR, LAST_YEAR + 1):
    # Process 50K
    file_50k = historical_path / f'results_{year}_50k.json'
    if file_50k.exists():
        with open(file_50k, 'r') as f:
            results_50k = json.load(f)
            for finisher in results_50k.get('finishers', []):
                name = normalize_name(finisher['first_name'], finisher['last_name'])
                if name in entrant_index:
                    if name not in veterans:
                        veterans[name] = {
                            'entrant_info': entrant_index[name],
                            '50k': [],
                            'marathon': [],
                            'dnf': []
                        }
                    
                    # Check if this is a DNF or finish
                    if finisher.get('status') == 'DNF':
                        veterans[name]['dnf'].append({
                            'year': year,
                            'distance': '50K',
                            'city': finisher.get('city'),
                            'state': finisher.get('state'),
                            'age': finisher.get('age'),
                            'division': finisher.get('division'),
                        })
                    else:
                        veterans[name]['50k'].append({
                            'year': year,
                            'place': finisher.get('place'),
                            'finish_time': finisher.get('finish_time_formatted'),
                            'finish_time_seconds': finisher.get('finish_time_seconds'),
                            'city': finisher.get('city'),
                            'state': finisher.get('state'),
                            'age': finisher.get('age'),
                            'division': finisher.get('division'),
                        })
    
    # Process Marathon
    file_marathon = historical_path / f'results_{year}_marathon.json'
    if file_marathon.exists():
        with open(file_marathon, 'r') as f:
            results_marathon = json.load(f)
            for finisher in results_marathon.get('finishers', []):
                name = normalize_name(finisher['first_name'], finisher['last_name'])
                if name in entrant_index:
                    if name not in veterans:
                        veterans[name] = {
                            'entrant_info': entrant_index[name],
                            '50k': [],
                            'marathon': [],
                            'dnf': []
                        }
                    veterans[name]['marathon'].append({
                        'year': year,
                        'place': finisher.get('place'),
                        'finish_time': finisher.get('finish_time_formatted'),
                        'finish_time_seconds': finisher.get('finish_time_seconds'),
                        'city': finisher.get('city'),
                        'state': finisher.get('state'),
                        'age': finisher.get('age'),
                        'division': finisher.get('division'),
                    })

# Filter: Only keep veterans with 50K finishes (at least 1)
veterans_50k_only = {
    name: data for name, data in veterans.items()
    if len(data['50k']) > 0
}

# Build the final structure with additional metadata
veterans_data = {
    'total_veterans': len(veterans_50k_only),
    'scraped_at': Path('data/entrants.json').stat().st_mtime,
    'veterans': []
}

for name, data in sorted(veterans_50k_only.items()):
    years_participated = len(set([f['year'] for f in data['50k'] + data['marathon']]))
    num_50k_finishes = len(data['50k'])
    num_marathon_finishes = len(data['marathon'])
    
    # Filter to last 4 years (2022-2025) for recent performance
    recent_years = [2022, 2023, 2024, 2025]
    recent_50k_finishes = [f for f in data['50k'] if f['year'] in recent_years]
    recent_marathon_finishes = [f for f in data['marathon'] if f['year'] in recent_years]
    recent_dnfs = [d for d in data['dnf'] if d['year'] in recent_years]
    
    # Build a year-by-year recent summary
    recent_summary = []
    for year in recent_years:
        year_50k = [f for f in recent_50k_finishes if f['year'] == year]
        year_marathon = [f for f in recent_marathon_finishes if f['year'] == year]
        year_dnf = [d for d in recent_dnfs if d['year'] == year]
        
        if year_50k:
            recent_summary.append(f"{year}: 50K")
        elif year_marathon:
            recent_summary.append(f"{year}: Marathon")
        elif year_dnf:
            recent_summary.append(f"{year}: DNF")
    
    recent_summary_str = " | ".join(recent_summary) if recent_summary else "No recent finishes"
    
    # Calculate average 50K finish time from recent years only
    recent_times = [f['finish_time_seconds'] for f in recent_50k_finishes if 'finish_time_seconds' in f and f['finish_time_seconds'] is not None]
    avg_recent_time_seconds = sum(recent_times) / len(recent_times) if recent_times else None
    
    # Calculate average finish position from recent years
    recent_positions = [f['place'] for f in recent_50k_finishes if 'place' in f]
    avg_position = sum(recent_positions) / len(recent_positions) if recent_positions else None
    
    # Format average time as HH:MM:SS
    avg_time_formatted = None
    if avg_recent_time_seconds:
        hours = int(avg_recent_time_seconds // 3600)
        minutes = int((avg_recent_time_seconds % 3600) // 60)
        seconds = int(avg_recent_time_seconds % 60)
        avg_time_formatted = f"{hours}:{minutes:02d}:{seconds:02d}"
    
    # Calculate Reliability Index
    # Formula: (50K finishes × 15) + (years participated × 10) - (marathon finishes × 5) + recency bonus
    # Recency bonus rewards latest 50K finishers: last 4 years get +2/+4/+6/+8 (oldest -> newest)
    # This rewards: consistent 50K finishing, longevity, but penalizes settling for marathon
    # Speed is NOT considered - we want steady reliable finishers, not fast ones
    recency_start = LAST_YEAR - 3
    recency_bonus = sum(
        max(0, (f['year'] - recency_start + 1)) * 2
        for f in data['50k']
        if f['year'] >= recency_start
    )
    reliability_index = (num_50k_finishes * 15) + (years_participated * 10) - (num_marathon_finishes * 5) + recency_bonus
    
    # Calculate 50K consistency rate (how often they finish 50K when they show up)
    consistency_rate = round((num_50k_finishes / years_participated) * 100) if years_participated > 0 else 0
    
    veteran_entry = {
        'name': {
            'first': data['entrant_info']['first_name'],
            'last': data['entrant_info']['last_name'],
        },
        'location': {
            'city': data['entrant_info']['city'],
            'state': data['entrant_info']['state'],
        },
        'age_category': data['entrant_info']['age'],
        'experience': {
            'years_participated': years_participated,
            '50k_finishes': num_50k_finishes,
            'marathon_finishes': num_marathon_finishes,
            'reliability_index': reliability_index,
            'recency_bonus': recency_bonus,
            'consistency_rate': consistency_rate,
            'avg_recent_time_seconds': avg_recent_time_seconds,
            'avg_recent_time_formatted': avg_time_formatted,
            'avg_recent_position': round(avg_position) if avg_position else None,
            'recent_finishes_count': len(recent_50k_finishes),
            'recent_marathon_count': len(recent_marathon_finishes),
            'recent_summary': recent_summary_str,
        },
        'finishes_50k': data['50k'],
        'finishes_marathon': data['marathon'],
        'recent_50k_finishes': recent_50k_finishes,
    }
    
    veterans_data['veterans'].append(veteran_entry)

# Calculate pace tiers based on recent finish time distribution
veterans_with_times = [v for v in veterans_data['veterans'] if v['experience']['avg_recent_time_seconds'] is not None]
if veterans_with_times:
    times = sorted([v['experience']['avg_recent_time_seconds'] for v in veterans_with_times])
    n = len(times)
    
    # Calculate quartiles
    q1 = times[n // 4]
    q2 = times[n // 2]  # median
    q3 = times[3 * n // 4]
    
    # Assign pace tier based on quartile position
    for vet in veterans_data['veterans']:
        avg_time = vet['experience']['avg_recent_time_seconds']
        if avg_time is None:
            vet['experience']['pace_tier'] = 'No Recent Data'
        elif avg_time <= q1:
            vet['experience']['pace_tier'] = 'Elite (Top 25%)'
        elif avg_time <= q2:
            vet['experience']['pace_tier'] = 'Fast (Top 50%)'
        elif avg_time <= q3:
            vet['experience']['pace_tier'] = 'Steady (Top 75%)'
        else:
            vet['experience']['pace_tier'] = 'Conservative (Back 25%)'

# Sort by reliability index (descending), then by years participated
veterans_data['veterans'].sort(
    key=lambda x: (-x['experience']['reliability_index'], -x['experience']['years_participated'])
)

# Save the processed data
with open('data/veterans_2026.json', 'w') as f:
    json.dump(veterans_data, f, indent=2)

print(f"✅ Built veterans data: {len(veterans_50k_only)} veterans found with 50K finishes")
print(f"   Saved to: data/veterans_2026.json")

# Print a quick summary
print("\n📊 Top Veterans (by Reliability Index):")
print(f"{'#':<3} {'Name':<25} {'RI':<4} {'Yrs':<4} {'50K':<4} {'Con%':<5} {'Pace Tier':<23} {'Avg Time (2022-25)':<18} {'Avg Pos'}")
print("-" * 120)
for i, vet in enumerate(veterans_data['veterans'][:20], 1):
    name = f"{vet['name']['first']} {vet['name']['last']}"
    exp = vet['experience']
    pace = exp['pace_tier']
    avg_time = exp['avg_recent_time_formatted'] or 'N/A'
    avg_pos = exp['avg_recent_position'] or 'N/A'
    recent_count = exp['recent_finishes_count']
    print(f"{i:<3} {name:<25} {exp['reliability_index']:<4} {exp['years_participated']:<4} {exp['50k_finishes']:<4} {exp['consistency_rate']:<5} {pace:<23} {avg_time:<18} {avg_pos} ({recent_count} recent)")
