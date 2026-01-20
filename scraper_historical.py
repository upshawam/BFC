#!/usr/bin/env python3
"""
Scraper for historical Barkley Fall Classic results.
Extracts finisher data from UltraSignup results pages for trend analysis.
Handles both 50K and Marathon distances for each year.
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
from playwright.sync_api import sync_playwright

# Configuration for all years - maps year to (50K_did, Marathon_did)
BARKLEY_HISTORICAL = {
    2025: (119817, 119818),
    2024: (108870, 108871),
    2023: (97857, 97858),
    2022: (88170, 88171),
    2021: (79789, 79790),
    2020: (71482, 71483),
    2019: (60848, 60849),
    2018: (50528, 50529),
    2017: (41232, 41233),
    2016: (34630, 34631),
    2015: (32215, 32216),
}

DATA_DIR = Path(__file__).parent / "data" / "historical"
RESULTS_DIR = DATA_DIR / "results"
ANALYSIS_DIR = DATA_DIR / "analysis"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

class HistoricalResultsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def scrape_year(self, year, did):
        """Scrape results for a specific year and distance."""
        distance = "50K" if did == BARKLEY_HISTORICAL[year][0] else "Marathon"
        print(f"Scraping {year} {distance} (did={did})...")
        url = f"https://ultrasignup.com/results_event.aspx?did={did}"
        
        try:
            # Use Playwright to render JavaScript
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for the jqGrid table to load
                try:
                    page.wait_for_selector('table#list', timeout=10000)
                except:
                    pass
                
                # Get rendered HTML
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                browser.close()
            
            # Extract results from the jqGrid table
            results = self._extract_results_from_jqgrid(soup, year, distance, did)
            
            if results['finishers']:
                # Save raw results
                output_file = RESULTS_DIR / f"results_{year}_{distance.lower().replace('k', 'k')}.json"
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                print(f"  ✓ Saved {len(results['finishers'])} {distance} finisher records")
                return results
            else:
                print(f"  ✗ No finishers found for {year} {distance}")
                return None
            
        except Exception as e:
            print(f"  ✗ Error scraping {year} {distance}: {e}")
            return None
    
    def _extract_results_from_jqgrid(self, soup, year, distance, did):
        """Extract finisher data from jqGrid table."""
        finishers = []
        dnf_count = 0
        dns_count = 0
        
        # Find the jqGrid table with id="list"
        grid_table = soup.find('table', {'id': 'list'})
        if not grid_table:
            return {
                'year': year,
                'distance': distance,
                'did': did,
                'scraped_at': datetime.now().isoformat(),
                'total_finishers': 0,
                'total_dnf': 0,
                'total_dns': 0,
                'finishers': []
            }
        
        # Find all data rows in tbody
        tbody = grid_table.find('tbody')
        if not tbody:
            return {
                'year': year,
                'distance': distance,
                'did': did,
                'scraped_at': datetime.now().isoformat(),
                'total_finishers': 0,
                'total_dnf': 0,
                'total_dns': 0,
                'finishers': []
            }
        
        rows = tbody.find_all('tr')
        
        for row_idx, row in enumerate(rows):
            # Get row classes
            row_classes = row.get('class', [])
            
            # Skip structure rows (jqgfirstrow), grouping headers (jqgroup), and rows without id
            row_id = row.get('id', '')
            if 'jqgfirstrow' in row_classes or 'jqgroup' in row_classes or not row_id or row_id.startswith('listghead'):
                continue
            
            cells = row.find_all('td')
            if len(cells) < 10:
                continue
            
            try:
                finisher = self._parse_jqgrid_row(cells, year, distance)
                if finisher:
                    finishers.append(finisher)
                    if finisher['status'] == 'DNF':
                        dnf_count += 1
                    elif finisher['status'] == 'DNS':
                        dns_count += 1
            except Exception as e:
                continue
        
        # Sort by place
        finishers.sort(key=lambda x: x['place'] if isinstance(x['place'], int) else float('inf'))
        
        return {
            'year': year,
            'distance': distance,
            'did': did,
            'scraped_at': datetime.now().isoformat(),
            'total_finishers': len([f for f in finishers if f['status'] == 'Finished']),
            'total_dnf': dnf_count,
            'total_dns': dns_count,
            'finishers': finishers
        }
    
    def _parse_jqgrid_row(self, cells, year, distance):
        """Parse a single row from jqGrid table."""
        try:
            # jqGrid column order: results link, place, first, last, city, state, age, division, dp, time, rank, (hidden cols)
            place_text = cells[1].get_text(strip=True)
            first_name = cells[2].get_text(strip=True)
            last_name = cells[3].get_text(strip=True)
            city = cells[4].get_text(strip=True)
            state = cells[5].get_text(strip=True)
            age_text = cells[6].get_text(strip=True)
            division = cells[7].get_text(strip=True)
            dp_text = cells[8].get_text(strip=True)
            time_text = cells[9].get_text(strip=True)
            
            # Parse place
            try:
                place = int(place_text)
            except (ValueError, IndexError):
                return None
            
            # Parse age
            try:
                age = int(age_text)
            except ValueError:
                age = None
            
            # Determine status and time
            status = "Finished"
            finish_time_seconds = None
            
            if time_text.upper() in ["DNF", "DNS", "DQ"]:
                status = time_text.upper()
            else:
                finish_time_seconds = self._parse_time(time_text)
            
            return {
                'year': year,
                'distance': distance,
                'place': place,
                'first_name': first_name,
                'last_name': last_name,
                'city': city,
                'state': state,
                'age': age,
                'division': division,
                'status': status,
                'finish_time_seconds': finish_time_seconds,
                'finish_time_formatted': time_text
            }
        except Exception as e:
            return None
    
    
    def _parse_time(self, time_str):
        """Convert HH:MM:SS to seconds."""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return None
    
    def scrape_all(self):
        """Scrape all years and distances."""
        all_results = []
        
        for year in sorted(BARKLEY_HISTORICAL.keys()):
            did_50k, did_marathon = BARKLEY_HISTORICAL[year]
            
            # Scrape 50K
            results_50k = self.scrape_year(year, did_50k)
            if results_50k:
                all_results.append(results_50k)
            time.sleep(2)  # Rate limiting
            
            # Scrape Marathon
            results_marathon = self.scrape_year(year, did_marathon)
            if results_marathon:
                all_results.append(results_marathon)
            time.sleep(2)  # Rate limiting
        
        # Save comprehensive archive
        archive_file = DATA_DIR / "barkley_archive_complete.json"
        with open(archive_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n✓ Saved complete archive to {archive_file}")
        return all_results

def main():
    scraper = HistoricalResultsScraper()
    scraper.scrape_all()

if __name__ == '__main__':
    main()
