# 🏈 NFL Parlay Generator Pro - Desktop Edition

**Professional-grade NFL parlay generation with live data, quantitative analytics, and Tony Romo-style narratives**

## 🚀 Quick Start

### 1. Create Desktop Icon
```powershell
.\create_desktop_app_shortcut.ps1
```

### 2. Launch Application
Double-click **"NFL Parlay Generator Pro"** on your desktop, or run:
```bash
.\launch_parlay_pro.bat
```

---

## ✨ Features

### 🔴 Live NFL Schedule
- **Real-time game data** from ESPN API
- Automatic detection of today's games
- Live odds, spreads, and totals
- One-click game loading

### 👥 Smart Roster Loading
- Pre-loaded team rosters for all 32 NFL teams
- Quick player selection by position (QB, RB, WR, TE)
- Multi-select support for batch predictions
- Works with players from **both teams**

### 📊 Confidence-Scored Predictions
- **Quantitative confidence scores** (0-100%) for every prediction
- **Orange borders** highlight predictions below 60% confidence
- Click **ℹ️ Data Sources** button to see exactly where to find the metrics
- Detailed statistical breakdowns

### 🎤 Tony Romo-Style Narrative Analysis
- Enthusiastic, conversational game analysis
- Bold predictions with personality
- Confidence-scored narratives
- Click **ℹ️** to see how the narrative was derived

### 🎨 Dynamic Team Themes
- Automatically updates colors based on selected team
- Uses official NFL team colors
- Modern, clean interface
- Single-window design (no popups!)

---

## 📖 How To Use

### Step 1: Load Today's Game
1. Click **🔄 Refresh Schedule** to load today's NFL games
2. Select a game from the list
3. Click **Load Selected Game**
4. Game info and team colors will update automatically

### Step 2: Add Players
1. Select a team from the dropdown (home or away)
2. Browse players by position (QB, RB, WR, TE tabs)
3. Hold Ctrl/Cmd to select multiple players
4. Click **➕ Add Selected Players**
5. Repeat for the other team if desired

### Step 3: Generate Predictions
1. Click **🎯 Generate Predictions**
2. Review predictions with confidence scores
3. **Orange borders** = Lower confidence (<60%)
4. **Green borders** = Higher confidence (≥60%)
5. Click **ℹ️ Data Sources** on any prediction to see where to find the stats

### Step 4: Review Narrative
1. Read the Tony Romo-style game analysis
2. Check the **Narrative Confidence** score
3. Click **ℹ️** to understand how the narrative was created
4. Click **🔄 Refresh Narrative** to regenerate

---

## 🔍 Understanding Confidence Scores

### What They Mean
- **75-100%**: High confidence, stable historical performance
- **60-74%**: Moderate confidence, some variance
- **Below 60%**: Low confidence, high variance (highlighted with orange border)

### How They're Calculated
```
Confidence = 100 × (1 - min(variance / threshold, 1.0))
```
- Lower historical variance = Higher confidence
- Based on player consistency over last 5 games
- Adjusted for opponent defense metrics

### Why Some Are Low
- **Injured/backup players**: Limited recent data
- **Rookie players**: No historical baseline
- **Matchup uncertainty**: Elite defense vs. average offense
- **Weather factors**: Outdoor games in poor conditions

---

## 🎓 Data Sources Guide

### Click the **ℹ️** button on any prediction to see:

#### 1. Historical Stats
- **Google Search**: `"[Player Name] NFL stats 2024"`
- **ESPN**: `ESPN.com/NFL/Players`
- **Pro-Football-Reference**: `Pro-Football-Reference.com`

#### 2. Recent Performance
- **NFL.com**: Season stats, last 5 games
- **FantasyPros**: Target/carry share data

#### 3. Matchup Data
- **TeamRankings**: Defensive rankings by position
- **Google**: `"[Team] vs [Opponent] [Position] stats"`

#### 4. Advanced Metrics (EPA/DVOA)
- **PFF.com** (Paid): EPA per play, DVOA
- **NFLSavant.com** (Free): Basic EPA data
- **Sharp Football Stats**: DVOA approximations

#### 5. Vegas Lines
- **DraftKings**
- **FanDuel**
- **BetMGM**

---

## 🔌 API Recommendations for Enhanced Accuracy

### Free APIs
1. **ESPN API** (Already integrated)
   - Live scores, schedules, basic stats
   - `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard`

2. **Pro-Football-Reference** (Web scraping)
   - Historical player data
   - Advanced metrics

3. **The Odds API** (Free tier: 500 requests/month)
   - Real-time betting lines
   - `https://the-odds-api.com`

### Paid APIs (For Pro Features)
1. **SportsDataIO** ($50-500/month)
   - Real-time play-by-play data
   - Player projections
   - Injury reports

2. **Pro Football Focus (PFF)** ($200+/year)
   - EPA, DVOA, Advanced metrics
   - Player grades

3. **RapidAPI NFL Bundle** ($10-100/month)
   - Multiple data sources
   - Historical trends

---

## ⚙️ Configuration

### Customizing Predictions
Edit the `PredictionEngine` class in `NFL_Parlay_Desktop_Pro.py`:

```python
# Base predictions by position (lines 425-445)
if position == "QB":
    base_yards = 250  # Adjust QB baseline
    variance = 45     # Adjust confidence calculation
```

### Adding More Teams
The app auto-loads all 32 NFL teams. To add custom rosters:

```python
# Edit DEFAULT_ROSTERS dictionary (line 82)
"Your Team": {
    "QB": [{"name": "Player Name", "number": "10"}],
    # ... more positions
}
```

### Changing Confidence Thresholds
```python
# Line 394: Calculate confidence
threshold = 0.5  # Lower = stricter confidence
```

---

## 🐛 Troubleshooting

### "No games today"
- Check your internet connection
- ESPN API may be down (try refreshing)
- During offseason, load a manual game

### Players not loading
- Ensure team name is spelled exactly as ESPN lists it
- Check console for error messages
- Default rosters are pre-loaded for testing

### Slow performance
- Reduce number of selected players
- Check network latency for API calls
- Consider caching game data locally

### Orange borders everywhere
- This means the default prediction model needs real data
- Click **ℹ️** to manually input actual player stats
- Integrate paid APIs for better predictions

---

## 🚀 Advanced Usage

### Manual Data Entry
1. Load a game
2. Click **ℹ️ Data Sources** on a prediction
3. Follow the links to gather real stats
4. Future feature: Manual stat input panel

### Building Custom Parlays
1. Generate predictions for 5-8 players
2. Focus on predictions with >70% confidence
3. Mix player types (QB + RB from opposing teams)
4. Use narrative analysis to validate game script

### Bankroll Management (Coming Soon)
- Kelly Criterion calculator
- Risk assessment per parlay
- Historical ROI tracking

---

## 📊 Technical Architecture

### Stack
- **Python 3.12+**
- **Tkinter** (Native GUI)
- **Requests** (API calls)
- **Pytz** (Timezone handling)

### Design Patterns
- **MVC Architecture**: Separate data, logic, and UI
- **Observer Pattern**: UI updates on data changes
- **Factory Pattern**: Prediction generation

### Performance
- **Asynchronous API calls**: Non-blocking UI
- **Lazy loading**: Rosters load on demand
- **Caching**: Game data cached per session

---

## 🛠️ Development

### Running from Source
```bash
python NFL_Parlay_Desktop_Pro.py
```

### Dependencies
```bash
pip install requests pytz
```

### Building Standalone EXE (Optional)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "NFL Parlay Pro" NFL_Parlay_Desktop_Pro.py
```

---

## 📝 Changelog

### v2.0.0 (Current)
- ✅ Single-window interface (no popups)
- ✅ Live ESPN schedule integration
- ✅ Team roster auto-loading
- ✅ Confidence-scored predictions
- ✅ Orange borders for <60% confidence
- ✅ Tony Romo-style narratives
- ✅ Data source tooltips
- ✅ Dynamic team themes
- ✅ Desktop icon creation

### v1.0.0 (Legacy)
- Basic GUI with manual entry
- No live data
- Simple predictions

---

## 🤝 Contributing

### To Add Features
1. Fork the repository
2. Create a feature branch
3. Add your code to `NFL_Parlay_Desktop_Pro.py`
4. Test thoroughly
5. Submit a pull request

### Feature Requests
- Manual stat input panel
- Historical parlay tracking
- Export to CSV/PDF
- Integration with sportsbooks
- Machine learning model upgrades

---

## 📜 License

MIT License - Free to use and modify

---

## 🏆 Credits

**Author**: NFL Analytics Team  
**Version**: 2.0.0  
**Python**: 3.12+  

Built with ❤️ for NFL betting enthusiasts

---

## ⚠️ Disclaimer

This tool is for **entertainment and educational purposes only**. 

- Not financial advice
- Gambling involves risk
- Bet responsibly
- Check local laws
- Past performance ≠ future results

**Always gamble within your means.**

---

## 🎯 Next Steps

1. ✅ Create desktop shortcut: `.\create_desktop_app_shortcut.ps1`
2. 🏈 Launch app and load today's game
3. 👥 Select players from both teams
4. 📊 Generate predictions with confidence scores
5. 🎤 Review Tony Romo narrative
6. 💰 Build your parlay!

**Good luck and may your predictions be sharp! 🏈📈**
