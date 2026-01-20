"""
Investigate how UltraSignup displays Finishers/DNF/DNS data
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def investigate_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "https://ultrasignup.com/results_event.aspx?did=119818"
        print(f"Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # Wait for jqGrid to load
        await page.wait_for_selector('table#list', timeout=60000)
        await asyncio.sleep(3)
        
        # Get the HTML content
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== SEARCHING FOR STATUS INDICATORS ===")
        # Look for text mentioning Finishers, DNF, DNS
        status_keywords = ["Finishers", "Did Not Finish", "Did Not Start", "DNF", "DNS"]
        for keyword in status_keywords:
            elements = soup.find_all(string=lambda text: text and keyword in text)
            if elements:
                print(f"\nFound '{keyword}':")
                for elem in elements[:3]:  # Show first 3 matches
                    parent = elem.parent
                    print(f"  Tag: {parent.name}, Class: {parent.get('class')}, Text: {elem.strip()[:100]}")
        
        print("\n=== CHECKING FOR FILTER/TAB CONTROLS ===")
        # Look for buttons, links, or tabs that might filter results
        buttons = soup.find_all(['button', 'a', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['tab', 'filter', 'status', 'button']))
        for btn in buttons[:10]:
            print(f"Element: {btn.name}, Class: {btn.get('class')}, Text: {btn.get_text(strip=True)[:50]}, ID: {btn.get('id')}")
        
        print("\n=== EXAMINING JQGRID TABLE STRUCTURE ===")
        # Get jqGrid column headers
        headers = soup.select('table#list thead th')
        print(f"Column headers ({len(headers)}):")
        for i, header in enumerate(headers):
            print(f"  Col {i}: {header.get_text(strip=True)}, ID: {header.get('id')}")
        
        print("\n=== CHECKING FOR JAVASCRIPT VARIABLES ===")
        # Check if there are any inline scripts that might contain data
        scripts = soup.find_all('script')
        for script in scripts:
            script_text = script.string if script.string else ""
            if 'DNF' in script_text or 'DNS' in script_text or 'status' in script_text.lower():
                print(f"Found script with status references:")
                print(f"  {script_text[:200]}...")
                break
        
        print("\n=== USING JAVASCRIPT TO INSPECT JQGRID DATA ===")
        # Try to get data directly from jqGrid
        try:
            # Get total record count
            record_count = await page.evaluate("jQuery('#list').jqGrid('getGridParam', 'reccount')")
            print(f"jqGrid record count: {record_count}")
            
            # Get all row IDs
            row_ids = await page.evaluate("jQuery('#list').jqGrid('getDataIDs')")
            print(f"Total row IDs: {len(row_ids)}")
            
            # Get first few rows of data
            print("\nSample row data:")
            for i, row_id in enumerate(row_ids[:5]):
                row_data = await page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{row_id}')")
                print(f"  Row {i+1} (ID={row_id}): {row_data}")
            
            # Check for any row with DNF or DNS
            print("\nSearching for DNF/DNS in row data...")
            dnf_count = 0
            dns_count = 0
            for row_id in row_ids:
                row_data = await page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{row_id}')")
                row_str = str(row_data)
                if 'DNF' in row_str:
                    dnf_count += 1
                    if dnf_count <= 3:
                        print(f"  Found DNF: {row_data}")
                if 'DNS' in row_str:
                    dns_count += 1
                    if dns_count <= 3:
                        print(f"  Found DNS: {row_data}")
            
            print(f"\nDNF count in jqGrid data: {dnf_count}")
            print(f"DNS count in jqGrid data: {dns_count}")
            
        except Exception as e:
            print(f"Error inspecting jqGrid: {e}")
        
        print("\n=== CHECKING FOR DROPDOWN/SELECT CONTROLS ===")
        # Look for select/dropdown that might filter by status
        selects = soup.find_all('select')
        for select in selects:
            print(f"Select: ID={select.get('id')}, Name={select.get('name')}")
            options = select.find_all('option')
            for opt in options:
                print(f"  Option: value={opt.get('value')}, text={opt.get_text(strip=True)}")
        
        print("\n\nBrowser window will stay open for 60 seconds for manual inspection...")
        print("Check if there are any visible controls to show DNF/DNS participants")
        await asyncio.sleep(60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(investigate_page())
