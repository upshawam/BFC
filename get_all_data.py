"""
Get ALL participants including DNF/DNS by examining jqGrid data source
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def get_all_results():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "https://ultrasignup.com/results_event.aspx?did=119818"
        print(f"Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector('table#list', timeout=60000)
        await asyncio.sleep(5)
        
        print("\n=== EXTRACTING ALL JQGRID DATA ===")
        
        # Get all row IDs
        row_ids = await page.evaluate("jQuery('#list').jqGrid('getDataIDs')")
        print(f"Total rows in grid: {len(row_ids)}")
        
        # Collect all rows
        all_rows = []
        status_counts = {}
        
        for row_id in row_ids:
            row_data = await page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{row_id}')")
            all_rows.append(row_data)
            
            status = row_data.get('status', '')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nStatus distribution:")
        for status, count in status_counts.items():
            print(f"  Status '{status}': {count} participants")
        
        print(f"\n=== CHECKING PAGE SOURCE FOR DATA ===")
        # Check if there's a data source in JavaScript
        scripts_content = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script'));
                return scripts.map(s => s.innerHTML).join('\\n');
            }
        """)
        
        # Look for data array or status values
        if '"status"' in scripts_content:
            print("Found 'status' in JavaScript - checking for data arrays...")
            # Extract portion around status
            idx = scripts_content.find('"status"')
            print(scripts_content[max(0, idx-200):idx+200])
        
        print(f"\n=== TRYING TO LOAD DNF/DNS DATA ===")
        # Try to call a function that might load different data
        try:
            # Check if there's a function to filter by status
            has_filter_func = await page.evaluate("""
                () => {
                    return typeof filterResults === 'function' || 
                           typeof loadStatus === 'function' ||
                           typeof showDNF === 'function';
                }
            """)
            print(f"Has filter function: {has_filter_func}")
            
            # Try to access jqGrid's internal data
            grid_data = await page.evaluate("""
                () => {
                    const grid = jQuery('#list');
                    // Try to get the data from the grid's data store
                    const data = grid.jqGrid('getGridParam', 'data');
                    if (data && data.length > 0) {
                        return {count: data.length, sample: data.slice(0, 3)};
                    }
                    return null;
                }
            """)
            print(f"Grid internal data: {grid_data}")
            
            # Check the postData which might contain filters
            post_data = await page.evaluate("jQuery('#list').jqGrid('getGridParam', 'postData')")
            print(f"Grid postData: {post_data}")
            
            # Check the URL where data is loaded from
            datatype = await page.evaluate("jQuery('#list').jqGrid('getGridParam', 'datatype')")
            url_param = await page.evaluate("jQuery('#list').jqGrid('getGridParam', 'url')")
            print(f"Grid datatype: {datatype}, url: {url_param}")
            
        except Exception as e:
            print(f"Error checking filter: {e}")
        
        print(f"\n=== CHECKING NETWORK REQUESTS ===")
        # Let's monitor network to see if data is loaded via AJAX
        print("Reloading page with network monitoring...")
        
        ajax_requests = []
        page.on('request', lambda request: ajax_requests.append({
            'url': request.url,
            'method': request.method,
            'post_data': request.post_data
        }) if 'aspx' in request.url or 'json' in request.url else None)
        
        await page.reload(wait_until='domcontentloaded')
        await page.wait_for_selector('table#list', timeout=60000)
        await asyncio.sleep(5)
        
        print(f"\nCaptured {len(ajax_requests)} AJAX requests:")
        for req in ajax_requests:
            print(f"  {req['method']} {req['url']}")
            if req['post_data']:
                print(f"    POST data: {req['post_data'][:200]}")
        
        # Save sample data
        with open('marathon_jqgrid_data.json', 'w') as f:
            json.dump(all_rows[:10], f, indent=2)
        print(f"\nSaved first 10 rows to marathon_jqgrid_data.json")
        
        print("\nBrowser staying open for manual inspection...")
        await asyncio.sleep(60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_all_results())
