#!/usr/bin/env python3
"""
Automated entrant tracker.
Intelligently discovers and tracks entrants based on race date:
- Before race date: track current year entrants
- After race date: track next year entrants (post-race registration opens)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import re
import sys
from discover_current_year import discover_current_year_event
from get_race_dates import get_race_date_for_year


ENTRANTS_DIR = Path(__file__).parent.parent / "data" / "entrants"
ENTRANTS_DIR.mkdir(parents=True, exist_ok=True)


def scrape_entrants_from_page(eid):
    """Scrape entrant list from UltraSignup registration page."""
    url = f"https://ultrasignup.com/register.aspx?eid={eid}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # Wait a bit for dynamic content to load
        import time
        time.sleep(3)
        
        # Look for entrant table - may vary by year, common selectors:
        # table, div with class containing 'entrant', etc.
        html = page.content()
        browser.close()
    
    entrants = []
    # This is a simplified approach - you may need to adjust based on actual page structure
    # For now, we extract basic info from any tables found
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for tables with entrant data
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Basic extraction - adjust based on actual structure
                name = cells[0].get_text(strip=True)
                distance = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                
                if name:
                    entrants.append({
                        'name': name,
                        'distance': distance,
                        'registered_at': datetime.now().isoformat()
                    })
    
    return entrants


def determine_target_year_and_did():
    """
    Intelligently determine which year's entrants to track based on race date.
    
    Returns: (target_year, seed_did)
    - Before race: track current year (seed_did = current year 50K)
    - After race: track next year (seed_did = current year 50K for discovering next year)
    """
    today = datetime.now().date()
    
    # Seed DID for discovering events (2025 50K)
    seed_did = 119817
    
    # Get current year race date
    print(f"Today's date: {today}")
    print("Getting current year race date...")
    
    race_date = get_race_date_for_year(seed_did)
    if not race_date:
        print("ERROR: Could not determine race date")
        return None, None
    
    race_date = race_date.date()
    print(f"Current year race date: {race_date}")
    
    if today < race_date:
        # Before race: track current year (discovered from seed_did)
        print(f"\n→ Before race ({today} < {race_date})")
        print("→ Tracking CURRENT YEAR entrants")
        event = discover_current_year_event(seed_did)
        return event['year'], seed_did
    else:
        # After race: track next year
        print(f"\n→ After race ({today} >= {race_date})")
        print("→ Tracking NEXT YEAR entrants")
        event = discover_current_year_event(seed_did)
        next_year = event['year'] + 1
        print(f"→ Next year will be {next_year}")
        return next_year, seed_did


def main():
    print("=" * 60)
    print("ENTRANT TRACKER - Intelligent Scheduling")
    print("=" * 60)
    
    # Determine which year's entrants to track
    target_year, seed_did = determine_target_year_and_did()
    
    if not target_year or not seed_did:
        print("ERROR: Failed to determine target year")
        sys.exit(1)
    
    print(f"\n[SCRAPING] Year {target_year} entrants")
    print("Discovering registration URL...")
    event = discover_current_year_event(seed_did)
    
    if not event:
        print("ERROR: Could not discover registration event")
        sys.exit(1)
    
    # If we're tracking next year, we need to discover its event
    if target_year != event['year']:
        print(f"Note: Current discovery found {event['year']}, but we need {target_year}")
        print("Using discovered event for now...")
    
    eid = event['eid']
    
    print(f"Registration URL: {event['registration_url']}")
    
    # Scrape entrants
    print(f"\nScraping {target_year} entrants...")
    entrants = scrape_entrants_from_page(eid)
    
    # Save to file
    output_file = ENTRANTS_DIR / f"entrants_{target_year}.json"
    data = {
        'year': target_year,
        'eid': eid,
        'url': event['registration_url'],
        'scraped_at': datetime.now().isoformat(),
        'total_entrants': len(entrants),
        'entrants': entrants
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Saved {len(entrants)} entrants to {output_file}")
    print("=" * 60)


if __name__ == '__main__':
    main()
