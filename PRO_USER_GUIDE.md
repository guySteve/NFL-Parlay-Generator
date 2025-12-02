# NFL Parlay Generator Pro - User Guide

## 🚀 Quick Start

### Installation

1. **Create Desktop Shortcut**:
   ```powershell
   Right-click "create_pro_shortcut.ps1" → Run with PowerShell
   ```
   This creates a desktop icon for easy access.

2. **Launch the App**:
   - Double-click the "NFL Parlay Generator Pro" icon on your desktop
   - OR run `launch_pro.bat` from the repository folder

---

## 📋 Features Overview

### 1. **Dynamic Team Theming**
- Select any NFL team and the entire UI updates with their team colors
- Automatic theming when you load a game from the schedule

### 2. **Live Schedule Integration**
- Automatically loads today's NFL games
- Click "Refresh" to update the schedule
- Select a game and click "Load Game ➜" to populate both teams

### 3. **Quantitative Metrics with Confidence Scores**
Every metric shows a **confidence indicator**:
- 🟢 **Green** (80%+): High confidence, reliable data
- 🟡 **Yellow** (60-79%): Moderate confidence
- 🟠 **Orange** (<60%): Low confidence, needs attention

**Orange Border Warning**: Calculations under 60% confidence are highlighted for review.

### 4. **Metric Info Buttons (ℹ)**
Click the **ℹ** button next to any metric to see:
- What the metric means
- Where to find the data (step-by-step Google search instructions)
- Quick links to data sources (RBSDM, Football Outsiders, NFL Next Gen Stats)
- Manual entry form to update values

### 5. **Tony Romo Narrative Analysis**
- Automatically generates a unique matchup description in Tony Romo's broadcasting style
- Shows confidence score for the narrative
- Click the **ℹ** button to see how the narrative was derived

### 6. **Single-Window Design**
- Everything in ONE scrollable window - no popup menus or separate tabs
- Smooth scrolling with mouse wheel support

### 7. **Multi-Team Player Support**
- Add players from BOTH teams in the same parlay
- Team names are just labels - the system predicts ALL players equally

---

## 🎮 How to Use

### Step 1: Load a Game
1. Check the "🔴 LIVE - Today's NFL Schedule" section
2. Select a game from the dropdown
3. Click **"Load Game ➜"**
4. The app will:
   - Load both team names
   - Apply the home team's color theme
   - Generate an initial narrative analysis

### Step 2: Adjust Game Context
1. Review the auto-populated teams (you can change them if needed)
2. Enter game lines:
   - **Spread**: Point spread for Team A (negative means favored)
   - **Total O/U**: Game total over/under
   - **Implied Total**: Expected points for Team A

3. Enter the **4 Quantitative Metrics**:
   - **Opponent Def EPA/Play**: Click ℹ to see where to find this
   - **Opponent DVOA Pass Def %**: Defense vs passing
   - **Opponent DVOA Run Def %**: Defense vs running
   - **Team A Off EPA L4**: Offensive performance last 4 games

4. Click **"💾 Save Game Context"** to update the narrative

### Step 3: Add Players
1. Enter **Player Name** (from either team)
2. Select **Stat Type**: Pass Yards, Rush Yards, Receptions, TDs, etc.
3. Enter the **Line** (betting line value)
4. Pick **Over/Under/Yes**
5. Click **"➕ Add Player"**

Repeat for all players in your parlay.

### Step 4: Generate Predictions
1. Review your added players in the display
2. Click **"🎯 Generate Parlay Predictions"**
3. View results:
   - Individual player probabilities
   - Confidence scores for each pick
   - Combined parlay probability
   - Expected value (EV)
   - Recommendation (Strong Play / Viable / High Risk)

---

## 📊 Understanding the Metrics

### EPA (Expected Points Added)
- Measures the value of each play
- **Negative** defensive EPA = good defense
- **Positive** offensive EPA = good offense
- Range: typically -0.20 to +0.30

### DVOA (Defense-adjusted Value Over Average)
- Adjusts for opponent strength
- **Negative** DVOA = better than average
- **Positive** DVOA = worse than average
- Example: -10% = elite, +10% = poor

### Where to Find Data

#### Quick Links:
1. **RBSDM.com** - EPA statistics (free)
   - Search: "RBSDM NFL EPA stats 2024"
   - Navigate to team pages for EPA/play data

2. **Football Outsiders** - DVOA rankings
   - https://www.footballoutsiders.com/stats/nfl/team-defense/2024
   - Provides pass/run DVOA splits

3. **NFL Next Gen Stats** - Advanced tracking
   - https://nextgenstats.nfl.com/
   - Player separation, route data, etc.

4. **Team Rankings** - Quick defensive stats
   - https://www.teamrankings.com/nfl/

---

## 💡 Pro Tips

### Building Better Parlays
1. **Check Confidence Scores**: Avoid picks with <60% confidence
2. **Use Both Teams**: Correlate game script (e.g., if Team A wins big, Team B QB throws more)
3. **Review Narratives**: Tony Romo analysis highlights key matchup advantages
4. **Manual Override**: Use the ℹ buttons to manually enter better data if available

### Interpreting Results
- **Combined Probability > 40%**: Strong play
- **Combined Probability 30-40%**: Viable play
- **Combined Probability < 30%**: High risk, consider reducing legs

### Common Workflows
1. **Quick Parlay**: Load game → Add 2-3 players → Generate
2. **Deep Analysis**: Load game → Click all ℹ buttons → Update metrics → Add players → Generate
3. **Multi-Game**: Change teams manually → Repeat for different games

---

## 🔧 Troubleshooting

### App Won't Open
- Right-click `launch_pro.bat` → Edit
- Check that Python is installed: `python --version`
- Install required packages: `pip install tkinter`

### Schedule Not Loading
- Click "🔄 Refresh Games"
- Check internet connection
- Manual entry still works without schedule

### Metrics Look Wrong
- Click the ℹ button for any metric
- Follow the "Where to find this data" instructions
- Manually enter correct values
- Values auto-save when you click "Save Game Context"

### Shortcut Not Working
- Re-run `create_pro_shortcut.ps1` with PowerShell
- Or manually double-click `launch_pro.bat`

---

## 📡 API Recommendations

### Free APIs to Enhance Accuracy

1. **NFL API** (unofficial)
   - https://github.com/nntrn/nfl-api
   - Live scores, schedules, team data

2. **ESPN API** (hidden/undocumented)
   - http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams
   - Team info, schedules

3. **The Odds API** (freemium)
   - https://the-odds-api.com/
   - Live betting lines (100 free requests/month)

4. **SportsData.io** (freemium)
   - https://sportsdata.io/nfl-api
   - Comprehensive NFL data (1000 calls/day free)

5. **NFLData Python Package**
   - `pip install nfl-data-py`
   - Historical play-by-play data for EPA calculations

### Implementation Note
The current version uses simulated data for demo purposes. To integrate real APIs:
1. Get API keys from the services above
2. Replace the `_load_schedule()` method in `NFL_GUI_Pro.py`
3. Add API calls in the prediction engine

---

## 🎨 Customization

### Change Default Theme
Edit line 46 in `NFL_GUI_Pro.py`:
```python
self.current_theme = NFL_TEAMS["Your Team Name"]
```

### Adjust Confidence Thresholds
Edit lines 195-201 in `NFL_GUI_Pro.py` to change color coding.

### Add More Stat Types
Edit line 477 to add new stat options:
```python
values=["Pass Yards", "Your New Stat", ...]
```

---

## 📞 Support

For questions or issues:
1. Check this guide first
2. Review the code comments in `NFL_GUI_Pro.py`
3. Test with sample data before live betting
4. Always verify predictions with your own analysis

---

## ⚖️ Disclaimer

This tool is for **entertainment and educational purposes only**. 

- Not financial advice
- Past performance doesn't guarantee future results
- Always gamble responsibly
- Verify all data independently
- Betting involves risk of loss

**Use at your own risk.**
