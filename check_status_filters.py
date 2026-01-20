"""
Check if there are radio buttons or links to filter by status (Finishers/DNF/DNS)
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def check_filters():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "https://ultrasignup.com/results_event.aspx?did=119818"
        print(f"Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector('table#list', timeout=60000)
        await asyncio.sleep(3)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n=== LOOKING FOR STATUS LABELS/LINKS ===")
        # Find the labels that say "Finishers - 198", etc.
        status_labels = soup.find_all('b')
        for label in status_labels:
            text = label.get_text(strip=True)
            if any(word in text for word in ['Finisher', 'Did Not', 'DNS', 'DNF']):
                print(f"Found label: {text}")
                parent = label.parent
                print(f"  Parent tag: {parent.name}, class: {parent.get('class')}, id: {parent.get('id')}")
                
                # Check if the parent or nearby elements are clickable
                if parent.name == 'a':
                    print(f"  LINK! href: {parent.get('href')}, onclick: {parent.get('onclick')}")
                
                # Check siblings
                siblings = list(parent.next_siblings)
                for sib in siblings[:3]:
                    if hasattr(sib, 'name'):
                        print(f"  Next sibling: {sib.name}, text: {sib.get_text(strip=True)[:50]}")
        
        print("\n=== LOOKING FOR RADIO BUTTONS ===")
        radios = soup.find_all('input', {'type': 'radio'})
        for radio in radios:
            print(f"Radio: name={radio.get('name')}, value={radio.get('value')}, id={radio.get('id')}, checked={radio.get('checked')}")
            label = soup.find('label', {'for': radio.get('id')})
            if label:
                print(f"  Label: {label.get_text(strip=True)}")
        
        print("\n=== CHECKING FOR ONCLICK/HREF WITH 'status' ===")
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            onclick = link.get('onclick', '')
            if 'status' in href.lower() or 'status' in onclick.lower():
                print(f"Found status link: {link.get_text(strip=True)[:50]}")
                print(f"  href: {href}")
                print(f"  onclick: {onclick}")
        
        print("\n=== TRYING TO CLICK ON 'Did Not Finish' ===")
        # Look for the "Did Not Finish" text and try to click it
        try:
            # Find element containing "Did Not Finish"
            dnf_element = await page.query_selector('text="Did Not Finish - 188"')
            if dnf_element:
                print("Found 'Did Not Finish - 188' element")
                # Check if it's clickable
                is_clickable = await dnf_element.evaluate('el => el.tagName === "A" || el.onclick != null')
                print(f"  Is clickable: {is_clickable}")
                
                if is_clickable or True:  # Try clicking anyway
                    print("  Attempting to click...")
                    await dnf_element.click()
                    await asyncio.sleep(3)
                    
                    # Check how many rows now
                    record_count = await page.evaluate("jQuery('#list').jqGrid('getGridParam', 'reccount')")
                    print(f"  After click - record count: {record_count}")
                    
                    # Get a sample row
                    row_ids = await page.evaluate("jQuery('#list').jqGrid('getDataIDs')")
                    if row_ids:
                        row_data = await page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{row_ids[0]}')")
                        print(f"  Sample row: {row_data}")
        except Exception as e:
            print(f"Error clicking DNF: {e}")
        
        print("\n=== CHECKING URL PARAMETERS ===")
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        print("\nBrowser staying open for 60 seconds - manually click on status filters...")
        await asyncio.sleep(60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_filters())
