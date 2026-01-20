#!/usr/bin/env python3
"""
Check for pagination or filtering controls on the UltraSignup results page.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def check_page_controls():
    url = "https://ultrasignup.com/results_event.aspx?did=119818"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Wait for table
        try:
            page.wait_for_selector('table#list', timeout=10000)
        except:
            pass
        
        # Get page content
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for jqGrid pager
        pager = soup.find('div', {'id': 'pager'})
        if pager:
            print("✓ Found pager controls:")
            print(pager.get_text(strip=True))
        
        # Look for grouping controls
        grouping = soup.find_all(text=lambda t: 'group' in t.lower() if t else False)
        if grouping:
            print(f"\n✓ Found {len(grouping)} references to 'group'")
        
        # Look for filter/search controls
        filters = soup.find_all(['input', 'select', 'button'])
        print(f"\n✓ Found {len(filters)} input/select/button elements")
        
        # Check for DNF/DNS groups specifically
        all_text = soup.get_text()
        if 'Did Not Finish' in all_text:
            print("\n✓ 'Did Not Finish' text found on page")
            # Try to expand groups
            page.wait_for_timeout(2000)
            
            # Look for expand buttons or group headers
            try:
                # Try clicking on group headers to expand
                groups = page.locator('.jqgroup').all()
                print(f"\n✓ Found {len(groups)} jqGrid groups")
                
                for i, group in enumerate(groups):
                    text = group.text_content()
                    print(f"  Group {i+1}: {text}")
                    
                    # Try to expand
                    try:
                        group.click()
                        page.wait_for_timeout(500)
                    except:
                        pass
                
                # Recountafter expanding
                page.wait_for_timeout(1000)
                new_html = page.content()
                new_soup = BeautifulSoup(new_html, 'html.parser')
                grid_table = new_soup.find('table', {'id': 'list'})
                if grid_table:
                    tbody = grid_table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        data_rows = [r for r in rows if r.get('id') and not r.get('id').startswith('listghead') and 'jqgfirstrow' not in r.get('class', [])]
                        print(f"\n✓ After expanding: {len(data_rows)} data rows")
                        
            except Exception as e:
                print(f"Error expanding groups: {e}")
        
        if 'Did Not Start' in all_text:
            print("\n✓ 'Did Not Start' text found on page")
        
        # Keep browser open for manual inspection
        print("\n\nBrowser will stay open for 30 seconds for manual inspection...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    check_page_controls()
