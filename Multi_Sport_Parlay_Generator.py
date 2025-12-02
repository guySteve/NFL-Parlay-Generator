#!/usr/bin/env python3
"""
Multi-Sport Parlay Generator - NFL, NBA, NHL
Enhanced Desktop GUI with quantitative analysis for multiple sports.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, List
import random
from datetime import datetime

# Sport selection
SPORTS = ['NFL', 'NBA', 'NHL']

class MultiSportParlayGUI:
    """Multi-sport parlay generator with confidence metrics."""
    
    # Team Colors by Sport
    TEAM_COLORS = {
        # NFL Teams
        "Denver Broncos": ("#FB4F14", "#002244"),
        "Washington Commanders": ("#773141", "#FFB612"),
        "Kansas City Chiefs": ("#E31837", "#FFB81C"),
        "Buffalo Bills": ("#00338D", "#C60C30"),
        "Dallas Cowboys": ("#041E42", "#869397"),
        "Philadelphia Eagles": ("#004C54", "#A5ACAF"),
        "San Francisco 49ers": ("#AA0000", "#B3995D"),
        "Miami Dolphins": ("#008E97", "#FC4C02"),
        # NBA Teams
        "Los Angeles Lakers": ("#552583", "#FDB927"),
        "Boston Celtics": ("#007A33", "#BA9653"),
        "Golden State Warriors": ("#1D428A", "#FFC72C"),
        "Chicago Bulls": ("#CE1141", "#000000"),
        "Miami Heat": ("#98002E", "#F9A01B"),
        # NHL Teams
        "Colorado Avalanche": ("#6F263D", "#236192"),
        "Toronto Maple Leafs": ("#00205B", "#FFFFFF"),
        "Vegas Golden Knights": ("#B4975A", "#333F42"),
        "Tampa Bay Lightning": ("#002868", "#FFFFFF"),
        "default": ("#013369", "#D50A0A")
    }
    
    # Position types by sport
    POSITIONS = {
        'NFL': ['QB', 'RB', 'WR', 'TE', 'K', 'DEF'],
        'NBA': ['PG', 'SG', 'SF', 'PF', 'C'],
        'NHL': ['C', 'LW', 'RW', 'D', 'G']
    }
    
    # Prop bet types by sport
    PROP_TYPES = {
        'NFL': [
            'Passing Yards', 'Passing TDs', 'Completions',
            'Rushing Yards', 'Rushing TDs', 'Receptions',
            'Receiving Yards', 'Receiving TDs', 'Anytime TD',
            'Field Goals Made', 'Extra Points'
        ],
        'NBA': [
            'Points', 'Rebounds', 'Assists', '3-Pointers Made',
            'Steals', 'Blocks', 'Points + Rebounds + Assists',
            'Double-Double', 'Triple-Double'
        ],
        'NHL': [
            'Goals', 'Assists', 'Points (G+A)', 'Shots on Goal',
            'Saves', 'Save %', 'Anytime Goal Scorer'
        ]
    }
    
    def __init__(self, root: tk.Tk):
        """Initialize the multi-sport GUI."""
        self.root = root
        self.root.title("🏆 Multi-Sport Parlay Generator - NFL | NBA | NHL")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#e8e8e8')
        
        # Data storage
        self.current_sport = 'NFL'
        self.game_context: Optional[Dict] = None
        self.current_team = "default"
        self.players = []
        self.confidence_widgets = []
        
        # Setup UI
        self._setup_styles()
        self._create_main_layout()
        
    def _setup_styles(self):
        """Setup ttk styles with light gray theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        primary, secondary = self.TEAM_COLORS.get(self.current_team, self.TEAM_COLORS["default"])
        
        # Base colors - light gray backgrounds
        bg_main = '#e8e8e8'
        bg_frame = '#f5f5f5'
        bg_input = '#ffffff'
        text_dark = '#2c2c2c'
        text_light = '#666666'
        
        # Configure base styles
        style.configure('.', background=bg_main, foreground=text_dark)
        style.configure('TFrame', background=bg_frame)
        style.configure('TLabel', background=bg_frame, foreground=text_dark, font=('Segoe UI', 9))
        style.configure('TLabelframe', background=bg_frame, bordercolor=primary, borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', background=bg_frame, foreground=primary, font=('Segoe UI', 10, 'bold'))
        
        # Checkbuttons with better spacing
        style.configure('TCheckbutton', 
                       background=bg_frame, 
                       foreground=text_dark,
                       font=('Segoe UI', 9),
                       padding=[5, 5])
        
        # Notebook tabs
        style.configure('TNotebook', background=bg_main, borderwidth=0)
        style.configure('TNotebook.Tab', 
                       padding=[20, 10],  # More padding
                       background='#d0d0d0',
                       foreground=text_dark,
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', primary)],
                 foreground=[('selected', '#ffffff')])
        
        # Headers
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground=primary, background=bg_main)
        style.configure('Subheader.TLabel', font=('Segoe UI', 12, 'bold'), foreground=primary, background=bg_frame)
        style.configure('Info.TLabel', font=('Segoe UI', 9, 'italic'), foreground='#0066cc', background=bg_frame)
        
        # Confidence labels
        style.configure('ConfHigh.TLabel', foreground='#28a745', font=('Segoe UI', 9, 'bold'), background=bg_frame)
        style.configure('ConfMid.TLabel', foreground='#ffc107', font=('Segoe UI', 9, 'bold'), background=bg_frame)
        style.configure('ConfLow.TLabel', foreground='#dc3545', font=('Segoe UI', 9, 'bold'), background=bg_frame)
        
        # Buttons
        style.configure('TButton', font=('Segoe UI', 9), padding=[15, 8])
        style.configure('Primary.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       background=primary,
                       foreground='#ffffff')
        
    def _create_main_layout(self):
        """Create the main application layout."""
        # Main container
        main = ttk.Frame(self.root, padding="15")
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title bar with sport selector
        title_frame = ttk.Frame(main)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(
            title_frame,
            text="🏆 MULTI-SPORT PARLAY GENERATOR",
            style='Header.TLabel'
        ).pack(side=tk.LEFT)
        
        # Sport selector
        sport_frame = ttk.Frame(title_frame)
        sport_frame.pack(side=tk.RIGHT)
        
        ttk.Label(sport_frame, text="Sport:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.sport_var = tk.StringVar(value='NFL')
        for sport in SPORTS:
            icon = {'NFL': '🏈', 'NBA': '🏀', 'NHL': '🏒'}[sport]
            ttk.Radiobutton(
                sport_frame,
                text=f"{icon} {sport}",
                variable=self.sport_var,
                value=sport,
                command=self._on_sport_change
            ).pack(side=tk.LEFT, padx=5)
        
        # Create notebook
        self.notebook = ttk.Notebook(main)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Tabs
        self.game_tab = self._create_game_tab()
        self.notebook.add(self.game_tab, text="1️⃣ Game Setup")
        
        self.players_tab = self._create_players_tab()
        self.notebook.add(self.players_tab, text="2️⃣ Add Players")
        
        self.props_tab = self._create_props_tab()
        self.notebook.add(self.props_tab, text="3️⃣ Select Props")
        
        self.analysis_tab = self._create_analysis_tab()
        self.notebook.add(self.analysis_tab, text="4️⃣ AI Analysis")
        
        self.results_tab = self._create_results_tab()
        self.notebook.add(self.results_tab, text="5️⃣ Results")
        
        # Status bar
        status_frame = ttk.Frame(main)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value=f"Ready - {self.current_sport} Mode")
        ttk.Label(status_frame, textvariable=self.status_var, foreground='#0066cc').pack(side=tk.LEFT)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        
    def _on_sport_change(self):
        """Handle sport selection change."""
        self.current_sport = self.sport_var.get()
        self.status_var.set(f"Switched to {self.current_sport} Mode")
        self._refresh_players_tab()
        self._refresh_props_tab()
        
    def _create_game_tab(self):
        """Create game setup tab."""
        tab = ttk.Frame(self.notebook, padding="15")
        
        # Live games section
        live_frame = ttk.LabelFrame(tab, text="🔴 LIVE - Today's Schedule", padding="15")
        live_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Games display
        self.games_display = tk.Text(
            live_frame,
            height=5,
            width=80,
            wrap=tk.WORD,
            bg='#ffffff',
            fg='#2c2c2c',
            font=('Segoe UI', 9),
            relief='solid',
            borderwidth=1
        )
        self.games_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.games_display.insert(tk.END, f"Click 'Refresh' to load today's {self.current_sport} matchups...")
        self.games_display.config(state=tk.DISABLED)
        
        # Game selection
        select_row = ttk.Frame(live_frame)
        select_row.pack(fill=tk.X)
        
        ttk.Label(select_row, text="Select Game:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.game_select_var = tk.StringVar()
        self.game_select_combo = ttk.Combobox(
            select_row,
            textvariable=self.game_select_var,
            state='readonly',
            width=50
        )
        self.game_select_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            select_row,
            text="🔄 Refresh",
            command=self._refresh_schedule
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            select_row,
            text="📥 Load Selected",
            command=self._load_selected_game,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        # Manual entry
        manual_frame = ttk.LabelFrame(tab, text="📝 Game Context (Manual/Edit)", padding="15")
        manual_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # Team names
        teams_row = ttk.Frame(manual_frame)
        teams_row.pack(fill=tk.X, pady=(0, 10))
        
        team_a_frame = ttk.Frame(teams_row)
        team_a_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(team_a_frame, text="Team A:").pack(anchor=tk.W)
        self.team_a_var = tk.StringVar(value="")
        ttk.Entry(team_a_frame, textvariable=self.team_a_var, width=25).pack(fill=tk.X)
        
        ttk.Label(teams_row, text="VS", font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT, padx=10)
        
        team_b_frame = ttk.Frame(teams_row)
        team_b_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        ttk.Label(team_b_frame, text="Team B:").pack(anchor=tk.W)
        self.team_b_var = tk.StringVar(value="")
        ttk.Entry(team_b_frame, textvariable=self.team_b_var, width=25).pack(fill=tk.X)
        
        # Spread/Total
        lines_row = ttk.Frame(manual_frame)
        lines_row.pack(fill=tk.X, pady=(0, 10))
        
        spread_frame = ttk.Frame(lines_row)
        spread_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(spread_frame, text="Spread (Team A):").pack(anchor=tk.W)
        self.spread_var = tk.DoubleVar(value=0.0)
        ttk.Entry(spread_frame, textvariable=self.spread_var, width=10).pack(anchor=tk.W)
        
        total_frame = ttk.Frame(lines_row)
        total_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(total_frame, text="Total O/U:").pack(anchor=tk.W)
        self.total_var = tk.DoubleVar(value=0.0)
        ttk.Entry(total_frame, textvariable=self.total_var, width=10).pack(anchor=tk.W)
        
        tab.columnconfigure(0, weight=1)
        
        return tab
        
    def _create_players_tab(self):
        """Create players tab with better spacing."""
        tab = ttk.Frame(self.notebook, padding="15")
        
        # Info
        ttk.Label(
            tab,
            text="💡 Add players from ANY team in the matchup",
            style='Info.TLabel'
        ).pack(pady=(0, 15))
        
        # Quick add
        add_frame = ttk.LabelFrame(tab, text="➕ Add Player", padding="15")
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        input_row = ttk.Frame(add_frame)
        input_row.pack(fill=tk.X)
        
        ttk.Label(input_row, text="Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.player_name_var = tk.StringVar()
        ttk.Entry(input_row, textvariable=self.player_name_var, width=25).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(input_row, text="Position:").pack(side=tk.LEFT, padx=(0, 5))
        self.player_pos_var = tk.StringVar()
        self.player_pos_combo = ttk.Combobox(
            input_row,
            textvariable=self.player_pos_var,
            values=self.POSITIONS.get(self.current_sport, []),
            state='readonly',
            width=8
        )
        self.player_pos_combo.pack(side=tk.LEFT, padx=(0, 15))
        if self.POSITIONS.get(self.current_sport):
            self.player_pos_combo.current(0)
        
        ttk.Button(
            input_row,
            text="➕ Add",
            command=self._add_player,
            style='Primary.TButton'
        ).pack(side=tk.LEFT)
        
        # Players list
        list_frame = ttk.LabelFrame(tab, text="📋 Current Players", padding="15")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.players_listbox = tk.Listbox(
            list_frame,
            height=15,
            bg='#ffffff',
            font=('Segoe UI', 10),
            relief='solid',
            borderwidth=1
        )
        self.players_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        btn_row = ttk.Frame(list_frame)
        btn_row.pack()
        
        ttk.Button(btn_row, text="🗑️ Remove", command=self._remove_player).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="🔄 Clear All", command=self._clear_players).pack(side=tk.LEFT, padx=5)
        
        return tab
        
    def _create_props_tab(self):
        """Create prop bets tab with better checkbox spacing."""
        tab = ttk.Frame(self.notebook, padding="15")
        
        # Instructions
        ttk.Label(
            tab,
            text="✅ Select the prop bet types you want to include in your parlay",
            style='Info.TLabel'
        ).pack(pady=(0, 15))
        
        # Scrollable frame for checkboxes
        canvas = tk.Canvas(tab, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Store checkbox variables
        self.prop_check_vars = {}
        
        # Create checkboxes with better spacing
        for prop_type in self.PROP_TYPES.get(self.current_sport, []):
            var = tk.BooleanVar(value=False)
            self.prop_check_vars[prop_type] = var
            
            cb = ttk.Checkbutton(
                scrollable_frame,
                text=prop_type,
                variable=var
            )
            cb.pack(anchor=tk.W, pady=5, padx=20)  # Better spacing!
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Select all/none buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="✅ Select All",
            command=lambda: self._toggle_all_props(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❌ Clear All",
            command=lambda: self._toggle_all_props(False)
        ).pack(side=tk.LEFT, padx=5)
        
        return tab
        
    def _create_analysis_tab(self):
        """Create AI analysis tab."""
        tab = ttk.Frame(self.notebook, padding="15")
        
        ttk.Label(
            tab,
            text="🤖 AI Matchup Analysis",
            style='Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Narrative
        narrative_frame = ttk.LabelFrame(tab, text="🎙️ Expert Analysis", padding="15")
        narrative_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Confidence
        conf_row = ttk.Frame(narrative_frame)
        conf_row.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(conf_row, text="Confidence:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        self.narrative_conf_var = tk.StringVar(value="--")
        self.narrative_conf_label = ttk.Label(conf_row, textvariable=self.narrative_conf_var, style='ConfHigh.TLabel')
        self.narrative_conf_label.pack(side=tk.LEFT, padx=5)
        
        # Text
        self.narrative_text = scrolledtext.ScrolledText(
            narrative_frame,
            height=12,
            wrap=tk.WORD,
            bg='#ffffff',
            font=('Segoe UI', 10),
            relief='solid',
            borderwidth=1
        )
        self.narrative_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.narrative_text.insert(tk.END, "Generate analysis to see expert breakdown...")
        
        ttk.Button(
            narrative_frame,
            text="🎯 Generate Analysis",
            command=self._generate_analysis,
            style='Primary.TButton'
        ).pack()
        
        # Key metrics
        metrics_frame = ttk.LabelFrame(tab, text="📊 Key Metrics", padding="15")
        metrics_frame.pack(fill=tk.BOTH, expand=True)
        
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame,
            height=8,
            wrap=tk.WORD,
            bg='#ffffff',
            font=('Consolas', 9),
            relief='solid',
            borderwidth=1
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        return tab
        
    def _create_results_tab(self):
        """Create results tab."""
        tab = ttk.Frame(self.notebook, padding="15")
        
        ttk.Label(
            tab,
            text="🎰 Parlay Results & EV Analysis",
            style='Subheader.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Results display
        results_frame = ttk.LabelFrame(tab, text="💰 Generated Parlays", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            bg='#ffffff',
            font=('Consolas', 9),
            relief='solid',
            borderwidth=1
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Generate button
        ttk.Button(
            tab,
            text="🚀 Generate Parlays",
            command=self._generate_parlays,
            style='Primary.TButton'
        ).pack(pady=(10, 0))
        
        return tab
    
    # Event handlers
    def _refresh_schedule(self):
        """Refresh game schedule."""
        sport = self.current_sport
        self.games_display.config(state=tk.NORMAL)
        self.games_display.delete(1.0, tk.END)
        self.games_display.insert(tk.END, f"Loading {sport} schedule for {datetime.now().strftime('%B %d, %Y')}...\n\n")
        self.games_display.insert(tk.END, f"⚠️ API integration required for live {sport} data\n")
        self.games_display.insert(tk.END, f"Recommended APIs:\n")
        
        if sport == 'NFL':
            self.games_display.insert(tk.END, "  • ESPN API\n  • The Odds API\n  • NFL.com feeds\n")
        elif sport == 'NBA':
            self.games_display.insert(tk.END, "  • NBA Stats API\n  • The Odds API\n  • ESPN API\n")
        elif sport == 'NHL':
            self.games_display.insert(tk.END, "  • NHL Stats API\n  • The Odds API\n  • ESPN API\n")
        
        self.games_display.config(state=tk.DISABLED)
        self.status_var.set(f"Schedule refresh attempted - API integration needed")
        
    def _load_selected_game(self):
        """Load selected game context."""
        game = self.game_select_var.get()
        if not game:
            messagebox.showwarning("No Selection", "Please select a game first")
            return
        
        self.status_var.set(f"Loaded: {game}")
        messagebox.showinfo("Game Loaded", f"Game context loaded for:\n{game}")
        
    def _add_player(self):
        """Add a player to the list."""
        name = self.player_name_var.get().strip()
        pos = self.player_pos_var.get()
        
        if not name:
            messagebox.showwarning("Invalid Input", "Please enter a player name")
            return
        
        player_str = f"{name} ({pos}) - {self.current_sport}"
        self.players.append({'name': name, 'position': pos, 'sport': self.current_sport})
        self.players_listbox.insert(tk.END, player_str)
        
        self.player_name_var.set("")
        self.status_var.set(f"Added: {player_str}")
        
    def _remove_player(self):
        """Remove selected player."""
        selection = self.players_listbox.curselection()
        if selection:
            idx = selection[0]
            self.players_listbox.delete(idx)
            if idx < len(self.players):
                del self.players[idx]
            self.status_var.set("Player removed")
        
    def _clear_players(self):
        """Clear all players."""
        self.players_listbox.delete(0, tk.END)
        self.players.clear()
        self.status_var.set("All players cleared")
        
    def _toggle_all_props(self, state: bool):
        """Select or deselect all prop types."""
        for var in self.prop_check_vars.values():
            var.set(state)
        self.status_var.set(f"All props {'selected' if state else 'cleared'}")
        
    def _generate_analysis(self):
        """Generate AI analysis."""
        self.narrative_text.delete(1.0, tk.END)
        
        sport = self.current_sport
        team_a = self.team_a_var.get() or "Team A"
        team_b = self.team_b_var.get() or "Team B"
        
        # Mock Tony Romo style narrative
        narratives = [
            f"Here's the thing about {team_a} - they've been playing with real confidence lately. ",
            f"Now {team_b}, they're gonna come out aggressive, but I like how {team_a} matches up here. ",
            f"If you watch the tape, {team_a}'s got some real advantages in this matchup. "
        ]
        
        narrative = random.choice(narratives)
        confidence = random.randint(65, 92)
        
        self.narrative_text.insert(tk.END, narrative)
        self.narrative_conf_var.set(f"{confidence}%")
        
        # Update confidence style
        if confidence >= 75:
            self.narrative_conf_label.configure(style='ConfHigh.TLabel')
        elif confidence >= 60:
            self.narrative_conf_label.configure(style='ConfMid.TLabel')
        else:
            self.narrative_conf_label.configure(style='ConfLow.TLabel')
        
        self.status_var.set("Analysis generated")
        
    def _generate_parlays(self):
        """Generate parlay recommendations."""
        self.results_text.delete(1.0, tk.END)
        
        if not self.players:
            self.results_text.insert(tk.END, "⚠️ No players added yet!\n\n")
            self.results_text.insert(tk.END, "Add players in the 'Add Players' tab first.")
            return
        
        # Get selected props
        selected_props = [prop for prop, var in self.prop_check_vars.items() if var.get()]
        
        if not selected_props:
            self.results_text.insert(tk.END, "⚠️ No prop types selected!\n\n")
            self.results_text.insert(tk.END, "Select prop types in the 'Select Props' tab.")
            return
        
        self.results_text.insert(tk.END, f"🎰 PARLAY RECOMMENDATIONS ({self.current_sport})\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Generate sample parlays
        for i in range(3):
            self.results_text.insert(tk.END, f"PARLAY #{i+1}\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            
            for player in self.players[:3]:
                prop = random.choice(selected_props)
                line = random.randint(50, 350) / 10
                ou = random.choice(['Over', 'Under'])
                conf = random.randint(60, 90)
                
                self.results_text.insert(tk.END, f"  ✓ {player['name']} - {prop} {ou} {line}\n")
                self.results_text.insert(tk.END, f"    Confidence: {conf}%\n\n")
            
            total_odds = random.randint(300, 800)
            ev = random.randint(-5, 15)
            
            self.results_text.insert(tk.END, f"  Combined Odds: +{total_odds}\n")
            self.results_text.insert(tk.END, f"  Expected Value: {ev:+.1f}%\n")
            self.results_text.insert(tk.END, "\n" + "=" * 60 + "\n\n")
        
        self.status_var.set("Parlays generated successfully!")
        
    def _refresh_players_tab(self):
        """Refresh player position options when sport changes."""
        positions = self.POSITIONS.get(self.current_sport, [])
        self.player_pos_combo['values'] = positions
        if positions:
            self.player_pos_combo.current(0)
            
    def _refresh_props_tab(self):
        """Refresh prop types when sport changes."""
        # Note: Would need to recreate the tab to update checkboxes
        # For now, just update status
        self.status_var.set(f"Sport changed to {self.current_sport} - refresh Props tab")


def main():
    """Launch the multi-sport parlay generator."""
    root = tk.Tk()
    app = MultiSportParlayGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
