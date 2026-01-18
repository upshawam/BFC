# GitHub Pages Setup

Your dashboard is ready to be hosted on GitHub Pages!

## Enable GitHub Pages

1. **Push your code to GitHub** (if you haven't already):
   ```bash
   git add -A
   git commit -m "Add dashboard and GitHub Pages config"
   git push origin main
   ```

2. **Go to your repository on GitHub**:
   - Click **Settings** (top right)
   - Scroll down to **Pages** section

3. **Configure GitHub Pages**:
   - Under "Source", select **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ (root)**
   - Click **Save**

4. **GitHub will build and deploy** - takes ~1-2 minutes

5. **Your site will be live at**:
   ```
   https://YourUsername.github.io/BFC/
   ```
   (Replace YourUsername with your actual GitHub username)

## What You're Getting

The dashboard includes:
- 📊 **Real-time stats** - Current entrants, waitlist admits, dropouts
- 📈 **Interactive charts** - Entrant count trends and daily changes
- 📝 **Activity log** - Recent changes and full history
- 🎯 **Projections** - Estimate when capacity will be reached
- 🔄 **Auto-updates** - Refreshes when the scraper runs daily

## How It Works

1. **Scraper runs daily** via GitHub Actions (8 AM UTC)
2. **Updates JSON/CSV files** in the `data/` folder
3. **Dashboard automatically reads** these files
4. **GitHub Pages serves** the static HTML + data

## Access Your Dashboard

Once deployed:
- **Full URL**: `https://YourUsername.github.io/BFC/`
- **Data files** visible at: `https://YourUsername.github.io/BFC/data/changes.json`

## Customization

### Change the schedule
Edit `.github/workflows/daily-check.yml`:
```yaml
- cron: '0 8 * * *'  # Change the time (format: minute hour day month day-of-week)
```

### Change capacity estimate
In `index.html`, find line with `const capacity = 2500;` and adjust the number.

### Customize dashboard colors
In `index.html`, find the `:root` or color definitions and modify:
- `#667eea` - Primary color (purple)
- `#764ba2` - Gradient color
- `#27ae60` - New entrants (green)
- `#e74c3c` - Dropouts (red)

## Troubleshooting

### Dashboard shows "Error loading data"
- Make sure `data/changes.json` and `data/history.csv` exist
- Run the scraper manually: `python scraper.py`
- Push the data to GitHub

### GitHub Pages not updating
- Check Actions tab for workflow errors
- Make sure main branch has all files
- Wait 1-2 minutes after pushing

### No data showing
- Scraper needs to run at least once
- Check `data/changes.json` exists locally
- Commit and push the data folder to GitHub

## File Structure (GitHub Pages)

```
BFC/
├── index.html              (Main dashboard)
├── _config.yml             (GitHub Pages config)
├── data/
│   ├── changes.json        (Change history)
│   ├── history.csv         (Timeline)
│   └── entrants.json       (Full list)
├── scraper.py              (Runs daily via Actions)
├── .github/
│   └── workflows/
│       └── daily-check.yml (Automation)
└── README.md
```

## Tips

✅ **Best Practices**:
- Check the dashboard daily
- Monitor the projection estimate
- Note when growth rate changes
- Track when close to your position on waitlist

💡 **What to Watch For**:
- Sudden increase in new admissions (good for you!)
- Waves of dropouts after admissions
- Seasonal patterns (time of day, day of week)
- Rate changes as race approaches

🎯 **Your Goal**:
- Use the projection to estimate when you clear the waitlist
- The daily admission count × days until race = spots that will open
- If you're monitoring your position, you can predict your fate!

---

Need help? Check the main README.md for more details about the tracker itself.
