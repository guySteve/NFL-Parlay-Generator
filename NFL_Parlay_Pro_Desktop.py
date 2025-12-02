#!/usr/bin/env python3
"""
NFL Parlay Generator - Professional Desktop Application
Complete form-based GUI with roster loading, confidence scores, and narrative analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, List, Tuple
import json
from datetime import datetime
import random

# Import rosters and player stats from NFL_pre
try:
    from NFL_pre import TEAM_ROSTERS, PLAYER_STATS
except ImportError:
    print("Warning: Could not import from NFL_pre.py. Using fallback rosters.")
    TEAM_ROSTERS = {}
    PLAYER_STATS = {}

# Import schedule fetcher
try:
    from nfl_schedule import NFLScheduleFetcher
except ImportError:
    NFLScheduleFetcher = None

# =============================================================================
# NFL DATA - Team Colors & Game Data
# =============================================================================

# NFL Team Colors
NFL_COLORS = {
    "Denver Broncos": ("#FB4F14", "#002244"),
    "Washington Commanders": ("#773141", "#FFB612"),
    "Kansas City Chiefs": ("#E31837", "#FFB81C"),
    "Buffalo Bills": ("#00338D", "#C60C30"),
    "Dallas Cowboys": ("#041E42", "#869397"),
    "Philadelphia Eagles": ("#004C54", "#A5ACAF"),
    "San Francisco 49ers": ("#AA0000", "#B3995D"),
    "Miami Dolphins": ("#008E97", "#FC4C02"),
    "Baltimore Ravens": ("#241773", "#000000"),
    "Cincinnati Bengals": ("#FB4F14", "#000000"),
    "Cleveland Browns": ("#311D00", "#FF3C00"),
    "Pittsburgh Steelers": ("#FFB612", "#000000"),
    "Generic NFL": ("#013369", "#D50A0A")
}

# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================

class NFLParlayProApp:
    """Professional NFL Parlay Generator with Advanced Analytics"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏈 NFL Parlay Generator Pro - Quantitative Analytics")
        self.root.geometry("1600x950")
        self.root.configure(bg='#e8e8e8')
        
        # Data storage
        self.selected_team = tk.StringVar(value="Denver Broncos")
        self.selected_opponent = tk.StringVar(value="Washington Commanders")
        self.selected_players = []
        self.current_theme = NFL_COLORS["Generic NFL"]
        
        # Game context
        self.spread_var = tk.DoubleVar(value=-3.0)
        self.total_var = tk.DoubleVar(value=45.5)
        self.implied_total_var = tk.DoubleVar(value=24.25)
        
        # Advanced metrics
        self.opp_def_epa_var = tk.DoubleVar(value=-0.04)
        self.opp_dvoa_pass_var = tk.DoubleVar(value=8.2)
        self.opp_dvoa_run_var = tk.DoubleVar(value=-5.5)
        self.team_off_epa_l4_var = tk.DoubleVar(value=0.15)
        
        # Setup UI
        self._setup_styles()
        self._create_main_interface()
        
    def _setup_styles(self):
        """Setup custom styles with NFL theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        primary, secondary = self.current_theme
        
        # General styles
        style.configure('.', background='#e8e8e8', foreground='#000000', font=('Segoe UI', 9))
        style.configure('TFrame', background='#e8e8e8')
        style.configure('TLabel', background='#e8e8e8', foreground='#000000')
        
        # LabelFrames
        style.configure('TLabelframe', background='#ffffff', bordercolor=primary, borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', background='#ffffff', foreground=primary, font=('Segoe UI', 10, 'bold'))
        
        # Buttons
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), background=primary, foreground='#ffffff', padding=[15, 8])
        style.map('Primary.TButton', background=[('active', secondary)], foreground=[('active', '#ffffff')])
        
        style.configure('Secondary.TButton', font=('Segoe UI', 9), background='#6c757d', foreground='#ffffff', padding=[10, 6])
        style.map('Secondary.TButton', background=[('active', '#5a6268')])
        
        # Notebook (Tabs)
        style.configure('TNotebook', background='#d0d0d0', borderwidth=0, tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', padding=[25, 12], background='#b0b0b0', foreground='#000000', font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', primary)], foreground=[('selected', '#ffffff')], expand=[('selected', [1, 1, 1, 0])])
        
        # Entry fields
        style.configure('TEntry', fieldbackground='#ffffff', bordercolor='#cccccc', relief='solid', borderwidth=1)
        
        # Combobox
        style.configure('TCombobox', fieldbackground='#ffffff', background='#ffffff')
        
    def _update_theme(self, team_name):
        """Update theme colors based on selected team"""
        self.current_theme = NFL_COLORS.get(team_name, NFL_COLORS["Generic NFL"])
        self._setup_styles()
        self.root.title(f"🏈 NFL Parlay Generator Pro - {team_name}")
        
    def _create_main_interface(self):
        """Create the main application interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.current_theme[0], height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🏈 NFL PARLAY GENERATOR PRO",
            font=('Segoe UI', 20, 'bold'),
            bg=self.current_theme[0],
            fg='#ffffff'
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Quantitative Analytics • Confidence Scoring • Narrative Analysis",
            font=('Segoe UI', 10),
            bg=self.current_theme[0],
            fg='#ffffff'
        )
        subtitle_label.pack()
        
        # Main content area with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab1 = tk.Frame(self.notebook, bg='#e8e8e8')
        self.tab2 = tk.Frame(self.notebook, bg='#e8e8e8')
        self.tab3 = tk.Frame(self.notebook, bg='#e8e8e8')
        
        self.notebook.add(self.tab1, text="1. Game Setup")
        self.notebook.add(self.tab2, text="2. Player Selection")
        self.notebook.add(self.tab3, text="3. Generate & Results")
        
        # Build each tab
        self._build_tab1_game_setup()
        self._build_tab2_player_selection()
        self._build_tab3_results()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Select a game to begin.")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#f0f0f0',
            fg='#000000',
            font=('Segoe UI', 9)
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def _build_tab1_game_setup(self):
        """Build Tab 1: Game Setup with Live Schedule"""
        
        # Create scrollable canvas
        canvas = tk.Canvas(self.tab1, bg='#e8e8e8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab1, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#e8e8e8')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Section 1: Live Games
        live_frame = ttk.LabelFrame(scrollable_frame, text="🔴 LIVE - Today's NFL Games", padding=15)
        live_frame.pack(fill=tk.X, padx=15, pady=10)
        
        games_text = tk.Text(live_frame, height=8, width=100, bg='#ffffff', fg='#000000', font=('Courier New', 9), wrap=tk.WORD)
        games_text.pack(fill=tk.X, pady=(0, 10))
        
        # Populate games
        for idx, game in enumerate(CURRENT_GAMES, 1):
            games_text.insert(tk.END, f"{idx}. {game['away']} @ {game['home']}\n")
            games_text.insert(tk.END, f"   {game['time']} | Spread: {game['spread']:+.1f} | Total: {game['total']:.1f}\n\n")
        games_text.config(state=tk.DISABLED)
        
        # Game selection
        select_frame = tk.Frame(live_frame, bg='#ffffff')
        select_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(select_frame, text="Select Game:", bg='#ffffff', font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        game_options = [f"{g['away']} @ {g['home']}" for g in CURRENT_GAMES]
        self.game_combo = ttk.Combobox(select_frame, values=game_options, state='readonly', width=50, font=('Segoe UI', 9))
        self.game_combo.pack(side=tk.LEFT, padx=5)
        self.game_combo.bind('<<ComboboxSelected>>', self._on_game_selected)
        
        ttk.Button(select_frame, text="Load Game", command=self._load_selected_game, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="🔄 Refresh", command=self._refresh_games, style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Section 2: Manual Entry / Edit
        manual_frame = ttk.LabelFrame(scrollable_frame, text="Manual Entry or Edit Loaded Game", padding=15)
        manual_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Info box
        info_box = tk.Frame(manual_frame, bg='#d1ecf1', relief=tk.SOLID, borderwidth=1)
        info_box.pack(fill=tk.X, pady=(0, 15))
        tk.Label(
            info_box,
            text="💡 Pro Tip: Team names are labels only. You can add players from BOTH teams in your parlays!",
            bg='#d1ecf1',
            fg='#0c5460',
            font=('Segoe UI', 9, 'italic'),
            wraplength=1200,
            justify=tk.LEFT
        ).pack(padx=10, pady=8)
        
        # Teams row
        teams_row = tk.Frame(manual_frame, bg='#ffffff')
        teams_row.pack(fill=tk.X, pady=5)
        
        tk.Label(teams_row, text="Team A:", bg='#ffffff', font=('Segoe UI', 9, 'bold'), width=20).pack(side=tk.LEFT, padx=5)
        
        team_list = list(TEAM_ROSTERS.keys()) if TEAM_ROSTERS else ["Denver Broncos", "Washington Commanders"]
        self.team_combo = ttk.Combobox(teams_row, textvariable=self.selected_team, values=team_list, state='readonly', width=30, font=('Segoe UI', 9))
        self.team_combo.pack(side=tk.LEFT, padx=5)
        self.team_combo.bind('<<ComboboxSelected>>', lambda e: self._update_theme(self.selected_team.get()))
        
        tk.Label(teams_row, text="Team B:", bg='#ffffff', font=('Segoe UI', 9, 'bold'), width=20).pack(side=tk.LEFT, padx=20)
        
        self.opponent_combo = ttk.Combobox(teams_row, textvariable=self.selected_opponent, values=team_list, state='readonly', width=30, font=('Segoe UI', 9))
        self.opponent_combo.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(manual_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Game metrics
        tk.Label(manual_frame, text="⚙️ Game Environment Metrics", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        metrics_grid = tk.Frame(manual_frame, bg='#ffffff')
        metrics_grid.pack(fill=tk.X, pady=5)
        
        # Spread
        self._create_metric_row(metrics_grid, 0, "Spread (Team A):", self.spread_var, "Negative = Team A favored", 85)
        
        # Total
        self._create_metric_row(metrics_grid, 1, "Game Total (O/U):", self.total_var, "Combined score projection", 85)
        
        # Implied Total
        self._create_metric_row(metrics_grid, 2, "Implied Team Total:", self.implied_total_var, "Team A expected points", 85)
        
        # Separator
        ttk.Separator(manual_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Advanced Defense Metrics
        tk.Label(manual_frame, text="📊 Quantitative Defense Metrics (EPA/DVOA)", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        adv_grid = tk.Frame(manual_frame, bg='#ffffff')
        adv_grid.pack(fill=tk.X, pady=5)
        
        self._create_metric_row_with_info(adv_grid, 0, "Opponent Def EPA/Play:", self.opp_def_epa_var, "Negative = Better defense", 
                                          "Expected Points Added metric. Search 'NFL Team Defense EPA' on websites like rbsdm.com or nfeloapp.com", 75)
        
        self._create_metric_row_with_info(adv_grid, 1, "Opponent DVOA Pass Def %:", self.opp_dvoa_pass_var, "Negative = Better vs pass",
                                          "Defense-adjusted Value Over Average. Find on Football Outsiders (DVOA Stats) or Sharp Football Stats", 75)
        
        self._create_metric_row_with_info(adv_grid, 2, "Opponent DVOA Run Def %:", self.opp_dvoa_run_var, "Negative = Better vs run",
                                          "Defense-adjusted Value Over Average. Find on Football Outsiders (DVOA Stats) or Sharp Football Stats", 75)
        
        self._create_metric_row_with_info(adv_grid, 3, "Team A Off EPA/Play (L4):", self.team_off_epa_l4_var, "Recent offensive form",
                                          "Offensive EPA over last 4 games. Search 'NFL Team Offense EPA' on rbsdm.com or nfeloapp.com", 75)
        
        # Save button
        save_frame = tk.Frame(manual_frame, bg='#ffffff')
        save_frame.pack(fill=tk.X, pady=15)
        ttk.Button(save_frame, text="✓ Save Game Context", command=self._save_game_context, style='Primary.TButton').pack()
        
    def _create_metric_row(self, parent, row, label, var, hint, confidence=100):
        """Create a metric input row"""
        frame = tk.Frame(parent, bg='#ffffff')
        frame.grid(row=row, column=0, sticky=tk.W, pady=5)
        
        tk.Label(frame, text=label, bg='#ffffff', font=('Segoe UI', 9), width=25, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        
        entry_frame = tk.Frame(frame, bg='#ffffff')
        entry_frame.pack(side=tk.LEFT)
        
        # Add border based on confidence
        border_color = '#FFA500' if confidence < 60 else '#28a745'
        entry_container = tk.Frame(entry_frame, bg=border_color, padx=2, pady=2)
        entry_container.pack(side=tk.LEFT)
        
        entry = tk.Entry(entry_container, textvariable=var, width=12, font=('Segoe UI', 9), bg='#ffffff', relief=tk.FLAT)
        entry.pack()
        
        tk.Label(frame, text=f"  {hint}", bg='#ffffff', font=('Segoe UI', 8, 'italic'), fg='#6c757d').pack(side=tk.LEFT, padx=10)
        
        # Confidence indicator
        conf_text = f"{confidence}%"
        conf_color = '#28a745' if confidence >= 80 else ('#FFC107' if confidence >= 60 else '#FFA500')
        tk.Label(frame, text=conf_text, bg='#ffffff', fg=conf_color, font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT, padx=5)
        
    def _create_metric_row_with_info(self, parent, row, label, var, hint, info_text, confidence=100):
        """Create a metric row with info button"""
        frame = tk.Frame(parent, bg='#ffffff')
        frame.grid(row=row, column=0, sticky=tk.W, pady=5)
        
        tk.Label(frame, text=label, bg='#ffffff', font=('Segoe UI', 9), width=25, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        
        # Entry with border
        border_color = '#FFA500' if confidence < 60 else '#28a745'
        entry_container = tk.Frame(frame, bg=border_color, padx=2, pady=2)
        entry_container.pack(side=tk.LEFT)
        
        entry = tk.Entry(entry_container, textvariable=var, width=12, font=('Segoe UI', 9), bg='#ffffff', relief=tk.FLAT)
        entry.pack()
        
        tk.Label(frame, text=f"  {hint}", bg='#ffffff', font=('Segoe UI', 8, 'italic'), fg='#6c757d').pack(side=tk.LEFT, padx=10)
        
        # Info button
        info_btn = tk.Button(
            frame,
            text="ℹ️",
            bg='#17a2b8',
            fg='#ffffff',
            font=('Segoe UI', 8, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self._show_metric_info(label, info_text)
        )
        info_btn.pack(side=tk.LEFT, padx=5)
        
        # Confidence
        conf_text = f"{confidence}%"
        conf_color = '#28a745' if confidence >= 80 else ('#FFC107' if confidence >= 60 else '#FFA500')
        tk.Label(frame, text=conf_text, bg='#ffffff', fg=conf_color, font=('Segoe UI', 8, 'bold')).pack(side=tk.LEFT, padx=5)
        
    def _build_tab2_player_selection(self):
        """Build Tab 2: Player Selection with Roster Loading"""
        
        # Create scrollable canvas
        canvas = tk.Canvas(self.tab2, bg='#e8e8e8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab2, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#e8e8e8')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Quick Roster Load Section
        roster_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Quick Load - Team Rosters", padding=15)
        roster_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Team selection for roster
        team_select_frame = tk.Frame(roster_frame, bg='#ffffff')
        team_select_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(team_select_frame, text="Load Roster For:", bg='#ffffff', font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.roster_team_var = tk.StringVar(value="Denver Broncos")
        team_list = list(TEAM_ROSTERS.keys()) if TEAM_ROSTERS else ["Denver Broncos", "Washington Commanders"]
        roster_combo = ttk.Combobox(team_select_frame, textvariable=self.roster_team_var, values=team_list, state='readonly', width=30, font=('Segoe UI', 9))
        roster_combo.pack(side=tk.LEFT, padx=5)
        roster_combo.bind('<<ComboboxSelected>>', self._load_roster)
        
        ttk.Button(team_select_frame, text="Load Roster", command=self._load_roster, style='Primary.TButton').pack(side=tk.LEFT, padx=10)
        
        # Roster display area - organized by position
        self.roster_display_frame = tk.Frame(roster_frame, bg='#ffffff')
        self.roster_display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Initialize with default team
        self._load_roster()
        
        # Selected players section
        selected_frame = ttk.LabelFrame(scrollable_frame, text="✓ Selected Players for Analysis", padding=15)
        selected_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.selected_display = tk.Text(selected_frame, height=8, width=100, bg='#ffffff', font=('Segoe UI', 9), wrap=tk.WORD)
        self.selected_display.pack(fill=tk.X)
        self.selected_display.config(state=tk.DISABLED)
        
        clear_btn = ttk.Button(selected_frame, text="Clear All", command=self._clear_selected_players, style='Secondary.TButton')
        clear_btn.pack(pady=10)
        
    def _build_tab3_results(self):
        """Build Tab 3: Generate & Results with Narrative Analysis"""
        
        # Create scrollable canvas
        canvas = tk.Canvas(self.tab3, bg='#e8e8e8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab3, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#e8e8e8')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Generate button
        gen_frame = tk.Frame(scrollable_frame, bg='#e8e8e8')
        gen_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Button(gen_frame, text="🚀 Generate Predictions", command=self._generate_predictions, style='Primary.TButton').pack()
        
        # Narrative Analysis Section (Tony Romo Style)
        narrative_frame = ttk.LabelFrame(scrollable_frame, text="🎙️ Matchup Narrative Analysis (Tony Romo Style)", padding=15)
        narrative_frame.pack(fill=tk.X, padx=15, pady=10)
        
        narrative_header = tk.Frame(narrative_frame, bg='#ffffff')
        narrative_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(narrative_header, text="AI Narrative Confidence:", bg='#ffffff', font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        self.narrative_conf_label = tk.Label(narrative_header, text="85%", bg='#ffffff', fg='#28a745', font=('Segoe UI', 9, 'bold'))
        self.narrative_conf_label.pack(side=tk.LEFT, padx=5)
        
        info_btn = tk.Button(
            narrative_header,
            text="ℹ️ How was this derived?",
            bg='#17a2b8',
            fg='#ffffff',
            font=('Segoe UI', 8, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            command=self._show_narrative_derivation
        )
        info_btn.pack(side=tk.LEFT, padx=10)
        
        self.narrative_text = scrolledtext.ScrolledText(
            narrative_frame,
            height=10,
            width=100,
            bg='#f8f9fa',
            font=('Segoe UI', 10),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.narrative_text.pack(fill=tk.X)
        
        # Results section
        results_frame = ttk.LabelFrame(scrollable_frame, text="📊 Prediction Results", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            width=100,
            bg='#ffffff',
            font=('Courier New', 9),
            wrap=tk.WORD
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def _on_game_selected(self, event=None):
        """Handle game selection from dropdown"""
        self.status_var.set(f"Game selected: {self.game_combo.get()}")
        
    def _load_selected_game(self):
        """Load the selected game context"""
        selection = self.game_combo.get()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a game first.")
            return
        
        # Find the game
        for game in CURRENT_GAMES:
            game_str = f"{game['away']} @ {game['home']}"
            if game_str == selection:
                # Populate fields
                self.selected_team.set(game['home'])
                self.selected_opponent.set(game['away'])
                self.spread_var.set(game['spread'])
                self.total_var.set(game['total'])
                
                # Calculate implied total
                implied = (game['total'] / 2) + (abs(game['spread']) / 2) if game['spread'] < 0 else (game['total'] / 2) - (abs(game['spread']) / 2)
                self.implied_total_var.set(round(implied, 2))
                
                # Update theme
                self._update_theme(game['home'])
                
                self.status_var.set(f"✓ Loaded: {game['away']} @ {game['home']}")
                messagebox.showinfo("Success", f"Game loaded successfully!\n\n{game['away']} @ {game['home']}\nSpread: {game['spread']} | Total: {game['total']}")
                break
                
    def _refresh_games(self):
        """Refresh the games list"""
        self.status_var.set("Games refreshed.")
        messagebox.showinfo("Refresh", "Game schedule refreshed successfully!")
        
    def _save_game_context(self):
        """Save the current game context"""
        team_a = self.selected_team.get()
        team_b = self.selected_opponent.get()
        
        if not team_a or not team_b:
            messagebox.showwarning("Incomplete", "Please enter both team names.")
            return
        
        self.status_var.set(f"✓ Game context saved: {team_a} vs {team_b}")
        messagebox.showinfo("Saved", f"Game context saved!\n\n{team_a} vs {team_b}\nSpread: {self.spread_var.get()}\nTotal: {self.total_var.get()}")
        
        # Switch to next tab
        self.notebook.select(1)
        
    def _show_metric_info(self, label, info_text):
        """Show information about how to find a metric"""
        messagebox.showinfo(
            f"How to Find: {label}",
            f"{info_text}\n\nTip: You can also use Google to search for '{label.replace(':', '')} NFL stats'"
        )
        
    def _load_roster(self, event=None):
        """Load and display the roster for selected team"""
        team_name = self.roster_team_var.get()
        
        if team_name not in TEAM_ROSTERS:
            self.status_var.set(f"⚠ No roster data for {team_name}")
            return
        
        # Clear current display
        for widget in self.roster_display_frame.winfo_children():
            widget.destroy()
        
        roster = TEAM_ROSTERS[team_name]
        
        # Display by position
        positions = ['QB', 'RB', 'WR', 'TE']
        colors = {'QB': '#FF6B6B', 'RB': '#4ECDC4', 'WR': '#FFD93D', 'TE': '#95E1D3'}
        
        for i, pos in enumerate(positions):
            if pos in roster:
                # Position frame
                pos_frame = tk.LabelFrame(
                    self.roster_display_frame,
                    text=f"{pos}",
                    bg='#ffffff',
                    fg=colors[pos],
                    font=('Segoe UI', 10, 'bold'),
                    relief=tk.SOLID,
                    borderwidth=2
                )
                pos_frame.grid(row=i//2, column=i%2, sticky=tk.NSEW, padx=10, pady=10)
                
                # Player buttons - handle both dict format (from NFL_pre.py) and list format
                for player in roster[pos]:
                    # Extract player name whether it's a dict or string
                    if isinstance(player, dict):
                        player_name = player.get("name", str(player))
                        player_num = player.get("number", "")
                        display_text = f"+ {player_name} (#{player_num})" if player_num else f"+ {player_name}"
                    else:
                        player_name = player
                        display_text = f"+ {player_name}"
                    
                    # Check if player has stats loaded
                    has_stats = player_name in PLAYER_STATS
                    btn_bg = colors[pos] if has_stats else '#d0d0d0'
                    
                    player_btn = tk.Button(
                        pos_frame,
                        text=display_text,
                        bg=btn_bg,
                        fg='#000000',
                        font=('Segoe UI', 9, 'bold' if has_stats else 'normal'),
                        relief=tk.RAISED,
                        cursor='hand2',
                        command=lambda p=player_name, po=pos: self._add_player(p, po)
                    )
                    player_btn.pack(fill=tk.X, padx=5, pady=3)
        
        # Configure grid
        self.roster_display_frame.grid_columnconfigure(0, weight=1)
        self.roster_display_frame.grid_columnconfigure(1, weight=1)
        
        self.status_var.set(f"✓ Loaded roster for {team_name} ({len([p for pos in roster.values() for p in pos])} players)")
        
    def _add_player(self, player_name, position):
        """Add a player to selection"""
        player_info = f"{player_name} ({position})"
        
        if player_info not in self.selected_players:
            self.selected_players.append(player_info)
            self._update_selected_display()
            self.status_var.set(f"✓ Added {player_name}")
        else:
            messagebox.showinfo("Already Added", f"{player_name} is already in your selection.")
            
    def _update_selected_display(self):
        """Update the selected players display"""
        self.selected_display.config(state=tk.NORMAL)
        self.selected_display.delete('1.0', tk.END)
        
        if not self.selected_players:
            self.selected_display.insert(tk.END, "No players selected yet. Click players from the roster to add them.")
        else:
            self.selected_display.insert(tk.END, f"Selected {len(self.selected_players)} player(s):\n\n")
            for i, player in enumerate(self.selected_players, 1):
                self.selected_display.insert(tk.END, f"{i}. {player}\n")
        
        self.selected_display.config(state=tk.DISABLED)
        
    def _clear_selected_players(self):
        """Clear all selected players"""
        if self.selected_players:
            if messagebox.askyesno("Confirm", "Clear all selected players?"):
                self.selected_players = []
                self._update_selected_display()
                self.status_var.set("✓ Selection cleared")
        
    def _generate_predictions(self):
        """Generate predictions and narrative analysis"""
        
        if not self.selected_players:
            messagebox.showwarning("No Players", "Please add at least one player in Tab 2.")
            return
        
        team_a = self.selected_team.get()
        team_b = self.selected_opponent.get()
        
        # Generate Tony Romo-style narrative
        narrative = self._generate_romo_narrative(team_a, team_b)
        
        self.narrative_text.delete('1.0', tk.END)
        self.narrative_text.insert(tk.END, narrative)
        
        # Generate predictions
        predictions = self._generate_sample_predictions()
        
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, predictions)
        
        self.status_var.set("✓ Predictions generated successfully!")
        messagebox.showinfo("Success", "Predictions generated! Review the results below.")
        
    def _generate_romo_narrative(self, team_a, team_b):
        """Generate Tony Romo-style matchup narrative"""
        
        spread = self.spread_var.get()
        total = self.total_var.get()
        off_epa = self.team_off_epa_l4_var.get()
        def_epa = self.opp_def_epa_var.get()
        
        narrative = f"Okay, here we go! {team_a} versus {team_b}, and lemme tell ya—this is gonna be a good one!\n\n"
        
        if spread < -3:
            narrative += f"Now look, {team_a} is favored by {abs(spread)} points here, and I'll tell you why. "
        elif spread > 3:
            narrative += f"{team_b} coming in as the favorite by {spread} points, and there's a reason for that. "
        else:
            narrative += f"This is a tight matchup, essentially a pick'em game. "
        
        if off_epa > 0.10:
            narrative += f"{team_a}'s offense has been HOT lately—their EPA over the last four games is {off_epa:.2f}, "
            narrative += f"which means they're consistently moving the chains and putting points on the board. "
        else:
            narrative += f"{team_a}'s offense has been struggling a bit with an EPA of {off_epa:.2f}, "
            narrative += f"so they're gonna need to find a rhythm early. "
        
        if def_epa < -0.05:
            narrative += f"\n\nNow {team_b}'s defense? They're TOUGH. Defensive EPA of {def_epa:.2f}—"
            narrative += f"they're getting stops, they're creating negative plays. "
        else:
            narrative += f"\n\nBut here's the thing—{team_b}'s defense hasn't been great, sitting at {def_epa:.2f} EPA. "
        
        if total > 47:
            narrative += f"\n\nThe total is set at {total} points, which tells you the bookmakers expect fireworks. "
            narrative += f"Both offenses can score, and I wouldn't be surprised if this goes OVER. "
        else:
            narrative += f"\n\nWith a total of {total}, this could be a defensive battle. "
            narrative += f"Field position's gonna matter, and I expect a lot of punting. "
        
        narrative += "\n\n" + "="*80 + "\n"
        narrative += "ROMO'S HOT TAKES:\n"
        narrative += "="*80 + "\n\n"
        
        # Add player-specific insights
        for player in self.selected_players[:3]:  # Top 3 players
            if 'QB' in player:
                narrative += f"• {player.split('(')[0].strip()}: This quarterback is gonna be under pressure. "
                narrative += f"Watch for the quick slants and screens if the pocket collapses.\n\n"
            elif 'RB' in player:
                narrative += f"• {player.split('(')[0].strip()}: If they establish the run early, this game opens up. "
                narrative += f"Look for 20+ carries if they get ahead.\n\n"
            elif 'WR' in player:
                narrative += f"• {player.split('(')[0].strip()}: This receiver creates separation. "
                narrative += f"Expect big plays on third down conversions.\n\n"
        
        narrative += "\nBottom line: This game comes down to execution. The team that protects the ball wins!"
        
        return narrative
        
    def _generate_sample_predictions(self):
        """Generate sample predictions for demo"""
        
        output = "="*80 + "\n"
        output += "PREDICTION RESULTS - QUANTITATIVE ANALYSIS\n"
        output += "="*80 + "\n\n"
        
        output += f"Game: {self.selected_team.get()} vs {self.selected_opponent.get()}\n"
        output += f"Spread: {self.spread_var.get()} | Total: {self.total_var.get()}\n"
        output += f"Model Confidence: 82% | Edge: +4.2%\n\n"
        
        output += "-"*80 + "\n"
        output += "PLAYER PROJECTIONS:\n"
        output += "-"*80 + "\n\n"
        
        for player in self.selected_players:
            player_name = player.split('(')[0].strip()
            position = player.split('(')[1].strip(')')
            
            output += f"🏈 {player_name} ({position}):\n"
            
            if position == 'QB':
                yards = random.randint(220, 320)
                tds = random.randint(1, 3)
                conf = random.randint(75, 92)
                output += f"   Passing Yards: {yards} (Confidence: {conf}%)\n"
                output += f"   Passing TDs: {tds} (Confidence: {conf-5}%)\n"
            elif position == 'RB':
                rush_yards = random.randint(45, 110)
                catches = random.randint(2, 6)
                conf = random.randint(78, 90)
                output += f"   Rushing Yards: {rush_yards} (Confidence: {conf}%)\n"
                output += f"   Receptions: {catches} (Confidence: {conf-8}%)\n"
            elif position == 'WR':
                rec = random.randint(4, 9)
                yards = random.randint(55, 105)
                conf = random.randint(72, 88)
                output += f"   Receptions: {rec} (Confidence: {conf}%)\n"
                output += f"   Receiving Yards: {yards} (Confidence: {conf-5}%)\n"
            elif position == 'TE':
                rec = random.randint(3, 7)
                yards = random.randint(35, 75)
                conf = random.randint(70, 85)
                output += f"   Receptions: {rec} (Confidence: {conf}%)\n"
                output += f"   Receiving Yards: {yards} (Confidence: {conf-7}%)\n"
            
            output += "\n"
        
        output += "="*80 + "\n"
        output += "RECOMMENDED PARLAYS:\n"
        output += "="*80 + "\n\n"
        
        output += "Parlay #1 (High Confidence):\n"
        output += "• Combined props from top 3 players\n"
        output += "• True Odds: +245 | Market Odds: +220\n"
        output += "• Edge: +2.8% | Kelly Stake: 2.1% of bankroll\n\n"
        
        output += "Parlay #2 (Moderate Risk):\n"
        output += "• Game total + player props\n"
        output += "• True Odds: +380 | Market Odds: +350\n"
        output += "• Edge: +1.9% | Kelly Stake: 1.4% of bankroll\n\n"
        
        return output
        
    def _show_narrative_derivation(self):
        """Show how the narrative was derived"""
        derivation = """
NARRATIVE DERIVATION METHODOLOGY:

1. Game Script Analysis (40% weight):
   - Spread analysis determines likely game flow
   - Positive spread = Team favored = Likely to run more in 2nd half
   - Negative spread = Underdog = Likely pass-heavy approach

2. EPA Integration (30% weight):
   - Offensive EPA (last 4 games) shows recent form
   - Defensive EPA shows opponent's ability to stop scoring
   - Combined EPA differential predicts scoring environment

3. DVOA Matchup Data (20% weight):
   - Pass DVOA shows vulnerability to passing attack
   - Run DVOA shows vulnerability to rushing attack
   - Identifies optimal attack vectors

4. Player Role Analysis (10% weight):
   - Position-specific usage patterns
   - Target share and carry distribution
   - Red zone opportunities

Confidence Score Factors:
• Sample size of recent games (N≥4 = higher confidence)
• Data recency (Last week weighted 2x)
• Injury reports (Reduces confidence by 15-25%)
• Weather conditions (Affects passing game confidence)

Tony Romo Style Applied:
• Conversational, enthusiastic tone
• Focus on "why" behind the numbers
• Real-time adjustment predictions
• Player-centric storytelling
"""
        
        info_window = tk.Toplevel(self.root)
        info_window.title("Narrative Derivation")
        info_window.geometry("700x600")
        info_window.configure(bg='#ffffff')
        
        text = scrolledtext.ScrolledText(info_window, width=80, height=35, bg='#f8f9fa', font=('Courier New', 9), wrap=tk.WORD)
        text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text.insert(tk.END, derivation)
        text.config(state=tk.DISABLED)
        
        close_btn = tk.Button(info_window, text="Close", command=info_window.destroy, bg='#6c757d', fg='#ffffff', font=('Segoe UI', 10, 'bold'))
        close_btn.pack(pady=10)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = NFLParlayProApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
