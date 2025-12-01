# 🏈 NFL Parlay Generator

A predictive analytics and projection builder for NFL player props. Features a modern web interface with pure projections, favorite team tracking, and multi-game support.

![NFL Parlay Generator](https://img.shields.io/badge/NFL-Parlay%20Generator-00d4aa?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

## ✨ Features

### Web App (`NFL_app.html`)
- **Pure Projections** - Model-based projections with floor/ceiling ranges and confidence scores
- **Favorite Team** - Save your team to localStorage, auto-selects their games
- **Game Selector** - Switch between multiple NFL matchups
- **Player Stats Dashboard** - View detailed stats for QBs, RBs, WRs, and TEs
- **Pick Builder** - Build your selection slate with confidence tracking
- **Analysis Tab** - Game script analysis and correlation guides
- **PWA Ready** - Installable as a Progressive Web App

### Console App (`NFL_pre.py`)
- **Rich TUI** - Beautiful terminal interface with Rich library
- **Weighted Projections** - L5 (65%) + Season (35%) weighted model
- **DVOA Modifiers** - Defense-adjusted projections
- **Correlation Engine** - Identifies correlated player props
- **Pre-loaded Stats** - Auto-fill from NFL.com data

## 🚀 Quick Start

### Web App (No Dependencies!)
```bash
# Start a local server
python -m http.server 8000

# Open in browser
http://localhost:8000/NFL_app.html
```

### Console App
```bash
# Install dependencies
pip install rich pydantic

# Run the app
python NFL_pre.py
```

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
├── NFL_app.html      # Web interface (PWA)
├── NFL_pre.py        # Console application
├── manifest.json     # PWA manifest
└── README.md
```

## 🔧 Configuration

### Favorite Team
Your favorite team is saved to `localStorage` and persists between sessions. Games featuring your team are highlighted with ⭐.

### Model Weights
Edit the `CONFIG` object in the JavaScript or Python file to adjust:
- `L5_WEIGHT` - Weight for last 5 games (default: 0.65)
- `SEASON_WEIGHT` - Weight for season average (default: 0.35)
- `ELITE_DAMPER` - Multiplier vs top-5 defenses (default: 0.88)
- `POOR_BOOST` - Multiplier vs bottom-5 defenses (default: 1.12)

## ⚠️ Disclaimer

This tool is for **entertainment and research purposes only**. Projections are based on historical data and statistical models. Always do your own research and gamble responsibly.

## 📝 License

MIT License - feel free to use and modify!

---

Made with 🏈 by an NFL analytics enthusiast
