import json
import csv

# Check entrants
with open('data/entrants.json') as f:
    data = json.load(f)
    count = data["count"]
    entrants = len(data["entrants"])
    print(f'Total entrants captured: {count}')
    print(f'Entrant records in dict: {entrants}')
    # Show a sample
    sample = list(data['entrants'].items())[:3]
    for key, entrant in sample:
        print(f'  - {entrant["first_name"]} {entrant["last_name"]} ({entrant["location"]})')

# Check changes
with open('data/changes.json') as f:
    changes = json.load(f)
    print(f'\nChanges recorded: {len(changes)}')
    if changes:
        latest = changes[-1]
        print(f'Latest: {latest["new_count"]} entrants')
        print(f'Total new: {latest["total_new"]}')
        print(f'Total dropped: {latest["total_dropped"]}')

# Check history
print('\nHistory CSV:')
with open('data/history.csv') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i <= 2:  # header + first row
            print(f'  {row}')
