#!/usr/bin/env python3
"""
Analyze entrant tracking data and generate reports
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = Path("data")
CHANGES_FILE = DATA_DIR / "changes.json"
HISTORY_FILE = DATA_DIR / "history.csv"

class TrackerAnalysis:
    def __init__(self):
        self.changes = self.load_changes()
        self.history = self.load_history()
    
    def load_changes(self) -> list:
        """Load all change records"""
        if CHANGES_FILE.exists():
            with open(CHANGES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def load_history(self) -> list:
        """Load history CSV"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return list(csv.DictReader(f))
        return []
    
    def total_waitlist_admits(self) -> int:
        """
        Calculate total people who've moved from waitlist to entrants
        This is the sum of all new entrants
        """
        total = 0
        for change in self.changes:
            total += change.get('total_new', 0)
        return total
    
    def total_dropouts(self) -> int:
        """Calculate total people who've dropped out"""
        total = 0
        for change in self.changes:
            total += change.get('total_dropped', 0)
        return total
    
    def average_daily_admits(self) -> float:
        """Calculate average daily admissions from waitlist"""
        if not self.changes or len(self.changes) < 2:
            return 0.0
        
        first_timestamp = self.changes[0]['timestamp']
        last_timestamp = self.changes[-1]['timestamp']
        
        try:
            first_date = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00'))
            last_date = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
            days_elapsed = (last_date - first_date).days
            
            if days_elapsed > 0:
                return self.total_waitlist_admits() / days_elapsed
        except:
            pass
        
        return 0.0
    
    def current_entrant_count(self) -> int:
        """Get current entrant count"""
        if self.changes:
            return self.changes[-1]['new_count']
        return 0
    
    def estimate_days_to_capacity(self, capacity: int = 500) -> float:
        """
        Estimate days until event reaches capacity
        Based on current growth rate
        """
        current = self.current_entrant_count()
        remaining = capacity - current
        daily_rate = self.average_daily_admits()
        
        if daily_rate <= 0:
            return float('inf')
        
        return remaining / daily_rate
    
    def get_recent_changes(self, days: int = 7) -> list:
        """Get changes from last N days"""
        if not self.changes:
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for change in self.changes:
            try:
                change_date = datetime.fromisoformat(change['timestamp'].replace('Z', '+00:00'))
                if change_date >= cutoff:
                    recent.append(change)
            except:
                pass
        
        return recent
    
    def print_summary(self):
        """Print a summary report"""
        print("\n" + "="*60)
        print("ENTRANT TRACKING ANALYSIS")
        print("="*60)
        
        print(f"\nCurrent Entrants: {self.current_entrant_count()}")
        print(f"Total Waitlist Admits: {self.total_waitlist_admits()}")
        print(f"Total Dropouts: {self.total_dropouts()}")
        print(f"Days Tracked: {len(self.changes)}")
        
        avg_daily = self.average_daily_admits()
        print(f"Average Daily Admits: {avg_daily:.2f}")
        
        # Estimate for 500 capacity
        days_to_500 = self.estimate_days_to_capacity(500)
        if days_to_500 != float('inf'):
            print(f"Est. Days to 500 entrants: {days_to_500:.1f}")
            if days_to_500 > 0:
                est_date = datetime.now() + timedelta(days=days_to_500)
                print(f"Est. Date to reach 500: {est_date.strftime('%Y-%m-%d')}")
        
        # Recent activity
        recent = self.get_recent_changes(7)
        if recent:
            print(f"\n--- Last 7 Days Activity ---")
            for change in recent[-5:]:  # Show last 5
                ts = change['timestamp']
                change_val = change['count_change']
                new_count = change['new_count']
                print(f"  {ts[:10]} | Count: {new_count:3d} | Change: {change_val:+3d} ({change['total_new']:+d}↑ {change['total_dropped']:+d}↓)")
        
        print("\n" + "="*60)
    
    def generate_csv_summary(self, filename: str = "summary.csv"):
        """Generate a summary CSV"""
        if not self.history:
            print("No history data available")
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Entrant_Count', 'Daily_Change', 'New_from_Waitlist', 'Dropouts'])
            
            for row in self.history:
                writer.writerow([
                    row['Date'][:10],
                    row['Total_Entrants'],
                    row['Net_Change'],
                    row['New_Entrants'],
                    row['Dropped_Entrants']
                ])
        
        print(f"✓ Summary saved to {filename}")

if __name__ == "__main__":
    analysis = TrackerAnalysis()
    analysis.print_summary()
    
    # Optionally generate summary CSV
    # analysis.generate_csv_summary("summary.csv")
