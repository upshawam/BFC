#!/usr/bin/env python3
"""
Analyze Barkley Fall Classic veterans - runners who participated multiple years.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

DATA_DIR = repo_root / "data" / "historical"
ANALYSIS_DIR = DATA_DIR / "analysis"

def analyze_veterans():
    """Find runners who participated in multiple years."""
    
    # Load complete archive
    archive_file = DATA_DIR / "barkley_archive_complete.json"
    with open(archive_file, 'r') as f:
        all_data = json.load(f)
    
    # Track each runner's participations
    # Key: (first_name, last_name) - Value: list of participation records
    runner_participations = defaultdict(list)
    
    for year_data in all_data:
        year = year_data['year']
        distance = year_data.get('distance', 'Unknown')
        
        for finisher in year_data.get('finishers', []):
            first_name = finisher.get('first_name', '').strip()
            last_name = finisher.get('last_name', '').strip()
            
            if not first_name or not last_name:
                continue
            
            # Use normalized name as key
            name_key = (first_name.lower(), last_name.lower())
            
            runner_participations[name_key].append({
                'year': year,
                'distance': distance,
                'status': finisher.get('status', 'Unknown'),
                'place': finisher.get('place'),
                'finish_time_seconds': finisher.get('finish_time_seconds'),
                'finish_time_formatted': finisher.get('finish_time_formatted', ''),
                'age': finisher.get('age'),
                'city': finisher.get('city', ''),
                'state': finisher.get('state', ''),
                'division': finisher.get('division', ''),
                # Store display name from first occurrence
                'display_name': f"{first_name} {last_name}"
            })
    
    # Filter to only multi-year participants
    veterans = []
    for name_key, participations in runner_participations.items():
        if len(participations) >= 2:
            # Sort by year
            participations.sort(key=lambda x: x['year'])
            
            # Calculate statistics
            years_participated = sorted(list(set(p['year'] for p in participations)))
            total_races = len(participations)
            finishes = len([p for p in participations if p['status'] == 'Finished'])
            dnfs = len([p for p in participations if p['status'] == 'DNF'])
            dns = len([p for p in participations if p['status'] == 'DNS'])
            
            # Calculate by distance
            races_50k = len([p for p in participations if p['distance'] == '50K'])
            races_marathon = len([p for p in participations if p['distance'] == 'Marathon'])
            finishes_50k = len([p for p in participations if p['distance'] == '50K' and p['status'] == 'Finished'])
            finishes_marathon = len([p for p in participations if p['distance'] == 'Marathon' and p['status'] == 'Finished'])
            
            # Get best finish time (if any)
            finish_times = [p['finish_time_seconds'] for p in participations 
                          if p['finish_time_seconds'] and p['status'] == 'Finished']
            best_time_seconds = min(finish_times) if finish_times else None
            best_time_formatted = None
            if best_time_seconds:
                hours = int(best_time_seconds // 3600)
                minutes = int((best_time_seconds % 3600) // 60)
                seconds = int(best_time_seconds % 60)
                best_time_formatted = f"{hours}:{minutes:02d}:{seconds:02d}"
            
            # Find best placement
            placements = [p['place'] for p in participations 
                         if p['place'] and isinstance(p['place'], int)]
            best_place = min(placements) if placements else None
            
            veterans.append({
                'name': participations[0]['display_name'],
                'total_participations': total_races,
                'years': years_participated,
                'year_range': f"{years_participated[0]}-{years_participated[-1]}" if len(years_participated) > 1 else str(years_participated[0]),
                'finishes': finishes,
                'dnf': dnfs,
                'dns': dns,
                'finish_rate': round(finishes / total_races * 100, 1) if total_races > 0 else 0,
                'races_50k': races_50k,
                'races_marathon': races_marathon,
                'finishes_50k': finishes_50k,
                'finishes_marathon': finishes_marathon,
                'best_time_formatted': best_time_formatted,
                'best_place': best_place,
                'most_recent_year': years_participated[-1],
                'location': participations[-1]['city'] + ', ' + participations[-1]['state'] if participations[-1]['city'] else participations[-1]['state'],
                'participations': participations
            })
    
    # Sort by total participations (descending), then by name
    veterans.sort(key=lambda x: (-x['total_participations'], x['name']))
    
    # Save to analysis file
    output_file = ANALYSIS_DIR / "veterans.json"
    with open(output_file, 'w') as f:
        json.dump(veterans, f, indent=2)
    
    print(f"✓ Found {len(veterans)} Barkley veterans")
    print(f"  Saved to {output_file}")
    
    # Print top veterans
    print("\nTop 10 Barkley Veterans:")
    for i, vet in enumerate(veterans[:10], 1):
        print(f"  {i}. {vet['name']}: {vet['total_participations']} races ({vet['year_range']}) - {vet['finishes']} finishes")
    
    return veterans

if __name__ == '__main__':
    analyze_veterans()
