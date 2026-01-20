# 📊 Barkley Fall Classic - Historical Analysis

Welcome to the historical analysis section! This comprehensive guide explains the 11 years of race data we've collected (2015-2025) and the meaningful metrics we're tracking.

## 🎯 Project Overview

This project now tracks **two main functions**:

### 1. **Live Entrant Tracker** (Current Year)
- Real-time monitoring of Barkley Fall Classic, Dam Yeti 50 Mile, and 55K entrant lists
- Captures waitlist movement and registration changes
- Accessible at: `index.html`

### 2. **Historical Analysis** (2015-2025)
- 11 years of race results with complete participant data
- Source of truth data scraped from UltraSignup
- Comprehensive metrics and trend analysis
- Accessible at: `historical.html`

---

## 📈 Historical Metrics

### Overall Statistics
- **Total Participants (2015-2025)**: 4,047 runners
- **Total Finishers**: 2,541 runners (62.8% finish rate)
- **Years Tracked**: 11 complete race seasons

### Marathon Performance
- **Average Finish Rate**: 69.2%
- **Hardest Year**: 2022 (24.0% finish rate)
- **Easiest Year**: 2015 (100.0% finish rate)

### 50K Performance
- **Average Finish Rate**: 87.4%
- **Observation**: 50K is significantly easier than Marathon
- **Consistency**: High completion rates across most years

---

## 📊 What the Charts Show

### 1. **Marathon Participation & Finish Rate Trend**
- Tracks marathon participant count over 11 years
- Shows finish rate trends (easier or harder years)
- Helps identify patterns in race difficulty

### 2. **50K Participation & Finish Rate Trend**
- Similar trend visualization for the 50K distance
- Demonstrates relative stability in 50K completion rates
- Shows smaller participant pool than marathon

### 3. **Finish Rate by Distance (Bar Chart)**
- Side-by-side comparison of marathon vs. 50K finish rates by year
- Visual identification of which years were toughest
- Quick reference for race difficulty history

### 4. **Participant Status Distribution (2025 - Latest Year)**
- Pie chart showing breakdown of 2025 results
- Categories: Finished, DNF (Did Not Finish), DNS (Did Not Start)
- Demonstrates typical finisher/non-finisher split

---

## 🔍 Understanding the Data

### Status Codes
The data includes participant status in categories:
- **Finished** (✓): Successfully completed the race
- **DNF**: Did Not Finish (started but withdrew)
- **DNS**: Did Not Start (registered but didn't start)
- **Disqualified** (rare): Failed to meet course requirements

### Data Quality
- ✅ **Source**: UltraSignup (official race registration platform)
- ✅ **Scraped**: Using Playwright browser automation + jqGrid JavaScript API
- ✅ **Verified**: Dynamically resolved event IDs for consistency
- ✅ **Complete**: All finishers, DNF, DNS, and DQ tracked separately

---

## 🏃 Year-by-Year Summary

The detailed table shows:
- **Participants**: Total runners registered for the distance
- **Finishers**: Number who completed the race
- **Finish Rate**: Percentage of finishers

### Interpreting Finish Rates
- **> 70%**: Relatively easy/fast-running year
- **40-70%**: Moderate difficulty
- **< 40%**: Challenging/tough conditions

---

## 🚀 How Data is Maintained

### Automated Updates
- **Results Scraping**: 3x weekly after race (Sept 23, Sept 30, Oct 7)
- **Entrant Tracking**: Daily during registration season (July-Oct)
- **Auto-Commits**: GitHub Actions handles data updates automatically

### Manual Analysis
- Run `analyze_historical.py` to regenerate insights
- Update historical.html with latest data
- All data stored in `data/historical/` directory

---

## 📁 Data Structure

```
data/historical/
├── results/              # Raw race results
│   ├── results_2015_50k.json
│   ├── results_2015_marathon.json
│   ├── ... (through 2025)
│   └── results_2025_marathon.json
├── analysis/             # Generated analysis files
│   └── barkley_analysis.json
└── barkley_archive_complete.json  # Backup
```

---

## 💡 Key Insights

### 1. **Marathon Gets Harder Over Time**
Recent years (2020s) show declining finish rates compared to early years (2015-2018), suggesting:
- Course conditions may be more variable
- Talent/competitiveness increasing
- Weather challenges more severe in recent years

### 2. **50K is Consistently Easier**
- 87% average finish rate vs. 69% for marathon
- More stable year-to-year
- Better for achieving finishing goals

### 3. **Participation Patterns**
- Marathon draws more runners (bigger field)
- 50K attracts smaller, more experienced cohort
- Both growing/stable over the decade

---

## 🔧 Advanced Features

### Dynamic Race Date Detection
The system automatically:
- Extracts actual race dates from UltraSignup
- Calculates intelligent workflow schedules
- Adjusts entrant tracking based on race timing

### Intelligent Scheduling
- **Before Race**: Tracks current year entrants
- **After Race**: Automatically switches to next year's registration
- **Workflow Dates**: Based on extracted race dates, not hardcoded values

---

## 📝 Usage

### For Quick Stats
Open `historical.html` in a web browser to see:
- Overall participation and finish rates
- Interactive trend charts
- Year-by-year comparison table
- Key insights and observations

### For Data Export
Access JSON files directly in `data/historical/results/` for:
- Individual finisher records (name, time, age, division)
- Status breakdowns
- Custom analysis or reporting

### For Updates
Run `analyze_historical.py` to:
- Regenerate all metrics and insights
- Check for data consistency
- Create updated analysis dumps

---

## 🎯 Future Enhancements

Planned additions:
- Age group analysis and records
- Gender performance metrics
- Time distribution analysis
- State-by-state participation maps
- Personal records and repeat runner tracking
- Weather impact analysis

---

## 📞 Questions?

For questions about the data:
1. Check the historical analysis page charts
2. Review the year-by-year summary table
3. Examine raw JSON files for specific records
4. Run `analyze_historical.py` for detailed metrics

---

**Last Updated**: January 2026  
**Data Range**: 2015-2025 (11 years)  
**Status**: ✅ Complete and Automated
