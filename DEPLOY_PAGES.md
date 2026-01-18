# GitHub Pages Dashboard - Quick Reference

Your interactive dashboard is ready to host on GitHub Pages!

## What You Get

A beautiful, real-time dashboard showing:
- 📊 Current entrant count (498)
- 📈 Interactive charts of entrant trends
- 📝 Recent activity log
- 🎯 Projection to capacity
- 📊 Daily change statistics

## Deploy in 3 Steps

### Step 1: Commit Your Code
```bash
cd c:\Users\Aaron\Documents\GitHub\BFC
git add -A
git commit -m "Frozen Head 50K entrant tracker - ready for GitHub Pages"
git push origin main
```

### Step 2: Enable GitHub Pages
1. Go to your repo on GitHub.com
2. Click **Settings** (top right)
3. Click **Pages** (left menu)
4. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ (root)**
5. Click **Save**

GitHub will build and deploy in 1-2 minutes.

### Step 3: Access Your Dashboard
Your site will be live at:
```
https://[YourUsername].github.io/BFC/
```

Replace `[YourUsername]` with your GitHub username.

Example: `https://aaronsmith.github.io/BFC/`

## What the Dashboard Shows

### Statistics Cards
- **Current Entrants**: Live count (498 at start)
- **Total From Waitlist**: Cumulative new entrants since tracking started
- **Total Dropouts**: Cumulative cancellations
- **Avg Daily Rate**: People getting in per day (grows over time)

### Entrant Count Chart
- Line chart showing 498 → ? over time
- Updates daily as scraper runs
- Helps visualize growth rate

### Daily Changes Chart
- Green bars = new entrants (admits from waitlist)
- Red bars = dropouts (cancellations)
- Shows the movement each day

### Analysis Section
- Key metrics summary
- Daily growth rate calculation
- **Projection to Capacity** showing estimated fill date

### Recent Activity
Two tabs:
1. **Recent Changes** - Last 10 checks with details
2. **Full History** - Complete CSV table of all checks

## How the Data Updates

```
Daily Schedule (8 AM UTC):
  ↓
GitHub Actions runs scraper.py
  ↓
Compares current list with yesterday
  ↓
Detects new entrants + dropouts
  ↓
Saves to data/changes.json
  ↓
Auto-commits to GitHub
  ↓
Dashboard reads new JSON
  ↓
Your site auto-updates
```

You don't need to do anything - it's all automated!

## Monitoring Your Position

If you know you're on the waitlist:

**Track your progress:**
1. Note your waitlist position
2. Watch "New Entrants" column in history
3. Calculate: Days until you = Position ÷ Daily Rate
4. Plan for that date

**Example:**
- You're 50th on waitlist
- 5 people admitted per day on average
- 50 ÷ 5 = 10 days until likely admission
- You should get in around 10 days

## Customizing Your Dashboard

### Change the Projection Capacity
Edit `index.html` (around line 740):
```javascript
const capacity = 2500;  // Change this number
```

### Change Update Time
Edit `.github/workflows/daily-check.yml`:
```yaml
- cron: '0 8 * * *'  # This is 8 AM UTC
```

Cron format: `minute hour day month day-of-week`
- `0 14 * * *` = 2 PM UTC (10 AM EST)
- `0 22 * * *` = 10 PM UTC (5 PM EST)
- `30 14 * * *` = 2:30 PM UTC

### Change Colors
Edit the CSS in `index.html`:
- Purple: `#667eea` → pick new hex color
- Green (new): `#27ae60` → pick new hex color
- Red (dropped): `#e74c3c` → pick new hex color

## How Visitors Use It

Once deployed, anyone can visit your dashboard URL and see:
- Live entrant count
- Beautiful charts
- Recent activity
- Projections
- All updated daily automatically

## Data Privacy

Your data includes:
- Entrant names
- Cities
- States/Locations
- Age categories
- Daily count changes

This is all **publicly visible on the event page anyway**, so you're just organizing it!

## File Structure on GitHub Pages

When deployed, the structure is:
```
https://yourname.github.io/BFC/
  ├── index.html           ← The dashboard
  ├── data/
  │   ├── changes.json     ← Historical changes
  │   ├── history.csv      ← Timeline data
  │   └── entrants.json    ← Current list
  ├── README.md
  ├── scraper.py           ← Not visible on web
  └── ... other files
```

The scraper (`scraper.py`) runs in GitHub Actions behind the scenes and updates the `data/` files.

## Troubleshooting

**Dashboard not loading?**
- Wait 5 minutes - GitHub Pages takes time to build
- Refresh your browser (Ctrl+F5)
- Check Actions tab for build errors

**Data not updating?**
- Check Actions tab → Daily Entrant List Check
- If red X, click to see error
- Data files might not have pushed correctly

**Can't find my page?**
- Go to repo Settings → Pages
- Copy the URL from "Your site is published at..."
- Make sure Settings shows main branch is selected

**Want to change update time?**
- Edit `.github/workflows/daily-check.yml`
- Modify the `cron` value
- Commit and push
- Next run will be at new time

## Example Dashboard URL

After setup, your public dashboard will be:

**GitHub Username**: `aaronsmith`
**Repository**: `BFC`
**Dashboard URL**: `https://aaronsmith.github.io/BFC/`

Anyone can visit this URL and see your tracker!

---

**Ready? Push to GitHub and enable Pages!**

```bash
git push origin main
# Then go to Settings → Pages → Deploy from branch → main
```

Your dashboard will be live in 1-2 minutes! 🚀
