#!/usr/bin/env python3
"""
Data Collection Guide - Step-by-Step Instructions for Finding Metrics

Provides detailed, beginner-friendly instructions for collecting EPA/DVOA data.
"""

from typing import Dict
from tkinter import messagebox


class DataCollectionGuide:
    """Provides step-by-step data collection instructions."""
    
    @staticmethod
    def get_instructions(metric_name: str) -> Dict[str, str]:
        """
        Get comprehensive instructions for collecting a specific metric.
        
        Args:
            metric_name: Name of the metric (e.g., "Opponent Def EPA/Play")
            
        Returns:
            Dictionary with title, description, steps, sources, and example
        """
        
        guides = {
            "Opponent Def EPA/Play:": {
                "title": "How to Find: Opponent Defensive EPA per Play",
                "what_is_it": (
                    "EPA (Expected Points Added) measures how many points a defense "
                    "prevents compared to what's expected. Negative = Good defense.\n\n"
                    "Example: -0.08 EPA means the defense prevents 0.08 points per play "
                    "compared to average."
                ),
                "step_by_step": """
**METHOD 1: RBSDM.com (FREE - Easiest)**

Step 1: Open your browser and go to:
        → https://rbsdm.com/stats/stats/

Step 2: Look for "Team Defense Stats" section

Step 3: Find the opponent team in the list
        → Example: Looking for "Denver Broncos"

Step 4: Find the "EPA/Play" column
        → This shows Defensive EPA per play
        → Copy this number (including negative sign if present)

Step 5: Paste into the tool
        → Example: -0.08 means good defense
        → Example: +0.05 means bad defense

**METHOD 2: nfelo.com (FREE - Alternative)**

Step 1: Go to → https://www.nfelo.com/

Step 2: Click on "Team Stats" in top menu

Step 3: Select "Defense" tab

Step 4: Find opponent team and look for "EPA/Play Def"

Step 5: Copy the value into the tool

**METHOD 3: Pro Football Reference (FREE)**

Step 1: Go to → https://www.pro-football-reference.com/

Step 2: Type opponent team name in search box
        → Example: "Denver Broncos"

Step 3: Click on current year team page

Step 4: Scroll to "Team Stats & Rankings"

Step 5: Look for "Expected Points" in defense section

Step 6: Convert to per-play (divide by plays)
                """,
                "google_search": 'Google: "[Team Name] defensive EPA 2024"',
                "confidence": "Manual entry from these sources = 85% confidence",
                "example": (
                    "✓ Denver Broncos defensive EPA: -0.08\n"
                    "✓ This means: Denver's defense PREVENTS 0.08 expected points per play\n"
                    "✓ Interpretation: Above average defense\n"
                    "✓ Effect: Slightly lower offensive projections for opponent"
                )
            },
            
            "Opponent DVOA Pass Def %:": {
                "title": "How to Find: Opponent DVOA Pass Defense %",
                "what_is_it": (
                    "DVOA (Defense-adjusted Value Over Average) measures how well a team "
                    "defends passes compared to league average, adjusted for opponent quality.\n\n"
                    "Negative % = Good pass defense\n"
                    "Positive % = Bad pass defense"
                ),
                "step_by_step": """
**METHOD 1: Football Outsiders (BEST SOURCE - Paid)**

Step 1: Go to → https://www.footballoutsiders.com/

Step 2: Navigate to "Stats" → "DVOA Ratings"

Step 3: Find "Defense" section

Step 4: Locate opponent team

Step 5: Look at "Pass Defense DVOA" column
        → Will show percentage like "-12.5%" or "+8.2%"

Step 6: Copy this percentage into the tool

**METHOD 2: Sharp Football Stats (FREE Trial)**

Step 1: Go to → https://www.sharpfootballstats.com/

Step 2: Sign up for free trial

Step 3: Go to "Defense Rankings"

Step 4: Filter by "Pass Defense"

Step 5: Find opponent team and their DVOA %

**METHOD 3: Estimate from Basic Stats (FREE but less accurate)**

Step 1: Go to → https://www.espn.com/nfl/stats/team

Step 2: Select "Passing Defense" 

Step 3: Find opponent team's yards per attempt allowed

Step 4: Use this conversion:
        → < 6.0 YPA = Elite (-15% DVOA)
        → 6.0-6.5 YPA = Good (-5% DVOA)
        → 6.5-7.0 YPA = Average (0% DVOA)
        → 7.0-7.5 YPA = Poor (+8% DVOA)
        → > 7.5 YPA = Very Poor (+15% DVOA)

**METHOD 4: Google Search Shortcut**

Step 1: Google search exactly:
        → "[Team Name] pass defense DVOA 2024"
        → Example: "Denver Broncos pass defense DVOA 2024"

Step 2: Look for articles from:
        • Football Outsiders
        • Sharp Football Analysis
        • The Athletic

Step 3: Find the Pass Def DVOA % in article
                """,
                "google_search": 'Google: "[Team Name] pass defense DVOA 2024"',
                "confidence": "Football Outsiders = 95% confidence, Estimated = 60% confidence",
                "example": (
                    "✓ Denver Broncos pass DVOA: +12.5%\n"
                    "✓ This means: Denver is 12.5% WORSE than average defending passes\n"
                    "✓ Interpretation: Weak pass defense\n"
                    "✓ Effect: QB and WR props trend OVER against Denver"
                )
            },
            
            "Opponent DVOA Run Def %:": {
                "title": "How to Find: Opponent DVOA Run Defense %",
                "what_is_it": (
                    "DVOA for run defense - same as pass DVOA but only for rushing plays.\n\n"
                    "Negative % = Good run defense\n"
                    "Positive % = Bad run defense"
                ),
                "step_by_step": """
**METHOD 1: Football Outsiders (BEST)**

Step 1: Go to → https://www.footballoutsiders.com/

Step 2: Navigate to "Stats" → "DVOA Ratings"

Step 3: Find "Defense" section

Step 4: Look at "Rush Defense DVOA" column (separate from pass)

Step 5: Copy the percentage for opponent team

**METHOD 2: Estimate from Basic Stats**

Step 1: Go to → https://www.espn.com/nfl/stats/team

Step 2: Select "Rushing Defense"

Step 3: Find opponent team's yards per carry allowed

Step 4: Use this conversion:
        → < 3.8 YPC = Elite (-15% DVOA)
        → 3.8-4.1 YPC = Good (-5% DVOA)
        → 4.1-4.4 YPC = Average (0% DVOA)
        → 4.4-4.7 YPC = Poor (+8% DVOA)
        → > 4.7 YPC = Very Poor (+15% DVOA)

**METHOD 3: Google Search**

Google: "[Team Name] run defense DVOA 2024"
Example: "Denver Broncos run defense DVOA 2024"
                """,
                "google_search": 'Google: "[Team Name] run defense DVOA 2024"',
                "confidence": "Football Outsiders = 95% confidence, Estimated = 60% confidence",
                "example": (
                    "✓ Denver Broncos run DVOA: -8.2%\n"
                    "✓ This means: Denver is 8.2% BETTER than average defending runs\n"
                    "✓ Interpretation: Strong run defense\n"
                    "✓ Effect: RB rushing props trend UNDER against Denver"
                )
            },
            
            "Team Off EPA (L4):": {
                "title": "How to Find: Team Offensive EPA (Last 4 Games)",
                "what_is_it": (
                    "Your team's offensive EPA over their last 4 games. Shows recent form.\n\n"
                    "Positive = Hot offense\n"
                    "Negative = Cold offense"
                ),
                "step_by_step": """
**METHOD 1: RBSDM.com Game Logs**

Step 1: Go to → https://rbsdm.com/stats/stats/

Step 2: Find "Team Offense Stats"

Step 3: Click on YOUR team (not opponent)

Step 4: Look at "Game Logs" or "Recent Games"

Step 5: Find EPA/Play for each of last 4 games:
        → Week 12: +0.15
        → Week 11: +0.22
        → Week 10: -0.05
        → Week 9: +0.18

Step 6: Calculate average:
        → (+0.15 + 0.22 - 0.05 + 0.18) / 4 = +0.125

Step 7: Enter +0.13 (rounded) into tool

**METHOD 2: nfelo.com Recent Form**

Step 1: Go to → https://www.nfelo.com/

Step 2: Find YOUR team's page

Step 3: Look for "Recent Performance" section

Step 4: Find average EPA from last 4 games

**METHOD 3: Manual Calculation from Box Scores**

Step 1: Go to → https://www.espn.com/nfl/team/schedule/_/name/[team-abbreviation]

Step 2: Look at last 4 games

Step 3: For each game, check:
        → Total yards gained
        → Plays run
        → Points scored

Step 4: Rough estimate:
        → 400+ yards, 25+ points = +0.15 EPA
        → 300-400 yards, 20-25 points = +0.05 EPA
        → 250-300 yards, 17-20 points = 0.00 EPA
        → < 250 yards, < 17 points = -0.10 EPA

Step 5: Average the 4 games

**Quick Google Method**

Google: "[Your Team] offensive EPA last 4 games"
Example: "Kansas City Chiefs offensive EPA last 4 games"
                """,
                "google_search": 'Google: "[Team Name] offensive EPA last 4 games"',
                "confidence": "Calculated from game logs = 85% confidence",
                "example": (
                    "✓ Kansas City Chiefs offensive EPA (L4): +0.18\n"
                    "✓ This means: Chiefs averaging +0.18 points above expected per play\n"
                    "✓ Interpretation: Offense is HOT right now\n"
                    "✓ Effect: Boosts all Chiefs offensive projections by ~5%"
                )
            }
        }
        
        return guides.get(metric_name, {
            "title": f"Instructions for {metric_name}",
            "what_is_it": "Data collection guide not available for this metric.",
            "step_by_step": "Please refer to documentation.",
            "google_search": "",
            "confidence": "Unknown",
            "example": "No example available"
        })
    
    @staticmethod
    def show_guide_dialog(metric_name: str):
        """Show data collection guide in a message box."""
        guide = DataCollectionGuide.get_instructions(metric_name)
        
        message = f"{guide['what_is_it']}\n\n{guide['step_by_step']}\n\n"
        message += f"📊 Example:\n{guide['example']}\n\n"
        message += f"🔍 Quick Search:\n{guide['google_search']}\n\n"
        message += f"✓ {guide['confidence']}"
        
        messagebox.showinfo(guide['title'], message)


# Test the guide
if __name__ == "__main__":
    import tkinter as tk
    
    root = tk.Tk()
    root.withdraw()
    
    # Show example guide
    DataCollectionGuide.show_guide_dialog("Opponent Def EPA/Play:")
    
    root.mainloop()
