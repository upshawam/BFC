# Automation Setup

## Overview

This project uses GitHub Actions workflows to automatically:

1. **Capture historical race results** - runs after each race (November 1st)
2. **Track entrant registration** - runs daily during registration season (July-October)

## Workflows

### `scrape-historical.yml`
- **Trigger**: November 1st at midnight (after the race finishes)
- **Task**: Scrapes complete race results from UltraSignup for the completed race year
- **Output**: Saves results to `data/historical/results/results_{year}_{distance}.json`
- **Notes**: Can also be triggered manually via GitHub Actions UI

### `scrape-entrants.yml`
- **Trigger**: Daily during July-October (registration season) at noon UTC
- **Task**: Dynamically discovers current year registration and captures entrants
- **Output**: Saves entrants to `data/entrants/entrants_{year}.json`
- **Notes**: Automatically finds next year's registration via "See the [year] event" link

## How It Works

### Dynamic Year Discovery

The system uses `discover_current_year.py` to:

1. Start with a known seed DID (most recent year's 50K event)
2. Navigate to that event's registration page
3. Find the "See the [current year] event" link (e.g., "See the 2026 event")
4. Extract the event ID (eid) for the new year
5. Use that to find the new year's entrants

Example:
```python
from discover_current_year import discover_current_year_event

event = discover_current_year_event(119817)  # 2025 50K DID
# Returns: {year: 2026, eid: 4327, registration_url: "..."}
```

### Automatic DID Resolution

The `scraper_historical.py` includes a `resolve_event_links()` method that dynamically discovers 50K/Marathon DIDs by reading toggle links on each year's page. This means:

- **No hardcoding required** - DIDs are pulled from the live page
- **Resilient to URL changes** - adapts if UltraSignup changes structure
- **Accurate crosslinks** - always gets the matching Marathon DID for a 50K page

## Manual Workflows

You can trigger these manually from GitHub:

1. Go to **Actions** tab in your GitHub repo
2. Select the workflow (e.g., "Scrape Historical Results")
3. Click "Run workflow"

## Future Enhancements

- [ ] Add email/Slack notifications when scrapes complete
- [ ] Add error handling and retry logic
- [ ] Create summary statistics report
- [ ] Archive old entrant data (e.g., entrants_2024.json → archive/)
- [ ] Generate analysis dashboards from scraped data

## Testing

Run scrapers locally before committing:

```bash
# Test historical scraper
python scraper_historical.py

# Test entrant discovery
python discover_current_year.py

# Test entrant scraping
python scripts/scrape_entrants.py
```

## Troubleshooting

**Workflow fails**: Check the Actions tab for error logs. Common issues:
- Network timeout: Increase `wait_until` timeout
- Page changed: Update selectors in scraping logic
- Bot detection: Add delays between requests

**DIDs not resolving**: Run `python resolve_all_dids.py` to verify all DIDs are discoverable
