#!/usr/bin/env python3
"""
NFL Schedule Fetcher

Fetches current NFL schedule from ESPN API to automatically detect
tonight's game or upcoming games.

Author: NFL Analytics Team
Version: 1.0.0
"""

import requests
from datetime import datetime, timedelta
from typing import Optional
import pytz


class NFLScheduleFetcher:
    """Fetches NFL schedule data from ESPN API."""
    
    ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    
    def __init__(self):
        """Initialize the schedule fetcher."""
        self.eastern_tz = pytz.timezone('US/Eastern')
    
    def get_todays_games(self) -> list[dict]:
        """
        Fetch today's NFL games.
        
        Returns:
            List of game dictionaries with team names, time, odds, etc.
        """
        try:
            response = requests.get(self.ESPN_API_BASE, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                game_info = self._parse_game(event)
                if game_info:
                    games.append(game_info)
            
            return games
            
        except Exception as e:
            print(f"Error fetching schedule: {e}")
            return []
    
    def get_games_for_date(self, date_str: str) -> list[dict]:
        """
        Fetch games for a specific date.
        
        Args:
            date_str: Date in YYYYMMDD format (e.g., "20241201")
            
        Returns:
            List of game dictionaries.
        """
        try:
            url = f"{self.ESPN_API_BASE}?dates={date_str}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                game_info = self._parse_game(event)
                if game_info:
                    games.append(game_info)
            
            return games
            
        except Exception as e:
            print(f"Error fetching schedule for {date_str}: {e}")
            return []
    
    def get_upcoming_games(self, days: int = 7) -> list[dict]:
        """
        Fetch upcoming games for the next N days.
        
        Args:
            days: Number of days to look ahead.
            
        Returns:
            List of game dictionaries sorted by date.
        """
        all_games = []
        today = datetime.now(self.eastern_tz)
        
        for i in range(days):
            check_date = today + timedelta(days=i)
            date_str = check_date.strftime("%Y%m%d")
            games = self.get_games_for_date(date_str)
            all_games.extend(games)
        
        # Sort by date
        all_games.sort(key=lambda g: g['datetime'])
        return all_games
    
    def get_tonights_game(self) -> Optional[dict]:
        """
        Get tonight's primetime game if any.
        
        Returns:
            Game dictionary or None if no game tonight.
        """
        games = self.get_todays_games()
        
        if not games:
            return None
        
        # Check for evening games (after 6 PM ET)
        now = datetime.now(self.eastern_tz)
        evening_cutoff = now.replace(hour=18, minute=0, second=0, microsecond=0)
        
        for game in games:
            game_time = game['datetime']
            # If game is in the evening or currently in progress
            if game_time >= evening_cutoff or game['status'] in ['IN', 'HALFTIME']:
                return game
        
        # If no evening game, return the first game of the day
        return games[0] if games else None
    
    def get_next_game(self) -> Optional[dict]:
        """
        Get the next upcoming game.
        
        Returns:
            Game dictionary or None.
        """
        upcoming = self.get_upcoming_games(days=7)
        
        if not upcoming:
            return None
        
        now = datetime.now(self.eastern_tz)
        
        # Find first game that hasn't started yet
        for game in upcoming:
            if game['datetime'] > now and game['status'] == 'PRE':
                return game
        
        return None
    
    def _parse_game(self, event: dict) -> Optional[dict]:
        """
        Parse a game event from ESPN API.
        
        Args:
            event: Event dictionary from API.
            
        Returns:
            Parsed game dictionary or None.
        """
        try:
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) != 2:
                return None
            
            # Determine home and away teams
            home_team = None
            away_team = None
            
            for comp in competitors:
                team_info = comp.get('team', {})
                if comp.get('homeAway') == 'home':
                    home_team = {
                        'name': team_info.get('displayName', 'Unknown'),
                        'abbr': team_info.get('abbreviation', ''),
                        'score': comp.get('score', '0')
                    }
                else:
                    away_team = {
                        'name': team_info.get('displayName', 'Unknown'),
                        'abbr': team_info.get('abbreviation', ''),
                        'score': comp.get('score', '0')
                    }
            
            # Get game time
            date_str = event.get('date', '')
            game_datetime = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            game_datetime_et = game_datetime.astimezone(self.eastern_tz)
            
            # Get odds if available
            odds_data = competition.get('odds', [])
            spread = None
            over_under = None
            
            if odds_data:
                odds = odds_data[0]
                spread = odds.get('spread')
                over_under = odds.get('overUnder')
            
            # Get game status
            status = event.get('status', {}).get('type', {}).get('state', 'PRE')
            
            return {
                'id': event.get('id'),
                'name': event.get('name', 'Unknown vs Unknown'),
                'short_name': event.get('shortName', ''),
                'home_team': home_team,
                'away_team': away_team,
                'datetime': game_datetime_et,
                'date_display': game_datetime_et.strftime('%a, %b %d at %I:%M %p ET'),
                'status': status,
                'spread': spread,
                'over_under': over_under,
                'venue': competition.get('venue', {}).get('fullName', 'Unknown'),
                'network': competition.get('broadcasts', [{}])[0].get('names', [''])[0] if competition.get('broadcasts') else None
            }
            
        except Exception as e:
            print(f"Error parsing game: {e}")
            return None
    
    def format_game_summary(self, game: dict) -> str:
        """
        Format a game into a readable summary.
        
        Args:
            game: Game dictionary.
            
        Returns:
            Formatted string.
        """
        if not game:
            return "No game data available"
        
        summary = f"{game['away_team']['name']} @ {game['home_team']['name']}\n"
        summary += f"📅 {game['date_display']}\n"
        
        if game['spread'] is not None:
            summary += f"📊 Spread: {game['spread']:+.1f}\n"
        if game['over_under'] is not None:
            summary += f"📈 O/U: {game['over_under']:.1f}\n"
        
        if game['network']:
            summary += f"📺 {game['network']}\n"
        
        if game['status'] != 'PRE':
            summary += f"⚡ Status: {game['status']}\n"
        
        return summary


def main():
    """Test the schedule fetcher."""
    fetcher = NFLScheduleFetcher()
    
    print("=" * 60)
    print("NFL SCHEDULE FETCHER - TEST")
    print("=" * 60)
    print()
    
    # Tonight's game
    print("🏈 TONIGHT'S GAME:")
    print("-" * 60)
    tonight = fetcher.get_tonights_game()
    if tonight:
        print(fetcher.format_game_summary(tonight))
    else:
        print("No game tonight")
    print()
    
    # Next game
    print("⏭️  NEXT GAME:")
    print("-" * 60)
    next_game = fetcher.get_next_game()
    if next_game:
        print(fetcher.format_game_summary(next_game))
    else:
        print("No upcoming games found")
    print()
    
    # Upcoming games
    print("📅 UPCOMING GAMES (Next 7 Days):")
    print("-" * 60)
    upcoming = fetcher.get_upcoming_games(days=7)
    if upcoming:
        for i, game in enumerate(upcoming[:10], 1):  # Show max 10
            print(f"{i}. {game['short_name']} - {game['date_display']}")
    else:
        print("No upcoming games found")


if __name__ == "__main__":
    main()
