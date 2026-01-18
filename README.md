# Ultramarathon Entrant Tracker

A Python-based automated tracker that monitors the entrant list for the Frozen Head 50K ultramarathon and tracks changes over time.

## Features

- **Daily Automated Checks**: GitHub Actions workflow runs every day at 8 AM UTC
- **Change Detection**: Identifies new entrants and dropouts
- **Data Persistence**: Maintains a history of all changes
- **CSV Export**: Track entrant count trends over time
- **Detailed Logging**: JSON records of all changes for analysis

## Current Status

- **Event**: Frozen Head State Park 50K, Tennessee
- **Current Entrants**: 498
- **Event Date**: September 19, 2026

## How It Works

### Scraper (`scraper.py`)
1. Fetches the entrant list from UltraSignup
2. Compares with previous snapshot
3. Identifies new entrants (likely from waitlist)
4. Identifies dropped entrants (cancellations)
5. Updates tracking files

### Data Files

```
data/
├── entrants.json          # Current entrant list snapshot
├── changes.json           # Complete history of all changes
└── history.csv            # Simplified timeline (count trends)
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run manually (optional):
```bash
python scraper.py
```

## GitHub Actions Setup

The project includes automated daily checking via `.github/workflows/daily-check.yml`:

- **Trigger**: Every day at 8 AM UTC (adjust cron in workflow file)
- **Alternative**: Manual trigger via GitHub Actions UI
- **Action**: Automatically commits and pushes changes to repo

### Adjusting Schedule

Edit `.github/workflows/daily-check.yml` to change the cron schedule:
```yaml
- cron: '0 8 * * *'  # Current: 8 AM UTC daily
```

Cron format: `minute hour day month day-of-week`

## Interpreting Results

### changes.json Structure
```json
{
  "timestamp": "2026-01-17T...",
  "count_change": +5,
  "new_count": 498,
  "previous_count": 493,
  "new_entrants": [...],
  "dropped_entrants": [...],
  "total_new": 5,
  "total_dropped": 0
}
```

### history.csv Columns
- **Date**: Check timestamp
- **Total_Entrants**: Current registered count
- **Previous_Count**: Count from previous check
- **New_Entrants**: People added since last check
- **Dropped_Entrants**: People who withdrew
- **Net_Change**: Change in count

## Insights You Can Track

1. **Waitlist Movement**: Count the cumulative new entrants over time to estimate how many waitlisters are getting in
2. **Dropout Patterns**: See if/when people cancel
3. **Growth Timeline**: Chart the entrant count over time to predict when a cutoff might happen
4. **Rate of Change**: Calculate how many spots open up per day

## Future Enhancements

- [ ] Email notifications when changes detected
- [ ] Slack webhook for alerts
- [ ] Detailed entrant demographics tracking
- [ ] Predict time to capacity based on growth rate
- [ ] Web dashboard for visualization
- [ ] Detect name duplicates or formatting changes

## Notes

- The scraper respects the website and uses proper User-Agent headers
- Data is stored locally in the repo for easy git history tracking
- Each run creates a timestamped record for auditing

## Files

- `scraper.py` - Main scraper script
- `requirements.txt` - Python dependencies
- `.github/workflows/daily-check.yml` - Automated daily check workflow
- `README.md` - This file
- `data/` - Directory for storing entrant data (created on first run)
