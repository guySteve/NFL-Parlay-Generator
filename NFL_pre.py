#!/usr/bin/env python3
"""
NFL Predictive Analytics & Parlay Generation System.

A production-grade console application for generating correlated NFL parlays
using Sharp betting data (EPA, DVOA, Target Share) through a weighted predictive engine.

Author: NFL Analytics Team
Version: 1.0.0
Python: 3.12+
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text
from rich import box


# =============================================================================
# NFL ROSTER DATA - Broncos vs Commanders (Week 13, 2024)
# =============================================================================

TEAM_ROSTERS: dict[str, dict[str, list[dict[str, str]]]] = {
    "Denver Broncos": {
        "QB": [
            {"name": "Bo Nix", "number": "10"},
            {"name": "Jarrett Stidham", "number": "8"},
        ],
        "RB": [
            {"name": "RJ Harvey", "number": "12"},
            {"name": "Jaleel McLaughlin", "number": "38"},
            {"name": "Tyler Badie", "number": "28"},
            {"name": "Audric Estime", "number": "23"},
        ],
        "WR": [
            {"name": "Courtland Sutton", "number": "14"},
            {"name": "Marvin Mims Jr.", "number": "19"},
            {"name": "Troy Franklin", "number": "11"},
            {"name": "Lil'Jordan Humphrey", "number": "17"},
            {"name": "Devaughn Vele", "number": "81"},
        ],
        "TE": [
            {"name": "Adam Trautman", "number": "82"},
            {"name": "Lucas Krull", "number": "85"},
            {"name": "Nate Adkins", "number": "45"},
        ],
    },
    "Washington Commanders": {
        "QB": [
            {"name": "Marcus Mariota", "number": "18"},
            {"name": "Jeff Driskel", "number": "6"},
        ],
        "RB": [
            {"name": "Brian Robinson Jr.", "number": "8"},
            {"name": "Austin Ekeler", "number": "30"},
            {"name": "Jeremy McNichols", "number": "26"},
            {"name": "Chris Rodriguez Jr.", "number": "36"},
        ],
        "WR": [
            {"name": "Terry McLaurin", "number": "17"},
            {"name": "Dyami Brown", "number": "2"},
            {"name": "Olamide Zaccheaus", "number": "14"},
            {"name": "Noah Brown", "number": "85"},
            {"name": "Luke McCaffrey", "number": "11"},
        ],
        "TE": [
            {"name": "Zach Ertz", "number": "86"},
            {"name": "John Bates", "number": "87"},
            {"name": "Ben Sinnott", "number": "82"},
        ],
    },
}

# Default game context for Broncos vs Commanders
DEFAULT_GAME_CONTEXTS: dict[str, dict[str, Any]] = {
    "Broncos @ Commanders": {
        "team_options": ["Denver Broncos", "Washington Commanders"],
        "spread": -3.0,  # Commanders favored
        "total": 45.5,
        "broncos_implied": 21.25,
        "commanders_implied": 24.25,
        "broncos_def_rank": 10,
        "commanders_def_rank": 18,
    }
}

# =============================================================================
# PRE-LOADED PLAYER STATS (2024 Season - Week 17 Data from NFL.com)
# =============================================================================

PLAYER_STATS: dict[str, dict[str, Any]] = {
    # ==================== DENVER BRONCOS ====================
    "Bo Nix": {
        "position": "QB",
        "games_played": 16,
        "passing_yards_season_total": 3775,
        "pass_attempts_season_total": 567,
        "pass_completions_season_total": 376,
        "passing_tds": 29,
        "interceptions": 12,
        "passer_rating": 93.3,
        "passing_yards_l5_avg": 245.0,  # ~3775/16 adjusted for recent play
        "pass_attempts_l5_avg": 35.0,
        "rush_yards_season_total": 430,  # Mobile QB
        "rush_yards_l5_avg": 28.0,
        "epa_per_play": 0.12,
        "cpoe": 2.1,
    },
    "RJ Harvey": {
        "position": "RB",
        "games_played": 8,
        "rush_yards_season_total": 285,
        "rush_attempts_season_total": 62,
        "rush_yards_l5_avg": 52.0,
        "rush_attempts_l5_avg": 11.0,
        "ypc": 4.6,
        "opportunity_share_pct": 35.0,
        "yco_per_att": 2.8,
    },
    "Jaleel McLaughlin": {
        "position": "RB",
        "games_played": 16,
        "rush_yards_season_total": 410,
        "rush_attempts_season_total": 95,
        "rush_yards_l5_avg": 30.0,
        "rush_attempts_l5_avg": 7.0,
        "ypc": 4.3,
        "opportunity_share_pct": 25.0,
        "yco_per_att": 2.4,
    },
    "Courtland Sutton": {
        "position": "WR",
        "games_played": 16,
        "rec_yards_season_total": 1081,
        "receptions_season_total": 81,
        "targets_season_total": 135,
        "receiving_tds": 8,
        "rec_yards_l5_avg": 68.0,
        "receptions_l5_avg": 5.0,
        "target_share_pct": 23.8,  # 135/567 targets
        "adot": 12.5,
        "air_yards_share": 28.0,
        "long_rec": 47,
    },
    "Marvin Mims Jr.": {
        "position": "WR",
        "games_played": 16,
        "rec_yards_season_total": 620,
        "receptions_season_total": 42,
        "targets_season_total": 68,
        "receiving_tds": 5,
        "rec_yards_l5_avg": 45.0,
        "receptions_l5_avg": 3.0,
        "target_share_pct": 12.0,
        "adot": 15.8,  # Deep threat
        "air_yards_share": 18.0,
        "long_rec": 65,
    },
    "Troy Franklin": {
        "position": "WR",
        "games_played": 14,
        "rec_yards_season_total": 320,
        "receptions_season_total": 28,
        "targets_season_total": 45,
        "receiving_tds": 2,
        "rec_yards_l5_avg": 32.0,
        "receptions_l5_avg": 2.5,
        "target_share_pct": 8.0,
        "adot": 10.5,
        "air_yards_share": 8.0,
        "long_rec": 38,
    },
    "Adam Trautman": {
        "position": "TE",
        "games_played": 16,
        "rec_yards_season_total": 280,
        "receptions_season_total": 32,
        "targets_season_total": 48,
        "receiving_tds": 3,
        "rec_yards_l5_avg": 20.0,
        "receptions_l5_avg": 2.2,
        "target_share_pct": 8.5,
        "adot": 7.5,
        "air_yards_share": 6.0,
        "long_rec": 28,
    },
    
    # ==================== WASHINGTON COMMANDERS ====================
    "Marcus Mariota": {
        "position": "QB",
        "games_played": 3,  # Limited action as backup
        "passing_yards_season_total": 485,
        "pass_attempts_season_total": 68,
        "pass_completions_season_total": 44,
        "passing_tds": 3,
        "interceptions": 1,
        "passer_rating": 91.5,
        "passing_yards_l5_avg": 165.0,  # Adjusted for recent starts
        "pass_attempts_l5_avg": 24.0,
        "rush_yards_season_total": 95,  # Mobile veteran
        "rush_yards_l5_avg": 32.0,
        "epa_per_play": 0.05,
        "cpoe": 0.5,
    },
    "Brian Robinson Jr.": {
        "position": "RB",
        "games_played": 13,
        "rush_yards_season_total": 658,
        "rush_attempts_season_total": 178,
        "rush_yards_l5_avg": 55.0,
        "rush_attempts_l5_avg": 15.0,
        "ypc": 3.7,
        "opportunity_share_pct": 52.0,
        "yco_per_att": 2.6,
    },
    "Austin Ekeler": {
        "position": "RB",
        "games_played": 14,
        "rush_yards_season_total": 320,
        "rush_attempts_season_total": 85,
        "rush_yards_l5_avg": 28.0,
        "rush_attempts_l5_avg": 7.0,
        "ypc": 3.8,
        "opportunity_share_pct": 28.0,
        "yco_per_att": 2.2,
        # Receiving threat
        "rec_yards_season_total": 380,
        "receptions_season_total": 48,
    },
    "Terry McLaurin": {
        "position": "WR",
        "games_played": 16,
        "rec_yards_season_total": 1096,
        "receptions_season_total": 82,
        "targets_season_total": 117,
        "receiving_tds": 13,
        "rec_yards_l5_avg": 72.0,
        "receptions_l5_avg": 5.5,
        "target_share_pct": 24.4,  # Primary target
        "adot": 13.2,
        "air_yards_share": 32.0,
        "long_rec": 86,
    },
    "Dyami Brown": {
        "position": "WR",
        "games_played": 16,
        "rec_yards_season_total": 315,
        "receptions_season_total": 25,
        "targets_season_total": 42,
        "receiving_tds": 2,
        "rec_yards_l5_avg": 25.0,
        "receptions_l5_avg": 2.0,
        "target_share_pct": 8.8,
        "adot": 14.5,
        "air_yards_share": 12.0,
        "long_rec": 52,
    },
    "Olamide Zaccheaus": {
        "position": "WR",
        "games_played": 15,
        "rec_yards_season_total": 385,
        "receptions_season_total": 35,
        "targets_season_total": 55,
        "receiving_tds": 4,
        "rec_yards_l5_avg": 30.0,
        "receptions_l5_avg": 2.8,
        "target_share_pct": 11.5,
        "adot": 9.8,
        "air_yards_share": 10.0,
        "long_rec": 42,
    },
    "Zach Ertz": {
        "position": "TE",
        "games_played": 15,
        "rec_yards_season_total": 520,
        "receptions_season_total": 58,
        "targets_season_total": 78,
        "receiving_tds": 4,
        "rec_yards_l5_avg": 38.0,
        "receptions_l5_avg": 4.2,
        "target_share_pct": 16.3,
        "adot": 7.8,
        "air_yards_share": 10.0,
        "long_rec": 35,
    },
}


# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

class Config:
    """Application configuration constants."""
    
    # Weighted Recency Configuration
    LAST_5_WEIGHT: float = 0.65
    SEASON_AVG_WEIGHT: float = 0.35
    
    # DVOA Opponent Rank Modifiers
    ELITE_DEFENSE_THRESHOLD: tuple[int, int] = (1, 5)
    ELITE_DEFENSE_DAMPER: float = 0.88
    POOR_DEFENSE_THRESHOLD: tuple[int, int] = (28, 32)
    POOR_DEFENSE_BOOST: float = 1.12
    
    # Efficiency Modifiers
    QB_EPA_THRESHOLD: float = 0.20
    QB_EPA_BOOST: float = 1.05
    WR_TARGET_SHARE_THRESHOLD: float = 28.0
    WR_VOLUME_FLOOR_BOOST: float = 1.08
    
    # Game Script Thresholds
    TRAILING_SCRIPT_SPREAD: float = 6.5
    LEADING_SCRIPT_SPREAD: float = -6.5
    EXPLOSIVE_TOTAL_THRESHOLD: float = 49.5
    
    # Confidence Calculation
    MIN_EDGE_FOR_CONFIDENCE: float = 2.0
    MAX_EDGE_FOR_CONFIDENCE: float = 15.0


# =============================================================================
# ENUMS
# =============================================================================

class Position(str, Enum):
    """Player position enumeration."""
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"


class BetType(str, Enum):
    """Bet type enumeration."""
    OVER = "Over"
    UNDER = "Under"


class GameScript(str, Enum):
    """Game script scenario enumeration."""
    TRAILING = "Trailing Script"
    LEADING = "Leading Script"
    EXPLOSIVE = "Explosive Stack"
    NEUTRAL = "Neutral Script"


# =============================================================================
# PYDANTIC DATA MODELS
# =============================================================================

class GameContext(BaseModel):
    """
    Game context containing betting lines and opponent information.
    
    Attributes:
        team: The team being analyzed.
        opponent: The opposing team.
        spread: Point spread (negative = favorite).
        total: Over/Under total points.
        implied_team_total: Implied total points for the team.
        opponent_rank: Opponent defensive rank (1-32, 1 being best).
    """
    team: Annotated[str, Field(min_length=2, max_length=50)]
    opponent: Annotated[str, Field(min_length=2, max_length=50)]
    spread: Annotated[float, Field(ge=-30, le=30)]
    total: Annotated[float, Field(ge=30, le=70)]
    implied_team_total: Annotated[float, Field(ge=10, le=45)]
    opponent_rank: Annotated[int, Field(ge=1, le=32)]
    
    @field_validator('team', 'opponent')
    @classmethod
    def capitalize_team_name(cls, v: str) -> str:
        """Capitalize team names for consistency."""
        return v.strip().title()


class QBStats(BaseModel):
    """
    Quarterback statistics model.
    
    Attributes:
        passing_yards_l5_avg: Average passing yards per game (last 5 games).
        passing_yards_season_total: Total passing yards for the season.
        rush_yards_l5_avg: Average rushing yards per game (last 5 games).
        rush_yards_season_total: Total rushing yards for the season.
        epa_per_play: Expected Points Added per play.
        cpoe: Completion Percentage Over Expected.
        pass_attempts_l5_avg: Average pass attempts per game (last 5 games).
        pass_attempts_season_total: Total pass attempts for the season.
        games_played: Number of games played this season.
    """
    passing_yards_l5_avg: Annotated[float, Field(ge=0, le=600, description="Avg passing yards per game (last 5)")]
    passing_yards_season_total: Annotated[float, Field(ge=0, le=6000, description="Total passing yards this season")]
    rush_yards_l5_avg: Annotated[float, Field(ge=-20, le=150, description="Avg rush yards per game (last 5)")]
    rush_yards_season_total: Annotated[float, Field(ge=-100, le=1500, description="Total rush yards this season")]
    epa_per_play: Annotated[float, Field(ge=-0.5, le=0.5, description="EPA per play")]
    cpoe: Annotated[float, Field(ge=-15, le=15, description="Completion % Over Expected")]
    pass_attempts_l5_avg: Annotated[float, Field(ge=15, le=60, description="Avg pass attempts per game (last 5)")]
    pass_attempts_season_total: Annotated[float, Field(ge=100, le=800, description="Total pass attempts this season")]
    games_played: Annotated[int, Field(ge=1, le=17, description="Games played this season")]


class RBStats(BaseModel):
    """
    Running back statistics model.
    
    Attributes:
        rush_yards_l5_avg: Average rushing yards per game (last 5 games).
        rush_yards_season_total: Total rushing yards for the season.
        opportunity_share_pct: Percentage of team rushing opportunities.
        yco_per_att: Yards after contact per attempt.
        rush_attempts_l5_avg: Average rush attempts per game (last 5 games).
        rush_attempts_season_total: Total rush attempts for the season.
        games_played: Number of games played this season.
    """
    rush_yards_l5_avg: Annotated[float, Field(ge=0, le=250, description="Avg rush yards per game (last 5)")]
    rush_yards_season_total: Annotated[float, Field(ge=0, le=2500, description="Total rush yards this season")]
    opportunity_share_pct: Annotated[float, Field(ge=0, le=100, description="Opportunity share %")]
    yco_per_att: Annotated[float, Field(ge=0, le=5, description="Yards after contact per attempt")]
    rush_attempts_l5_avg: Annotated[float, Field(ge=0, le=35, description="Avg rush attempts per game (last 5)")]
    rush_attempts_season_total: Annotated[float, Field(ge=0, le=400, description="Total rush attempts this season")]
    games_played: Annotated[int, Field(ge=1, le=17, description="Games played this season")]


class WRTEStats(BaseModel):
    """
    Wide receiver / Tight end statistics model.
    
    Attributes:
        rec_yards_l5_avg: Average receiving yards per game (last 5 games).
        rec_yards_season_total: Total receiving yards for the season.
        target_share_pct: Percentage of team targets.
        adot: Average depth of target.
        air_yards_share: Share of team air yards.
        receptions_l5_avg: Average receptions per game (last 5 games).
        receptions_season_total: Total receptions for the season.
        games_played: Number of games played this season.
    """
    rec_yards_l5_avg: Annotated[float, Field(ge=0, le=250, description="Avg receiving yards per game (last 5)")]
    rec_yards_season_total: Annotated[float, Field(ge=0, le=2000, description="Total receiving yards this season")]
    target_share_pct: Annotated[float, Field(ge=0, le=50, description="Target share %")]
    adot: Annotated[float, Field(ge=-5, le=25, description="Average depth of target")]
    air_yards_share: Annotated[float, Field(ge=0, le=60, description="Air yards share %")]
    receptions_l5_avg: Annotated[float, Field(ge=0, le=18, description="Avg receptions per game (last 5)")]
    receptions_season_total: Annotated[float, Field(ge=0, le=200, description="Total receptions this season")]
    games_played: Annotated[int, Field(ge=1, le=17, description="Games played this season")]


class MarketLines(BaseModel):
    """
    Vegas prop lines for a player.
    
    Attributes:
        player_name: Name of the player.
        position: Player position.
        passing_yards: Passing yards line (QB only).
        rush_yards: Rushing yards line.
        rec_yards: Receiving yards line (WR/TE only).
        receptions: Receptions line (WR/TE only).
        pass_attempts: Pass attempts line (QB only).
        rush_attempts: Rush attempts line (RB only).
    """
    player_name: Annotated[str, Field(min_length=2, max_length=100)]
    position: Position
    passing_yards: float | None = None
    rush_yards: float | None = None
    rec_yards: float | None = None
    receptions: float | None = None
    pass_attempts: float | None = None
    rush_attempts: float | None = None
    
    @field_validator('player_name')
    @classmethod
    def format_player_name(cls, v: str) -> str:
        """Format player name consistently."""
        return v.strip().title()


# =============================================================================
# PLAYER DATA CONTAINER
# =============================================================================

@dataclass
class PlayerData:
    """
    Container for player information, stats, and market lines.
    
    Attributes:
        name: Player name.
        position: Player position.
        stats: Position-specific statistics (QBStats, RBStats, or WRTEStats).
        market_lines: Vegas prop lines for comparison.
    """
    name: str
    position: Position
    stats: QBStats | RBStats | WRTEStats
    market_lines: MarketLines


# =============================================================================
# PROJECTION RESULT
# =============================================================================

@dataclass
class Projection:
    """
    Individual stat projection result.
    
    Attributes:
        player_name: Name of the player.
        position: Player position.
        stat_type: Type of stat projected.
        projected_value: Model's projected value.
        market_line: Vegas line for comparison.
        edge: Difference between projection and line.
        recommendation: Over/Under recommendation.
        confidence: Confidence score (0-100).
    """
    player_name: str
    position: Position
    stat_type: str
    projected_value: float
    market_line: float
    edge: float
    recommendation: BetType
    confidence: float


@dataclass
class ParlayLeg:
    """
    Single leg of a parlay bet.
    
    Attributes:
        player_name: Player name.
        stat_type: Stat type for the bet.
        line: Vegas line.
        direction: Over or Under.
        edge: Edge percentage.
    """
    player_name: str
    stat_type: str
    line: float
    direction: BetType
    edge: float


@dataclass
class CorrelatedParlay:
    """
    Correlated parlay recommendation.
    
    Attributes:
        game_script: The game script scenario.
        legs: List of parlay legs.
        combined_confidence: Overall confidence score.
        correlation_strength: Strength of leg correlation.
    """
    game_script: GameScript
    legs: list[ParlayLeg]
    combined_confidence: float
    correlation_strength: str


# =============================================================================
# PREDICTION STRATEGY PATTERN
# =============================================================================

class PredictionStrategy(ABC):
    """Abstract base class for prediction strategies."""
    
    @abstractmethod
    def calculate_base_projection(
        self,
        last_5_avg: float,
        season_avg: float
    ) -> float:
        """Calculate base projection using weighted recency."""
        pass
    
    @abstractmethod
    def apply_dvoa_modifier(
        self,
        value: float,
        opponent_rank: int
    ) -> float:
        """Apply DVOA-based opponent modifier."""
        pass


class StandardPredictionStrategy(PredictionStrategy):
    """
    Standard prediction strategy using weighted recency and DVOA modifiers.
    
    Implements the core prediction logic with configurable weights and thresholds.
    """
    
    def calculate_base_projection(
        self,
        last_5_avg: float,
        season_avg: float
    ) -> float:
        """
        Calculate base projection using weighted recency.
        
        Args:
            last_5_avg: Average over last 5 games.
            season_avg: Season-long average.
            
        Returns:
            Weighted projection value.
        """
        return (
            last_5_avg * Config.LAST_5_WEIGHT +
            season_avg * Config.SEASON_AVG_WEIGHT
        )
    
    def apply_dvoa_modifier(
        self,
        value: float,
        opponent_rank: int
    ) -> float:
        """
        Apply DVOA-based opponent modifier.
        
        Args:
            value: Base projection value.
            opponent_rank: Opponent defensive rank (1-32).
            
        Returns:
            Modified projection value.
        """
        elite_min, elite_max = Config.ELITE_DEFENSE_THRESHOLD
        poor_min, poor_max = Config.POOR_DEFENSE_THRESHOLD
        
        if elite_min <= opponent_rank <= elite_max:
            return value * Config.ELITE_DEFENSE_DAMPER
        elif poor_min <= opponent_rank <= poor_max:
            return value * Config.POOR_DEFENSE_BOOST
        return value


# =============================================================================
# PREDICTION ENGINE
# =============================================================================

class PredictionEngine:
    """
    Core prediction engine for NFL player props.
    
    Uses weighted recency, DVOA modifiers, and efficiency adjustments
    to generate player stat projections.
    
    Attributes:
        strategy: The prediction strategy to use.
        game_context: Current game context.
    """
    
    def __init__(
        self,
        strategy: PredictionStrategy | None = None,
        game_context: GameContext | None = None
    ):
        """
        Initialize the prediction engine.
        
        Args:
            strategy: Prediction strategy (defaults to StandardPredictionStrategy).
            game_context: Game context for opponent adjustments.
        """
        self.strategy = strategy or StandardPredictionStrategy()
        self.game_context = game_context
    
    def set_game_context(self, context: GameContext) -> None:
        """Set the game context for predictions."""
        self.game_context = context
    
    async def generate_projections(
        self,
        player: PlayerData
    ) -> list[Projection]:
        """
        Generate all projections for a player.
        
        Args:
            player: Player data container.
            
        Returns:
            List of projection results.
        """
        if not self.game_context:
            raise ValueError("Game context must be set before generating projections")
        
        projections: list[Projection] = []
        
        if player.position == Position.QB:
            projections.extend(await self._project_qb(player))
        elif player.position == Position.RB:
            projections.extend(await self._project_rb(player))
        elif player.position in (Position.WR, Position.TE):
            projections.extend(await self._project_wr_te(player))
        
        return projections
    
    async def _project_qb(self, player: PlayerData) -> list[Projection]:
        """Generate QB projections."""
        stats: QBStats = player.stats  # type: ignore
        lines = player.market_lines
        projections: list[Projection] = []
        
        # Calculate season per-game averages from totals
        season_pass_avg = stats.passing_yards_season_total / stats.games_played
        season_rush_avg = stats.rush_yards_season_total / stats.games_played
        season_attempts_avg = stats.pass_attempts_season_total / stats.games_played
        
        # Passing Yards Projection
        if lines.passing_yards is not None:
            base_pass = self.strategy.calculate_base_projection(
                stats.passing_yards_l5_avg, season_pass_avg
            )
            adjusted_pass = self.strategy.apply_dvoa_modifier(
                base_pass, self.game_context.opponent_rank
            )
            
            # EPA Efficiency Modifier
            if stats.epa_per_play > Config.QB_EPA_THRESHOLD:
                adjusted_pass *= Config.QB_EPA_BOOST
            
            projections.append(self._create_projection(
                player, "Passing Yards", adjusted_pass, lines.passing_yards
            ))
        
        # Rush Yards Projection
        if lines.rush_yards is not None:
            base_rush = self.strategy.calculate_base_projection(
                stats.rush_yards_l5_avg, season_rush_avg
            )
            adjusted_rush = self.strategy.apply_dvoa_modifier(
                base_rush, self.game_context.opponent_rank
            )
            projections.append(self._create_projection(
                player, "Rush Yards", adjusted_rush, lines.rush_yards
            ))
        
        # Pass Attempts Projection
        if lines.pass_attempts is not None:
            base_attempts = self.strategy.calculate_base_projection(
                stats.pass_attempts_l5_avg, season_attempts_avg
            )
            # Adjust attempts based on game script
            if self.game_context.spread > Config.TRAILING_SCRIPT_SPREAD:
                base_attempts *= 1.08  # Trailing = more passing
            elif self.game_context.spread < Config.LEADING_SCRIPT_SPREAD:
                base_attempts *= 0.92  # Leading = less passing
            
            projections.append(self._create_projection(
                player, "Pass Attempts", base_attempts, lines.pass_attempts
            ))
        
        return projections
    
    async def _project_rb(self, player: PlayerData) -> list[Projection]:
        """Generate RB projections."""
        stats: RBStats = player.stats  # type: ignore
        lines = player.market_lines
        projections: list[Projection] = []
        
        # Calculate season per-game averages from totals
        season_rush_avg = stats.rush_yards_season_total / stats.games_played
        season_attempts_avg = stats.rush_attempts_season_total / stats.games_played
        
        # Rush Yards Projection
        if lines.rush_yards is not None:
            base_rush = self.strategy.calculate_base_projection(
                stats.rush_yards_l5_avg, season_rush_avg
            )
            adjusted_rush = self.strategy.apply_dvoa_modifier(
                base_rush, self.game_context.opponent_rank
            )
            
            # Opportunity Share adjustment
            if stats.opportunity_share_pct > 70:
                adjusted_rush *= 1.05  # Workhorse bonus
            
            # Game script adjustment
            if self.game_context.spread < Config.LEADING_SCRIPT_SPREAD:
                adjusted_rush *= 1.10  # Leading = more rushing
            elif self.game_context.spread > Config.TRAILING_SCRIPT_SPREAD:
                adjusted_rush *= 0.88  # Trailing = less rushing
            
            projections.append(self._create_projection(
                player, "Rush Yards", adjusted_rush, lines.rush_yards
            ))
        
        # Rush Attempts Projection
        if lines.rush_attempts is not None:
            base_attempts = self.strategy.calculate_base_projection(
                stats.rush_attempts_l5_avg, season_attempts_avg
            )
            
            # Game script adjustment
            if self.game_context.spread < Config.LEADING_SCRIPT_SPREAD:
                base_attempts *= 1.12
            elif self.game_context.spread > Config.TRAILING_SCRIPT_SPREAD:
                base_attempts *= 0.85
            
            projections.append(self._create_projection(
                player, "Rush Attempts", base_attempts, lines.rush_attempts
            ))
        
        return projections
    
    async def _project_wr_te(self, player: PlayerData) -> list[Projection]:
        """Generate WR/TE projections."""
        stats: WRTEStats = player.stats  # type: ignore
        lines = player.market_lines
        projections: list[Projection] = []
        
        # Calculate season per-game averages from totals
        season_rec_yards_avg = stats.rec_yards_season_total / stats.games_played
        season_receptions_avg = stats.receptions_season_total / stats.games_played
        
        # Receiving Yards Projection
        if lines.rec_yards is not None:
            base_rec = self.strategy.calculate_base_projection(
                stats.rec_yards_l5_avg, season_rec_yards_avg
            )
            adjusted_rec = self.strategy.apply_dvoa_modifier(
                base_rec, self.game_context.opponent_rank
            )
            
            # Target Share Volume Floor
            if stats.target_share_pct > Config.WR_TARGET_SHARE_THRESHOLD:
                min_projection = lines.rec_yards * 0.95
                adjusted_rec = max(adjusted_rec * Config.WR_VOLUME_FLOOR_BOOST, min_projection)
            
            projections.append(self._create_projection(
                player, "Rec Yards", adjusted_rec, lines.rec_yards
            ))
        
        # Receptions Projection
        if lines.receptions is not None:
            base_rec = self.strategy.calculate_base_projection(
                stats.receptions_l5_avg, season_receptions_avg
            )
            
            # Target share boost
            if stats.target_share_pct > 25:
                base_rec *= 1.05
            
            projections.append(self._create_projection(
                player, "Receptions", base_rec, lines.receptions
            ))
        
        return projections
    
    def _create_projection(
        self,
        player: PlayerData,
        stat_type: str,
        projected: float,
        line: float
    ) -> Projection:
        """Create a projection result with edge calculation."""
        edge = ((projected - line) / line) * 100
        recommendation = BetType.OVER if projected > line else BetType.UNDER
        confidence = self._calculate_confidence(abs(edge))
        
        return Projection(
            player_name=player.name,
            position=player.position,
            stat_type=stat_type,
            projected_value=round(projected, 1),
            market_line=line,
            edge=round(edge, 2),
            recommendation=recommendation,
            confidence=round(confidence, 1)
        )
    
    def _calculate_confidence(self, edge_magnitude: float) -> float:
        """
        Calculate confidence score based on edge magnitude.
        
        Args:
            edge_magnitude: Absolute edge percentage.
            
        Returns:
            Confidence score (0-100).
        """
        if edge_magnitude < Config.MIN_EDGE_FOR_CONFIDENCE:
            return 35 + (edge_magnitude / Config.MIN_EDGE_FOR_CONFIDENCE) * 15
        elif edge_magnitude > Config.MAX_EDGE_FOR_CONFIDENCE:
            return 95.0
        else:
            normalized = (edge_magnitude - Config.MIN_EDGE_FOR_CONFIDENCE) / (
                Config.MAX_EDGE_FOR_CONFIDENCE - Config.MIN_EDGE_FOR_CONFIDENCE
            )
            return 50 + normalized * 45


# =============================================================================
# CORRELATION LOGIC ENGINE
# =============================================================================

class CorrelationEngine:
    """
    Engine for finding correlated parlay opportunities.
    
    Identifies game script scenarios and builds correlated multi-leg parlays
    based on expected game flow.
    """
    
    def __init__(self, game_context: GameContext):
        """
        Initialize the correlation engine.
        
        Args:
            game_context: Current game context.
        """
        self.game_context = game_context
    
    def determine_game_script(self) -> GameScript:
        """
        Determine the expected game script.
        
        Returns:
            GameScript enum value.
        """
        if self.game_context.spread > Config.TRAILING_SCRIPT_SPREAD:
            return GameScript.TRAILING
        elif self.game_context.spread < Config.LEADING_SCRIPT_SPREAD:
            return GameScript.LEADING
        elif self.game_context.total > Config.EXPLOSIVE_TOTAL_THRESHOLD:
            return GameScript.EXPLOSIVE
        return GameScript.NEUTRAL
    
    def find_correlated_parlays(
        self,
        projections: list[Projection]
    ) -> list[CorrelatedParlay]:
        """
        Find correlated parlay opportunities based on game script.
        
        Args:
            projections: List of all player projections.
            
        Returns:
            List of correlated parlay recommendations.
        """
        game_script = self.determine_game_script()
        parlays: list[CorrelatedParlay] = []
        
        if game_script == GameScript.TRAILING:
            parlay = self._build_trailing_parlay(projections)
            if parlay:
                parlays.append(parlay)
        
        elif game_script == GameScript.LEADING:
            parlay = self._build_leading_parlay(projections)
            if parlay:
                parlays.append(parlay)
        
        elif game_script == GameScript.EXPLOSIVE:
            parlay = self._build_explosive_parlay(projections)
            if parlay:
                parlays.append(parlay)
        
        # Also check for explosive even if not primary script
        if game_script != GameScript.EXPLOSIVE and self.game_context.total > 47:
            parlay = self._build_explosive_parlay(projections)
            if parlay:
                parlays.append(parlay)
        
        return parlays
    
    def _build_trailing_parlay(
        self,
        projections: list[Projection]
    ) -> CorrelatedParlay | None:
        """
        Build trailing script parlay.
        
        Correlation: QB Attempts Over + WR Receptions Over + RB Rush Yards Under
        """
        legs: list[ParlayLeg] = []
        
        # Find QB Pass Attempts (prefer Over)
        qb_attempts = self._find_projection(
            projections, Position.QB, "Pass Attempts"
        )
        if qb_attempts:
            legs.append(ParlayLeg(
                player_name=qb_attempts.player_name,
                stat_type="Pass Attempts",
                line=qb_attempts.market_line,
                direction=BetType.OVER,
                edge=qb_attempts.edge if qb_attempts.recommendation == BetType.OVER else -qb_attempts.edge
            ))
        
        # Find WR Receptions (prefer Over)
        wr_rec = self._find_best_projection(
            projections, [Position.WR, Position.TE], "Receptions", BetType.OVER
        )
        if wr_rec:
            legs.append(ParlayLeg(
                player_name=wr_rec.player_name,
                stat_type="Receptions",
                line=wr_rec.market_line,
                direction=BetType.OVER,
                edge=wr_rec.edge if wr_rec.recommendation == BetType.OVER else -wr_rec.edge
            ))
        
        # Find RB Rush Yards (prefer Under in trailing)
        rb_rush = self._find_projection(
            projections, Position.RB, "Rush Yards"
        )
        if rb_rush:
            legs.append(ParlayLeg(
                player_name=rb_rush.player_name,
                stat_type="Rush Yards",
                line=rb_rush.market_line,
                direction=BetType.UNDER,
                edge=-rb_rush.edge if rb_rush.recommendation == BetType.OVER else rb_rush.edge
            ))
        
        if len(legs) >= 2:
            return CorrelatedParlay(
                game_script=GameScript.TRAILING,
                legs=legs,
                combined_confidence=self._calculate_parlay_confidence(legs),
                correlation_strength="Strong" if len(legs) == 3 else "Moderate"
            )
        return None
    
    def _build_leading_parlay(
        self,
        projections: list[Projection]
    ) -> CorrelatedParlay | None:
        """
        Build leading script parlay.
        
        Correlation: RB Rush Attempts Over + QB Pass Attempts Under
        """
        legs: list[ParlayLeg] = []
        
        # Find RB Rush Attempts (prefer Over)
        rb_attempts = self._find_projection(
            projections, Position.RB, "Rush Attempts"
        )
        if rb_attempts:
            legs.append(ParlayLeg(
                player_name=rb_attempts.player_name,
                stat_type="Rush Attempts",
                line=rb_attempts.market_line,
                direction=BetType.OVER,
                edge=rb_attempts.edge if rb_attempts.recommendation == BetType.OVER else -rb_attempts.edge
            ))
        
        # Find RB Rush Yards (often correlates with leading)
        rb_yards = self._find_projection(
            projections, Position.RB, "Rush Yards"
        )
        if rb_yards:
            legs.append(ParlayLeg(
                player_name=rb_yards.player_name,
                stat_type="Rush Yards",
                line=rb_yards.market_line,
                direction=BetType.OVER,
                edge=rb_yards.edge if rb_yards.recommendation == BetType.OVER else -rb_yards.edge
            ))
        
        # Find QB Pass Attempts (prefer Under in leading)
        qb_attempts = self._find_projection(
            projections, Position.QB, "Pass Attempts"
        )
        if qb_attempts:
            legs.append(ParlayLeg(
                player_name=qb_attempts.player_name,
                stat_type="Pass Attempts",
                line=qb_attempts.market_line,
                direction=BetType.UNDER,
                edge=-qb_attempts.edge if qb_attempts.recommendation == BetType.OVER else qb_attempts.edge
            ))
        
        if len(legs) >= 2:
            return CorrelatedParlay(
                game_script=GameScript.LEADING,
                legs=legs,
                combined_confidence=self._calculate_parlay_confidence(legs),
                correlation_strength="Strong" if len(legs) == 3 else "Moderate"
            )
        return None
    
    def _build_explosive_parlay(
        self,
        projections: list[Projection]
    ) -> CorrelatedParlay | None:
        """
        Build explosive game parlay.
        
        Correlation: QB Passing Yards Over + WR1 Receiving Yards Over
        """
        legs: list[ParlayLeg] = []
        
        # Find QB Passing Yards
        qb_yards = self._find_projection(
            projections, Position.QB, "Passing Yards"
        )
        if qb_yards:
            legs.append(ParlayLeg(
                player_name=qb_yards.player_name,
                stat_type="Passing Yards",
                line=qb_yards.market_line,
                direction=BetType.OVER,
                edge=qb_yards.edge if qb_yards.recommendation == BetType.OVER else -qb_yards.edge
            ))
        
        # Find best WR Rec Yards
        wr_yards = self._find_best_projection(
            projections, [Position.WR, Position.TE], "Rec Yards", BetType.OVER
        )
        if wr_yards:
            legs.append(ParlayLeg(
                player_name=wr_yards.player_name,
                stat_type="Rec Yards",
                line=wr_yards.market_line,
                direction=BetType.OVER,
                edge=wr_yards.edge if wr_yards.recommendation == BetType.OVER else -wr_yards.edge
            ))
        
        if len(legs) >= 2:
            return CorrelatedParlay(
                game_script=GameScript.EXPLOSIVE,
                legs=legs,
                combined_confidence=self._calculate_parlay_confidence(legs),
                correlation_strength="Strong"
            )
        return None
    
    def _find_projection(
        self,
        projections: list[Projection],
        position: Position,
        stat_type: str
    ) -> Projection | None:
        """Find first matching projection."""
        for proj in projections:
            if proj.position == position and proj.stat_type == stat_type:
                return proj
        return None
    
    def _find_best_projection(
        self,
        projections: list[Projection],
        positions: list[Position],
        stat_type: str,
        preferred_direction: BetType
    ) -> Projection | None:
        """Find best projection matching criteria with preferred direction."""
        candidates = [
            p for p in projections
            if p.position in positions and p.stat_type == stat_type
        ]
        
        if not candidates:
            return None
        
        # Prefer projections matching direction, then by edge magnitude
        matching = [c for c in candidates if c.recommendation == preferred_direction]
        if matching:
            return max(matching, key=lambda p: abs(p.edge))
        return max(candidates, key=lambda p: abs(p.edge))
    
    def _calculate_parlay_confidence(self, legs: list[ParlayLeg]) -> float:
        """Calculate combined parlay confidence."""
        if not legs:
            return 0.0
        
        total_edge = sum(leg.edge for leg in legs)
        avg_edge = total_edge / len(legs)
        
        # Base confidence from average edge
        base = 50 + min(avg_edge * 2, 30)
        
        # Bonus for multiple legs with positive edge
        positive_legs = sum(1 for leg in legs if leg.edge > 0)
        bonus = positive_legs * 5
        
        return min(base + bonus, 95)


# =============================================================================
# RICH UI DASHBOARD
# =============================================================================

class Dashboard:
    """
    Rich-based terminal user interface for the NFL Analytics Dashboard.
    
    Provides professional rendering of projections, comparisons, and parlay slips.
    """
    
    def __init__(self):
        """Initialize the dashboard with a Rich console."""
        self.console = Console()
    
    def render_header(self) -> None:
        """Render the application header."""
        header = Text()
        header.append("🏈 NFL PREDICTIVE ANALYTICS ", style="bold cyan")
        header.append("& ", style="white")
        header.append("PARLAY GENERATION SYSTEM", style="bold green")
        
        self.console.print()
        self.console.print(Panel(
            header,
            box=box.DOUBLE,
            border_style="cyan",
            padding=(1, 2)
        ))
        self.console.print()
    
    def render_game_context(self, context: GameContext) -> None:
        """Render the game context panel."""
        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Matchup", f"{context.team} @ {context.opponent}")
        table.add_row("Spread", f"{context.spread:+.1f}")
        table.add_row("Total", f"{context.total:.1f}")
        table.add_row("Implied Team Total", f"{context.implied_team_total:.1f}")
        table.add_row("Opponent Def Rank", self._format_defense_rank(context.opponent_rank))
        
        self.console.print(Panel(
            table,
            title="[bold]📊 Game Context[/bold]",
            border_style="blue"
        ))
        self.console.print()
    
    def render_projections_table(
        self,
        projections: list[Projection],
        title: str = "Tale of the Tape"
    ) -> None:
        """
        Render the projections comparison table.
        
        Args:
            projections: List of projections to display.
            title: Table title.
        """
        table = Table(
            title=f"[bold yellow]📈 {title}[/bold yellow]",
            box=box.ROUNDED,
            show_lines=True,
            header_style="bold magenta"
        )
        
        table.add_column("Player", style="cyan", width=18)
        table.add_column("Pos", justify="center", width=4)
        table.add_column("Stat", style="white", width=14)
        table.add_column("Projection", justify="right", style="green", width=10)
        table.add_column("Line", justify="right", style="yellow", width=8)
        table.add_column("Edge", justify="right", width=8)
        table.add_column("Pick", justify="center", width=8)
        table.add_column("Conf", justify="right", width=6)
        
        for proj in projections:
            edge_style = "green" if proj.edge > 0 else "red"
            pick_style = "bold green" if proj.recommendation == BetType.OVER else "bold red"
            conf_style = self._get_confidence_style(proj.confidence)
            
            table.add_row(
                proj.player_name,
                proj.position.value,
                proj.stat_type,
                f"{proj.projected_value:.1f}",
                f"{proj.market_line:.1f}",
                f"[{edge_style}]{proj.edge:+.1f}%[/{edge_style}]",
                f"[{pick_style}]{proj.recommendation.value}[/{pick_style}]",
                f"[{conf_style}]{proj.confidence:.0f}%[/{conf_style}]"
            )
        
        self.console.print(table)
        self.console.print()
    
    def render_parlay_slip(self, parlay: CorrelatedParlay) -> None:
        """
        Render a recommended parlay slip.
        
        Args:
            parlay: Correlated parlay recommendation.
        """
        # Build parlay content
        content = Text()
        content.append(f"Game Script: ", style="dim")
        content.append(f"{parlay.game_script.value}\n", style="bold yellow")
        content.append(f"Correlation: ", style="dim")
        content.append(f"{parlay.correlation_strength}\n\n", style="bold cyan")
        
        for i, leg in enumerate(parlay.legs, 1):
            edge_style = "green" if leg.edge > 0 else "red"
            content.append(f"  {i}. ", style="white")
            content.append(f"{leg.player_name} ", style="bold")
            content.append(f"{leg.stat_type} ", style="cyan")
            content.append(f"{leg.direction.value} {leg.line:.1f} ", style="yellow")
            content.append(f"[{edge_style}]({leg.edge:+.1f}%)[/{edge_style}]\n")
        
        # Confidence bar
        conf = parlay.combined_confidence
        bar_filled = int(conf / 5)
        bar_empty = 20 - bar_filled
        conf_color = self._get_confidence_style(conf)
        
        content.append(f"\n  Confidence: ", style="dim")
        content.append(f"[{conf_color}]{'█' * bar_filled}{'░' * bar_empty}[/{conf_color}] ")
        content.append(f"[{conf_color}]{conf:.1f}%[/{conf_color}]")
        
        self.console.print(Panel(
            content,
            title="[bold green]🎰 RECOMMENDED PARLAY SLIP[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
        self.console.print()
    
    def render_no_parlays(self) -> None:
        """Render message when no correlated parlays found."""
        self.console.print(Panel(
            "[yellow]No strong correlated parlays identified for current game context.\n"
            "Consider individual plays based on the projections table above.[/yellow]",
            title="[bold yellow]⚠️ Parlay Analysis[/bold yellow]",
            border_style="yellow"
        ))
        self.console.print()
    
    def render_error(self, message: str) -> None:
        """Render an error message."""
        self.console.print(Panel(
            f"[red]{message}[/red]",
            title="[bold red]❌ Error[/bold red]",
            border_style="red"
        ))
    
    def render_success(self, message: str) -> None:
        """Render a success message."""
        self.console.print(f"[green]✓[/green] {message}")
    
    def render_info(self, message: str) -> None:
        """Render an info message."""
        self.console.print(f"[cyan]ℹ[/cyan] {message}")
    
    def _format_defense_rank(self, rank: int) -> str:
        """Format defense rank with color coding."""
        if rank <= 5:
            return f"[red]#{rank} (Elite)[/red]"
        elif rank <= 10:
            return f"[yellow]#{rank} (Good)[/yellow]"
        elif rank >= 28:
            return f"[green]#{rank} (Poor)[/green]"
        elif rank >= 20:
            return f"[cyan]#{rank} (Below Avg)[/cyan]"
        return f"#{rank} (Average)"
    
    def _get_confidence_style(self, confidence: float) -> str:
        """Get style based on confidence level."""
        if confidence >= 75:
            return "bold green"
        elif confidence >= 60:
            return "green"
        elif confidence >= 50:
            return "yellow"
        return "red"
    
    def render_review_screen(
        self,
        game_context: GameContext,
        players: list[PlayerData]
    ) -> None:
        """
        Render a comprehensive review screen showing all entered data.
        
        Args:
            game_context: The game context data.
            players: List of all player data entered.
        """
        self.console.print()
        self.console.print(Panel(
            "[bold cyan]📋 DATA REVIEW - Verify All Entries Before Generating[/bold cyan]",
            box=box.DOUBLE,
            border_style="cyan"
        ))
        self.console.print()
        
        # Game Context Table
        self.render_game_context(game_context)
        
        # Players Table
        if players:
            self._render_players_summary(players)
            
            # Detailed stats for each player
            for i, player in enumerate(players, 1):
                self._render_player_detail(player, i)
    
    def _render_players_summary(self, players: list[PlayerData]) -> None:
        """Render a summary table of all players."""
        table = Table(
            title="[bold magenta]👥 Players Summary[/bold magenta]",
            box=box.ROUNDED,
            show_lines=True,
            header_style="bold cyan"
        )
        
        table.add_column("#", justify="center", width=3)
        table.add_column("Player Name", style="white", width=20)
        table.add_column("Position", justify="center", width=6)
        table.add_column("Games", justify="center", width=6)
        table.add_column("Key Stat (L5 Avg)", justify="right", width=18)
        table.add_column("Season Total", justify="right", width=14)
        
        for i, player in enumerate(players, 1):
            key_stat_l5, key_stat_season, stat_name = self._get_key_stats(player)
            table.add_row(
                str(i),
                player.name,
                player.position.value,
                str(player.stats.games_played),
                f"{stat_name}: {key_stat_l5:.1f}",
                f"{key_stat_season:.1f}"
            )
        
        self.console.print(table)
        self.console.print()
    
    def _render_player_detail(self, player: PlayerData, index: int) -> None:
        """Render detailed stats for a single player."""
        stats_table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold",
            padding=(0, 1)
        )
        stats_table.add_column("Stat", style="cyan", width=25)
        stats_table.add_column("L5 Avg/Game", justify="right", style="yellow", width=12)
        stats_table.add_column("Season Total", justify="right", style="green", width=12)
        stats_table.add_column("Line", justify="right", style="magenta", width=10)
        
        lines = player.market_lines
        
        if player.position == Position.QB:
            stats: QBStats = player.stats  # type: ignore
            season_pass_avg = stats.passing_yards_season_total / stats.games_played
            season_rush_avg = stats.rush_yards_season_total / stats.games_played
            season_att_avg = stats.pass_attempts_season_total / stats.games_played
            
            stats_table.add_row(
                "Passing Yards",
                f"{stats.passing_yards_l5_avg:.1f}",
                f"{stats.passing_yards_season_total:.0f} ({season_pass_avg:.1f}/g)",
                f"{lines.passing_yards:.1f}" if lines.passing_yards else "-"
            )
            stats_table.add_row(
                "Rush Yards",
                f"{stats.rush_yards_l5_avg:.1f}",
                f"{stats.rush_yards_season_total:.0f} ({season_rush_avg:.1f}/g)",
                f"{lines.rush_yards:.1f}" if lines.rush_yards else "-"
            )
            stats_table.add_row(
                "Pass Attempts",
                f"{stats.pass_attempts_l5_avg:.1f}",
                f"{stats.pass_attempts_season_total:.0f} ({season_att_avg:.1f}/g)",
                f"{lines.pass_attempts:.1f}" if lines.pass_attempts else "-"
            )
            stats_table.add_row("EPA/Play", f"{stats.epa_per_play:.3f}", "-", "-")
            stats_table.add_row("CPOE", f"{stats.cpoe:.1f}%", "-", "-")
            
        elif player.position == Position.RB:
            stats: RBStats = player.stats  # type: ignore
            season_rush_avg = stats.rush_yards_season_total / stats.games_played
            season_att_avg = stats.rush_attempts_season_total / stats.games_played
            
            stats_table.add_row(
                "Rush Yards",
                f"{stats.rush_yards_l5_avg:.1f}",
                f"{stats.rush_yards_season_total:.0f} ({season_rush_avg:.1f}/g)",
                f"{lines.rush_yards:.1f}" if lines.rush_yards else "-"
            )
            stats_table.add_row(
                "Rush Attempts",
                f"{stats.rush_attempts_l5_avg:.1f}",
                f"{stats.rush_attempts_season_total:.0f} ({season_att_avg:.1f}/g)",
                f"{lines.rush_attempts:.1f}" if lines.rush_attempts else "-"
            )
            stats_table.add_row("Opportunity Share", f"{stats.opportunity_share_pct:.1f}%", "-", "-")
            stats_table.add_row("YCO/Att", f"{stats.yco_per_att:.2f}", "-", "-")
            
        else:  # WR/TE
            stats: WRTEStats = player.stats  # type: ignore
            season_rec_avg = stats.rec_yards_season_total / stats.games_played
            season_receptions_avg = stats.receptions_season_total / stats.games_played
            
            stats_table.add_row(
                "Receiving Yards",
                f"{stats.rec_yards_l5_avg:.1f}",
                f"{stats.rec_yards_season_total:.0f} ({season_rec_avg:.1f}/g)",
                f"{lines.rec_yards:.1f}" if lines.rec_yards else "-"
            )
            stats_table.add_row(
                "Receptions",
                f"{stats.receptions_l5_avg:.1f}",
                f"{stats.receptions_season_total:.0f} ({season_receptions_avg:.1f}/g)",
                f"{lines.receptions:.1f}" if lines.receptions else "-"
            )
            stats_table.add_row("Target Share", f"{stats.target_share_pct:.1f}%", "-", "-")
            stats_table.add_row("ADOT", f"{stats.adot:.1f}", "-", "-")
            stats_table.add_row("Air Yards Share", f"{stats.air_yards_share:.1f}%", "-", "-")
        
        self.console.print(Panel(
            stats_table,
            title=f"[bold][{index}] {player.name} ({player.position.value})[/bold]",
            border_style="blue",
            padding=(0, 1)
        ))
        self.console.print()
    
    def _get_key_stats(self, player: PlayerData) -> tuple[float, float, str]:
        """Get key stats for summary display."""
        if player.position == Position.QB:
            stats: QBStats = player.stats  # type: ignore
            return stats.passing_yards_l5_avg, stats.passing_yards_season_total, "Pass Yds"
        elif player.position == Position.RB:
            stats: RBStats = player.stats  # type: ignore
            return stats.rush_yards_l5_avg, stats.rush_yards_season_total, "Rush Yds"
        else:
            stats: WRTEStats = player.stats  # type: ignore
            return stats.rec_yards_l5_avg, stats.rec_yards_season_total, "Rec Yds"
    
    def render_edit_menu(self, num_players: int) -> None:
        """Render the edit menu options."""
        self.console.print(Panel(
            "[bold]Edit Options:[/bold]\n\n"
            "  [cyan]G[/cyan] - Edit Game Context\n"
            f"  [cyan]1-{num_players}[/cyan] - Edit Player (by number)\n"
            "  [cyan]A[/cyan] - Add Another Player\n"
            "  [cyan]D[/cyan] - Delete a Player\n"
            "  [cyan]R[/cyan] - Run Analysis (Generate Projections)\n"
            "  [cyan]Q[/cyan] - Quit",
            title="[bold yellow]⚙️ Actions[/bold yellow]",
            border_style="yellow"
        ))


# =============================================================================
# INPUT HANDLER
# =============================================================================

class InputHandler:
    """
    Handles user input for the NFL Analytics application.
    
    Uses Rich prompts for professional input collection with validation.
    """
    
    def __init__(self, console: Console):
        """Initialize with Rich console."""
        self.console = console
    
    def display_roster_selection(self, team: str) -> None:
        """Display the roster for a team in a formatted table with stats indicators."""
        if team not in TEAM_ROSTERS:
            return
        
        roster = TEAM_ROSTERS[team]
        
        table = Table(
            title=f"[bold]{team} - Available Players[/bold]",
            box=box.ROUNDED,
            show_lines=True,
            header_style="bold cyan"
        )
        table.add_column("QB", style="yellow", width=28)
        table.add_column("RB", style="green", width=28)
        table.add_column("WR", style="magenta", width=28)
        table.add_column("TE", style="cyan", width=28)
        
        max_len = max(
            len(roster.get("QB", [])),
            len(roster.get("RB", [])),
            len(roster.get("WR", [])),
            len(roster.get("TE", []))
        )
        
        def format_player(player: dict, pos: str) -> str:
            """Format player name with stats indicator."""
            name = player["name"]
            num = player["number"]
            has_stats = name in PLAYER_STATS
            indicator = "[green]✓[/green]" if has_stats else "[dim]○[/dim]"
            return f"#{num} {name} {indicator}"
        
        for i in range(max_len):
            qb = format_player(roster["QB"][i], "QB") if i < len(roster["QB"]) else ""
            rb = format_player(roster["RB"][i], "RB") if i < len(roster["RB"]) else ""
            wr = format_player(roster["WR"][i], "WR") if i < len(roster["WR"]) else ""
            te = format_player(roster["TE"][i], "TE") if i < len(roster["TE"]) else ""
            
            table.add_row(qb, rb, wr, te)
        
        self.console.print(table)
        self.console.print("[dim]  ✓ = Stats pre-loaded  |  ○ = Manual entry required[/dim]")
        self.console.print()
    
    async def select_game_and_team(self) -> tuple[str, str, GameContext]:
        """
        Let user select from available games and teams.
        
        Returns:
            Tuple of (selected_team, opponent, GameContext).
        """
        self.console.print(Panel(
            "[bold cyan]🏈 TONIGHT'S GAME: Denver Broncos @ Washington Commanders[/bold cyan]\n\n"
            "[dim]Pre-loaded rosters available for quick player selection![/dim]",
            box=box.DOUBLE,
            border_style="green"
        ))
        self.console.print()
        
        # Show game info
        game_data = DEFAULT_GAME_CONTEXTS["Broncos @ Commanders"]
        
        info_table = Table(box=box.SIMPLE, show_header=False)
        info_table.add_column("", style="cyan")
        info_table.add_column("", style="white")
        info_table.add_row("Spread", f"Commanders {game_data['spread']}")
        info_table.add_row("Total", f"{game_data['total']}")
        info_table.add_row("Broncos Implied", f"{game_data['broncos_implied']}")
        info_table.add_row("Commanders Implied", f"{game_data['commanders_implied']}")
        
        self.console.print(info_table)
        self.console.print()
        
        # Select which team to analyze
        self.console.print("[cyan]Which team do you want to build a parlay for?[/cyan]")
        self.console.print("  1. Denver Broncos")
        self.console.print("  2. Washington Commanders")
        self.console.print("  3. Both Teams (Mixed Parlay)")
        self.console.print("  4. Manual Entry (Custom Game)")
        
        choice = IntPrompt.ask("\n[cyan]Select option[/cyan]", default=1)
        
        if choice == 4:
            # Fall back to manual entry
            context = await self.get_game_context()
            return context.team, context.opponent, context
        
        # Set up context based on selection
        if choice == 1:
            team = "Denver Broncos"
            opponent = "Washington Commanders"
            spread = -game_data['spread']  # Broncos perspective
            implied = game_data['broncos_implied']
            opp_rank = game_data['commanders_def_rank']
        elif choice == 2:
            team = "Washington Commanders"
            opponent = "Denver Broncos"
            spread = game_data['spread']
            implied = game_data['commanders_implied']
            opp_rank = game_data['broncos_def_rank']
        else:  # Both teams
            team = "Mixed"
            opponent = "Broncos vs Commanders"
            spread = 0.0
            implied = game_data['total'] / 2
            opp_rank = 14  # Average
        
        context = GameContext(
            team=team,
            opponent=opponent,
            spread=spread,
            total=game_data['total'],
            implied_team_total=implied,
            opponent_rank=opp_rank
        )
        
        return team, opponent, context
    
    async def select_players_from_roster(
        self,
        primary_team: str,
        num_players: int = 6
    ) -> list[tuple[str, str, Position]]:
        """
        Let user select multiple players from roster.
        
        Args:
            primary_team: Primary team being analyzed.
            num_players: Number of players to select.
            
        Returns:
            List of (player_name, team, position) tuples.
        """
        selected: list[tuple[str, str, Position]] = []
        
        # Determine which rosters to show
        if primary_team == "Mixed":
            teams_to_show = list(TEAM_ROSTERS.keys())
        elif primary_team in TEAM_ROSTERS:
            teams_to_show = [primary_team]
            # Option to add from opponent
            other_team = [t for t in TEAM_ROSTERS.keys() if t != primary_team]
            if other_team:
                teams_to_show.extend(other_team)
        else:
            teams_to_show = []
        
        # Display rosters
        for team in teams_to_show:
            self.display_roster_selection(team)
        
        self.console.print(Panel(
            f"[bold]Select {num_players} players for your parlay analysis[/bold]\n\n"
            "[dim]Type the player name exactly as shown, or type 'done' when finished.\n"
            "You can select from either team.[/dim]",
            title="[bold cyan]👥 Player Selection[/bold cyan]",
            border_style="cyan"
        ))
        
        while len(selected) < num_players:
            remaining = num_players - len(selected)
            self.console.print(f"\n[yellow]Players selected: {len(selected)}/{num_players}[/yellow]")
            
            if selected:
                self.console.print("[dim]Current selections:[/dim]")
                for i, (name, team, pos) in enumerate(selected, 1):
                    self.console.print(f"  {i}. {name} ({pos.value}) - {team}")
            
            player_input = Prompt.ask(
                f"\n[cyan]Enter player name ({remaining} remaining)[/cyan]",
                default="done" if len(selected) >= 1 else ""
            ).strip()
            
            if player_input.lower() == "done":
                if len(selected) >= 1:
                    break
                else:
                    self.console.print("[red]Select at least 1 player.[/red]")
                    continue
            
            # Find player in rosters
            found = False
            for team, roster in TEAM_ROSTERS.items():
                for pos_key, players in roster.items():
                    for player in players:
                        if player["name"].lower() == player_input.lower():
                            position = Position(pos_key)
                            selected.append((player["name"], team, position))
                            self.console.print(
                                f"[green]✓ Added {player['name']} ({pos_key}) from {team}[/green]"
                            )
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            
            if not found:
                self.console.print(f"[red]Player '{player_input}' not found. Check spelling.[/red]")
                # Suggest close matches
                self._suggest_players(player_input)
        
        return selected
    
    def _suggest_players(self, search: str) -> None:
        """Suggest players with similar names."""
        suggestions = []
        search_lower = search.lower()
        
        for team, roster in TEAM_ROSTERS.items():
            for pos_key, players in roster.items():
                for player in players:
                    name = player["name"].lower()
                    # Simple fuzzy match - contains any word
                    if any(word in name for word in search_lower.split()):
                        suggestions.append(f"{player['name']} ({pos_key})")
        
        if suggestions:
            self.console.print("[dim]Did you mean:[/dim]")
            for s in suggestions[:5]:
                self.console.print(f"  [cyan]• {s}[/cyan]")
    
    async def batch_enter_player_stats(
        self,
        player_selections: list[tuple[str, str, Position]]
    ) -> list[PlayerData]:
        """
        Enter stats for multiple players in sequence.
        
        Args:
            player_selections: List of (name, team, position) tuples.
            
        Returns:
            List of PlayerData objects.
        """
        players: list[PlayerData] = []
        total = len(player_selections)
        
        self.console.print(Panel(
            f"[bold]Now entering stats for {total} players[/bold]\n\n"
            "[dim]Enter Last 5 game averages and season totals for each player.\n"
            "Pro tip: Have your stats ready from ESPN, PFF, or FantasyPros![/dim]",
            title="[bold cyan]📊 Batch Stats Entry[/bold cyan]",
            border_style="cyan"
        ))
        
        for i, (name, team, position) in enumerate(player_selections, 1):
            self.console.print()
            self.console.print(Panel(
                f"[bold]Player {i}/{total}: {name}[/bold]\n"
                f"[dim]Team: {team} | Position: {position.value}[/dim]",
                border_style="yellow"
            ))
            
            try:
                if position == Position.QB:
                    stats = await self._get_qb_stats()
                    lines = await self._get_qb_lines(name)
                elif position == Position.RB:
                    stats = await self._get_rb_stats()
                    lines = await self._get_rb_lines(name)
                else:
                    stats = await self._get_wr_te_stats()
                    lines = await self._get_wr_te_lines(name, position)
                
                players.append(PlayerData(
                    name=name,
                    position=position,
                    stats=stats,
                    market_lines=lines
                ))
                
                self.console.print(f"[green]✓ {name} stats saved[/green]")
                
            except ValidationError as e:
                self.console.print(f"[red]Error with {name}: {e.errors()[0]['msg']}[/red]")
                self.console.print("[yellow]Skipping this player...[/yellow]")
        
        return players
    
    async def get_game_context(self) -> GameContext:
        """
        Collect game context from user input.
        
        Returns:
            Validated GameContext model.
        """
        self.console.print(Panel(
            "[cyan]Enter the game details for analysis[/cyan]",
            title="[bold]📋 Game Setup[/bold]",
            border_style="cyan"
        ))
        
        while True:
            try:
                team = Prompt.ask("[cyan]Team being analyzed[/cyan]")
                opponent = Prompt.ask("[cyan]Opponent[/cyan]")
                spread = FloatPrompt.ask(
                    "[cyan]Point Spread[/cyan] (negative = favorite)",
                    default=0.0
                )
                total = FloatPrompt.ask("[cyan]Game Total (O/U)[/cyan]", default=45.0)
                implied_total = FloatPrompt.ask(
                    "[cyan]Implied Team Total[/cyan]",
                    default=round((total - spread) / 2, 1)
                )
                opponent_rank = IntPrompt.ask(
                    "[cyan]Opponent Defensive Rank[/cyan] (1-32)",
                    default=16
                )
                
                context = GameContext(
                    team=team,
                    opponent=opponent,
                    spread=spread,
                    total=total,
                    implied_team_total=implied_total,
                    opponent_rank=opponent_rank
                )
                self.console.print()
                return context
                
            except ValidationError as e:
                self.console.print(f"[red]Validation Error: {e.errors()[0]['msg']}[/red]")
                self.console.print("[yellow]Please try again.[/yellow]\n")
    
    async def get_player_data(self) -> PlayerData | None:
        """
        Collect player data from user input.
        
        Returns:
            PlayerData container or None if user declines.
        """
        self.console.print()
        add_player = Confirm.ask("[cyan]Add a player for analysis?[/cyan]")
        
        if not add_player:
            return None
        
        self.console.print()
        name = Prompt.ask("[cyan]Player Name[/cyan]")
        
        # Position selection
        self.console.print("\n[cyan]Position:[/cyan]")
        self.console.print("  1. QB (Quarterback)")
        self.console.print("  2. RB (Running Back)")
        self.console.print("  3. WR (Wide Receiver)")
        self.console.print("  4. TE (Tight End)")
        
        pos_choice = IntPrompt.ask("[cyan]Select position[/cyan]", default=1)
        position_map = {1: Position.QB, 2: Position.RB, 3: Position.WR, 4: Position.TE}
        position = position_map.get(pos_choice, Position.QB)
        
        self.console.print()
        
        try:
            if position == Position.QB:
                stats = await self._get_qb_stats()
                lines = await self._get_qb_lines(name)
            elif position == Position.RB:
                stats = await self._get_rb_stats()
                lines = await self._get_rb_lines(name)
            else:
                stats = await self._get_wr_te_stats()
                lines = await self._get_wr_te_lines(name, position)
            
            return PlayerData(
                name=name,
                position=position,
                stats=stats,
                market_lines=lines
            )
            
        except ValidationError as e:
            self.console.print(f"[red]Validation Error: {e.errors()[0]['msg']}[/red]")
            return None
    
    async def _get_qb_stats_fast(self, name: str) -> tuple[QBStats, MarketLines]:
        """
        Fast QB stats + lines entry on single screen.
        Auto-populates from PLAYER_STATS if available.
        
        Args:
            name: Player name for display.
            
        Returns:
            Tuple of (QBStats, MarketLines).
        """
        # Get pre-loaded stats if available
        preload = PLAYER_STATS.get(name, {})
        has_preload = bool(preload) and preload.get("position") == "QB"
        
        if has_preload:
            self.console.print(Panel(
                f"[bold green]✓ Found pre-loaded stats for {name}![/bold green]\n"
                "[dim]Review and adjust if needed, or just press Enter to accept[/dim]",
                title="[bold blue]🎯 QB Data Entry (AUTO-FILLED)[/bold blue]",
                border_style="green"
            ))
        else:
            self.console.print(Panel(
                f"[bold]{name}[/bold] - QB Stats & Lines\n"
                "[dim]Press Enter to accept defaults, or type value[/dim]",
                title="[bold blue]🎯 QB Data Entry[/bold blue]",
                border_style="blue"
            ))
        
        # Defaults from preload or standard defaults
        def_games = preload.get("games_played", 12)
        def_pass_l5 = preload.get("passing_yards_l5_avg", 250.0)
        def_rush_l5 = preload.get("rush_yards_l5_avg", 15.0)
        def_att_l5 = preload.get("pass_attempts_l5_avg", 35.0)
        def_pass_tot = preload.get("passing_yards_season_total", round(def_pass_l5 * def_games))
        def_rush_tot = preload.get("rush_yards_season_total", round(def_rush_l5 * def_games))
        def_att_tot = preload.get("pass_attempts_season_total", round(def_att_l5 * def_games))
        def_epa = preload.get("epa_per_play", 0.10)
        def_cpoe = preload.get("cpoe", 2.0)
        
        # Quick input table display
        self.console.print("[cyan]━━━ STATS ━━━[/cyan]")
        games = IntPrompt.ask("  Games Played", default=def_games)
        
        self.console.print("\n[yellow]  L5 Avg/Game:[/yellow]")
        pass_l5 = FloatPrompt.ask("    Pass Yds", default=def_pass_l5)
        rush_l5 = FloatPrompt.ask("    Rush Yds", default=def_rush_l5)
        att_l5 = FloatPrompt.ask("    Pass Att", default=def_att_l5)
        
        self.console.print("\n[green]  Season Totals:[/green]")
        pass_tot = FloatPrompt.ask("    Pass Yds", default=def_pass_tot)
        rush_tot = FloatPrompt.ask("    Rush Yds", default=def_rush_tot)
        att_tot = FloatPrompt.ask("    Pass Att", default=def_att_tot)
        
        self.console.print("\n[magenta]  Efficiency:[/magenta]")
        epa = FloatPrompt.ask("    EPA/Play", default=def_epa)
        cpoe = FloatPrompt.ask("    CPOE", default=def_cpoe)
        
        self.console.print("\n[cyan]━━━ VEGAS LINES ━━━[/cyan]")
        line_pass = FloatPrompt.ask("  Pass Yds Line", default=round(pass_l5 - 5, 1))
        line_rush = FloatPrompt.ask("  Rush Yds Line", default=round(rush_l5 - 2, 1))
        line_att = FloatPrompt.ask("  Pass Att Line", default=round(att_l5 - 2, 1))
        
        stats = QBStats(
            games_played=games,
            passing_yards_l5_avg=pass_l5,
            passing_yards_season_total=pass_tot,
            rush_yards_l5_avg=rush_l5,
            rush_yards_season_total=rush_tot,
            epa_per_play=epa,
            cpoe=cpoe,
            pass_attempts_l5_avg=att_l5,
            pass_attempts_season_total=att_tot
        )
        
        lines = MarketLines(
            player_name=name,
            position=Position.QB,
            passing_yards=line_pass,
            rush_yards=line_rush,
            pass_attempts=line_att
        )
        
        return stats, lines
    
    async def _get_rb_stats_fast(self, name: str) -> tuple[RBStats, MarketLines]:
        """
        Fast RB stats + lines entry on single screen.
        Auto-populates from PLAYER_STATS if available.
        
        Args:
            name: Player name for display.
            
        Returns:
            Tuple of (RBStats, MarketLines).
        """
        # Get pre-loaded stats if available
        preload = PLAYER_STATS.get(name, {})
        has_preload = bool(preload) and preload.get("position") == "RB"
        
        if has_preload:
            self.console.print(Panel(
                f"[bold green]✓ Found pre-loaded stats for {name}![/bold green]\n"
                "[dim]Review and adjust if needed, or just press Enter to accept[/dim]",
                title="[bold green]🎯 RB Data Entry (AUTO-FILLED)[/bold green]",
                border_style="green"
            ))
        else:
            self.console.print(Panel(
                f"[bold]{name}[/bold] - RB Stats & Lines\n"
                "[dim]Press Enter to accept defaults, or type value[/dim]",
                title="[bold green]🎯 RB Data Entry[/bold green]",
                border_style="green"
            ))
        
        # Defaults from preload or standard defaults
        def_games = preload.get("games_played", 12)
        def_rush_l5 = preload.get("rush_yards_l5_avg", 70.0)
        def_att_l5 = preload.get("rush_attempts_l5_avg", 15.0)
        def_rush_tot = preload.get("rush_yards_season_total", round(def_rush_l5 * def_games))
        def_att_tot = preload.get("rush_attempts_season_total", round(def_att_l5 * def_games))
        def_opp_share = preload.get("opportunity_share_pct", 60.0)
        def_yco = preload.get("yco_per_att", 2.5)
        
        self.console.print("[cyan]━━━ STATS ━━━[/cyan]")
        games = IntPrompt.ask("  Games Played", default=def_games)
        
        self.console.print("\n[yellow]  L5 Avg/Game:[/yellow]")
        rush_l5 = FloatPrompt.ask("    Rush Yds", default=def_rush_l5)
        att_l5 = FloatPrompt.ask("    Rush Att", default=def_att_l5)
        
        self.console.print("\n[green]  Season Totals:[/green]")
        rush_tot = FloatPrompt.ask("    Rush Yds", default=def_rush_tot)
        att_tot = FloatPrompt.ask("    Rush Att", default=def_att_tot)
        
        self.console.print("\n[magenta]  Efficiency:[/magenta]")
        opp_share = FloatPrompt.ask("    Opp Share %", default=def_opp_share)
        yco = FloatPrompt.ask("    YCO/Att", default=def_yco)
        
        self.console.print("\n[cyan]━━━ VEGAS LINES ━━━[/cyan]")
        line_rush = FloatPrompt.ask("  Rush Yds Line", default=round(rush_l5 - 5, 1))
        line_att = FloatPrompt.ask("  Rush Att Line", default=round(att_l5 - 1, 1))
        
        stats = RBStats(
            games_played=games,
            rush_yards_l5_avg=rush_l5,
            rush_yards_season_total=rush_tot,
            opportunity_share_pct=opp_share,
            yco_per_att=yco,
            rush_attempts_l5_avg=att_l5,
            rush_attempts_season_total=att_tot
        )
        
        lines = MarketLines(
            player_name=name,
            position=Position.RB,
            rush_yards=line_rush,
            rush_attempts=line_att
        )
        
        return stats, lines
    
    async def _get_wr_te_stats_fast(self, name: str, position: Position) -> tuple[WRTEStats, MarketLines]:
        """
        Fast WR/TE stats + lines entry on single screen.
        Auto-populates from PLAYER_STATS if available.
        
        Args:
            name: Player name for display.
            position: WR or TE position.
            
        Returns:
            Tuple of (WRTEStats, MarketLines).
        """
        # Get pre-loaded stats if available
        preload = PLAYER_STATS.get(name, {})
        pos_str = position.value  # "WR" or "TE"
        has_preload = bool(preload) and preload.get("position") == pos_str
        
        pos_label = "WR" if position == Position.WR else "TE"
        
        if has_preload:
            self.console.print(Panel(
                f"[bold green]✓ Found pre-loaded stats for {name}![/bold green]\n"
                "[dim]Review and adjust if needed, or just press Enter to accept[/dim]",
                title=f"[bold magenta]🎯 {pos_label} Data Entry (AUTO-FILLED)[/bold magenta]",
                border_style="green"
            ))
        else:
            self.console.print(Panel(
                f"[bold]{name}[/bold] - {pos_label} Stats & Lines\n"
                "[dim]Press Enter to accept defaults, or type value[/dim]",
                title=f"[bold magenta]🎯 {pos_label} Data Entry[/bold magenta]",
                border_style="magenta"
            ))
        
        # Defaults from preload or standard defaults
        def_games = preload.get("games_played", 12)
        def_rec_l5 = preload.get("rec_yards_l5_avg", 70.0)
        def_catches_l5 = preload.get("receptions_l5_avg", 5.0)
        def_rec_tot = preload.get("rec_yards_season_total", round(def_rec_l5 * def_games))
        def_catches_tot = preload.get("receptions_season_total", round(def_catches_l5 * def_games))
        def_tgt_share = preload.get("target_share_pct", 22.0)
        def_adot = preload.get("adot", 10.0)
        def_air_share = preload.get("air_yards_share", 25.0)
        
        self.console.print("[cyan]━━━ STATS ━━━[/cyan]")
        games = IntPrompt.ask("  Games Played", default=def_games)
        
        self.console.print("\n[yellow]  L5 Avg/Game:[/yellow]")
        rec_l5 = FloatPrompt.ask("    Rec Yds", default=def_rec_l5)
        catches_l5 = FloatPrompt.ask("    Catches", default=def_catches_l5)
        
        self.console.print("\n[green]  Season Totals:[/green]")
        rec_tot = FloatPrompt.ask("    Rec Yds", default=def_rec_tot)
        catches_tot = FloatPrompt.ask("    Catches", default=def_catches_tot)
        
        self.console.print("\n[magenta]  Efficiency:[/magenta]")
        tgt_share = FloatPrompt.ask("    Target Share %", default=def_tgt_share)
        adot = FloatPrompt.ask("    ADOT", default=def_adot)
        air_share = FloatPrompt.ask("    Air Yds Share %", default=def_air_share)
        
        self.console.print("\n[cyan]━━━ VEGAS LINES ━━━[/cyan]")
        line_rec = FloatPrompt.ask("  Rec Yds Line", default=round(rec_l5 - 5, 1))
        line_catches = FloatPrompt.ask("  Receptions Line", default=round(catches_l5 - 0.5, 1))
        
        stats = WRTEStats(
            games_played=games,
            rec_yards_l5_avg=rec_l5,
            rec_yards_season_total=rec_tot,
            target_share_pct=tgt_share,
            adot=adot,
            air_yards_share=air_share,
            receptions_l5_avg=catches_l5,
            receptions_season_total=catches_tot
        )
        
        lines = MarketLines(
            player_name=name,
            position=position,
            rec_yards=line_rec,
            receptions=line_catches
        )
        
        return stats, lines
    
    async def batch_enter_player_stats_fast(
        self,
        player_selections: list[tuple[str, str, Position]]
    ) -> list[PlayerData]:
        """
        FAST batch entry - stats + lines on same screen per player.
        
        Args:
            player_selections: List of (name, team, position) tuples.
            
        Returns:
            List of PlayerData objects.
        """
        players: list[PlayerData] = []
        total = len(player_selections)
        
        self.console.print(Panel(
            f"[bold]⚡ SPEED ENTRY MODE - {total} Players[/bold]\n\n"
            "[dim]Stats auto-populate from NFL.com data where available!\n"
            "Just press Enter to accept pre-loaded stats.\n"
            "Vegas lines need manual entry (check DraftKings/FanDuel).[/dim]",
            title="[bold cyan]🚀 Fast Data Entry (AUTO-FILL ENABLED)[/bold cyan]",
            border_style="cyan"
        ))
        
        for i, (name, team, position) in enumerate(player_selections, 1):
            self.console.print()
            self.console.print(f"[bold yellow]═══ Player {i}/{total} ═══[/bold yellow]")
            
            try:
                if position == Position.QB:
                    stats, lines = await self._get_qb_stats_fast(name)
                elif position == Position.RB:
                    stats, lines = await self._get_rb_stats_fast(name)
                else:
                    stats, lines = await self._get_wr_te_stats_fast(name, position)
                
                players.append(PlayerData(
                    name=name,
                    position=position,
                    stats=stats,
                    market_lines=lines
                ))
                
                self.console.print(f"\n[green]✓ {name} complete![/green]")
                
            except ValidationError as e:
                self.console.print(f"[red]Error: {e.errors()[0]['msg']}[/red]")
                retry = Confirm.ask("[yellow]Retry this player?[/yellow]", default=True)
                if retry:
                    # Decrement to retry same player
                    continue
        
        return players
    
    async def _get_qb_stats(self) -> QBStats:
        """Collect QB statistics."""
        self.console.print(Panel(
            "[cyan]Enter QB Sharp Stats[/cyan]\n"
            "[dim]L5 = Last 5 Games Average per game | Season = Total for the season[/dim]",
            title="[bold]🎯 QB Statistics[/bold]",
            border_style="blue"
        ))
        
        return QBStats(
            games_played=IntPrompt.ask("  [cyan]Games Played This Season[/cyan]", default=12),
            passing_yards_l5_avg=FloatPrompt.ask("  [cyan]Passing Yards (L5 Avg/Game)[/cyan]", default=250.0),
            passing_yards_season_total=FloatPrompt.ask("  [cyan]Passing Yards (Season Total)[/cyan]", default=2900.0),
            rush_yards_l5_avg=FloatPrompt.ask("  [cyan]Rush Yards (L5 Avg/Game)[/cyan]", default=15.0),
            rush_yards_season_total=FloatPrompt.ask("  [cyan]Rush Yards (Season Total)[/cyan]", default=150.0),
            epa_per_play=FloatPrompt.ask("  [cyan]EPA Per Play[/cyan] (-0.5 to 0.5)", default=0.10),
            cpoe=FloatPrompt.ask("  [cyan]CPOE[/cyan] (Completion % Over Expected)", default=2.0),
            pass_attempts_l5_avg=FloatPrompt.ask("  [cyan]Pass Attempts (L5 Avg/Game)[/cyan]", default=35.0),
            pass_attempts_season_total=FloatPrompt.ask("  [cyan]Pass Attempts (Season Total)[/cyan]", default=400.0)
        )
    
    async def _get_rb_stats(self) -> RBStats:
        """Collect RB statistics."""
        self.console.print(Panel(
            "[cyan]Enter RB Sharp Stats[/cyan]\n"
            "[dim]L5 = Last 5 Games Average per game | Season = Total for the season[/dim]",
            title="[bold]🎯 RB Statistics[/bold]",
            border_style="blue"
        ))
        
        return RBStats(
            games_played=IntPrompt.ask("  [cyan]Games Played This Season[/cyan]", default=12),
            rush_yards_l5_avg=FloatPrompt.ask("  [cyan]Rush Yards (L5 Avg/Game)[/cyan]", default=70.0),
            rush_yards_season_total=FloatPrompt.ask("  [cyan]Rush Yards (Season Total)[/cyan]", default=780.0),
            opportunity_share_pct=FloatPrompt.ask("  [cyan]Opportunity Share %[/cyan]", default=60.0),
            yco_per_att=FloatPrompt.ask("  [cyan]Yards After Contact/Att[/cyan]", default=2.5),
            rush_attempts_l5_avg=FloatPrompt.ask("  [cyan]Rush Attempts (L5 Avg/Game)[/cyan]", default=15.0),
            rush_attempts_season_total=FloatPrompt.ask("  [cyan]Rush Attempts (Season Total)[/cyan]", default=168.0)
        )
    
    async def _get_wr_te_stats(self) -> WRTEStats:
        """Collect WR/TE statistics."""
        self.console.print(Panel(
            "[cyan]Enter WR/TE Sharp Stats[/cyan]\n"
            "[dim]L5 = Last 5 Games Average per game | Season = Total for the season[/dim]",
            title="[bold]🎯 WR/TE Statistics[/bold]",
            border_style="blue"
        ))
        
        return WRTEStats(
            games_played=IntPrompt.ask("  [cyan]Games Played This Season[/cyan]", default=12),
            rec_yards_l5_avg=FloatPrompt.ask("  [cyan]Receiving Yards (L5 Avg/Game)[/cyan]", default=70.0),
            rec_yards_season_total=FloatPrompt.ask("  [cyan]Receiving Yards (Season Total)[/cyan]", default=780.0),
            target_share_pct=FloatPrompt.ask("  [cyan]Target Share %[/cyan]", default=22.0),
            adot=FloatPrompt.ask("  [cyan]ADOT[/cyan] (Avg Depth of Target)", default=10.0),
            air_yards_share=FloatPrompt.ask("  [cyan]Air Yards Share %[/cyan]", default=25.0),
            receptions_l5_avg=FloatPrompt.ask("  [cyan]Receptions (L5 Avg/Game)[/cyan]", default=5.0),
            receptions_season_total=FloatPrompt.ask("  [cyan]Receptions (Season Total)[/cyan]", default=54.0)
        )
    
    async def _get_qb_lines(self, name: str) -> MarketLines:
        """Collect QB market lines."""
        self.console.print(Panel(
            f"[cyan]Enter Vegas Lines for {name}[/cyan]",
            title="[bold]💰 Market Lines[/bold]",
            border_style="yellow"
        ))
        
        return MarketLines(
            player_name=name,
            position=Position.QB,
            passing_yards=FloatPrompt.ask("  [yellow]Passing Yards Line[/yellow]", default=245.5),
            rush_yards=FloatPrompt.ask("  [yellow]Rush Yards Line[/yellow]", default=15.5),
            pass_attempts=FloatPrompt.ask("  [yellow]Pass Attempts Line[/yellow]", default=32.5)
        )
    
    async def _get_rb_lines(self, name: str) -> MarketLines:
        """Collect RB market lines."""
        self.console.print(Panel(
            f"[cyan]Enter Vegas Lines for {name}[/cyan]",
            title="[bold]💰 Market Lines[/bold]",
            border_style="yellow"
        ))
        
        return MarketLines(
            player_name=name,
            position=Position.RB,
            rush_yards=FloatPrompt.ask("  [yellow]Rush Yards Line[/yellow]", default=65.5),
            rush_attempts=FloatPrompt.ask("  [yellow]Rush Attempts Line[/yellow]", default=14.5)
        )
    
    async def _get_wr_te_lines(self, name: str, position: Position) -> MarketLines:
        """Collect WR/TE market lines."""
        self.console.print(Panel(
            f"[cyan]Enter Vegas Lines for {name}[/cyan]",
            title="[bold]💰 Market Lines[/bold]",
            border_style="yellow"
        ))
        
        return MarketLines(
            player_name=name,
            position=position,
            rec_yards=FloatPrompt.ask("  [yellow]Receiving Yards Line[/yellow]", default=60.5),
            receptions=FloatPrompt.ask("  [yellow]Receptions Line[/yellow]", default=4.5)
        )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class NFLAnalyticsApp:
    """
    Main application orchestrator for NFL Predictive Analytics.
    
    Coordinates all components including input handling, prediction engine,
    correlation logic, and dashboard rendering.
    """
    
    def __init__(self):
        """Initialize the application components."""
        self.console = Console()
        self.dashboard = Dashboard()
        self.input_handler = InputHandler(self.console)
        self.prediction_engine = PredictionEngine()
        self.game_context: GameContext | None = None
        self.players: list[PlayerData] = []
        self.projections: list[Projection] = []
        self.selected_team: str = ""
    
    async def run(self) -> None:
        """
        Main application execution flow.
        
        Orchestrates the complete workflow from input collection
        through review/edit to analysis and dashboard rendering.
        """
        try:
            # Render header
            self.dashboard.render_header()
            
            # Step 1: Select game and team (with pre-loaded rosters)
            self.console.print(Panel(
                "[bold]Choose your entry method:[/bold]\n\n"
                "  [cyan]1[/cyan] - Quick Start: Tonight's Game (Broncos vs Commanders)\n"
                "       [dim]Pre-loaded rosters, select 6 players from menu[/dim]\n\n"
                "  [cyan]2[/cyan] - Manual Entry: Custom Game\n"
                "       [dim]Enter all data manually[/dim]",
                title="[bold green]🏈 Welcome to NFL Parlay Generator[/bold green]",
                border_style="green"
            ))
            
            mode = IntPrompt.ask("\n[cyan]Select mode[/cyan]", default=1)
            
            if mode == 1:
                await self._roster_based_flow()
            else:
                await self._manual_entry_flow()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Analysis cancelled by user.[/yellow]")
        except ValidationError as e:
            self.dashboard.render_error(f"Data validation failed: {e}")
        except Exception as e:
            self.dashboard.render_error(f"Unexpected error: {str(e)}")
            raise
    
    async def _roster_based_flow(self) -> None:
        """Flow using pre-loaded rosters for quick player selection."""
        self.console.print()
        
        # Select game and team
        self.selected_team, opponent, self.game_context = await self.input_handler.select_game_and_team()
        
        self.console.print()
        self.console.print(f"[green]✓ Game Context set: {self.selected_team} vs {opponent}[/green]")
        self.console.print()
        
        # Ask how many players
        num_players = IntPrompt.ask(
            "[cyan]How many players to analyze?[/cyan]",
            default=6
        )
        num_players = min(max(num_players, 1), 10)  # Clamp between 1-10
        
        # Select players from roster
        player_selections = await self.input_handler.select_players_from_roster(
            self.selected_team,
            num_players
        )
        
        if not player_selections:
            self.console.print("[red]No players selected. Exiting.[/red]")
            return
        
        # Use FAST batch entry for all selected players
        self.players = await self.input_handler.batch_enter_player_stats_fast(player_selections)
        
        if not self.players:
            self.console.print("[red]No valid player data. Exiting.[/red]")
            return
        
        # Go to review/edit loop
        await self._review_edit_loop()
    
    async def _manual_entry_flow(self) -> None:
        """Original manual entry flow."""
        # Step 1: Collect game context
        self.game_context = await self.input_handler.get_game_context()
        
        # Step 2: Collect all players
        self.console.print(Panel(
            "[cyan]Add all players for analysis.[/cyan]\n"
            "[dim]You'll be able to review and edit everything before generating projections.[/dim]",
            title="[bold]👥 Player Entry[/bold]",
            border_style="cyan"
        ))
        
        while True:
            player = await self.input_handler.get_player_data()
            if player is None:
                if not self.players:
                    self.console.print("[yellow]At least one player is required.[/yellow]")
                    continue
                break
            
            self.players.append(player)
            self.dashboard.render_success(
                f"Added {player.name} ({player.position.value}) - "
                f"{len(self.players)} player(s) total"
            )
        
        # Step 3: Review/Edit Loop
        await self._review_edit_loop()
    
    async def _review_edit_loop(self) -> None:
        """Handle the review/edit/generate loop."""
        while True:
            # Clear screen and show review
            self.console.clear()
            self.dashboard.render_header()
            self.dashboard.render_review_screen(self.game_context, self.players)
            self.dashboard.render_edit_menu(len(self.players))
            
            # Get user action
            action = Prompt.ask(
                "\n[bold cyan]Enter your choice[/bold cyan]",
                default="R"
            ).strip().upper()
            
            if action == "Q":
                self.console.print("[yellow]Exiting without generating projections.[/yellow]")
                return
            
            elif action == "R":
                # Run analysis
                confirmed = Confirm.ask(
                    "[bold green]Ready to generate projections?[/bold green]"
                )
                if confirmed:
                    await self._run_analysis()
                    return
            
            elif action == "G":
                # Edit game context
                self.console.print()
                self.game_context = await self.input_handler.get_game_context()
            
            elif action == "A":
                # Add another player
                player = await self.input_handler.get_player_data()
                if player:
                    self.players.append(player)
                    self.dashboard.render_success(f"Added {player.name}")
            
            elif action == "D":
                # Delete a player
                if self.players:
                    await self._delete_player()
                else:
                    self.console.print("[yellow]No players to delete.[/yellow]")
            
            elif action.isdigit():
                # Edit specific player
                idx = int(action) - 1
                if 0 <= idx < len(self.players):
                    await self._edit_player(idx)
                else:
                    self.console.print(f"[red]Invalid player number. Enter 1-{len(self.players)}[/red]")
                    await asyncio.sleep(1)
            
            else:
                self.console.print("[red]Invalid option. Please try again.[/red]")
                await asyncio.sleep(1)
    
    async def _delete_player(self) -> None:
        """Delete a player from the list."""
        self.console.print("\n[cyan]Players:[/cyan]")
        for i, p in enumerate(self.players, 1):
            self.console.print(f"  {i}. {p.name} ({p.position.value})")
        
        try:
            idx = IntPrompt.ask("[cyan]Enter player number to delete[/cyan]") - 1
            if 0 <= idx < len(self.players):
                removed = self.players.pop(idx)
                self.dashboard.render_success(f"Removed {removed.name}")
            else:
                self.console.print("[red]Invalid player number.[/red]")
        except (ValueError, KeyboardInterrupt):
            pass
    
    async def _edit_player(self, idx: int) -> None:
        """Edit a specific player's data."""
        player = self.players[idx]
        self.console.print(f"\n[bold]Editing {player.name} ({player.position.value})[/bold]")
        self.console.print("\n[cyan]What would you like to edit?[/cyan]")
        self.console.print("  1. Stats (Sharp Data)")
        self.console.print("  2. Market Lines (Vegas)")
        self.console.print("  3. Both")
        self.console.print("  4. Cancel")
        
        choice = IntPrompt.ask("[cyan]Select option[/cyan]", default=4)
        
        try:
            if choice == 1 or choice == 3:
                # Re-enter stats
                if player.position == Position.QB:
                    player.stats = await self.input_handler._get_qb_stats()
                elif player.position == Position.RB:
                    player.stats = await self.input_handler._get_rb_stats()
                else:
                    player.stats = await self.input_handler._get_wr_te_stats()
            
            if choice == 2 or choice == 3:
                # Re-enter lines
                if player.position == Position.QB:
                    player.market_lines = await self.input_handler._get_qb_lines(player.name)
                elif player.position == Position.RB:
                    player.market_lines = await self.input_handler._get_rb_lines(player.name)
                else:
                    player.market_lines = await self.input_handler._get_wr_te_lines(
                        player.name, player.position
                    )
            
            if choice in (1, 2, 3):
                self.dashboard.render_success(f"Updated {player.name}")
                
        except ValidationError as e:
            self.console.print(f"[red]Validation Error: {e.errors()[0]['msg']}[/red]")
    
    async def _run_analysis(self) -> None:
        """Run the prediction and correlation analysis."""
        self.console.clear()
        self.dashboard.render_header()
        
        # Set game context for engine
        self.prediction_engine.set_game_context(self.game_context)
        
        # Generate projections
        self.dashboard.render_info("Running prediction engine...")
        self.console.print()
        
        self.projections = []
        for player in self.players:
            player_projections = await self.prediction_engine.generate_projections(player)
            self.projections.extend(player_projections)
        
        # Render game context
        self.dashboard.render_game_context(self.game_context)
        
        # Render projections table
        self.dashboard.render_projections_table(self.projections)
        
        # Find correlated parlays
        self.dashboard.render_info("Analyzing correlation opportunities...")
        self.console.print()
        
        correlation_engine = CorrelationEngine(self.game_context)
        parlays = correlation_engine.find_correlated_parlays(self.projections)
        
        # Render parlay recommendations
        if parlays:
            for parlay in parlays:
                self.dashboard.render_parlay_slip(parlay)
        else:
            self.dashboard.render_no_parlays()
        
        # Final summary
        self._render_summary(parlays)
        
        # Option to go back and edit
        self.console.print()
        if Confirm.ask("[cyan]Would you like to edit data and re-run analysis?[/cyan]", default=False):
            await self._review_edit_loop()
    
    def _render_summary(self, parlays: list[CorrelatedParlay]) -> None:
        """Render final analysis summary."""
        summary = Text()
        summary.append("Analysis Complete\n\n", style="bold green")
        summary.append(f"• Players Analyzed: {len(self.players)}\n", style="white")
        summary.append(f"• Total Projections: {len(self.projections)}\n", style="white")
        summary.append(f"• Correlated Parlays: {len(parlays)}\n", style="white")
        
        # Best individual play
        if self.projections:
            best = max(self.projections, key=lambda p: abs(p.edge))
            summary.append(f"\n🎯 Best Edge: ", style="cyan")
            summary.append(
                f"{best.player_name} {best.stat_type} {best.recommendation.value} "
                f"({best.edge:+.1f}%)\n",
                style="bold yellow"
            )
        
        self.console.print(Panel(
            summary,
            title="[bold]📊 Analysis Summary[/bold]",
            border_style="green"
        ))


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    """Application entry point."""
    app = NFLAnalyticsApp()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
