"""
Test 2024 with detailed debugging
"""
from playwright.sync_api import sync_playwright
import time

print("Testing 2024 50K page loading...")
url_50k = "https://ultrasignup.com/results_event.aspx?did=108870"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print(f"Loading {url_50k}")
    page.goto(url_50k, wait_until='domcontentloaded', timeout=90000)
    
    print("Page loaded. Waiting 10 seconds for content to render...")
    time.sleep(10)
    
    # Check if table exists
    try:
        table = page.query_selector('table#list')
        if table:
            print("✓ Table found!")
            
            # Try to get row count
            row_ids = page.evaluate("jQuery('#list').jqGrid('getDataIDs')")
            print(f"✓ Row count: {len(row_ids)}")
            
            # Get first row
            if row_ids:
                first_row = page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{row_ids[0]}')")
                print(f"✓ First row: {first_row}")
        else:
            print("✗ Table not found")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nKeeping browser open for inspection...")
    time.sleep(30)
    browser.close()
