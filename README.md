# 🏈 NFL Parlay Generator

A professional-grade NFL predictive analytics system that generates correlated parlays using Sharp betting data (EPA, DVOA, Target Share) through a weighted predictive engine.

## 🎯 Features

- **🔴 Live NFL Schedule**: Automatically fetches today's games and upcoming matchups from ESPN API
- **🖥️ Desktop GUI Application**: User-friendly form-based interface with tabbed navigation
- **📊 Weighted Recency Model**: Combines last 5 games (65%) with season averages (35%)
- **🛡️ DVOA Opponent Adjustments**: Modifies projections based on defensive strength
- **⚡ Efficiency Modifiers**: EPA, CPOE, Target Share, Air Yards integration
- **🎮 Game Script Analysis**: Identifies Trailing, Leading, and Explosive scenarios
- **🔗 Correlation Engine**: Builds multi-leg parlays based on expected game flow
- **📦 Pre-loaded Player Stats**: 2024 season data from NFL.com

## 🚀 Quick Start

### Prerequisites

```bash
pip install pydantic rich requests pytz
```

### Run the Desktop GUI

```bash
python NFL_GUI.py
```

The GUI will automatically load today's NFL games from ESPN API on startup!

### GUI Workflow

1. **Tab 1 - Game Setup**: 
   - 🔴 View today's games loaded automatically from ESPN
   - Select any game from the dropdown
   - Auto-populates spread, total, and team info
   - Or enter custom game details manually

2. **Tab 2 - Add Players**:
   - Select from pre-loaded rosters (Broncos/Commanders/etc)
   - ✓ Auto-fill stats from NFL.com data (green checkmarks)
   - Add custom players manually
   - Edit or delete players with buttons

3. **Tab 3 - Review & Generate**:
   - Review all entered data
   - 🚀 Generate projections with one click

4. **Tab 4 - Results**:
   - View projection table with edges
   - See correlated parlay recommendations
   - Identify best individual plays

## 📊 Projection Model

The projection engine uses a weighted average approach:

| Factor | Weight | Description |
|--------|--------|-------------|
| Last 5 Games | 65% | Recent performance trend |
| Season Average | 35% | Full season baseline |
| Defense Modifier | ±12% | Adjusted for opponent rank |
| EPA Boost | +5% | For efficient QBs (EPA > 0.20) |
| Target Share Boost | +8% | For high-volume receivers (>28%) |

## 🎮 Supported Stats

| Position | Projections |
|----------|-------------|
| **QB** | Pass Yds, Rush Yds, Pass Att, Pass TDs |
| **RB** | Rush Yds, Rush Att, Yards/Carry |
| **WR/TE** | Rec Yds, Receptions, Targets |

## 📁 Project Structure

```
NFL-Parlay-Generator/
├── NFL_GUI.py           # 🖥️ Desktop GUI application (RECOMMENDED)
├── NFL_pre.py           # 💻 Console/terminal application
├── nfl_schedule.py      # 📡 Live schedule fetcher (ESPN API)
├── NFL_app.html         # 🌐 Web interface (legacy)
├── README.md            # 📖 Documentation
└── manifest.json        # 📦 Project metadata
```

## 📡 Live Schedule API

The schedule fetcher automatically pulls:
- ✅ Today's games with odds/lines
- 🌙 Tonight's primetime matchups  
- 📅 Upcoming games for next 7 days
- ⚡ Real-time game status (pre-game, in-progress, final)

Test it standalone:
```bash
python nfl_schedule.py
```

Use it programmatically:
```python
from nfl_schedule import NFLScheduleFetcher

fetcher = NFLScheduleFetcher()
tonight = fetcher.get_tonights_game()
upcoming = fetcher.get_upcoming_games(days=7)

# Today it found:
# 🔴 Giants @ Patriots (Mon Night Football, 8:15 PM ET)
# Spread: -7.5 | O/U: 46.5
```

## 🔧 Configuration

### Favorite Team
In the web app, your favorite team is saved to `localStorage` and persists between sessions.

### Model Weights
Edit the `Config` class in `NFL_pre.py` to adjust:
```python
LAST_5_WEIGHT = 0.65              # Recent form weight
SEASON_AVG_WEIGHT = 0.35          # Season baseline weight
ELITE_DEFENSE_DAMPER = 0.88       # Top 5 defense modifier
POOR_DEFENSE_BOOST = 1.12         # Bottom 5 defense modifier
QB_EPA_THRESHOLD = 0.20           # EPA threshold for boost
WR_TARGET_SHARE_THRESHOLD = 28.0  # Volume floor threshold
```

## 🎓 Data Sources

- **Player Stats**: NFL.com official statistics (2024 season) - pre-loaded
- **Schedule/Odds**: ESPN API (live, auto-updated)
- **Sharp Metrics**: EPA, CPOE, DVOA, Target Share, Air Yards
- **Vegas Lines**: Manual entry (check DraftKings, FanDuel, BetMGM, etc.)

## 💻 Alternative Interfaces

### Console App (Terminal)
For advanced users who prefer terminal:

```bash
python NFL_pre.py
```

Features:
- Rich terminal UI with colored tables
- Roster-based player selection
- Auto-fill from pre-loaded stats
- Review/edit before generation
- Interactive navigation

### Web App (Browser)
Single-file HTML app:

```bash
python -m http.server 8000
# Open http://localhost:8000/NFL_app.html
```

Features:
- PWA installable
- Favorite team tracking
- Multi-game support
- No backend required

## ⚠️ Disclaimer

This tool is for **entertainment and research purposes only**. Projections are based on historical data and statistical models. Always do your own research and gamble responsibly.

## 📝 License

MIT License - feel free to use and modify!

---

Made with 🏈 by an NFL analytics enthusiast
