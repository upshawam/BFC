#!/usr/bin/env python3
"""
Debug version of historical scraper to see what's being scraped.
"""

import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_marathon_debug():
    """Debug scrape of 2025 Marathon."""
    year = 2025
    did = 119818
    distance = "Marathon"
    url = f"https://ultrasignup.com/results_event.aspx?did={did}"
    
    print(f"Scraping {year} {distance} (did={did})...")
    print(f"URL: {url}")
    
    try:
        # Use Playwright to render JavaScript
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Loading page...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for the jqGrid table to load
            print("Waiting for jqGrid table...")
            try:
                page.wait_for_selector('table#list', timeout=10000)
                print("✓ jqGrid table found")
            except:
                print("✗ jqGrid table not found")
            
            # Get rendered HTML
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            browser.close()
        
        # Extract results
        print("\nParsing results...")
        finishers = []
        dnf_count = 0
        dns_count = 0
        
        # Find the jqGrid table
        grid_table = soup.find('table', {'id': 'list'})
        if not grid_table:
            print("✗ No grid table found in soup")
            return
        
        tbody = grid_table.find('tbody')
        if not tbody:
            print("✗ No tbody found")
            return
        
        rows = tbody.find_all('tr')
        print(f"Total rows in tbody: {len(rows)}")
        
        data_row_count = 0
        for row_idx, row in enumerate(rows):
            row_classes = row.get('class', [])
            row_id = row.get('id', '')
            
            # Skip structure rows
            if 'jqgfirstrow' in row_classes or 'jqgroup' in row_classes or not row_id or row_id.startswith('listghead'):
                continue
            
            cells = row.find_all('td')
            if len(cells) < 10:
                continue
            
            data_row_count += 1
            
            # Show first 3 rows in detail
            if data_row_count <= 3:
                print(f"\n=== Row {data_row_count} (id={row_id}) ===")
                for i, cell in enumerate(cells[:12]):
                    text = cell.get_text(strip=True)
                    print(f"  Cell[{i}]: '{text}'")
            
            # Show a DNF example
            time_text = cells[9].get_text(strip=True) if len(cells) > 9 else ""
            if time_text.upper() == 'DNF' and dnf_count == 0:
                print(f"\n=== DNF Example (Row {data_row_count}, id={row_id}) ===")
                for i, cell in enumerate(cells[:12]):
                    text = cell.get_text(strip=True)
                    print(f"  Cell[{i}]: '{text}'")
                dnf_count += 1
            elif time_text.upper() == 'DNF':
                dnf_count += 1
            elif time_text.upper() == 'DNS':
                if dns_count == 0:
                    print(f"\n=== DNS Example (Row {data_row_count}, id={row_id}) ===")
                    for i, cell in enumerate(cells[:12]):
                        text = cell.get_text(strip=True)
                        print(f"  Cell[{i}]: '{text}'")
                dns_count += 1
        
        finished_count = data_row_count - dnf_count - dns_count
        
        print(f"\n=== SUMMARY ===")
        print(f"Total data rows: {data_row_count}")
        print(f"Finished: {finished_count}")
        print(f"DNF: {dnf_count}")
        print(f"DNS: {dns_count}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    scrape_marathon_debug()
