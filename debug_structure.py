#!/usr/bin/env python3
"""Debug script to examine UltraSignup page structure."""

import requests
from bs4 import BeautifulSoup

# Check 2025 50K results
print("=" * 60)
print("2025 50K Results (did=119817)")
print("=" * 60)

r = requests.get('https://ultrasignup.com/results_event.aspx?did=119817')
soup = BeautifulSoup(r.text, 'html.parser')

# Find all tables
tables = soup.find_all('table')
print(f"\nTotal tables on page: {len(tables)}\n")

# Check for jqGrid table
jqgrid = soup.find('table', {'id': 'list'})
if jqgrid:
    print("✓ Found jqGrid table (id='list')")
else:
    print("✗ No jqGrid table found")

# Look for regular results table
for i, table in enumerate(tables[:15]):
    rows = table.find_all('tr')
    if len(rows) > 10:  # Likely a results table
        print(f"\nTable {i}: {len(rows)} rows")
        print(f"  ID: {table.get('id')}")
        print(f"  Class: {table.get('class')}")
        
        # Check first few rows
        for j, row in enumerate(rows[:5]):
            cells = row.find_all(['td', 'th'])
            cell_text = [c.get_text(strip=True)[:20] for c in cells[:10]]
            print(f"  Row {j}: {cell_text}")

print("\n" + "=" * 60)
print("2025 Marathon Results (did=119818)")
print("=" * 60)

r2 = requests.get('https://ultrasignup.com/results_event.aspx?did=119818')
soup2 = BeautifulSoup(r2.text, 'html.parser')

# Look for result count
result_text = soup2.get_text()
if "Finishers" in result_text:
    # Find the text with counts
    lines = result_text.split('\n')
    for line in lines:
        if 'Finisher' in line or 'Did Not' in line:
            print(line.strip())

# Find all tables
tables2 = soup2.find_all('table')
print(f"\nTotal tables on page: {len(tables2)}\n")

for i, table in enumerate(tables2[:15]):
    rows = table.find_all('tr')
    if len(rows) > 10:  # Likely a results table
        print(f"\nTable {i}: {len(rows)} rows")
        print(f"  ID: {table.get('id')}")
        print(f"  Class: {table.get('class')}")
        
        # Check first few rows
        for j, row in enumerate(rows[:5]):
            cells = row.find_all(['td', 'th'])
            cell_text = [c.get_text(strip=True)[:20] for c in cells[:10]]
            print(f"  Row {j}: {cell_text}")
