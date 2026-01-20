from playwright.sync_api import sync_playwright
from datetime import datetime

url = "https://ultrasignup.com/results_event.aspx?did=119817"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=60000)
    
    # Look for text content on the page
    text = page.text_content('body')
    
    # Search for patterns like "October 24, 2025"
    import re
    patterns = [
        r'(October|September|November|August|July|June|May|April|March|February|January)\s+(\d{1,2}),?\s+(\d{4})',
        r'(\d{1,2})-(\d{1,2})-(\d{4})',
    ]
    
    print("Full text content sample (first 2000 chars):")
    print(text[:2000])
    print("\n" + "="*80)
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            print(f"Found matches for pattern: {pattern}")
            for match in matches[:5]:
                print(f"  {match}")
    
    browser.close()
