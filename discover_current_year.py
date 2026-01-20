#!/usr/bin/env python3
"""
Discover current/next year Barkley Fall Classic registration.
Given a seed DID (any year's event), navigate to registration and find the
"See the current year event" link to auto-discover the next year's eid.
"""

from playwright.sync_api import sync_playwright
import re
import json


def discover_current_year_event(seed_did):
    """
    Given a seed DID (from any BFC year), discover the current year registration.
    
    Returns: {year: int, eid: int, did_50k: int, registration_url: str}
    """
    # Start from the seed event's registration page
    reg_url = f"https://ultrasignup.com/register.aspx?did={seed_did}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(reg_url, wait_until='domcontentloaded', timeout=60000)
        
        # Look for the "See the [year] event" link
        link_elem = page.query_selector('a#ContentPlaceHolder1_hlCurrentEventPage')
        if not link_elem:
            browser.close()
            return None
        
        href = link_elem.get_attribute('href')
        link_text = link_elem.inner_text()
        browser.close()
    
    if not href or 'eid=' not in href:
        return None
    
    # Extract eid from href
    try:
        eid = int(re.search(r'eid=(\d+)', href).group(1))
    except (AttributeError, ValueError):
        return None
    
    # Extract year from link text (e.g., "See the 2026 event" -> 2026)
    year_match = re.search(r'(\d{4})', link_text)
    year = int(year_match.group(1)) if year_match else None
    
    return {
        'year': year,
        'eid': eid,
        'registration_url': f"https://ultrasignup.com/register.aspx?eid={eid}",
        'href': href
    }


def discover_year_50k_did(year_eid):
    """
    From a registration page EID, scrape the 50K event DID.
    This will be used as the seed for fetching marathon DID via toggle links.
    """
    url = f"https://ultrasignup.com/register.aspx?eid={year_eid}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # Look for a link to the event results or entry page that contains did=
        # Often in the page there's a link like: /results_event.aspx?did=XXXXX
        scripts = page.evaluate("document.documentElement.outerHTML")
        browser.close()
    
    # Search for did parameter in the HTML
    matches = re.findall(r'did=(\d+)', scripts)
    if matches:
        # Return the first unique DID (likely the 50K)
        return int(matches[0])
    
    return None


def main():
    # Start with a known seed (2025 50K)
    seed_did = 119817
    
    print(f"Starting discovery from seed DID: {seed_did}")
    print(f"Registration page: https://ultrasignup.com/register.aspx?did={seed_did}")
    
    event = discover_current_year_event(seed_did)
    print(f"\nDiscovered next year event:")
    print(json.dumps(event, indent=2))
    
    if event:
        print(f"\n2026 Registration URL: {event['registration_url']}")
        print(f"EID: {event['eid']}")
        print(f"Year: {event['year']}")


if __name__ == '__main__':
    main()
