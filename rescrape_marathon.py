#!/usr/bin/env python3
"""
Re-scrape with detailed logging to see what parsing is doing.
"""

import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_with_logging():
    year = 2025
    did = 119818
    distance = "Marathon"
    url = f"https://ultrasignup.com/results_event.aspx?did={did}"
    
    print(f"Scraping {year} {distance}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        try:
            page.wait_for_selector('table#list', timeout=10000)
        except:
            pass
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        browser.close()
    
    # Parse
    finishers = []
    grid_table = soup.find('table', {'id': 'list'})
    tbody = grid_table.find('tbody')
    rows = tbody.find_all('tr')
    
    print(f"Total rows: {len(rows)}")
    
    def parse_time(time_str):
        """Convert HH:MM:SS to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return None
    
    success_count = 0
    fail_count = 0
    
    for row_idx, row in enumerate(rows):
        row_classes = row.get('class', [])
        row_id = row.get('id', '')
        
        if 'jqgfirstrow' in row_classes or 'jqgroup' in row_classes or not row_id or row_id.startswith('listghead'):
            continue
        
        cells = row.find_all('td')
        if len(cells) < 10:
            continue
        
        try:
            # Parse based on debug info: Cell[1]=place, Cell[2]=first, Cell[3]=last, etc.
            place_text = cells[1].get_text(strip=True)
            first_name = cells[2].get_text(strip=True)
            last_name = cells[3].get_text(strip=True)
            city = cells[4].get_text(strip=True)
            state = cells[5].get_text(strip=True)
            age_text = cells[6].get_text(strip=True)
            division = cells[7].get_text(strip=True)
            time_text = cells[9].get_text(strip=True)
            
            # Parse place
            try:
                place = int(place_text)
            except (ValueError, IndexError):
                if fail_count < 3:
                    print(f"FAIL Row {row_idx}: Could not parse place '{place_text}'")
                fail_count += 1
                continue
            
            # Parse age
            try:
                age = int(age_text)
            except ValueError:
                age = None
            
            # Determine status and time
            status = "Finished"
            finish_time_seconds = None
            
            if time_text.upper() in ["DNF", "DNS", "DQ"]:
                status = time_text.upper()
            else:
                finish_time_seconds = parse_time(time_text)
            
            finisher = {
                'year': year,
                'distance': distance,
                'place': place,
                'first_name': first_name,
                'last_name': last_name,
                'city': city,
                'state': state,
                'age': age,
                'division': division,
                'status': status,
                'finish_time_seconds': finish_time_seconds,
                'finish_time_formatted': time_text
            }
            
            finishers.append(finisher)
            success_count += 1
            
            # Show first 3 and first DNF/DNS examples
            if success_count <= 3:
                print(f"SUCCESS Row {row_idx}: Place={place}, Name={first_name} {last_name}, Time={time_text}, Status={status}")
            elif status in ['DNF', 'DNS']:
                print(f"SUCCESS Row {row_idx}: Place={place}, Name={first_name} {last_name}, Time={time_text}, Status={status}")
                
        except Exception as e:
            if fail_count < 3:
                print(f"EXCEPTION Row {row_idx}: {e}")
            fail_count += 1
    
    print(f"\n=== PARSE RESULTS ===")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Finishers: {len([f for f in finishers if f['status'] == 'Finished'])}")
    print(f"DNF: {len([f for f in finishers if f['status'] == 'DNF'])}")
    print(f"DNS: {len([f for f in finishers if f['status'] == 'DNS'])}")
    
    # Save
    output = {
        'year': year,
        'distance': distance,
        'did': did,
        'scraped_at': datetime.now().isoformat(),
        'total_finishers': len([f for f in finishers if f['status'] == 'Finished']),
        'total_dnf': len([f for f in finishers if f['status'] == 'DNF']),
        'total_dns': len([f for f in finishers if f['status'] == 'DNS']),
        'finishers': finishers
    }
    
    output_file = Path("results_2025_marathon_NEW.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Saved to {output_file}")

if __name__ == '__main__':
    scrape_with_logging()
