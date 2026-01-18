# Frozen Head 50K Entrant Tracker - Setup Complete ✅

## What's Ready

Your automated entrant tracking system is **fully functional and ready to deploy**!

### ✅ Data Capture
- **Scraper**: `scraper.py` - Captures all 498 entrants with full details
  - First name, Last name, City, Location, Age category
  - Compares day-to-day to detect changes
  - Tracks new entrants (from waitlist) and dropouts

### ✅ Data Storage
- **entrants.json** - Complete snapshot of current entrants list
- **changes.json** - Full history of all detected changes with timestamps
- **history.csv** - Simple timeline for analysis (Date, Count, Changes)

### ✅ Automation
- **GitHub Actions Workflow** - Runs daily at 8 AM UTC (configurable)
- **Auto-commit** - Changes committed to repo automatically
- **Dashboard** - `index.html` displays results in real-time

### ✅ Dashboard Features
- 📊 **Live Stats**: Current entrants, new admits, dropouts
- 📈 **Interactive Charts**: Entrant trends and daily changes
- 📝 **Activity Log**: Shows recent changes and full history
- 🎯 **Projections**: Estimates when capacity will be reached
- 🔄 **Auto-refresh**: Updates when new data is available

## Current Status

```
Event: Frozen Head 50K (Sep 19, 2026)
Current Entrants: 498
Last Updated: 2026-01-17
Changes Tracked: 2 checks
```

**Sample Data Captured:**
- Zack Beavin (MA) - M30-39
- Adam Stackpole (OH) - M30-39
- Caleb Baity (NC) - M30-39
- ... and 495 more

## How to Deploy

### Step 1: Verify Everything Works Locally
```bash
python scraper.py
python analyze.py
```

### Step 2: Push to GitHub
```bash
git add -A
git commit -m "Initial entrant tracker setup with 498 entrants baseline"
git push origin main
```

### Step 3: Enable GitHub Pages
1. Go to repository Settings
2. Scroll to "Pages"
3. Select: Deploy from a branch → main → / (root)
4. Click Save

### Step 4: Your Dashboard is Live!
Visit: `https://YourUsername.github.io/BFC/`

(Replace YourUsername with your actual GitHub username)

## What Happens Daily

1. **8 AM UTC**: GitHub Actions runs `scraper.py`
2. **Scraper**: Fetches current entrant list, compares with previous day
3. **Analysis**: Detects new entrants and dropouts
4. **Storage**: Updates JSON and CSV files
5. **Commit**: Automatically commits changes to repository
6. **Dashboard**: Displays updated data (refreshes when you visit)

## Key Metrics You'll Track

- **Total Entrants**: Current registered count
- **Waitlist Admits**: Cumulative people moved from waitlist to confirmed
- **Dropouts**: Cumulative cancellations
- **Daily Growth Rate**: Average spots clearing per day
- **Projection**: Estimated date to reach capacity (2500)

## Understanding the Data

### Example Entry in changes.json
```json
{
  "timestamp": "2026-01-17T23:45:12.657712",
  "new_count": 498,
  "previous_count": 498,
  "count_change": 0,
  "total_new": 0,
  "total_dropped": 0,
  "new_entrants": [],
  "dropped_entrants": []
}
```

### Example Row in history.csv
```
Date,Total_Entrants,Previous_Count,New_Entrants,Dropped_Entrants,Net_Change
2026-01-17T23:44:44.259558,498,0,0,0,0
```

## Using the Data

### To Track Your Position
If you know you're Nth on the waitlist:
- Watch how many people get in each day (New_Entrants column)
- Calculate: Days until your number is reached = N / daily_average

### To Predict Race Day
- Use the growth rate to estimate final count
- Adjust for seasonal patterns (holidays, weather)
- Plan logistics based on final count projection

### To Monitor Trends
- Check if admits accelerate as race date approaches
- Look for dropouts (cancellations) after big admits
- Notice any day-of-week patterns

## Customization Options

### Change Scraping Schedule
Edit `.github/workflows/daily-check.yml`:
```yaml
- cron: '0 8 * * *'  # minute hour day month day-of-week
# Examples:
# '0 0 * * *'   = Every day at midnight
# '0 12 * * *'  = Every day at noon
# '0 8 * * MON' = Every Monday at 8 AM
```

### Change Capacity Estimate
Edit `index.html`, find line with:
```javascript
const capacity = 2500;
```
Change 2500 to your estimated capacity.

### Update Colors
Edit `index.html` CSS section:
- `#667eea` → Primary purple
- `#27ae60` → New entrants green
- `#e74c3c` → Dropouts red

## Files Overview

```
BFC/
├── scraper.py              ← Main script (runs daily)
├── analyze.py              ← Manual analysis tool
├── verify.py               ← Data verification (for testing)
├── index.html              ← Dashboard (live on GitHub Pages)
├── requirements.txt        ← Python dependencies
├── _config.yml             ← GitHub Pages config
├── README.md               ← Full documentation
├── QUICKSTART.md           ← Setup guide
├── GITHUB_PAGES.md         ← Deployment guide
├── .gitignore              ← Git ignore rules
├── .github/
│   └── workflows/
│       └── daily-check.yml ← GitHub Actions automation
└── data/
    ├── entrants.json       ← Current entrant snapshot
    ├── changes.json        ← Change history
    └── history.csv         ← Timeline summary
```

## Next Steps

1. ✅ Test locally (done - 498 entrants captured)
2. ⏭️ Push to GitHub
3. ⏭️ Enable GitHub Pages
4. ⏭️ View dashboard at your GitHub Pages URL
5. ⏭️ Dashboard auto-updates daily at 8 AM UTC

## Troubleshooting

**Q: Dashboard shows "Error loading data"**
- Make sure `data/changes.json` exists
- Manually run: `python scraper.py`
- Push files to GitHub

**Q: GitHub Actions not running**
- Check Actions tab for error messages
- Make sure workflow file exists at: `.github/workflows/daily-check.yml`
- Re-run manually from Actions tab

**Q: Count is wrong again**
- The scraper now correctly identifies the "498 Entrants" text
- If count shows 0, the website structure may have changed
- Run `python verify.py` to check

---

**Your tracker is ready to go! 🎯**

Push to GitHub and enable Pages to see your dashboard live.
