#!/usr/bin/env python3
"""
Ultramarathon Entrant List Tracker
Scrapes and tracks changes in entrant lists from UltraSignup
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from pathlib import Path
import hashlib

# Configuration
EVENT_URL = "https://ultrasignup.com/entrants_event.aspx?did=131025"
DATA_DIR = Path("data")
ENTRANTS_FILE = DATA_DIR / "entrants.json"
CHANGES_FILE = DATA_DIR / "changes.json"
HISTORY_FILE = DATA_DIR / "history.csv"

class EntrantTracker:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        
    def scrape_entrants(self) -> dict:
        """
        Scrape the entrant list from UltraSignup
        Returns a dictionary with entrant info
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(EVENT_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract entrant count from page text
            # Looking for "498 Entrants" pattern
            current_count = 0
            for text in soup.strings:
                text_str = str(text).strip()
                if "Entrants" in text_str and any(c.isdigit() for c in text_str):
                    # Extract first number
                    import re
                    match = re.search(r'(\d+)\s+Entrants', text_str)
                    if match:
                        current_count = int(match.group(1))
                        if current_count > 500:  # The "2026 The Barkley..." has 2026 in it
                            current_count = 0  # Reset, keep looking
                        elif current_count < 500:  # 498 is the right one
                            break
            
            entrants = {}
            
            # Find the main entrants table (table index 2 based on page structure)
            tables = soup.find_all('table')
            if len(tables) >= 3:
                table = tables[2]  # The entrants table
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    # Columns: [0]Rank%, [1]AgeRank%, [2]Results, [3]Target, [4]Age, [5]empty, [6]First, [7]Last, [8]City, [9]Location, [10]empty, [11]Bib, [12]Finishes, [13]Results-link
                    if len(cells) >= 10:
                        try:
                            first_name = cells[6].text.strip()
                            last_name = cells[7].text.strip()
                            city = cells[8].text.strip()
                            location = cells[9].text.strip()
                            age = cells[4].text.strip()
                            
                            # Validate that we have a real entrant (not empty)
                            if first_name and last_name:
                                # Create a unique key for the entrant
                                entrant_key = f"{first_name}_{last_name}_{location}".lower()
                                entrants[entrant_key] = {
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'city': city,
                                    'location': location,
                                    'age': age
                                }
                        except (IndexError, AttributeError):
                            continue
            
            return {
                'count': current_count,
                'entrants': entrants,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error scraping entrants: {e}")
            import traceback
            traceback.print_exc()
            return {'count': 0, 'entrants': {}, 'timestamp': datetime.now().isoformat()}
    
    def load_previous_data(self) -> dict:
        """Load previously saved entrant data"""
        if ENTRANTS_FILE.exists():
            with open(ENTRANTS_FILE, 'r') as f:
                return json.load(f)
        return {'count': 0, 'entrants': {}, 'timestamp': None}
    
    def save_current_data(self, data: dict):
        """Save current entrant data"""
        with open(ENTRANTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def find_changes(self, previous: dict, current: dict) -> dict:
        """
        Compare previous and current data to find changes
        Matches entrants by name and location
        """
        prev_entrants = set(previous.get('entrants', {}).keys())
        curr_entrants = set(current.get('entrants', {}).keys())
        
        new_entrants = curr_entrants - prev_entrants
        dropped_entrants = prev_entrants - curr_entrants
        
        # Build detailed lists
        new_list = []
        for key in sorted(new_entrants):
            entrant = current['entrants'][key].copy()
            entrant['key'] = key
            new_list.append(entrant)
        
        dropped_list = []
        for key in sorted(dropped_entrants):
            entrant = previous['entrants'][key].copy()
            entrant['key'] = key
            dropped_list.append(entrant)
        
        changes = {
            'timestamp': datetime.now().isoformat(),
            'count_change': current['count'] - previous.get('count', 0),
            'new_count': current['count'],
            'previous_count': previous.get('count', 0),
            'new_entrants': new_list,
            'dropped_entrants': dropped_list,
            'total_new': len(new_entrants),
            'total_dropped': len(dropped_entrants)
        }
        
        return changes
    
    def save_changes(self, changes: dict):
        """Save changes to file"""
        all_changes = []
        
        if CHANGES_FILE.exists():
            with open(CHANGES_FILE, 'r') as f:
                all_changes = json.load(f)
        
        all_changes.append(changes)
        
        with open(CHANGES_FILE, 'w') as f:
            json.dump(all_changes, f, indent=2)
    
    def append_to_history(self, changes: dict):
        """Append changes to CSV history file"""
        file_exists = HISTORY_FILE.exists()
        
        with open(HISTORY_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow([
                    'Date', 'Total_Entrants', 'Previous_Count', 'New_Entrants', 
                    'Dropped_Entrants', 'Net_Change'
                ])
            
            writer.writerow([
                changes['timestamp'],
                changes['new_count'],
                changes['previous_count'],
                changes['total_new'],
                changes['total_dropped'],
                changes['count_change']
            ])
    
    def run(self):
        """Execute the tracker"""
        print(f"[{datetime.now().isoformat()}] Starting entrant tracking...")
        
        # Scrape current data
        print("Scraping entrant list...")
        current_data = self.scrape_entrants()
        print(f"Found {current_data['count']} entrants")
        
        # Load previous data
        previous_data = self.load_previous_data()
        
        # Find changes
        if previous_data['count'] > 0:
            changes = self.find_changes(previous_data, current_data)
            
            print(f"\n=== CHANGES DETECTED ===")
            print(f"Previous count: {changes['previous_count']}")
            print(f"Current count: {changes['new_count']}")
            print(f"Net change: {changes['count_change']:+d}")
            print(f"New entrants: {changes['total_new']}")
            print(f"Dropped entrants: {changes['total_dropped']}")
            
            if changes['new_entrants']:
                print(f"\n--- New Entrants ({len(changes['new_entrants'])}) ---")
                for entrant in changes['new_entrants'][:10]:  # Show first 10
                    print(f"  {entrant['first_name']} {entrant['last_name']} ({entrant['location']})")
                if len(changes['new_entrants']) > 10:
                    print(f"  ... and {len(changes['new_entrants']) - 10} more")
            
            if changes['dropped_entrants']:
                print(f"\n--- Dropped Entrants ({len(changes['dropped_entrants'])}) ---")
                for entrant in changes['dropped_entrants'][:10]:  # Show first 10
                    print(f"  {entrant['first_name']} {entrant['last_name']} ({entrant['location']})")
                if len(changes['dropped_entrants']) > 10:
                    print(f"  ... and {len(changes['dropped_entrants']) - 10} more")
            
            # Save changes
            self.save_changes(changes)
            self.append_to_history(changes)
        else:
            print("No previous data to compare. This is the first run.")
            # Still create baseline files for first run
            changes = {
                'timestamp': datetime.now().isoformat(),
                'count_change': 0,
                'new_count': current_data['count'],
                'previous_count': 0,
                'new_entrants': [],
                'dropped_entrants': [],
                'total_new': 0,
                'total_dropped': 0
            }
            self.save_changes(changes)
            self.append_to_history(changes)
        
        # Save current data
        self.save_current_data(current_data)
        print(f"\n✓ Data saved to {ENTRANTS_FILE}")
        print(f"✓ Changes logged to {CHANGES_FILE}")
        print(f"✓ History updated in {HISTORY_FILE}")

if __name__ == "__main__":
    tracker = EntrantTracker()
    tracker.run()
