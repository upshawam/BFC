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
# Map of event keys to (display name, url). Add more events here as needed.
EVENTS = {
    'frozen_head_50k': (
        'Frozen Head 50K',
        'https://ultrasignup.com/entrants_event.aspx?did=131025'
    ),
    'other_race_50m': (
        'Other Race 50 Miler',
        'https://ultrasignup.com/entrants_event.aspx?did=127637'
    ),
    'other_race_55k': (
        'Other Race 55K',
        'https://ultrasignup.com/entrants_event.aspx?did=127638'
    )
}

DATA_DIR = Path("data")

def data_paths_for(key: str):
    """Return per-event data file paths for given event key."""
    DATA_DIR.mkdir(exist_ok=True)
    entrants = DATA_DIR / f"entrants_{key}.json"
    changes = DATA_DIR / f"changes_{key}.json"
    history = DATA_DIR / f"history_{key}.csv"
    return entrants, changes, history


class EntrantTracker:
    def __init__(self, event_key: str = 'frozen_head_50k'):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        if event_key not in EVENTS:
            raise ValueError(f"Unknown event key: {event_key}")

        self.event_key = event_key
        self.event_name, self.event_url = EVENTS[event_key]
        self.ENTRANTS_FILE, self.CHANGES_FILE, self.HISTORY_FILE = data_paths_for(event_key)

        # Notification config read from environment variables
        import os
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', '0')) if os.getenv('SMTP_PORT') else None
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.notify_to = os.getenv('NOTIFY_TO')
        self.notify_from = os.getenv('NOTIFY_FROM')
        
    def scrape_entrants(self) -> dict:
        """
        Scrape the entrant list from UltraSignup
        Returns a dictionary with entrant info
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.event_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
            # Count is the actual number of entrants scraped (most reliable source)
            current_count = len(entrants)
            
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
        """Load previously saved entrant data for this event"""
        if self.ENTRANTS_FILE.exists():
            with open(self.ENTRANTS_FILE, 'r') as f:
                return json.load(f)
        return {'count': 0, 'entrants': {}, 'timestamp': None}
    
    def save_current_data(self, data: dict):
        """Save current entrant data for this event"""
        with open(self.ENTRANTS_FILE, 'w') as f:
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
        """Save changes to file for this event"""
        all_changes = []

        if self.CHANGES_FILE.exists():
            with open(self.CHANGES_FILE, 'r') as f:
                try:
                    all_changes = json.load(f)
                except Exception:
                    all_changes = []

        all_changes.append(changes)

        with open(self.CHANGES_FILE, 'w') as f:
            json.dump(all_changes, f, indent=2)
    
    def append_to_history(self, changes: dict):
        """Append changes to CSV history file for this event"""
        file_exists = self.HISTORY_FILE.exists()

        with open(self.HISTORY_FILE, 'a', newline='') as f:
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

    def send_notification(self, changes: dict):
        """Send an email notification if SMTP config is present."""
        # Only attempt to send if configured
        if not (self.smtp_host and self.notify_to and self.notify_from):
            return

        try:
            import smtplib
            from email.message import EmailMessage

            subject = f"[{self.event_name}] Entrant list changed: {changes['count_change']:+d}"
            body_lines = [f"Event: {self.event_name}", f"Time: {changes['timestamp']}", f"Net change: {changes['count_change']}\n"]
            if changes.get('total_new'):
                body_lines.append(f"New entrants: {changes['total_new']}")
            if changes.get('total_dropped'):
                body_lines.append(f"Dropped entrants: {changes['total_dropped']}")

            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = self.notify_from
            msg['To'] = self.notify_to
            msg.set_content('\n'.join(body_lines))

            # Connect and send
            if self.smtp_port:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_host, timeout=10)

            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except Exception:
                pass

            if self.smtp_user and self.smtp_pass:
                server.login(self.smtp_user, self.smtp_pass)

            server.send_message(msg)
            server.quit()
            print(f"✓ Notification sent to {self.notify_to}")
        except Exception as e:
            print(f"Warning: failed to send notification: {e}")
    
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
        if previous_data.get('count', 0) > 0:
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

            # Send notification if configured and there was a change
            if changes['count_change'] != 0:
                self.send_notification(changes)
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
        print(f"\n✓ Data saved to {self.ENTRANTS_FILE}")
        print(f"✓ Changes logged to {self.CHANGES_FILE}")
        print(f"✓ History updated in {self.HISTORY_FILE}")

if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Entrant list tracker (multi-event)')
    parser.add_argument('--event', '-e', help='Event key to track (overrides EVENT_KEY env var)')
    args = parser.parse_args()

    event_key = args.event or os.getenv('EVENT_KEY', 'frozen_head_50k')
    tracker = EntrantTracker(event_key=event_key)
    print(f"Tracking event: {tracker.event_name} (key={tracker.event_key})")
    tracker.run()
