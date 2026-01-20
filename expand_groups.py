#!/usr/bin/env python3
"""
Try to expand all groups and get DNF/DNS data.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def scrape_with_groups():
    url = "https://ultrasignup.com/results_event.aspx?did=119818"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Wait for table
        try:
            page.wait_for_selector('table#list', timeout=10000)
            print("✓ Table loaded")
        except:
            print("✗ Table not found")
            return
        
        # Look for group headers
        try:
            # Find all group header rows (they have class 'jqgroup')
            page.wait_for_timeout(2000)
            
            # Get current row count
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            grid_table = soup.find('table', {'id': 'list'})
            tbody = grid_table.find('tbody')
            rows = tbody.find_all('tr')
            
            # Count different row types
            data_rows = []
            group_rows = []
            for row in rows:
                row_classes = row.get('class', [])
                row_id = row.get('id', '')
                
                if 'jqgroup' in row_classes:
                    group_rows.append(row)
                    # Get text of group header
                    text = row.get_text(strip=True)
                    print(f"Found group: {text}")
                elif row_id and not row_id.startswith('listghead') and 'jqgfirstrow' not in row_classes:
                    data_rows.append(row)
            
            print(f"\nGroups found: {len(group_rows)}")
            print(f"Data rows found: {len(data_rows)}")
            
            # Try clicking on each group header to expand
            if len(group_rows) > 0:
                print("\nAttempting to expand groups...")
                
                # Use Playwright to click on group headers
                group_elements = page.locator('tr.jqgroup').all()
                print(f"Playwright found {len(group_elements)} group elements")
                
                for i, group in enumerate(group_elements):
                    try:
                        text = group.text_content()
                        print(f"Clicking group {i+1}: {text}")
                        group.click()
                        page.wait_for_timeout(500)
                    except Exception as e:
                        print(f"Error clicking group {i+1}: {e}")
                
                # Re-count after expanding
                page.wait_for_timeout(2000)
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                grid_table = soup.find('table', {'id': 'list'})
                tbody = grid_table.find('tbody')
                rows = tbody.find_all('tr')
                
                new_data_rows = []
                for row in rows:
                    row_classes = row.get('class', [])
                    row_id = row.get('id', '')
                    
                    if row_id and not row_id.startswith('listghead') and 'jqgfirstrow' not in row_classes and 'jqgroup' not in row_classes:
                        new_data_rows.append(row)
                        
                        # Check for DNF/DNS
                        cells = row.find_all('td')
                        if len(cells) > 9:
                            time_text = cells[9].get_text(strip=True)
                            if time_text.upper() in ['DNF', 'DNS']:
                                first = cells[2].get_text(strip=True)
                                last = cells[3].get_text(strip=True)
                                print(f"Found {time_text}: {first} {last}")
                
                print(f"\nData rows after expanding: {len(new_data_rows)}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Keep browser open
        print("\nKeeping browser open for manual inspection (60 seconds)...")
        page.wait_for_timeout(60000)
        
        browser.close()

if __name__ == '__main__':
    scrape_with_groups()
