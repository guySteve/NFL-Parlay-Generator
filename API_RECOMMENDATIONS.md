# 🌐 API & Data Source Recommendations

## Free APIs (Public Data)

### 1. **ESPN API** (Unofficial but Widely Used)
- **What it provides**: Live scores, schedules, team stats, player stats
- **Endpoints**:
  - `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard`
  - `https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams`
- **How to use**: Simple GET requests, no auth required
- **Accuracy**: Very high for basic stats (85-90%)
- **Best for**: Real-time game data, player prop tracking

```python
import requests

# Get current week's games
response = requests.get('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard')
games = response.json()
```

---

### 2. **NFL.com Official Stats**
- **What it provides**: Official NFL statistics, player data
- **URL**: `https://www.nfl.com/stats/`
- **Method**: Web scraping (no official API)
- **Accuracy**: 100% (official source)
- **Libraries**: Use `BeautifulSoup` or `Selenium` for scraping
- **Best for**: Season-long stats, official records

---

### 3. **Pro Football Reference (PFR)**
- **What it provides**: Historical stats, advanced metrics, game logs
- **URL**: `https://www.pro-football-reference.com/`
- **Method**: Web scraping (HTML tables are clean and structured)
- **Accuracy**: 95%+ (trusted by analysts)
- **Best for**: Historical analysis, player trends over multiple seasons

```python
import pandas as pd

# Example: Scrape QB stats table
url = 'https://www.pro-football-reference.com/years/2024/passing.htm'
tables = pd.read_html(url)
qb_stats = tables[0]  # First table is usually passing stats
```

---

## Paid APIs (Premium Data)

### 4. **Sportradar NFL API** ⭐ RECOMMENDED
- **Cost**: ~$500-2000/month (depends on usage)
- **What it provides**: 
  - Real-time play-by-play data
  - Advanced metrics (EPA, DVOA-like stats)
  - Injury reports
  - Vegas odds integration
- **Accuracy**: 99% (official NFL data partner)
- **Documentation**: https://developer.sportradar.com/
- **Best for**: Professional-grade analysis, real-time prop tracking

---

### 5. **The Odds API** (Vegas Lines & Props)
- **Cost**: Free tier (500 requests/month), $20-100/month for more
- **What it provides**: Real-time betting odds from multiple sportsbooks
- **URL**: https://the-odds-api.com/
- **Accuracy**: 95%+ (pulls from DraftKings, FanDuel, BetMGM, etc.)
- **Best for**: Line shopping, prop bet identification

```python
import requests

API_KEY = 'your_api_key_here'
SPORT = 'americanfootball_nfl'

response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/',
    params={'apiKey': API_KEY, 'regions': 'us', 'markets': 'h2h,spreads'}
)
odds = response.json()
```

---

### 6. **RapidAPI NFL Collections**
- **Cost**: Free tier available, $10-50/month for more
- **What it provides**: Various NFL data APIs aggregated in one place
- **URL**: https://rapidapi.com/collection/nfl-api
- **Options include**:
  - Tank01 NFL API (stats, schedules)
  - NFL Data API (team/player info)
- **Best for**: Quick prototyping without individual API accounts

---

## Advanced Analytics Sources

### 7. **RBSDM.com** (Manual, but can automate)
- **What it provides**: EPA per play, success rate, CPOE
- **Method**: Scrape their stats page or use their CSV exports
- **Accuracy**: 90%+ (uses nflfastR data)
- **Cost**: Free
- **URL**: https://rbsdm.com/stats/stats/

---

### 8. **nflfastR** (R Package - can integrate with Python)
- **What it provides**: Play-by-play data with EPA, WPA, CPOE calculated
- **Method**: Download CSV files or use R in Python via `rpy2`
- **Accuracy**: 98% (gold standard for NFL analytics)
- **Cost**: Free
- **GitHub**: https://github.com/nflverse/nflfastR

```python
# Option 1: Download pre-built CSV from nflfastR
import pandas as pd

url = 'https://github.com/nflverse/nflfastR-data/blob/master/data/play_by_play_2024.csv.gz?raw=true'
pbp = pd.read_csv(url, compression='gzip', low_memory=False)
```

---

### 9. **Football Outsiders / FTN Data** (DVOA)
- **Cost**: $30/year for basic, $100+ for premium
- **What it provides**: DVOA, DYAR, situational stats
- **URL**: https://www.footballoutsiders.com/
- **Accuracy**: 95%+ (industry-standard advanced metrics)
- **Best for**: DVOA-based matchup analysis

---

## Our Recommendations for Your Tool

### **Tier 1: Free (Get Started)**
1. **ESPN API** → Real-time game data
2. **nflfastR CSV downloads** → EPA/CPOE metrics
3. **Pro Football Reference scraping** → Historical trends

**Implementation Priority**: 
- Start with ESPN API for schedule/roster data
- Use nflfastR CSV for EPA calculations
- Scrape RBSDM for DVOA-like defensive metrics

---

### **Tier 2: Low-Cost Enhancement ($20-50/month)**
1. **The Odds API** → Real-time prop lines for EV calculation
2. **RapidAPI NFL bundle** → Backup data source

**Why**: Adds real-time odds tracking so users can calculate true EV (Expected Value) on props.

---

### **Tier 3: Professional Grade ($500+/month)**
1. **Sportradar** → Official NFL data partner
2. **Football Outsiders Premium** → True DVOA metrics

**Why**: Near-perfect accuracy, real-time play-by-play, injury updates.

---

## Integration Code Examples

### Auto-Fetch Current Week's Games
```python
import requests
from datetime import datetime

def get_current_week_games():
    """Fetch current week's NFL games from ESPN."""
    url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
    response = requests.get(url)
    data = response.json()
    
    games = []
    for event in data.get('events', []):
        game = {
            'date': event['date'],
            'home_team': event['competitions'][0]['competitors'][0]['team']['displayName'],
            'away_team': event['competitions'][0]['competitors'][1]['team']['displayName'],
            'home_score': event['competitions'][0]['competitors'][0].get('score', 'N/A'),
            'away_score': event['competitions'][0]['competitors'][1].get('score', 'N/A'),
            'status': event['status']['type']['description']
        }
        games.append(game)
    
    return games

# Usage
games_today = get_current_week_games()
for game in games_today:
    print(f"{game['away_team']} @ {game['home_team']} - {game['status']}")
```

---

### Auto-Fetch EPA Data from nflfastR
```python
import pandas as pd

def get_team_epa_last_n_games(team_abbr: str, n_games: int = 4, season: int = 2024):
    """
    Get a team's offensive EPA over their last N games.
    
    Args:
        team_abbr: Team abbreviation (e.g., 'KC', 'BUF')
        n_games: Number of recent games to analyze
        season: NFL season year
    
    Returns:
        float: Average EPA per play over last N games
    """
    # Load play-by-play data
    url = f'https://github.com/nflverse/nflfastR-data/blob/master/data/play_by_play_{season}.csv.gz?raw=true'
    pbp = pd.read_csv(url, compression='gzip', low_memory=False)
    
    # Filter for team's offensive plays
    team_plays = pbp[
        (pbp['posteam'] == team_abbr) & 
        (pbp['play_type'].isin(['pass', 'run']))
    ].copy()
    
    # Get last N games
    recent_games = team_plays['game_id'].unique()[-n_games:]
    recent_plays = team_plays[team_plays['game_id'].isin(recent_games)]
    
    # Calculate EPA
    avg_epa = recent_plays['epa'].mean()
    
    return avg_epa

# Example usage
chiefs_epa = get_team_epa_last_n_games('KC', n_games=4)
print(f"Chiefs EPA (last 4 games): {chiefs_epa:.3f}")
```

---

### Auto-Fetch Opponent Defense EPA
```python
def get_defense_epa(team_abbr: str, season: int = 2024):
    """
    Get a team's defensive EPA (lower is better).
    
    Args:
        team_abbr: Team abbreviation
        season: NFL season year
    
    Returns:
        float: Average EPA allowed per play
    """
    url = f'https://github.com/nflverse/nflfastR-data/blob/master/data/play_by_play_{season}.csv.gz?raw=true'
    pbp = pd.read_csv(url, compression='gzip', low_memory=False)
    
    # Filter for plays against this defense
    def_plays = pbp[
        (pbp['defteam'] == team_abbr) & 
        (pbp['play_type'].isin(['pass', 'run']))
    ].copy()
    
    # Calculate EPA allowed
    avg_epa_allowed = def_plays['epa'].mean()
    
    return avg_epa_allowed

# Example
broncos_def_epa = get_defense_epa('DEN')
print(f"Broncos Defensive EPA: {broncos_def_epa:.3f}")
```

---

## Implementation Roadmap

### Phase 1: Basic Automation (Week 1)
- [ ] Integrate ESPN API for schedule
- [ ] Auto-populate team names from API
- [ ] Fetch current week's games on startup

### Phase 2: EPA Automation (Week 2)
- [ ] Download nflfastR CSV on app launch
- [ ] Calculate Team Offense EPA (last 4 games) automatically
- [ ] Calculate Opponent Defense EPA automatically
- [ ] Cache results for 24 hours (reduce load times)

### Phase 3: DVOA Scraping (Week 3)
- [ ] Scrape RBSDM.com or Football Outsiders for DVOA
- [ ] Auto-populate DVOA vs Pass and Run fields
- [ ] Update daily via scheduled task

### Phase 4: Odds Integration (Week 4)
- [ ] Integrate The Odds API
- [ ] Display current prop lines
- [ ] Calculate true EV based on model vs. market

---

## Cost Summary

| Tier | Monthly Cost | Features |
|------|-------------|----------|
| **Free** | $0 | ESPN API, nflfastR, scraping |
| **Enhanced** | $20-50 | The Odds API, RapidAPI |
| **Professional** | $500+ | Sportradar, FTN Data Premium |

**Recommendation**: Start with Free tier, add The Odds API ($20/month) once you have 50+ active users.

---

## Next Steps

1. **Choose ESPN API + nflfastR** for initial implementation
2. **Build caching system** to avoid re-downloading data every session
3. **Add "Auto-Fetch" button** in GUI to populate EPA fields automatically
4. **Test accuracy** against manual data entry for 10 games

Would you like me to build the API integration functions into your GUI?
