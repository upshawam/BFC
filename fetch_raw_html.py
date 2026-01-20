#!/usr/bin/env python3
"""
Manual test - fetch and save the raw HTML from the 2025 Marathon results page
to examine the actual structure.
"""

import requests
from pathlib import Path

url = "https://ultrasignup.com/results_event.aspx?did=119818"
print(f"Fetching: {url}")

response = requests.get(url)
html = response.text

# Save to file for examination
output = Path("marathon_2025_raw.html")
with open(output, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Saved raw HTML to: {output}")
print(f"File size: {len(html)} bytes")

# Look for key patterns
if 'Finisher' in html:
    print("\n✓ Found 'Finisher' in HTML")
if 'Did Not Finish' in html or 'DNF' in html:
    print("✓ Found DNF references")
if 'Did Not Start' in html or 'DNS' in html:
    print("✓ Found DNS references")

# Check for jqGrid
if 'id="list"' in html:
    print("✓ Found jqGrid table (id='list')")
else:
    print("✗ No jqGrid table in initial HTML (requires JavaScript)")

# Look for result counts in text
import re
patterns = [
    r'(\d+)\s+Finisher',
    r'Did Not Finish\s*-\s*(\d+)',
    r'Did Not Start\s*-\s*(\d+)',
]

for pattern in patterns:
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        print(f"Pattern '{pattern}': {matches}")
