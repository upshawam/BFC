#!/usr/bin/env python3
"""
Master script for historical Barkley Fall Classic data collection and analysis.
Runs scraper and analyzer for complete historical dataset.
"""

import sys
from pathlib import Path
import time

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from scraper_historical import HistoricalResultsScraper
from analyzer_historical import HistoricalAnalyzer

def main():
    print("=" * 60)
    print("BARKLEY FALL CLASSIC - HISTORICAL DATA COLLECTION")
    print("=" * 60)
    print()
    
    # Step 1: Scrape all years
    print("STEP 1: Scraping historical results from UltraSignup")
    print("-" * 60)
    scraper = HistoricalResultsScraper()
    results = scraper.scrape_all()
    print()
    
    if not results:
        print("✗ Scraping failed. Exiting.")
        return False
    
    # Step 2: Run analysis
    print("STEP 2: Running comprehensive analysis")
    print("-" * 60)
    analyzer = HistoricalAnalyzer()
    analyzer.generate_all_analysis()
    print()
    
    # Summary
    print("=" * 60)
    print("✓ COMPLETE!")
    print("=" * 60)
    print()
    print("Generated files:")
    data_dir = repo_root / "data" / "historical"
    
    results_dir = data_dir / "results"
    if results_dir.exists():
        result_files = list(results_dir.glob("*.json"))
        print(f"\nResults ({len(result_files)} files):")
        for f in sorted(result_files):
            print(f"  • {f.name}")
    
    analysis_dir = data_dir / "analysis"
    if analysis_dir.exists():
        analysis_files = list(analysis_dir.glob("*.json"))
        print(f"\nAnalysis ({len(analysis_files)} files):")
        for f in sorted(analysis_files):
            size_kb = f.stat().st_size / 1024
            print(f"  • {f.name} ({size_kb:.1f} KB)")
    
    archive = data_dir / "barkley_archive_complete.json"
    if archive.exists():
        size_mb = archive.stat().st_size / (1024 * 1024)
        print(f"\nMaster Archive:")
        print(f"  • {archive.name} ({size_mb:.2f} MB)")
    
    print()
    print("View the historical analysis at: historical_analysis.html")
    print()
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
