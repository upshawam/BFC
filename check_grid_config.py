#!/usr/bin/env python3
"""
Check the jqGrid configuration to see if grouping is enabled.
"""

from playwright.sync_api import sync_playwright
import re

def check_grid_config():
    url = "https://ultrasignup.com/results_event.aspx?did=119818"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        try:
            page.wait_for_selector('table#list', timeout=10000)
        except:
            pass
        
        # Get the page source
        html = page.content()
        
        # Look for jqGrid initialization
        if 'jqGrid' in html:
            print("✓ jqGrid found in page")
            
            # Look for grouping configuration
            if 'grouping' in html.lower():
                print("✓ Grouping mentioned in page")
                
                # Extract grouping config
                pattern = r'grouping\s*:\s*\{[^}]+\}'
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    print(f"\nGrouping config: {match[:200]}")
            
            # Look for groupField
            if 'groupField' in html:
                print("✓ groupField found")
                pattern = r'groupField\s*:\s*["\']([^"\']+)["\']'
                matches = re.findall(pattern, html)
                for match in matches:
                    print(f"  groupField: {match}")
            
            # Look for status field
            if 'status' in html.lower():
                print("✓ 'status' mentioned in page")
        
        # Check for any JavaScript that might load data
        scripts = page.locator('script').all()
        print(f"\n✓ Found {len(scripts)} script tags")
        
        # Try to evaluate JavaScript to get grid data
        try:
            # Get the number of rows from jqGrid
            row_count = page.evaluate("""() => {
                try {
                    return $('#list').jqGrid('getGridParam', 'reccount');
                } catch(e) {
                    return null;
                }
            }""")
            print(f"\njqGrid reccount: {row_count}")
            
            # Get all row IDs
            row_ids = page.evaluate("""() => {
                try {
                    return $('#list').jqGrid('getDataIDs');
                } catch(e) {
                    return [];
                }
            }""")
            print(f"Row IDs count: {len(row_ids) if row_ids else 0}")
            
            if row_ids and len(row_ids) > 0:
                # Get data for first few rows
                for i, row_id in enumerate(row_ids[:5]):
                    row_data = page.evaluate(f"""() => {{
                        try {{
                            return $('#list').jqGrid('getRowData', '{row_id}');
                        }} catch(e) {{
                            return null;
                        }}
                    }}""")
                    if row_data:
                        print(f"\nRow {i+1} (id={row_id}): {row_data}")
                
                # Look for DNF/DNS
                for row_id in row_ids:
                    row_data = page.evaluate(f"""() => {{
                        try {{
                            return $('#list').jqGrid('getRowData', '{row_id}');
                        }} catch(e) {{
                            return null;
                        }}
                    }}""")
                    if row_data and 'time' in row_data:
                        time_val = row_data.get('time', '').upper()
                        if 'DNF' in time_val or 'DNS' in time_val:
                            print(f"Found {time_val}: {row_data.get('first', '')} {row_data.get('last', '')}")
        except Exception as e:
            print(f"Error evaluating JavaScript: {e}")
        
        browser.close()

if __name__ == '__main__':
    check_grid_config()
