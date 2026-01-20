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
    2024: (108870, 116578),
    2023: (97857, 108677),
    2022: (88170, 97828),
    2021: (79789, 88389),
    2020: (71482, 79480),
    2019: (60848, 71684),
    2018: (50528, 60817),
    2017: (41232, 50516),
    2016: (34630, 34629),
    2015: (32215, 34599),
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

    def resolve_event_links(self, seed_did):
        """Resolve sibling event DIDs (50K/Marathon) from a seed event page.
        Returns a dict like {'50K': did, 'Marathon': did} discovered from the toggle links.
        """
        url = f"https://ultrasignup.com/results_event.aspx?did={seed_did}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            # Look for the toggle container with the event links
            links = page.evaluate(
                """
                () => {
                    const container = document.querySelector('div.unit-1.text-right');
                    if (!container) return [];
                    return Array.from(container.querySelectorAll('a')).map(a => ({
                        text: (a.textContent || '').trim(),
                        href: a.getAttribute('href') || ''
                    }));
                }
                """
            )
            browser.close()
        mapping = {}
        for link in links:
            href = link.get('href', '')
            text = link.get('text', '')
            if 'did=' in href:
                try:
                    did_val = int(href.split('did=')[1].split('#')[0])
                    # Normalize distance label
                    label = text.lower()
                    if '50k' in label:
                        mapping['50K'] = did_val
                    elif 'marathon' in label:
                        mapping['Marathon'] = did_val
                except ValueError:
                    continue
        return mapping
    
    def scrape_year(self, year, did):
        """Scrape results for a specific year and distance."""
        distance = "50K" if did == BARKLEY_HISTORICAL[year][0] else "Marathon"
        print(f"Scraping {year} {distance} (did={did})...")
        url = f"https://ultrasignup.com/results_event.aspx?did={did}"
        
        try:
            # Use Playwright to render JavaScript and extract jqGrid data
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='domcontentloaded', timeout=90000)
                
                # Wait for jqGrid table to load with generous timeout
                page.wait_for_selector('table#list', timeout=30000)
                
                # Give jqGrid extra time to populate with data
                time.sleep(10)
                
                # Extract results using jqGrid JavaScript API
                results = self._extract_from_jqgrid_api(page, year, distance, did)
                
                browser.close()
            
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
    
    def _extract_from_jqgrid_api(self, page, year, distance, did):
        """Extract data using jqGrid JavaScript API to get status codes."""
        # Get all row IDs from jqGrid
        row_ids = page.evaluate("jQuery('#list').jqGrid('getDataIDs')")
        
        finishers = []
        status_counts = {'1': 0, '2': 0, '3': 0, '5': 0}
        
        for row_id in row_ids:
            # Get full row data from jqGrid (includes status field)
            row_data = page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{row_id}')")
            
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
            elif status_code == '5':
                status = 'Disqualified'
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
                finish_time_seconds = self._parse_time(finish_time_formatted)
            
            # Parse age
            age = None
            try:
                age_text = str(row_data.get('age', ''))
                if age_text and age_text != '':
                    age = int(age_text)
            except:
                pass
            
            finisher_data = {
                'year': year,
                'distance': distance,
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
        
        # Sort by status (Finished first) then by place
        finishers.sort(key=lambda x: (0 if x['status'] == 'Finished' else (1 if x['status'] == 'DNF' else 2), x['place']))
        
        return {
            'year': year,
            'distance': distance,
            'did': did,
            'scraped_at': datetime.now().isoformat(),
            'total_finishers': status_counts.get('1', 0),
            'total_dnf': status_counts.get('2', 0),
            'total_dns': status_counts.get('3', 0),
            'total_disqualified': status_counts.get('5', 0),
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
