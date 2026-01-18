# Quick Start Guide

## Initial Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the First Scan
```bash
python scraper.py
```

This creates your baseline data in the `data/` folder:
- `entrants.json` - The full entrant list snapshot
- `changes.json` - Detected changes
- `history.csv` - Simplified history

## Manual Usage

### Check for changes right now
```bash
python scraper.py
```

### Analyze tracking data
```bash
python analyze.py
```

This shows you:
- Total people admitted from waitlist
- Total dropouts
- Average daily admission rate
- Estimate of when 500 entrants will be reached
- Recent activity

## Setting Up Automated Daily Checks

The project includes GitHub Actions automation. To enable:

1. **Push to GitHub** (if not already):
   ```bash
   git add -A
   git commit -m "Initial entrant tracker setup"
   git push origin main
   ```

2. **Go to GitHub repository settings**:
   - Settings → Actions → General
   - Make sure "Allow all actions and reusable workflows" is enabled

3. **The workflow will run automatically** at 8 AM UTC every day

4. **Manual trigger**:
   - Go to Actions → "Daily Entrant List Check"
   - Click "Run workflow"

## What Gets Tracked

### Each Check Records:
- ✅ Total current entrants
- ✅ New entrants since last check
- ✅ Dropped entrants since last check
- ✅ Net change in count
- ✅ Timestamp of check

### Data Stored:
- Full entrant details (name, location)
- Change history with timestamps
- Timeline CSV for easy analysis

## Understanding Your Data

### Example Change Event:
```json
{
  "timestamp": "2026-01-17T12:30:00",
  "count_change": 5,
  "new_count": 498,
  "previous_count": 493,
  "new_entrants": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "location": "CA"
    }
  ],
  "total_new": 5,
  "total_dropped": 0
}
```

### What This Means:
- 5 new people registered (likely from waitlist)
- 0 people withdrew
- You moved up 5 spots on the waitlist (if there is one)

## Tips for Your Situation

1. **Track the acceleration**: Early on, admits might be slow. As the race date approaches, expect faster movement.

2. **Compare to event size**: Knowing the cap helps predict when you'll definitely get in.

3. **Watch for patterns**: 
   - Do admits happen on certain days?
   - Are there waves of dropouts?

4. **Calculate your position**: If you know how many people were on the waitlist before you, you can track when you're likely to clear it.

## Troubleshooting

### GitHub Actions Not Running?
- Check Actions tab for any error messages
- Ensure workflow file is in `.github/workflows/daily-check.yml`
- Re-run manually: Actions → Daily Entrant List Check → Run workflow

### Scraper Not Finding Data?
- Website structure may have changed
- You may need to update the CSS selectors in `scraper.py`
- Run: `python scraper.py` and check output

### Git Issues?
- Make sure you have git configured:
  ```bash
  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
  ```

## Next Steps

1. Run the scraper a few times manually to build initial history
2. Set up the GitHub Actions workflow for daily automated checks
3. Use `analyze.py` to monitor trends
4. Adjust tracking frequency in the workflow if needed

---

**Questions?** Check the README.md for more detailed information.
