# 🏆 Multi-Sport Parlay Generator Guide

## Features

### Supported Sports
- 🏈 **NFL** - Football parlays with player props
- 🏀 **NBA** - Basketball parlays with player props  
- 🏒 **NHL** - Hockey parlays with player props

### Key Improvements
✅ **Fixed Checkbox Spacing** - Props now have proper padding (no more squishing!)
✅ **Multi-Sport Support** - Switch between NFL, NBA, NHL with one click
✅ **Better Tab Padding** - Tabs are larger and easier to click
✅ **Sport-Specific Props** - Each sport has relevant prop bet types
✅ **Position Filtering** - Positions update based on selected sport

## How to Create Desktop Shortcut

### Option 1: Run PowerShell Script (Recommended)
1. Right-click `create_desktop_shortcut.ps1`
2. Select "Run with PowerShell"
3. A shortcut will appear on your desktop!

### Option 2: Manual Shortcut
1. Right-click `launch_multisport.bat`
2. Select "Send to" → "Desktop (create shortcut)"
3. Rename it to "Multi-Sport Parlay Generator"

## Sport-Specific Features

### NFL Props
- Passing Yards, TDs, Completions
- Rushing Yards, TDs
- Receptions, Receiving Yards, TDs
- Anytime TD Scorer
- Field Goals, Extra Points

### NBA Props
- Points, Rebounds, Assists
- 3-Pointers Made
- Steals, Blocks
- Points + Rebounds + Assists (PRA)
- Double-Double, Triple-Double

### NHL Props
- Goals, Assists, Points (G+A)
- Shots on Goal
- Saves, Save Percentage
- Anytime Goal Scorer

## Recommended APIs for Live Data

### NFL
- ESPN API (free tier available)
- The Odds API (sports betting lines)
- NFL.com official feeds

### NBA
- NBA Stats API (official, free)
- The Odds API
- ESPN API

### NHL
- NHL Stats API (official, free)
- The Odds API
- ESPN API

## Tips for Maximum Profit

1. **Mix Sports** - Diversify across NFL, NBA, and NHL games on the same day
2. **Correlation** - Look for positive correlations (e.g., team winning + star player props)
3. **Line Shopping** - Compare odds across multiple sportsbooks
4. **Bankroll Management** - Never bet more than 1-5% of bankroll per parlay
5. **Volume** - More games = more opportunities, but be selective

## Advanced Features (Coming Soon)

- Live odds integration
- Historical correlation analysis
- EV calculator with Kelly Criterion
- Automated line comparisons
- Injury/news alerts
- Performance tracking

## Troubleshooting

**Issue**: Checkboxes look squished
**Fix**: Checkbox padding has been increased to `[5, 5]` with `pady=5` spacing

**Issue**: Can't switch sports
**Fix**: Use radio buttons at top right (🏈 NFL | 🏀 NBA | 🏒 NHL)

**Issue**: Desktop shortcut doesn't work
**Fix**: Make sure Python is in your system PATH, or edit the batch file to include full Python path

## Contact & Support

For issues or feature requests, check the project README or documentation files.

---

**Remember**: This tool is for educational and entertainment purposes. Always gamble responsibly!
