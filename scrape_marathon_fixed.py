"""
Fixed Marathon scraper using jqGrid API to get status codes
"""
import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def scrape_marathon_fixed():
    """Scrape Marathon results using jqGrid JavaScript API"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://ultrasignup.com/results_event.aspx?did=119818"
        print(f"Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector('table#list', timeout=60000)
        await asyncio.sleep(5)
        
        print("Extracting data using jqGrid API...")
        
        # Get all row IDs
        row_ids = await page.evaluate("jQuery('#list').jqGrid('getDataIDs')")
        print(f"Total rows: {len(row_ids)}")
        
        # Collect all rows
        finishers = []
        status_counts = {'1': 0, '2': 0, '3': 0}
        
        for row_id in row_ids:
            row_data = await page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{row_id}')")
            
            # Status codes: 1=Finisher, 2=DNF, 3=DNS
            status_code = str(row_data.get('status', ''))
            status_counts[status_code] = status_counts.get(status_code, 0) + 1
            
            # Map status code to text
            if status_code == '1':
                status = 'Finished'
            elif status_code == '2':
                status = 'DNF'
            elif status_code == '3':
                status = 'DNS'
            else:
                status = 'Unknown'
            
            # Parse place
            place = 0
            try:
                place_text = str(row_data.get('place', '0'))
                if place_text and place_text != '0':
                    place = int(place_text)
            except:
                pass
            
            # Parse time (only for finishers)
            finish_time_seconds = None
            finish_time_formatted = row_data.get('formattime', '')
            
            if status == 'Finished' and finish_time_formatted:
                try:
                    parts = finish_time_formatted.split(':')
                    if len(parts) == 3:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        seconds = int(parts[2])
                        finish_time_seconds = hours * 3600 + minutes * 60 + seconds
                except:
                    pass
            
            # Parse age
            age = None
            try:
                age_text = str(row_data.get('age', ''))
                if age_text and age_text != '':
                    age = int(age_text)
            except:
                pass
            
            finisher_data = {
                'year': 2025,
                'distance': 'Marathon',
                'place': place,
                'first_name': row_data.get('firstname', ''),
                'last_name': row_data.get('lastname', ''),
                'city': row_data.get('city', ''),
                'state': row_data.get('state', ''),
                'age': age,
                'division': row_data.get('agegroup', ''),
                'status': status,
                'finish_time_seconds': finish_time_seconds,
                'finish_time_formatted': finish_time_formatted if status == 'Finished' else ''
            }
            
            finishers.append(finisher_data)
        
        print(f"\nStatus counts:")
        print(f"  Status 1 (Finished): {status_counts.get('1', 0)}")
        print(f"  Status 2 (DNF): {status_counts.get('2', 0)}")
        print(f"  Status 3 (DNS): {status_counts.get('3', 0)}")
        
        # Create output structure
        results = {
            'year': 2025,
            'distance': 'Marathon',
            'did': 119818,
            'scraped_at': datetime.now().isoformat(),
            'total_finishers': status_counts.get('1', 0),
            'total_dnf': status_counts.get('2', 0),
            'total_dns': status_counts.get('3', 0),
            'finishers': finishers
        }
        
        # Save to file
        output_file = 'data/historical/results/results_2025_marathon.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nSaved {len(finishers)} participants to {output_file}")
        print(f"Finishers: {results['total_finishers']}")
        print(f"DNF: {results['total_dnf']}")
        print(f"DNS: {results['total_dns']}")
        
        # Show sample of each status
        print("\nSample Finisher:")
        finished = [f for f in finishers if f['status'] == 'Finished']
        if finished:
            print(f"  {finished[0]['first_name']} {finished[0]['last_name']} - Place {finished[0]['place']} - {finished[0]['finish_time_formatted']}")
        
        print("\nSample DNF:")
        dnf = [f for f in finishers if f['status'] == 'DNF']
        if dnf:
            print(f"  {dnf[0]['first_name']} {dnf[0]['last_name']}")
        
        print("\nSample DNS:")
        dns = [f for f in finishers if f['status'] == 'DNS']
        if dns:
            print(f"  {dns[0]['first_name']} {dns[0]['last_name']}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_marathon_fixed())
