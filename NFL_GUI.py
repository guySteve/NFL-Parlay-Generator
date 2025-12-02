#!/usr/bin/env python3
"""
NFL Parlay Generator - Desktop GUI Application

A tkinter-based graphical interface for the NFL prediction engine.
Provides form-based input, tabbed navigation, and visual results display.

Author: NFL Analytics Team
Version: 1.0.0
Python: 3.12+
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
from typing import Optional
from NFL_pre import (
    Position, GameContext, QBStats, RBStats, WRTEStats, MarketLines,
    PlayerData, PredictionEngine, CorrelationEngine, Projection,
    CorrelatedParlay, TEAM_ROSTERS, PLAYER_STATS, DEFAULT_GAME_CONTEXTS
)
from nfl_schedule import NFLScheduleFetcher


class NFLParlayGUI:
    """Main GUI application for NFL Parlay Generator."""
    
    # NFL Team Colors (Primary, Secondary)
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
        "default": ("#013369", "#D50A0A")  # Generic NFL colors
    }
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("🏈 NFL Parlay Generator - Quantitative Analytics")
        self.root.geometry("1400x900")
        
        # Data storage
        self.game_context: Optional[GameContext] = None
        self.players: list[PlayerData] = []
        self.projections: list[Projection] = []
        self.current_team_colors = self.NFL_COLORS["default"]
        
        # Prediction engine
        self.prediction_engine = PredictionEngine()
        
        # Schedule fetcher
        self.schedule_fetcher = NFLScheduleFetcher()
        self.current_games: list[dict] = []
        
        # Setup UI
        self._setup_styles()
        self._create_widgets()
        
        # Load today's games on startup
        self._load_live_schedule()
        
    def _setup_styles(self):
        """Setup ttk styles with NFL theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Get current team colors
        primary, secondary = self.current_team_colors
        
        # Main theme colors
        style.configure('.', background='#f5f5f5', foreground='#000000')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabelframe', background='#ffffff', bordercolor=primary, borderwidth=2)
        style.configure('TLabelframe.Label', background='#ffffff', foreground=primary, font=('Arial', 10, 'bold'))
        
        # Notebook (tabs)
        style.configure('TNotebook', background='#e0e0e0', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       padding=[20, 10], 
                       background='#d0d0d0',
                       foreground='#000000',
                       font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', primary)],
                 foreground=[('selected', '#ffffff')])
        
        # Labels
        style.configure('Header.TLabel', font=('Arial', 16, 'bold'), foreground=primary, background='#f5f5f5')
        style.configure('Subheader.TLabel', font=('Arial', 12, 'bold'), foreground=secondary, background='#ffffff')
        style.configure('Success.TLabel', foreground='#28a745', font=('Arial', 10, 'bold'), background='#f5f5f5')
        style.configure('Warning.TLabel', foreground='#fd7e14', font=('Arial', 10, 'bold'), background='#f5f5f5')
        style.configure('Error.TLabel', foreground='#dc3545', font=('Arial', 10, 'bold'), background='#f5f5f5')
        style.configure('Confidence.TLabel', font=('Arial', 9, 'italic'), background='#ffffff')
        
        # Buttons
        style.configure('Primary.TButton', 
                       font=('Arial', 10, 'bold'),
                       background=primary,
                       foreground='#ffffff',
                       borderwidth=0,
                       padding=[20, 10])
        style.map('Primary.TButton',
                 background=[('active', secondary)])
        
        # Entry fields
        style.configure('TEntry', fieldbackground='#ffffff', bordercolor=primary, borderwidth=1)
        
        # Combobox
        style.configure('TCombobox', fieldbackground='#ffffff', bordercolor=primary)
    
    def _update_theme(self, team_name: str):
        """Update the GUI theme based on selected team."""
        self.current_team_colors = self.NFL_COLORS.get(team_name, self.NFL_COLORS["default"])
        self._setup_styles()
        self.root.title(f"🏈 NFL Parlay Generator - {team_name}")
        self.status_var.set(f"Theme updated for {team_name}")
        
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(
            main_container,
            text="🏈 NFL PARLAY GENERATOR",
            style='Header.TLabel'
        )
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Tab 1: Game Setup
        self.game_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.game_tab, text="1. Game Setup")
        self._create_game_tab()
        
        # Tab 2: Players
        self.players_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.players_tab, text="2. Add Players")
        self._create_players_tab()
        
        # Tab 3: Review & Generate
        self.review_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.review_tab, text="3. Review & Generate")
        self._create_review_tab()
        
        # Tab 4: Results
        self.results_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.results_tab, text="4. Results")
        self._create_results_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Start by setting up game context in Tab 1.")
        status_bar = ttk.Label(main_container, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
    def _create_game_tab(self):
        """Create the game setup tab."""
        # Quick Load Section - Live Games
        quick_frame = ttk.LabelFrame(self.game_tab, text="🔴 LIVE - Today's NFL Games", padding="10")
        quick_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Game selection area
        games_container = ttk.Frame(quick_frame)
        games_container.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.games_display = tk.Text(games_container, height=6, width=60, wrap=tk.WORD)
        self.games_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.games_display.config(state=tk.DISABLED)
        
        games_scroll = ttk.Scrollbar(games_container, command=self.games_display.yview)
        games_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.games_display['yscrollcommand'] = games_scroll.set
        
        # Game selection dropdown
        ttk.Label(quick_frame, text="Select Game:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.game_select_var = tk.StringVar()
        self.game_select_combo = ttk.Combobox(
            quick_frame,
            textvariable=self.game_select_var,
            state='readonly',
            width=50
        )
        self.game_select_combo.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(quick_frame)
        btn_frame.grid(row=3, column=0, pady=5)
        
        ttk.Button(
            btn_frame,
            text="🔄 Refresh Games",
            command=self._load_live_schedule
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Load Selected Game",
            command=self._load_selected_game
        ).pack(side=tk.LEFT, padx=2)
        
        # Manual Entry Section
        manual_frame = ttk.LabelFrame(self.game_tab, text="Manual Entry (or edit loaded game)", padding="10")
        manual_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Info label
        info_label = ttk.Label(
            manual_frame, 
            text="💡 Team names are just labels - you can add players from either team!",
            font=('Arial', 8, 'italic'),
            foreground='blue'
        )
        info_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Team field
        ttk.Label(manual_frame, text="Team A:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.team_var = tk.StringVar(value="Denver Broncos")
        ttk.Entry(manual_frame, textvariable=self.team_var, width=30).grid(row=1, column=1, pady=2)
        
        # Opponent field
        ttk.Label(manual_frame, text="Team B:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.opponent_var = tk.StringVar(value="Washington Commanders")
        ttk.Entry(manual_frame, textvariable=self.opponent_var, width=30).grid(row=2, column=1, pady=2)
        
        # Separator
        ttk.Separator(manual_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Section label
        ttk.Label(manual_frame, text="Game Environment Metrics", font=('Arial', 9, 'bold')).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 5))
        
        # Spread field
        ttk.Label(manual_frame, text="Spread (Team A):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.spread_var = tk.DoubleVar(value=-3.0)
        ttk.Entry(manual_frame, textvariable=self.spread_var, width=15).grid(row=5, column=1, pady=2, sticky=tk.W)
        
        # Total field
        ttk.Label(manual_frame, text="Game Total (O/U):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.total_var = tk.DoubleVar(value=45.5)
        ttk.Entry(manual_frame, textvariable=self.total_var, width=15).grid(row=6, column=1, pady=2, sticky=tk.W)
        
        # Implied Total field
        ttk.Label(manual_frame, text="Implied Team Total:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.implied_var = tk.DoubleVar(value=21.25)
        ttk.Entry(manual_frame, textvariable=self.implied_var, width=15).grid(row=7, column=1, pady=2, sticky=tk.W)
        
        # Separator
        ttk.Separator(manual_frame, orient='horizontal').grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Section label - Advanced Metrics
        metrics_label = ttk.Label(manual_frame, text="⚙️ Quantitative Defense Metrics (EPA/DVOA)", font=('Arial', 9, 'bold'))
        metrics_label.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(5, 5))
        
        # 1. Opponent Defensive EPA
        ttk.Label(manual_frame, text="Opponent Def EPA/Play:").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.opp_def_epa_var = tk.DoubleVar(value=-0.04)
        epa_entry = ttk.Entry(manual_frame, textvariable=self.opp_def_epa_var, width=15)
        epa_entry.grid(row=10, column=1, pady=2, sticky=tk.W)
        ttk.Label(manual_frame, text="(Negative = better defense)", font=('Arial', 7, 'italic'), foreground='gray').grid(row=10, column=1, sticky=tk.E, padx=(0, 5))
        
        # 2. Opponent DVOA Pass Defense
        ttk.Label(manual_frame, text="Opponent DVOA Pass Def %:").grid(row=11, column=0, sticky=tk.W, pady=2)
        self.opp_dvoa_pass_var = tk.DoubleVar(value=8.2)
        dvoa_pass_entry = ttk.Entry(manual_frame, textvariable=self.opp_dvoa_pass_var, width=15)
        dvoa_pass_entry.grid(row=11, column=1, pady=2, sticky=tk.W)
        ttk.Label(manual_frame, text="(Negative = better vs pass)", font=('Arial', 7, 'italic'), foreground='gray').grid(row=11, column=1, sticky=tk.E, padx=(0, 5))
        
        # 3. Opponent DVOA Run Defense
        ttk.Label(manual_frame, text="Opponent DVOA Run Def %:").grid(row=12, column=0, sticky=tk.W, pady=2)
        self.opp_dvoa_run_var = tk.DoubleVar(value=-5.5)
        dvoa_run_entry = ttk.Entry(manual_frame, textvariable=self.opp_dvoa_run_var, width=15)
        dvoa_run_entry.grid(row=12, column=1, pady=2, sticky=tk.W)
        ttk.Label(manual_frame, text="(Negative = better vs run)", font=('Arial', 7, 'italic'), foreground='gray').grid(row=12, column=1, sticky=tk.E, padx=(0, 5))
        
        # 4. Team A Offensive EPA (Recent Form)
        ttk.Label(manual_frame, text="Team A Off EPA/Play (L4):").grid(row=13, column=0, sticky=tk.W, pady=2)
        self.team_off_epa_l4_var = tk.DoubleVar(value=0.15)
        off_epa_entry = ttk.Entry(manual_frame, textvariable=self.team_off_epa_l4_var, width=15)
        off_epa_entry.grid(row=13, column=1, pady=2, sticky=tk.W)
        ttk.Label(manual_frame, text="(Last 4 games avg)", font=('Arial', 7, 'italic'), foreground='gray').grid(row=13, column=1, sticky=tk.E, padx=(0, 5))
        
        # Save button
        save_btn = ttk.Button(
            manual_frame,
            text="Save Game Context",
            command=self._save_game_context
        )
        save_btn.grid(row=14, column=0, columnspan=2, pady=10)
        
        # Status label
        self.game_status_var = tk.StringVar(value="")
        ttk.Label(manual_frame, textvariable=self.game_status_var, style='Success.TLabel').grid(
            row=15, column=0, columnspan=2
        )
        
    def _create_players_tab(self):
        """Create the players tab."""
        # Info label at top
        info_label = ttk.Label(
            self.players_tab,
            text="💡 Add players from ANY team in the game - QB from Team A, WR from Team B, etc.",
            font=('Arial', 9, 'bold'),
            foreground='blue'
        )
        info_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Roster selection
        roster_frame = ttk.LabelFrame(self.players_tab, text="Select from Any Team Roster", padding="10")
        roster_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(roster_frame, text="Team:").grid(row=0, column=0, sticky=tk.W)
        self.roster_team_var = tk.StringVar(value="Denver Broncos")
        team_combo = ttk.Combobox(
            roster_frame,
            textvariable=self.roster_team_var,
            values=list(TEAM_ROSTERS.keys()),
            state='readonly',
            width=25
        )
        team_combo.grid(row=0, column=1, padx=5)
        team_combo.bind('<<ComboboxSelected>>', self._update_roster_players)
        
        ttk.Label(roster_frame, text="Player:").grid(row=1, column=0, sticky=tk.W)
        self.roster_player_var = tk.StringVar()
        self.player_combo = ttk.Combobox(
            roster_frame,
            textvariable=self.roster_player_var,
            state='readonly',
            width=25
        )
        self.player_combo.grid(row=1, column=1, padx=5)
        
        add_roster_btn = ttk.Button(
            roster_frame,
            text="Add Selected Player",
            command=self._add_from_roster
        )
        add_roster_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Update roster initially
        self._update_roster_players()
        
        # Manual add section
        manual_frame = ttk.LabelFrame(self.players_tab, text="Manual Player Entry", padding="10")
        manual_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(manual_frame, text="Player Name:").grid(row=0, column=0, sticky=tk.W)
        self.manual_name_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.manual_name_var, width=30).grid(row=0, column=1)
        
        ttk.Label(manual_frame, text="Position:").grid(row=1, column=0, sticky=tk.W)
        self.manual_pos_var = tk.StringVar(value="QB")
        ttk.Combobox(
            manual_frame,
            textvariable=self.manual_pos_var,
            values=['QB', 'RB', 'WR', 'TE'],
            state='readonly',
            width=10
        ).grid(row=1, column=1, sticky=tk.W)
        
        add_manual_btn = ttk.Button(
            manual_frame,
            text="Add Player & Enter Stats",
            command=self._add_manual_player
        )
        add_manual_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Current players list
        list_frame = ttk.LabelFrame(self.players_tab, text="Current Players (Can be from different teams!)", padding="10")
        list_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Listbox with scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.players_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, height=10)
        self.players_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.players_listbox.yview)
        
        # Buttons for list management
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Edit Selected", command=self._edit_selected_player).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Selected", command=self._delete_selected_player).pack(side=tk.LEFT, padx=2)
        
        self.players_tab.rowconfigure(3, weight=1)
        self.players_tab.columnconfigure(0, weight=1)
        
    def _create_review_tab(self):
        """Create the review & generate tab."""
        # Review display
        review_frame = ttk.LabelFrame(self.review_tab, text="Data Summary", padding="10")
        review_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.review_text = scrolledtext.ScrolledText(review_frame, width=80, height=25, wrap=tk.WORD)
        self.review_text.pack(fill=tk.BOTH, expand=True)
        
        # Generate button
        gen_frame = ttk.Frame(self.review_tab)
        gen_frame.grid(row=1, column=0, pady=10)
        
        self.generate_btn = ttk.Button(
            gen_frame,
            text="🚀 GENERATE PROJECTIONS",
            command=self._generate_projections
        )
        self.generate_btn.pack()
        
        self.review_tab.rowconfigure(0, weight=1)
        self.review_tab.columnconfigure(0, weight=1)
        
    def _create_results_tab(self):
        """Create the results tab."""
        # Results display
        results_frame = ttk.LabelFrame(self.results_tab, text="Projections & Parlays", padding="10")
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=80, height=30, wrap=tk.WORD, font=('Courier', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colored output
        self.results_text.tag_config('header', font=('Courier', 12, 'bold'), foreground='#00aaff')
        self.results_text.tag_config('success', foreground='#00ff00')
        self.results_text.tag_config('warning', foreground='#ffaa00')
        self.results_text.tag_config('error', foreground='#ff0000')
        self.results_text.tag_config('bold', font=('Courier', 10, 'bold'))
        
        self.results_tab.rowconfigure(0, weight=1)
        self.results_tab.columnconfigure(0, weight=1)
        
    def _load_default_game(self):
        """Load default Broncos @ Commanders game."""
        game_data = DEFAULT_GAME_CONTEXTS["Broncos @ Commanders"]
        
        # Ask which team
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Team")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Which team are you analyzing?", font=('Arial', 10, 'bold')).pack(pady=10)
        
        choice_var = tk.StringVar(value="Broncos")
        
        ttk.Radiobutton(dialog, text="Denver Broncos", variable=choice_var, value="Broncos").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(dialog, text="Washington Commanders", variable=choice_var, value="Commanders").pack(anchor=tk.W, padx=20)
        
        def apply_choice():
            team = choice_var.get()
            if team == "Broncos":
                self.team_var.set("Denver Broncos")
                self.opponent_var.set("Washington Commanders")
                self.spread_var.set(3.0)  # Underdogs
                self.implied_var.set(game_data['broncos_implied'])
                self.def_rank_var.set(game_data['commanders_def_rank'])
            else:
                self.team_var.set("Washington Commanders")
                self.opponent_var.set("Denver Broncos")
                self.spread_var.set(-3.0)  # Favorites
                self.implied_var.set(game_data['commanders_implied'])
                self.def_rank_var.set(game_data['broncos_def_rank'])
            
            self.total_var.set(game_data['total'])
            
            dialog.destroy()
            self._save_game_context()
        
        ttk.Button(dialog, text="Apply", command=apply_choice).pack(pady=10)
    
    def _load_live_schedule(self):
        """Load live NFL schedule from API."""
        try:
            # Show loading status
            self.games_display.config(state=tk.NORMAL)
            self.games_display.delete('1.0', tk.END)
            self.games_display.insert(tk.END, "🔄 Loading games from ESPN API...")
            self.games_display.config(state=tk.DISABLED)
            self.root.update()
            
            # Fetch games
            tonight = self.schedule_fetcher.get_tonights_game()
            upcoming = self.schedule_fetcher.get_upcoming_games(days=7)
            
            # Combine and deduplicate
            all_games = []
            seen_ids = set()
            
            if tonight and tonight['id'] not in seen_ids:
                all_games.append(tonight)
                seen_ids.add(tonight['id'])
            
            for game in upcoming[:10]:  # Max 10 games
                if game['id'] not in seen_ids:
                    all_games.append(game)
                    seen_ids.add(game['id'])
            
            self.current_games = all_games
            
            # Display in text area
            self.games_display.config(state=tk.NORMAL)
            self.games_display.delete('1.0', tk.END)
            
            if not all_games:
                self.games_display.insert(tk.END, "⚠️ No games found. Check your internet connection or try manual entry below.")
            else:
                if tonight:
                    self.games_display.insert(tk.END, "🔴 TONIGHT'S GAME:\n", 'header')
                    self.games_display.insert(tk.END, self.schedule_fetcher.format_game_summary(tonight))
                    self.games_display.insert(tk.END, "\n" + "-" * 50 + "\n\n")
                
                if len(all_games) > (1 if tonight else 0):
                    self.games_display.insert(tk.END, "📅 UPCOMING GAMES:\n", 'header')
                    start_idx = 1 if tonight else 0
                    for game in all_games[start_idx:]:
                        summary = f"{game['short_name']} - {game['date_display']}\n"
                        self.games_display.insert(tk.END, summary)
            
            self.games_display.config(state=tk.DISABLED)
            
            # Populate dropdown
            game_options = [
                f"{game['away_team']['name']} @ {game['home_team']['name']} - {game['date_display']}"
                for game in all_games
            ]
            self.game_select_combo['values'] = game_options
            if game_options:
                self.game_select_combo.current(0)
            
            self.status_var.set(f"✓ Loaded {len(all_games)} game(s) from ESPN API")
            
        except Exception as e:
            self.games_display.config(state=tk.NORMAL)
            self.games_display.delete('1.0', tk.END)
            self.games_display.insert(tk.END, f"❌ Error loading games: {str(e)}\n\n")
            self.games_display.insert(tk.END, "💡 Use manual entry below to enter game details.")
            self.games_display.config(state=tk.DISABLED)
            self.status_var.set("Error loading schedule - use manual entry")
    
    def _load_selected_game(self):
        """Load the selected game from the dropdown."""
        selection_idx = self.game_select_combo.current()
        if selection_idx < 0 or selection_idx >= len(self.current_games):
            messagebox.showwarning("No Selection", "Please select a game from the dropdown.")
            return
        
        game = self.current_games[selection_idx]
        
        # Show info dialog - no need to pick a team for analysis!
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Game")
        dialog.geometry("450x280")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(
            dialog,
            text="📊 Load Game Context",
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        ttk.Label(
            dialog,
            text=game['name'],
            font=('Arial', 11)
        ).pack(pady=5)
        
        # Info frame
        info_frame = ttk.Frame(dialog)
        info_frame.pack(pady=10, padx=20)
        
        if game['spread'] is not None:
            ttk.Label(info_frame, text=f"Spread: {game['spread']:+.1f}", font=('Arial', 10)).pack()
        if game['over_under'] is not None:
            ttk.Label(info_frame, text=f"Total: {game['over_under']:.1f}", font=('Arial', 10)).pack()
        
        ttk.Label(
            dialog,
            text="💡 Note: You can analyze players from BOTH teams!",
            font=('Arial', 9, 'italic'),
            foreground='blue'
        ).pack(pady=10)
        
        ttk.Label(
            dialog,
            text="Team selection is just for reference.\nAdd any players you want in Tab 2.",
            font=('Arial', 9)
        ).pack(pady=5)
        
        # Choice frame
        choice_frame = ttk.LabelFrame(dialog, text="Select Primary Team (Optional)", padding="10")
        choice_frame.pack(pady=10, padx=20, fill=tk.X)
        
        choice_var = tk.StringVar(value="away")
        
        ttk.Radiobutton(
            choice_frame,
            text=f"{game['away_team']['name']} (Away)",
            variable=choice_var,
            value="away"
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        ttk.Radiobutton(
            choice_frame,
            text=f"{game['home_team']['name']} (Home)",
            variable=choice_var,
            value="home"
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        def apply_choice():
            team_choice = choice_var.get()
            
            if team_choice == "away":
                your_team = game['away_team']['name']
                opponent = game['home_team']['name']
                # Away team perspective - spread is usually negative if they're underdogs
                spread = game['spread'] if game['spread'] else 0.0
            else:
                your_team = game['home_team']['name']
                opponent = game['away_team']['name']
                # Home team perspective - flip the spread
                spread = -game['spread'] if game['spread'] else 0.0
            
            # Set form values
            self.team_var.set(your_team)
            self.opponent_var.set(opponent)
            self.spread_var.set(spread)
            self.total_var.set(game['over_under'] if game['over_under'] else 45.0)
            
            # Calculate implied total (simple formula)
            total = game['over_under'] if game['over_under'] else 45.0
            implied = (total + spread) / 2
            self.implied_var.set(round(implied, 2))
            
            # Default defense rank to middle
            self.def_rank_var.set(16)
            
            dialog.destroy()
            self._save_game_context()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Apply", command=apply_choice).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def _save_game_context(self):
        """Save the game context."""
        try:
            self.game_context = GameContext(
                team=self.team_var.get(),
                opponent=self.opponent_var.get(),
                spread=self.spread_var.get(),
                total=self.total_var.get(),
                implied_team_total=self.implied_var.get(),
                # Advanced quantitative metrics
                opponent_def_epa=self.opp_def_epa_var.get(),
                opponent_dvoa_pass=self.opp_dvoa_pass_var.get(),
                opponent_dvoa_run=self.opp_dvoa_run_var.get(),
                team_offense_epa_l4=self.team_off_epa_l4_var.get()
            )
            self.game_status_var.set(f"✓ Game context saved: {self.game_context.team} vs {self.game_context.opponent}")
            self.status_var.set("Game context set with EPA/DVOA metrics. Move to Tab 2 to add players.")
        except Exception as e:
            messagebox.showerror("Validation Error", f"Invalid game context: {str(e)}")
            
    def _update_roster_players(self, event=None):
        """Update the player combobox based on selected team."""
        team = self.roster_team_var.get()
        if team in TEAM_ROSTERS:
            roster = TEAM_ROSTERS[team]
            players = []
            for pos, player_list in roster.items():
                for player in player_list:
                    has_stats = player['name'] in PLAYER_STATS
                    indicator = "✓" if has_stats else "○"
                    players.append(f"{indicator} {player['name']} ({pos})")
            self.player_combo['values'] = players
            if players:
                self.player_combo.current(0)
                
    def _add_from_roster(self):
        """Add a player from the roster."""
        selection = self.roster_player_var.get()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a player from the roster.")
            return
        
        # Parse selection
        parts = selection.split('(')
        name = parts[0].strip().replace('✓ ', '').replace('○ ', '')
        pos = parts[1].strip(')')
        
        # Open stats entry dialog
        self._open_stats_dialog(name, Position(pos))
        
    def _add_manual_player(self):
        """Add a player manually."""
        name = self.manual_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a player name.")
            return
        
        pos = Position(self.manual_pos_var.get())
        self._open_stats_dialog(name, pos)
        
    def _open_stats_dialog(self, name: str, position: Position):
        """Open a dialog to enter player stats and lines."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Enter Stats - {name} ({position.value})")
        dialog.geometry("500x600")
        
        # Get preloaded stats if available
        preload = PLAYER_STATS.get(name, {})
        has_preload = bool(preload) and preload.get("position") == position.value
        
        if has_preload:
            ttk.Label(
                dialog,
                text=f"✓ Auto-filled from NFL.com data for {name}",
                foreground='green',
                font=('Arial', 10, 'bold')
            ).pack(pady=5)
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Stats fields based on position
        fields = {}
        row = 0
        
        if position == Position.QB:
            fields = self._create_qb_fields(scrollable_frame, preload)
        elif position == Position.RB:
            fields = self._create_rb_fields(scrollable_frame, preload)
        else:
            fields = self._create_wr_te_fields(scrollable_frame, preload)
        
        # Save button
        def save_player():
            try:
                # Create stats and lines based on position
                if position == Position.QB:
                    stats = QBStats(
                        games_played=int(fields['games'].get()),
                        passing_yards_l5_avg=float(fields['pass_l5'].get()),
                        passing_yards_season_total=float(fields['pass_tot'].get()),
                        rush_yards_l5_avg=float(fields['rush_l5'].get()),
                        rush_yards_season_total=float(fields['rush_tot'].get()),
                        epa_per_play=float(fields['epa'].get()),
                        cpoe=float(fields['cpoe'].get()),
                        pass_attempts_l5_avg=float(fields['att_l5'].get()),
                        pass_attempts_season_total=float(fields['att_tot'].get())
                    )
                    lines = MarketLines(
                        player_name=name,
                        position=position,
                        passing_yards=float(fields['line_pass'].get()),
                        rush_yards=float(fields['line_rush'].get()) if fields['line_rush'].get() else None,
                        pass_attempts=float(fields['line_att'].get()) if fields['line_att'].get() else None
                    )
                elif position == Position.RB:
                    stats = RBStats(
                        games_played=int(fields['games'].get()),
                        rush_yards_l5_avg=float(fields['rush_l5'].get()),
                        rush_yards_season_total=float(fields['rush_tot'].get()),
                        opportunity_share_pct=float(fields['opp_share'].get()),
                        yco_per_att=float(fields['yco'].get()),
                        rush_attempts_l5_avg=float(fields['att_l5'].get()),
                        rush_attempts_season_total=float(fields['att_tot'].get())
                    )
                    lines = MarketLines(
                        player_name=name,
                        position=position,
                        rush_yards=float(fields['line_rush'].get()),
                        rush_attempts=float(fields['line_att'].get()) if fields['line_att'].get() else None
                    )
                else:
                    stats = WRTEStats(
                        games_played=int(fields['games'].get()),
                        rec_yards_l5_avg=float(fields['rec_l5'].get()),
                        rec_yards_season_total=float(fields['rec_tot'].get()),
                        target_share_pct=float(fields['tgt_share'].get()),
                        adot=float(fields['adot'].get()),
                        air_yards_share=float(fields['air_share'].get()),
                        receptions_l5_avg=float(fields['catches_l5'].get()),
                        receptions_season_total=float(fields['catches_tot'].get())
                    )
                    lines = MarketLines(
                        player_name=name,
                        position=position,
                        rec_yards=float(fields['line_rec'].get()),
                        receptions=float(fields['line_catches'].get()) if fields['line_catches'].get() else None
                    )
                
                # Add player
                player = PlayerData(name=name, position=position, stats=stats, market_lines=lines)
                self.players.append(player)
                self._update_players_list()
                
                dialog.destroy()
                messagebox.showinfo("Success", f"Added {name} successfully!")
                
            except Exception as e:
                messagebox.showerror("Validation Error", f"Invalid data: {str(e)}")
        
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=100, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save Player", command=save_player).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _create_qb_fields(self, parent, preload):
        """Create QB input fields."""
        fields = {}
        row = 0
        
        # Helper function
        def add_field(label, key, default):
            nonlocal row
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.StringVar(value=str(preload.get(key, default)))
            entry = ttk.Entry(parent, textvariable=var, width=15)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            fields[key.split('_')[0] + ('_' + key.split('_')[-1] if 'l5' in key or 'tot' in key or 'line' in key else '')] = var
            row += 1
            return var
        
        ttk.Label(parent, text="STATS", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        fields['games'] = add_field("Games Played:", 'games_played', 12)
        fields['pass_l5'] = add_field("Pass Yds (L5 avg):", 'passing_yards_l5_avg', 250.0)
        fields['pass_tot'] = add_field("Pass Yds (Season):", 'passing_yards_season_total', 3000.0)
        fields['rush_l5'] = add_field("Rush Yds (L5 avg):", 'rush_yards_l5_avg', 15.0)
        fields['rush_tot'] = add_field("Rush Yds (Season):", 'rush_yards_season_total', 180.0)
        fields['att_l5'] = add_field("Pass Att (L5 avg):", 'pass_attempts_l5_avg', 35.0)
        fields['att_tot'] = add_field("Pass Att (Season):", 'pass_attempts_season_total', 420.0)
        fields['epa'] = add_field("EPA/Play:", 'epa_per_play', 0.10)
        fields['cpoe'] = add_field("CPOE:", 'cpoe', 2.0)
        
        ttk.Label(parent, text="VEGAS LINES", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        fields['line_pass'] = add_field("Pass Yds Line:", 'line_pass', 245.5)
        fields['line_rush'] = add_field("Rush Yds Line:", 'line_rush', 15.5)
        fields['line_att'] = add_field("Pass Att Line:", 'line_att', 32.5)
        
        return fields
    
    def _create_rb_fields(self, parent, preload):
        """Create RB input fields."""
        fields = {}
        row = 0
        
        def add_field(label, key, default):
            nonlocal row
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.StringVar(value=str(preload.get(key, default)))
            entry = ttk.Entry(parent, textvariable=var, width=15)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            row += 1
            return var
        
        ttk.Label(parent, text="STATS", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        fields['games'] = add_field("Games Played:", 'games_played', 12)
        fields['rush_l5'] = add_field("Rush Yds (L5 avg):", 'rush_yards_l5_avg', 70.0)
        fields['rush_tot'] = add_field("Rush Yds (Season):", 'rush_yards_season_total', 840.0)
        fields['att_l5'] = add_field("Rush Att (L5 avg):", 'rush_attempts_l5_avg', 15.0)
        fields['att_tot'] = add_field("Rush Att (Season):", 'rush_attempts_season_total', 180.0)
        fields['opp_share'] = add_field("Opportunity Share %:", 'opportunity_share_pct', 60.0)
        fields['yco'] = add_field("YCO/Att:", 'yco_per_att', 2.5)
        
        ttk.Label(parent, text="VEGAS LINES", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        fields['line_rush'] = add_field("Rush Yds Line:", 'line_rush', 65.5)
        fields['line_att'] = add_field("Rush Att Line:", 'line_att', 14.5)
        
        return fields
    
    def _create_wr_te_fields(self, parent, preload):
        """Create WR/TE input fields."""
        fields = {}
        row = 0
        
        def add_field(label, key, default):
            nonlocal row
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.StringVar(value=str(preload.get(key, default)))
            entry = ttk.Entry(parent, textvariable=var, width=15)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            row += 1
            return var
        
        ttk.Label(parent, text="STATS", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        fields['games'] = add_field("Games Played:", 'games_played', 12)
        fields['rec_l5'] = add_field("Rec Yds (L5 avg):", 'rec_yards_l5_avg', 70.0)
        fields['rec_tot'] = add_field("Rec Yds (Season):", 'rec_yards_season_total', 840.0)
        fields['catches_l5'] = add_field("Catches (L5 avg):", 'receptions_l5_avg', 5.0)
        fields['catches_tot'] = add_field("Catches (Season):", 'receptions_season_total', 60.0)
        fields['tgt_share'] = add_field("Target Share %:", 'target_share_pct', 22.0)
        fields['adot'] = add_field("ADOT:", 'adot', 10.0)
        fields['air_share'] = add_field("Air Yards Share %:", 'air_yards_share', 25.0)
        
        ttk.Label(parent, text="VEGAS LINES", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        fields['line_rec'] = add_field("Rec Yds Line:", 'line_rec', 65.5)
        fields['line_catches'] = add_field("Receptions Line:", 'line_catches', 4.5)
        
        return fields
        
    def _update_players_list(self):
        """Update the players listbox."""
        self.players_listbox.delete(0, tk.END)
        for player in self.players:
            self.players_listbox.insert(tk.END, f"{player.name} ({player.position.value})")
        self.status_var.set(f"{len(self.players)} player(s) added. Review in Tab 3 when ready.")
        
    def _edit_selected_player(self):
        """Edit the selected player."""
        selection = self.players_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a player to edit.")
            return
        
        idx = selection[0]
        player = self.players[idx]
        
        # Remove and re-add
        self.players.pop(idx)
        self._update_players_list()
        self._open_stats_dialog(player.name, player.position)
        
    def _delete_selected_player(self):
        """Delete the selected player."""
        selection = self.players_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a player to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Delete this player?"):
            idx = selection[0]
            player = self.players.pop(idx)
            self._update_players_list()
            messagebox.showinfo("Deleted", f"Removed {player.name}")
            
    def _update_review(self):
        """Update the review text."""
        self.review_text.delete('1.0', tk.END)
        
        if not self.game_context:
            self.review_text.insert('1.0', "⚠ No game context set. Go to Tab 1 to set up the game.\n")
            return
        
        # Game context
        self.review_text.insert(tk.END, "═" * 60 + "\n")
        self.review_text.insert(tk.END, "GAME CONTEXT\n")
        self.review_text.insert(tk.END, "═" * 60 + "\n\n")
        self.review_text.insert(tk.END, f"Matchup: {self.game_context.team} @ {self.game_context.opponent}\n")
        self.review_text.insert(tk.END, f"Spread: {self.game_context.spread:+.1f}\n")
        self.review_text.insert(tk.END, f"Total: {self.game_context.total:.1f}\n")
        self.review_text.insert(tk.END, f"Implied Team Total: {self.game_context.implied_team_total:.1f}\n")
        self.review_text.insert(tk.END, f"Opponent Def Rank: #{self.game_context.opponent_rank}\n\n")
        
        # Players
        self.review_text.insert(tk.END, "═" * 60 + "\n")
        self.review_text.insert(tk.END, f"PLAYERS ({len(self.players)})\n")
        self.review_text.insert(tk.END, "═" * 60 + "\n\n")
        
        if not self.players:
            self.review_text.insert(tk.END, "⚠ No players added. Go to Tab 2 to add players.\n")
        else:
            for i, player in enumerate(self.players, 1):
                self.review_text.insert(tk.END, f"{i}. {player.name} ({player.position.value})\n")
                self.review_text.insert(tk.END, f"   Games Played: {player.stats.games_played}\n")
                
                if player.position == Position.QB:
                    self.review_text.insert(tk.END, f"   Pass Yds: {player.stats.passing_yards_l5_avg:.1f} (L5) | {player.stats.passing_yards_season_total:.0f} (Season)\n")
                    self.review_text.insert(tk.END, f"   Line: {player.market_lines.passing_yards:.1f}\n")
                elif player.position == Position.RB:
                    self.review_text.insert(tk.END, f"   Rush Yds: {player.stats.rush_yards_l5_avg:.1f} (L5) | {player.stats.rush_yards_season_total:.0f} (Season)\n")
                    self.review_text.insert(tk.END, f"   Line: {player.market_lines.rush_yards:.1f}\n")
                else:
                    self.review_text.insert(tk.END, f"   Rec Yds: {player.stats.rec_yards_l5_avg:.1f} (L5) | {player.stats.rec_yards_season_total:.0f} (Season)\n")
                    self.review_text.insert(tk.END, f"   Line: {player.market_lines.rec_yards:.1f}\n")
                
                self.review_text.insert(tk.END, "\n")
        
    def _generate_projections(self):
        """Generate projections and display results."""
        if not self.game_context:
            messagebox.showerror("Missing Data", "Please set up game context in Tab 1.")
            return
        
        if not self.players:
            messagebox.showerror("Missing Data", "Please add at least one player in Tab 2.")
            return
        
        # Update review
        self._update_review()
        
        # Run async generation
        asyncio.run(self._async_generate())
        
    async def _async_generate(self):
        """Async generation of projections."""
        try:
            self.status_var.set("Generating projections...")
            self.generate_btn.config(state='disabled')
            
            # Set game context
            self.prediction_engine.set_game_context(self.game_context)
            
            # Generate projections
            self.projections = []
            for player in self.players:
                player_projections = await self.prediction_engine.generate_projections(player)
                self.projections.extend(player_projections)
            
            # Find correlated parlays
            correlation_engine = CorrelationEngine(self.game_context)
            parlays = correlation_engine.find_correlated_parlays(self.projections)
            
            # Display results
            self._display_results(parlays)
            
            # Switch to results tab
            self.notebook.select(3)
            
            self.status_var.set("✓ Projections complete! View results in Tab 4.")
            self.generate_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate projections: {str(e)}")
            self.generate_btn.config(state='normal')
            
    def _display_results(self, parlays: list[CorrelatedParlay]):
        """Display results in the results tab."""
        self.results_text.delete('1.0', tk.END)
        
        # Header
        self.results_text.insert(tk.END, "=" * 80 + "\n", 'bold')
        self.results_text.insert(tk.END, "NFL PARLAY GENERATOR - PROJECTIONS & ANALYSIS\n", 'header')
        self.results_text.insert(tk.END, "=" * 80 + "\n\n", 'bold')
        
        # Game Context
        self.results_text.insert(tk.END, f"Game: {self.game_context.team} @ {self.game_context.opponent}\n")
        self.results_text.insert(tk.END, f"Spread: {self.game_context.spread:+.1f} | Total: {self.game_context.total:.1f}\n\n")
        
        # Projections Table
        self.results_text.insert(tk.END, "PROJECTIONS TABLE\n", 'header')
        self.results_text.insert(tk.END, "-" * 80 + "\n")
        self.results_text.insert(tk.END, f"{'Player':<18} {'Pos':<4} {'Stat':<14} {'Proj':<8} {'Line':<8} {'Edge':<8} {'Pick':<6} {'Conf':<6}\n")
        self.results_text.insert(tk.END, "-" * 80 + "\n")
        
        for proj in self.projections:
            edge_tag = 'success' if proj.edge > 0 else 'error'
            pick_tag = 'success' if proj.recommendation.value == "Over" else 'warning'
            
            line = f"{proj.player_name:<18} {proj.position.value:<4} {proj.stat_type:<14} "
            line += f"{proj.projected_value:<8.1f} {proj.market_line:<8.1f} "
            self.results_text.insert(tk.END, line)
            self.results_text.insert(tk.END, f"{proj.edge:+7.1f}% ", edge_tag)
            self.results_text.insert(tk.END, f"{proj.recommendation.value:<6} ", pick_tag)
            self.results_text.insert(tk.END, f"{proj.confidence:>5.0f}%\n")
        
        self.results_text.insert(tk.END, "\n\n")
        
        # Parlays
        if parlays:
            self.results_text.insert(tk.END, "RECOMMENDED PARLAYS\n", 'header')
            self.results_text.insert(tk.END, "=" * 80 + "\n\n")
            
            for i, parlay in enumerate(parlays, 1):
                self.results_text.insert(tk.END, f"PARLAY #{i}\n", 'bold')
                self.results_text.insert(tk.END, f"Game Script: {parlay.game_script.value}\n")
                self.results_text.insert(tk.END, f"Correlation: {parlay.correlation_strength}\n")
                self.results_text.insert(tk.END, f"Combined Confidence: ", 'bold')
                self.results_text.insert(tk.END, f"{parlay.combined_confidence:.1f}%\n", 'success')
                self.results_text.insert(tk.END, "\nLegs:\n")
                
                for j, leg in enumerate(parlay.legs, 1):
                    edge_tag = 'success' if leg.edge > 0 else 'error'
                    self.results_text.insert(tk.END, f"  {j}. {leg.player_name} - {leg.stat_type} {leg.direction.value} {leg.line:.1f} ")
                    self.results_text.insert(tk.END, f"({leg.edge:+.1f}%)\n", edge_tag)
                
                self.results_text.insert(tk.END, "\n" + "-" * 80 + "\n\n")
        else:
            self.results_text.insert(tk.END, "No strong correlated parlays found.\n", 'warning')
            self.results_text.insert(tk.END, "Consider individual plays based on the projections above.\n\n")
        
        # Summary
        best = max(self.projections, key=lambda p: abs(p.edge)) if self.projections else None
        if best:
            self.results_text.insert(tk.END, "BEST EDGE\n", 'header')
            self.results_text.insert(tk.END, f"{best.player_name} {best.stat_type} {best.recommendation.value} ", 'bold')
            self.results_text.insert(tk.END, f"({best.edge:+.1f}%)\n", 'success' if best.edge > 0 else 'error')


def main():
    """Entry point for the GUI application."""
    root = tk.Tk()
    app = NFLParlayGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
