#!/usr/bin/env python3
"""Debug script using Playwright to see rendered content."""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def check_50k():
    print("=" * 80)
    print("2025 50K Results (did=119817)")
    print("=" * 80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://ultrasignup.com/results_event.aspx?did=119817', wait_until='networkidle', timeout=30000)
        
        # Wait for table
        try:
            page.wait_for_selector('table#list', timeout=10000)
        except:
            pass
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        browser.close()
    
    # Find jqGrid table
    grid_table = soup.find('table', {'id': 'list'})
    if grid_table:
        tbody = grid_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"\nTotal rows in tbody: {len(rows)}")
            
            # Check first 5 data rows
            data_rows = 0
            for i, row in enumerate(rows):
                row_id = row.get('id', '')
                row_classes = row.get('class', [])
                
                # Skip structure/grouping rows
                if 'jqgfirstrow' in row_classes or 'jqgroup' in row_classes or not row_id or row_id.startswith('listghead'):
                    continue
                
                cells = row.find_all('td')
                if len(cells) < 10:
                    continue
                
                data_rows += 1
                if data_rows <= 5:
                    print(f"\nRow {data_rows} (id={row_id}):")
                    for j, cell in enumerate(cells[:12]):
                        text = cell.get_text(strip=True)
                        print(f"  Cell[{j}]: {text[:40]}")
            
            print(f"\nTotal data rows found: {data_rows}")

def check_marathon():
    print("\n" + "=" * 80)
    print("2025 Marathon Results (did=119818)")
    print("=" * 80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://ultrasignup.com/results_event.aspx?did=119818', wait_until='networkidle', timeout=30000)
        
        # Wait for table
        try:
            page.wait_for_selector('table#list', timeout=10000)
        except:
            pass
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        browser.close()
    
    # Find jqGrid table
    grid_table = soup.find('table', {'id': 'list'})
    if grid_table:
        tbody = grid_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"\nTotal rows in tbody: {len(rows)}")
            
            # Check first 5 data rows
            data_rows = 0
            for i, row in enumerate(rows):
                row_id = row.get('id', '')
                row_classes = row.get('class', [])
                
                # Skip structure/grouping rows
                if 'jqgfirstrow' in row_classes or 'jqgroup' in row_classes or not row_id or row_id.startswith('listghead'):
                    continue
                
                cells = row.find_all('td')
                if len(cells) < 10:
                    continue
                
                data_rows += 1
                if data_rows <= 3:
                    print(f"\nRow {data_rows} (id={row_id}):")
                    for j, cell in enumerate(cells[:12]):
                        text = cell.get_text(strip=True)
                        print(f"  Cell[{j}]: {text[:40]}")
                elif data_rows <= 6 and 'DNF' in ' '.join([c.get_text(strip=True) for c in cells]):
                    print(f"\nRow {data_rows} (DNF example, id={row_id}):")
                    for j, cell in enumerate(cells[:12]):
                        text = cell.get_text(strip=True)
                        print(f"  Cell[{j}]: {text[:40]}")
            
            print(f"\nTotal data rows found: {data_rows}")
            
            # Count DNF/DNS in data
            dnf_count = 0
            dns_count = 0
            finished_count = 0
            
            for row in rows:
                row_id = row.get('id', '')
                row_classes = row.get('class', [])
                
                if 'jqgfirstrow' in row_classes or 'jqgroup' in row_classes or not row_id or row_id.startswith('listghead'):
                    continue
                
                cells = row.find_all('td')
                if len(cells) >= 10:
                    time_text = cells[9].get_text(strip=True).upper()
                    if time_text == 'DNF':
                        dnf_count += 1
                    elif time_text == 'DNS':
                        dns_count += 1
                    elif ':' in time_text:
                        finished_count += 1
            
            print(f"\nCounts:")
            print(f"  Finished: {finished_count}")
            print(f"  DNF: {dnf_count}")
            print(f"  DNS: {dns_count}")
            print(f"  Total: {finished_count + dnf_count + dns_count}")

if __name__ == '__main__':
    check_50k()
    check_marathon()
