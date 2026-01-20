# 🏔️ Barkley Fall Classic - Historical Analysis System

Complete historical results archiving and trend analysis for Barkley Fall Classic (2015-2025)

## Overview

This system scrapes, analyzes, and visualizes historical Barkley Fall Classic results from UltraSignup. It tracks demographic trends, finish statistics, and performance metrics across 11 years of 50K and Marathon events.

## What's Included

### 1. **Scraper** (`scraper_historical.py`)
- Scrapes all historical Barkley results from UltraSignup
- Handles both 50K and Marathon distances
- Years: 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
- Uses Playwright for JavaScript rendering
- Extracts: Place, Name, City/State, Age, Gender, Finish Time, Status (Finished/DNF/DNS)

**Run manually:**
```bash
python scraper_historical.py
```

### 2. **Analyzer** (`analyzer_historical.py`)
Generates 7 different analysis reports:

#### Reports Generated:
- **yearly_summary.json** - Year-by-year stats (starters, finishers, finish rates)
- **demographic_trends.json** - Age and gender distribution over time
- **finish_statistics.json** - Time statistics (avg, median, min, max, stdev)
- **location_analysis.json** - Top 100 locations of participants
- **age_analysis.json** - Age group participation and finish rates
- **gender_trends.json** - Gender-specific participation metrics
- **distance_comparison.json** - 50K vs Marathon comparison

**Run manually:**
```bash
python analyzer_historical.py
```

### 3. **Master Script** (`scripts/scrape_historical.py`)
Orchestrates both scraping and analysis in one command:
```bash
python scripts/scrape_historical.py
```

### 4. **Dashboard** (`historical_analysis.html`)
Interactive visualization with:
- **Overview Tab**: Yearly summary with charts and tables
- **Demographics Tab**: Age trends, gender participation, average age
- **Performance Tab**: Finish times, DNF/DNS trends, detailed statistics
- **Locations Tab**: Geographic distribution of racers
- **Distance Tab**: 50K vs Marathon performance comparison

Open in browser: `historical_analysis.html`

## Data Structure

```
data/historical/
├── barkley_archive_complete.json    # Master archive (all years/distances)
├── results/
│   ├── results_2015_50k.json        # 145 finishers
│   ├── results_2015_marathon.json   # (none this year)
│   ├── results_2016_50k.json        # 119 finishers
│   ├── results_2016_marathon.json   # 45 finishers
│   └── ... (18 files total)
└── analysis/
    ├── yearly_summary.json
    ├── demographic_trends.json
    ├── finish_statistics.json
    ├── location_analysis.json
    ├── age_analysis.json
    ├── gender_trends.json
    └── distance_comparison.json
```

## Key Statistics

**Total Participants Across All Years: 2,700+**

### By Year (50K + Marathon combined):
- 2015: 145 racers
- 2016: 164 racers
- 2017: 120 racers
- 2018: 367 racers
- 2019: 475 racers
- 2020: 243 racers
- 2021: 177 racers
- 2022: 107 racers
- 2023: 407 racers
- 2024: 113 racers
- 2025: 456 racers (2025 Marathon still filling up)

### Trends Visible:
- 50K typically attracts 100-400+ finishers
- Marathon attracts 20-450+ finishers
- Finish rates vary by year and distance
- Predominant age groups: 30-49
- Growing female participation over time
- Geographic diversity: racers from all 50 states and international

## How to Use the Data

### Analyze Specific Trends:
```python
import json

# Load complete archive
with open('data/historical/barkley_archive_complete.json') as f:
    data = json.load(f)

# Find 50K finishers from specific year
year_2024 = [r for r in data if r['year'] == 2024 and r['distance'] == '50K']
finishers = [f for f in year_2024[0]['finishers'] if f['status'] == 'Finished']

# Analyze finish times
times = [f['finish_time_seconds']/3600 for f in finishers if f['finish_time_seconds']]
avg_time = sum(times) / len(times)  # in hours
```

### Generate Custom Reports:
- Use analysis files as JSON to build custom queries
- Combine multiple years for trend analysis
- Export to spreadsheets for further analysis
- Create new visualizations with Chart.js

## Future Enhancement Ideas

- **DNS/DNF Analysis**: Dive deeper into why racers don't finish
- **Time Progression**: Track how finishing times have evolved
- **Repeat Racer Analysis**: Identify who runs multiple years
- **Elite Performance**: Track top finishers across years
- **Weather Impact**: Correlate finish rates with weather conditions
- **Pacing Analysis**: Study front-runner vs. back-of-pack strategies
- **Regional Hubs**: Identify major feeder regions
- **Age Group Analysis**: Deep dive into age-specific performance

## Technical Details

### Technologies Used:
- **Python 3.11.3**
- **Playwright**: Browser automation for JavaScript rendering
- **BeautifulSoup4**: HTML parsing
- **Chart.js 3.9.1**: Client-side visualizations
- **JSON**: All data in JSON format for flexibility

### Scraping Notes:
- Each request includes 2-second delay for rate limiting
- Data persisted immediately after each successful scrape
- Graceful error handling for missing or incomplete data
- All data stored locally in repo (no external API calls needed)

### Data Quality:
- All data sourced directly from UltraSignup results pages
- Validates basic data structure before saving
- Handles variations in data format across years
- Preserves original finish time formats

## File Locations

All data and scripts in this repo:
- Core scrapers: `scraper_historical.py`, `analyzer_historical.py`
- Master script: `scripts/scrape_historical.py`
- Dashboard: `historical_analysis.html`
- Raw data: `data/historical/results/*.json`
- Analysis: `data/historical/analysis/*.json`
- Archive: `data/historical/barkley_archive_complete.json`

## Maintenance

**Re-scrape latest data:**
```bash
# Update with new 2025 data or corrections
python scripts/scrape_historical.py
```

**Manual scraping:**
```bash
# Scrape specific year/distance
python scraper_historical.py  # Modify BARKLEY_HISTORICAL dict as needed
```

**Analysis only (re-generate from existing data):**
```bash
python analyzer_historical.py
```

## Questions & Analysis Ideas

This dataset enables answers to questions like:
- How have Barkley participation numbers trended?
- What's the typical finish time for 50K vs Marathon?
- Where do most racers come from?
- How has the gender ratio changed?
- What age groups are most successful?
- Are there geographic clusters of fast finishers?
- How do finish rates vary by distance and year?

All this data is now in your repo, ready to explore!
