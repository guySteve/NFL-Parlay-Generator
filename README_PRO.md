# 🏈 NFL Parlay Generator Pro

> **Quantitative Analytics Engine for NFL Player Props & Parlays**

A desktop application that combines statistical analysis, confidence scoring, and narrative generation to help analyze NFL player prop bets.

---

## ✨ Key Features

### 🎨 **Dynamic NFL Theming**
- Automatically applies team colors when you select a game
- Supports all 32 NFL teams with official color schemes
- Modern, clean interface with light gray backgrounds (easy on the eyes)

### 📊 **Confidence-Scored Metrics**
Every metric shows a confidence indicator:
- **Green (80%+)**: High confidence
- **Yellow (60-79%)**: Moderate confidence  
- **Orange (<60%)**: ⚠️ Low confidence - orange border warning

### ℹ️ **Interactive Metric Info**
Click the **ℹ** button next to any metric to see:
- **What it means**: Plain English explanation
- **Where to find it**: Step-by-step Google search instructions
- **Quick links**: Direct links to RBSDM, Football Outsiders, NFL Next Gen Stats
- **Manual entry**: Update values on the spot

### 🎙️ **Tony Romo Narrative Analysis**
- Auto-generates matchup breakdowns in Tony Romo's broadcasting style
- Shows narrative confidence score
- Explains how the analysis was derived
- Updates when you change metrics

### 🏃 **Multi-Team Player Support**
- Add players from **BOTH teams** in one parlay
- System treats all players equally regardless of team
- Perfect for game script correlations (e.g., "If Team A wins big, Team B QB throws more")

### 🖥️ **Single-Window Design**
- No popups or separate tabs (as requested!)
- Everything in one scrollable interface
- Mouse wheel scrolling support
- Resizable but looks great at 1400x950

---

## 🚀 Installation & Launch

### First Time Setup

1. **Create Desktop Shortcut**:
   ```
   Right-click "create_pro_shortcut.ps1" → Run with PowerShell
   ```

2. **Launch App**:
   - Double-click **"NFL Parlay Generator Pro"** icon on desktop
   - Or run `launch_pro.bat` from the repo folder

### Requirements
- Python 3.8+
- tkinter (usually included with Python)
- No external dependencies needed!

---

## 📖 How to Use

### Quick Start (5 Steps)

1. **Load Today's Game**
   - Check "🔴 LIVE - Today's NFL Schedule"
   - Select a game from dropdown
   - Click **"Load Game ➜"**

2. **Review/Edit Metrics**
   - Game lines auto-populate
   - Click ℹ️ on any metric to learn where to find data
   - Manually update if needed

3. **Save Context**
   - Click **"💾 Save Game Context"**
   - Tony Romo narrative generates automatically

4. **Add Players**
   - Enter player name (from either team)
   - Select stat type, line, and Over/Under
   - Click **"➕ Add Player"**
   - Repeat for all parlay legs

5. **Generate Predictions**
   - Click **"🎯 Generate Parlay Predictions"**
   - Review results, probabilities, and recommendations

---

## 📊 The 4 Key Metrics

### 1. Opponent Def EPA/Play
- **What**: Expected Points Added per play by the defense
- **Better**: More negative (e.g., -0.10)
- **Find**: RBSDM.com → Team defense stats

### 2. Opponent DVOA Pass Def %
- **What**: Defense vs pass, adjusted for opponent quality
- **Better**: More negative (e.g., -8.5%)
- **Find**: FootballOutsiders.com → Team defense DVOA

### 3. Opponent DVOA Run Def %
- **What**: Defense vs run, adjusted for opponent quality
- **Better**: More negative (e.g., -12.0%)
- **Find**: FootballOutsiders.com → Team defense DVOA

### 4. Team Offense EPA L4
- **What**: Offensive EPA per play over last 4 games (recent form)
- **Better**: More positive (e.g., +0.18)
- **Find**: RBSDM.com → Filter by last 4 games

---

## 🔗 Data Sources

### Free Resources

| Source | Use Case | Link |
|--------|----------|------|
| **RBSDM** | EPA Statistics | rbsdm.com/stats/stats/ |
| **Football Outsiders** | DVOA Rankings | footballoutsiders.com/stats/nfl/team-defense |
| **NFL Next Gen** | Advanced Metrics | nextgenstats.nfl.com |
| **Team Rankings** | Quick Stats | teamrankings.com/nfl |

### APIs for Developers

| API | Purpose | Free Tier |
|-----|---------|-----------|
| **The Odds API** | Live betting lines | 100 requests/mo |
| **SportsData.io** | Comprehensive data | 1000 calls/day |
| **nfl-data-py** | Play-by-play history | Unlimited (local) |
| **ESPN Hidden API** | Schedules & teams | Unlimited |

See `PRO_USER_GUIDE.md` for API integration details.

---

## 💡 Pro Tips

### Building Better Parlays
1. ✅ **Check all confidence scores** - avoid anything <60%
2. 🎯 **Use game script correlation** - pair winning team with losing team's pass-heavy players
3. 📖 **Read the narrative** - Tony Romo analysis highlights key advantages
4. 🔍 **Manually verify** - always double-check data via ℹ️ buttons

### Interpreting Results
- **>40% combined probability** = Strong play
- **30-40%** = Viable play, proceed with caution
- **<30%** = High risk, consider fewer legs

### Common Workflows

**Quick Parlay (2 mins)**:
```
Load game → Add 2-3 players → Generate
```

**Deep Analysis (10 mins)**:
```
Load game → Click all ℹ️ buttons → Update metrics → Review narrative → Add players → Generate
```

**Multi-Game Parlay**:
```
Manually change Team A/B → Update metrics → Add players → Repeat for next game
```

---

## 🎨 Customization

### Change Default Theme
Edit line 46 in `NFL_GUI_Pro.py`:
```python
self.current_theme = NFL_TEAMS["Your Favorite Team"]
```

### Adjust Confidence Color Thresholds
Edit lines 195-201 in `NFL_GUI_Pro.py`:
```python
if confidence >= 80:  # Change to 85 for stricter green
    bg, fg = "#28a745", "white"
```

### Add More Stat Types
Edit line 477 to include new props:
```python
values=["Pass Yards", "Pass TDs", "Your Custom Stat", ...]
```

---

## 🐛 Troubleshooting

### App Won't Open
- **Check Python**: `python --version` in command prompt
- **Install tkinter**: Usually pre-installed, but run `pip install tk` if needed
- **Run as admin**: Right-click `launch_pro.bat` → Run as administrator

### Schedule Not Loading
- Click **"🔄 Refresh Games"**
- Check internet connection
- Manual entry always works as fallback

### Metrics Seem Wrong
- Click the **ℹ️** button for any metric
- Follow the instructions to find current data
- Manually update the value
- Re-save game context

### Shortcut Missing
- Re-run `create_pro_shortcut.ps1`
- Or bookmark `launch_pro.bat` for quick access

---

## 📁 Project Structure

```
NFL-Parlay-Generator/
├── NFL_GUI_Pro.py           # Main application (NEW!)
├── launch_pro.bat            # Windows launcher
├── create_pro_shortcut.ps1   # Desktop shortcut creator
├── PRO_USER_GUIDE.md         # Detailed user manual
├── QUICK_REFERENCE.txt       # One-page cheat sheet
├── README_PRO.md             # This file
└── [other files...]          # Legacy versions
```

---

## 🆚 Comparison: Pro vs Original

| Feature | Original GUI | Pro Version |
|---------|--------------|-------------|
| **Interface** | Multi-tab, popups | Single scrollable window |
| **Theming** | Generic | Dynamic NFL team colors |
| **Metrics** | Simple rank (1-32) | 4 quantitative EPA/DVOA metrics |
| **Confidence** | None | All metrics scored with ℹ️ help |
| **Narrative** | None | Tony Romo-style analysis |
| **Player Input** | Single team focus | Both teams equally supported |
| **Data Help** | None | Interactive guides for every metric |
| **Styling** | High contrast | Easy-on-eyes light gray |

---

## ⚖️ Disclaimer

**For entertainment and educational purposes only.**

- This is NOT financial advice
- Past performance does not guarantee future results
- Sports betting involves risk of loss
- Always gamble responsibly
- Verify all data independently before placing bets
- Models are simplified for demonstration

**Use at your own risk. The developers assume no liability for any losses.**

---

## 🤝 Contributing

Found a bug? Have a feature request?

1. Check existing issues in the repo
2. Create a new issue with details
3. For data source suggestions, see `PRO_USER_GUIDE.md`

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🏆 Credits

- **Statistical Models**: Based on EPA/DVOA frameworks from Football Outsiders and RBSDM
- **Design Inspiration**: Modern sports analytics dashboards
- **Narrative Engine**: Inspired by Tony Romo's broadcasting style
- **Color Schemes**: Official NFL team branding

---

## 📞 Support

For detailed instructions, see:
- **PRO_USER_GUIDE.md** - Comprehensive manual
- **QUICK_REFERENCE.txt** - One-page cheat sheet

---

**Good luck and bet responsibly! 🏈**
