"""
Test scraper on 2024 results and display statistics
"""
from scraper_historical import HistoricalResultsScraper, BARKLEY_HISTORICAL
import json

scraper = HistoricalResultsScraper()

print("=" * 80)
print("SCRAPING 2024 RESULTS")
print("=" * 80)

# Get correct DIDs from BARKLEY_HISTORICAL
did_50k, did_marathon = BARKLEY_HISTORICAL[2024]

# Scrape 2024 50K
print("\n" + "=" * 80)
print("2024 50K RESULTS")
print("=" * 80)
results_50k = scraper.scrape_year(2024, did_50k)

if results_50k:
    print(f"\nStatus Counts:")
    print(f"  Finishers: {results_50k['total_finishers']}")
    print(f"  DNF: {results_50k['total_dnf']}")
    print(f"  DNS: {results_50k['total_dns']}")
    print(f"  Total: {len(results_50k['finishers'])}")
    
    # Get finishers
    finishers = [f for f in results_50k['finishers'] if f['status'] == 'Finished']
    dnf = [f for f in results_50k['finishers'] if f['status'] == 'DNF']
    dns = [f for f in results_50k['finishers'] if f['status'] == 'DNS']
    
    print(f"\n--- TOP 3 FINISHERS ---")
    for i, f in enumerate(finishers[:3]):
        print(f"{i+1}. {f['first_name']} {f['last_name']} - Place {f['place']} - Time: {f['finish_time_formatted']}")
    
    if len(finishers) > 3:
        print(f"\n--- LAST 3 FINISHERS ---")
        for i, f in enumerate(finishers[-3:]):
            print(f"{len(finishers)-2+i}. {f['first_name']} {f['last_name']} - Place {f['place']} - Time: {f['finish_time_formatted']}")
    
    if dnf:
        print(f"\nDNF Samples:")
        for i, d in enumerate(dnf[:3]):
            print(f"  {i+1}. {d['first_name']} {d['last_name']}")
    
    if dns:
        print(f"\nDNS Samples:")
        for i, d in enumerate(dns[:3]):
            print(f"  {i+1}. {d['first_name']} {d['last_name']}")

# Scrape 2024 Marathon
print("\n\n" + "=" * 80)
print("2024 MARATHON RESULTS")
print("=" * 80)
results_marathon = scraper.scrape_year(2024, did_marathon)

if results_marathon:
    print(f"\nStatus Counts:")
    print(f"  Finishers: {results_marathon['total_finishers']}")
    print(f"  DNF: {results_marathon['total_dnf']}")
    print(f"  DNS: {results_marathon['total_dns']}")
    print(f"  Total: {len(results_marathon['finishers'])}")
    
    # Get finishers
    finishers = [f for f in results_marathon['finishers'] if f['status'] == 'Finished']
    dnf = [f for f in results_marathon['finishers'] if f['status'] == 'DNF']
    dns = [f for f in results_marathon['finishers'] if f['status'] == 'DNS']
    
    print(f"\n--- TOP 3 FINISHERS ---")
    for i, f in enumerate(finishers[:3]):
        print(f"{i+1}. {f['first_name']} {f['last_name']} - Place {f['place']} - Time: {f['finish_time_formatted']}")
    
    if len(finishers) > 3:
        print(f"\n--- LAST 3 FINISHERS ---")
        for i, f in enumerate(finishers[-3:]):
            print(f"{len(finishers)-2+i}. {f['first_name']} {f['last_name']} - Place {f['place']} - Time: {f['finish_time_formatted']}")
    
    if dnf:
        print(f"\nDNF Samples:")
        for i, d in enumerate(dnf[:3]):
            print(f"  {i+1}. {d['first_name']} {d['last_name']}")
    
    if dns:
        print(f"\nDNS Samples:")
        for i, d in enumerate(dns[:3]):
            print(f"  {i+1}. {d['first_name']} {d['last_name']}")

print("\n" + "=" * 80)
