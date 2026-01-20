#!/usr/bin/env python3
"""
Get the race date and important dates for a given year.
Allows dynamic workflow scheduling based on actual race dates.
"""

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import re


def get_race_date_for_year(seed_did):
    """
    Get the race date from the UltraSignup event page.
    
    Args: seed_did - any DID for the year (50K or Marathon)
    Returns: datetime object of race date, or None if not found
    """
    url = f"https://ultrasignup.com/results_event.aspx?did={seed_did}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # Get text content
        text = page.text_content('body')
        browser.close()
    
    # Look for date in format "Month DD, YYYY"
    import re
    match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', text)
    
    if match:
        try:
            month_name, day, year = match.groups()
            return datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y")
        except ValueError:
            pass
    
    return None


def calculate_workflow_dates(race_date):
    """
    Given a race date, calculate important workflow dates.
    
    Returns dict with:
    - race_date: the race date
    - results_scrape_start: a few days after race (when results finalize)
    - results_scrape_end: 3 weeks after race (last chance for director corrections)
    - lottery_opens: ~Sept 1st of that year
    - selection_date: ~Halloween (Oct 31)
    - registration_start: July 1st
    - registration_end: day before race
    """
    year = race_date.year
    
    return {
        'race_date': race_date.isoformat(),
        'race_date_obj': race_date,
        
        # Results scraping: start 3 days after race, run weekly for 3 weeks
        'results_scrape_start': (race_date + timedelta(days=3)).isoformat(),
        'results_scrape_end': (race_date + timedelta(days=21)).isoformat(),
        'results_scrape_frequency': 'weekly',  # Every Friday at 2pm UTC
        
        # Entrant tracking: starts when lottery opens (Sept 1)
        'lottery_opens': f"{year}-09-01T00:00:00",
        'selection_date': f"{year}-10-31T23:59:59",  # ~Halloween
        
        # Registration: July 1 through day before race
        'registration_start': f"{year}-07-01T00:00:00",
        'registration_end': (race_date - timedelta(days=1)).isoformat(),
        'registration_tracking_frequency': 'daily',  # Every day during registration
    }


def main():
    # Test with 2025 race
    print("Getting race dates for historical years...")
    
    test_dids = {
        2025: 119817,  # 2025 50K
        2024: 108870,  # 2024 50K
    }
    
    for year, did in test_dids.items():
        race_date = get_race_date_for_year(did)
        if race_date:
            print(f"\n{year} Race Date: {race_date.strftime('%B %d, %Y')}")
            dates = calculate_workflow_dates(race_date)
            print(f"  Results scraping: {dates['results_scrape_start']} to {dates['results_scrape_end']}")
            print(f"  Entrant tracking starts: {dates['lottery_opens']}")
            print(f"  Selection date: {dates['selection_date']}")
            print(f"  Registration: {dates['registration_start']} to {dates['registration_end']}")
        else:
            print(f"\n{year}: Could not find race date")


if __name__ == '__main__':
    main()
