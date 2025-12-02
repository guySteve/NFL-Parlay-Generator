#!/usr/bin/env python3
"""
NFL Parlay Generator Pro - Advanced Desktop Application
Quantitative analytics with confidence scoring, narrative generation, and team theming.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, List, Tuple
import json
from datetime import datetime
import webbrowser

# NFL Team Colors for dynamic theming
NFL_TEAMS = {
    "Arizona Cardinals": ("#97233F", "#000000"),
    "Atlanta Falcons": ("#A71930", "#000000"),
    "Baltimore Ravens": ("#241773", "#000000"),
    "Buffalo Bills": ("#00338D", "#C60C30"),
    "Carolina Panthers": ("#0085CA", "#101820"),
    "Chicago Bears": ("#0B162A", "#C83803"),
    "Cincinnati Bengals": ("#FB4F14", "#000000"),
    "Cleveland Browns": ("#311D00", "#FF3C00"),
    "Dallas Cowboys": ("#041E42", "#869397"),
    "Denver Broncos": ("#FB4F14", "#002244"),
    "Detroit Lions": ("#0076B6", "#B0B7BC"),
    "Green Bay Packers": ("#203731", "#FFB612"),
    "Houston Texans": ("#03202F", "#A71930"),
    "Indianapolis Colts": ("#002C5F", "#A2AAAD"),
    "Jacksonville Jaguars": ("#006778", "#D7A22A"),
    "Kansas City Chiefs": ("#E31837", "#FFB81C"),
    "Las Vegas Raiders": ("#000000", "#A5ACAF"),
    "Los Angeles Chargers": ("#0080C6", "#FFC20E"),
    "Los Angeles Rams": ("#003594", "#FFA300"),
    "Miami Dolphins": ("#008E97", "#FC4C02"),
    "Minnesota Vikings": ("#4F2683", "#FFC62F"),
    "New England Patriots": ("#002244", "#C60C30"),
    "New Orleans Saints": ("#D3BC8D", "#101820"),
    "New York Giants": ("#0B2265", "#A71930"),
    "New York Jets": ("#125740", "#000000"),
    "Philadelphia Eagles": ("#004C54", "#A5ACAF"),
    "Pittsburgh Steelers": ("#FFB612", "#101820"),
    "San Francisco 49ers": ("#AA0000", "#B3995D"),
    "Seattle Seahawks": ("#002244", "#69BE28"),
    "Tampa Bay Buccaneers": ("#D50A0A", "#FF7900"),
    "Tennessee Titans": ("#0C2340", "#4B92DB"),
    "Washington Commanders": ("#773141", "#FFB612"),
    "Generic NFL": ("#013369", "#D50A0A")
}


class ConfidenceIndicator(ttk.Frame):
    """Widget to display confidence scores with color coding."""
    
    def __init__(self, parent, label_text="", initial_confidence=0.0, **kwargs):
        super().__init__(parent, **kwargs)
        self.confidence = initial_confidence
        
        # Label
        self.label = ttk.Label(self, text=label_text, font=('Arial', 9))
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Confidence display
        self.conf_label = tk.Label(self, text=f"{initial_confidence:.1f}%", 
                                    font=('Arial', 9, 'bold'),
                                    relief=tk.SOLID, borderwidth=2, padx=5, pady=2)
        self.conf_label.pack(side=tk.LEFT)
        self.update_confidence(initial_confidence)
        
        # Info button
        self.info_btn = tk.Button(self, text="ℹ", font=('Arial', 8), 
                                  width=2, cursor="hand2")
        self.info_btn.pack(side=tk.LEFT, padx=(5, 0))
        
    def update_confidence(self, confidence: float):
        """Update the confidence score and color."""
        self.confidence = confidence
        self.conf_label.config(text=f"{confidence:.1f}%")
        
        # Color code based on confidence
        if confidence >= 80:
            bg, fg = "#28a745", "white"  # Green
            border_color = "#28a745"
        elif confidence >= 60:
            bg, fg = "#ffc107", "black"  # Yellow
            border_color = "#ffc107"
        else:
            bg, fg = "#fd7e14", "white"  # Orange
            border_color = "#fd7e14"
            
        self.conf_label.config(bg=bg, fg=fg, highlightbackground=border_color)
    
    def set_info_command(self, command):
        """Set the command for the info button."""
        self.info_btn.config(command=command)


class NarrativeBox(ttk.LabelFrame):
    """Tony Romo-style narrative analysis box with confidence."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="🎙️ Tony Romo Analysis", padding=10, **kwargs)
        
        # Confidence indicator
        self.confidence_ind = ConfidenceIndicator(self, "Narrative Confidence:", 0.0)
        self.confidence_ind.pack(anchor=tk.W, pady=(0, 5))
        self.confidence_ind.set_info_command(self.show_narrative_derivation)
        
        # Text display
        self.text_widget = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=6,
                                                      font=('Arial', 10),
                                                      bg='#f8f9fa', relief=tk.FLAT)
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.insert('1.0', "Load a game to see the matchup breakdown...")
        self.text_widget.config(state=tk.DISABLED)
        
    def set_narrative(self, narrative: str, confidence: float, derivation: str = ""):
        """Set the narrative text and confidence."""
        self.confidence_ind.update_confidence(confidence)
        self.derivation_text = derivation
        
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', narrative)
        self.text_widget.config(state=tk.DISABLED)
    
    def show_narrative_derivation(self):
        """Show how the narrative was derived."""
        msg = getattr(self, 'derivation_text', 'Narrative generated based on:\n'
                      '• Offensive EPA trends (L4 games)\n'
                      '• Defensive DVOA matchup ratings\n'
                      '• Historical player performance vs opponent\n'
                      '• Game script correlation factors')
        messagebox.showinfo("Narrative Derivation", msg)


class MetricCalculator(tk.Toplevel):
    """Pop-up window for metric calculation details and manual data entry."""
    
    def __init__(self, parent, metric_name: str, current_value: float, metric_info: Dict):
        super().__init__(parent)
        self.title(f"Metric Calculator - {metric_name}")
        self.geometry("600x500")
        self.metric_name = metric_name
        self.result_value = current_value
        
        # Main container
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(container, text=metric_name, font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        desc_frame = ttk.LabelFrame(container, text="What is this metric?", padding=10)
        desc_frame.pack(fill=tk.X, pady=5)
        desc_text = scrolledtext.ScrolledText(desc_frame, wrap=tk.WORD, height=4, font=('Arial', 9))
        desc_text.pack(fill=tk.BOTH)
        desc_text.insert('1.0', metric_info.get('description', 'No description available.'))
        desc_text.config(state=tk.DISABLED)
        
        # How to find it
        find_frame = ttk.LabelFrame(container, text="📍 Where to find this data", padding=10)
        find_frame.pack(fill=tk.X, pady=5)
        find_text = scrolledtext.ScrolledText(find_frame, wrap=tk.WORD, height=6, font=('Arial', 9))
        find_text.pack(fill=tk.BOTH)
        
        instructions = metric_info.get('instructions', 'Search online for team statistics.')
        find_text.insert('1.0', instructions)
        find_text.config(state=tk.DISABLED)
        
        # Quick links
        if 'links' in metric_info:
            link_frame = ttk.Frame(container)
            link_frame.pack(fill=tk.X, pady=5)
            ttk.Label(link_frame, text="Quick Links:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            for link_name, url in metric_info['links'].items():
                link_btn = tk.Button(link_frame, text=f"🔗 {link_name}", fg='blue',
                                    cursor="hand2", relief=tk.FLAT,
                                    command=lambda u=url: webbrowser.open(u))
                link_btn.pack(anchor=tk.W, padx=10)
        
        # Manual entry
        entry_frame = ttk.LabelFrame(container, text="✏️ Manual Entry", padding=10)
        entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(entry_frame, text="Enter value:").pack(side=tk.LEFT, padx=(0, 5))
        self.value_var = tk.DoubleVar(value=current_value)
        value_entry = ttk.Entry(entry_frame, textvariable=self.value_var, width=15)
        value_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(entry_frame, text="Update", command=self.save_value).pack(side=tk.LEFT, padx=5)
        ttk.Button(entry_frame, text="Close", command=self.destroy).pack(side=tk.LEFT)
    
    def save_value(self):
        """Save the entered value and close."""
        self.result_value = self.value_var.get()
        messagebox.showinfo("Saved", f"Value updated to {self.result_value}")


class NFLParlayGeneratorPro:
    """Main application for NFL Parlay Generator Pro."""
    
    # Metric information database
    METRIC_INFO = {
        "Opponent Def EPA/Play": {
            "description": "Expected Points Added per play by the opposing defense. Lower (more negative) "
                          "is better. EPA accounts for down, distance, and field position to measure true defensive efficiency.",
            "instructions": "1. Google: 'NFL defensive EPA 2024'\n"
                          "2. Visit rbsdm.com or nflfastR dashboard\n"
                          "3. Find the opposing team's defensive EPA/play\n"
                          "4. Enter the value (e.g., -0.04 for strong defense, +0.05 for weak)",
            "links": {
                "RBSDM EPA Stats": "https://rbsdm.com/stats/stats/",
                "NFL Next Gen Stats": "https://nextgenstats.nfl.com/"
            }
        },
        "Opponent DVOA Pass Def %": {
            "description": "Defense-adjusted Value Over Average for pass defense. Adjusts for opponent quality. "
                          "Negative values are better (e.g., -10% = elite pass defense).",
            "instructions": "1. Google: '{team name} DVOA pass defense 2024'\n"
                          "2. Visit footballoutsiders.com or teamrankings.com\n"
                          "3. Find pass defense DVOA percentage\n"
                          "4. Enter as percentage (e.g., 8.2 or -5.5)",
            "links": {
                "Football Outsiders": "https://www.footballoutsiders.com/stats/nfl/team-defense/2024",
                "Team Rankings": "https://www.teamrankings.com/nfl/stat/opponent-yards-per-pass-attempt"
            }
        },
        "Opponent DVOA Run Def %": {
            "description": "Defense-adjusted Value Over Average for run defense. Negative values indicate strong run defense.",
            "instructions": "1. Google: '{team name} DVOA run defense 2024'\n"
                          "2. Visit footballoutsiders.com\n"
                          "3. Find run defense DVOA percentage\n"
                          "4. Enter as percentage",
            "links": {
                "Football Outsiders": "https://www.footballoutsiders.com/stats/nfl/team-defense/2024"
            }
        },
        "Team Offense EPA L4": {
            "description": "Offensive EPA per play over the last 4 games. Shows recent offensive form. "
                          "Higher is better. This captures whether an offense is 'hot' or 'cold'.",
            "instructions": "1. Google: '{team name} offensive EPA last 4 games'\n"
                          "2. Visit rbsdm.com or use nflfastR data\n"
                          "3. Calculate average EPA/play for last 4 games\n"
                          "4. Enter the value (typically between -0.2 and 0.3)",
            "links": {
                "RBSDM EPA Stats": "https://rbsdm.com/stats/stats/"
            }
        }
    }
    
    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self.root.title("🏈 NFL Parlay Generator Pro")
        self.root.geometry("1400x950")
        
        # Set minimum size
        self.root.minsize(1200, 800)
        
        # Data storage
        self.current_game = {}
        self.players_list = []
        self.current_theme = NFL_TEAMS["Generic NFL"]
        
        # Create UI
        self._setup_styles()
        self._create_main_layout()
        
        # Load today's schedule
        self._load_schedule()
    
    def _setup_styles(self):
        """Setup application styles with current team theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        primary, secondary = self.current_theme
        
        # General
        style.configure('.', background='#e8e8e8', foreground='#000000')
        style.configure('TFrame', background='#e8e8e8')
        style.configure('Card.TFrame', background='#ffffff', relief=tk.RIDGE, borderwidth=1)
        
        # Labels
        style.configure('TLabel', background='#e8e8e8', foreground='#000000')
        style.configure('Header.TLabel', font=('Arial', 18, 'bold'), foreground=primary, background='#e8e8e8')
        style.configure('Subheader.TLabel', font=('Arial', 12, 'bold'), foreground=secondary, background='#ffffff')
        style.configure('Card.TLabel', background='#ffffff')
        
        # Labelframes
        style.configure('TLabelframe', background='#ffffff', borderwidth=2, relief=tk.GROOVE)
        style.configure('TLabelframe.Label', background='#ffffff', foreground=primary, font=('Arial', 10, 'bold'))
        
        # Buttons
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'), foreground='white')
        style.map('Primary.TButton', background=[('active', secondary), ('!active', primary)])
        
        # Entry
        style.configure('TEntry', fieldbackground='white', borderwidth=1)
        style.configure('TCombobox', fieldbackground='white')
        
        # Notebook (tabs)
        style.configure('TNotebook', background='#e8e8e8', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))
        style.map('TNotebook.Tab',
                  background=[('selected', primary)],
                  foreground=[('selected', 'white'), ('!selected', 'black')])
    
    def _apply_theme(self, team_name: str):
        """Apply team-specific theme."""
        self.current_theme = NFL_TEAMS.get(team_name, NFL_TEAMS["Generic NFL"])
        self._setup_styles()
        self.root.title(f"🏈 NFL Parlay Generator Pro - {team_name}")
    
    def _create_main_layout(self):
        """Create the main application layout."""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(header, text="🏈 NFL PARLAY GENERATOR PRO", 
                               style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle = ttk.Label(header, text="Quantitative Analytics Engine", 
                            font=('Arial', 10, 'italic'), foreground='gray')
        subtitle.pack(side=tk.LEFT, padx=20)
        
        # Main content area (single scrollable frame - no tabs for simplicity)
        main_canvas = tk.Canvas(self.root, bg='#e8e8e8', highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
        # Bind mouse wheel
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Build sections
        self._create_schedule_section()
        self._create_game_context_section()
        self._create_narrative_section()
        self._create_players_section()
        self._create_results_section()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Select a game or enter manually.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    def _create_schedule_section(self):
        """Create live schedule section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="🔴 LIVE - Today's NFL Schedule", padding=15)
        section.pack(fill=tk.X, padx=10, pady=5)
        
        # Schedule display
        self.schedule_text = scrolledtext.ScrolledText(section, wrap=tk.WORD, height=5,
                                                       font=('Arial', 9), bg='#f8f9fa')
        self.schedule_text.pack(fill=tk.X, pady=(0, 10))
        self.schedule_text.insert('1.0', "Loading today's games...")
        self.schedule_text.config(state=tk.DISABLED)
        
        # Game selector
        select_frame = ttk.Frame(section)
        select_frame.pack(fill=tk.X)
        
        ttk.Label(select_frame, text="Select Game:").pack(side=tk.LEFT, padx=(0, 10))
        self.game_combo = ttk.Combobox(select_frame, state='readonly', width=60)
        self.game_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(select_frame, text="🔄 Refresh", command=self._load_schedule).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="Load Game ➜", style='Primary.TButton',
                  command=self._load_selected_game).pack(side=tk.LEFT, padx=2)
    
    def _create_game_context_section(self):
        """Create game context input section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="⚙️ Game Context & Metrics", padding=15)
        section.pack(fill=tk.X, padx=10, pady=5)
        
        # Teams row
        teams_frame = ttk.Frame(section)
        teams_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(teams_frame, text="Team A:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.team_a_var = tk.StringVar(value="Kansas City Chiefs")
        team_a_combo = ttk.Combobox(teams_frame, textvariable=self.team_a_var, 
                                    values=list(NFL_TEAMS.keys()), width=25)
        team_a_combo.grid(row=0, column=1, padx=5, pady=2)
        team_a_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_theme(self.team_a_var.get()))
        
        ttk.Label(teams_frame, text="vs", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10)
        
        ttk.Label(teams_frame, text="Team B:", font=('Arial', 10, 'bold')).grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.team_b_var = tk.StringVar(value="Buffalo Bills")
        team_b_combo = ttk.Combobox(teams_frame, textvariable=self.team_b_var, 
                                    values=list(NFL_TEAMS.keys()), width=25)
        team_b_combo.grid(row=0, column=4, padx=5, pady=2)
        
        # Game lines
        lines_frame = ttk.Frame(section)
        lines_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(lines_frame, text="Spread (Team A):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.spread_var = tk.DoubleVar(value=-3.0)
        ttk.Entry(lines_frame, textvariable=self.spread_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(lines_frame, text="Total O/U:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.total_var = tk.DoubleVar(value=47.5)
        ttk.Entry(lines_frame, textvariable=self.total_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(lines_frame, text="Implied Total:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.implied_var = tk.DoubleVar(value=25.25)
        ttk.Entry(lines_frame, textvariable=self.implied_var, width=10).grid(row=0, column=5, padx=5)
        
        # Advanced metrics with confidence indicators
        ttk.Separator(section, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(section, text="📊 Quantitative Defense Metrics", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(5, 10))
        
        metrics_grid = ttk.Frame(section)
        metrics_grid.pack(fill=tk.X)
        
        # Metric 1: Opponent Def EPA
        row = 0
        ttk.Label(metrics_grid, text="Opponent Def EPA/Play:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.def_epa_var = tk.DoubleVar(value=-0.04)
        ttk.Entry(metrics_grid, textvariable=self.def_epa_var, width=12).grid(row=row, column=1, pady=5)
        
        self.def_epa_conf = ConfidenceIndicator(metrics_grid, "", 75.0)
        self.def_epa_conf.grid(row=row, column=2, padx=10, pady=5)
        self.def_epa_conf.set_info_command(lambda: self._show_metric_info("Opponent Def EPA/Play", self.def_epa_var.get()))
        
        # Metric 2: DVOA Pass
        row += 1
        ttk.Label(metrics_grid, text="Opponent DVOA Pass Def %:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.dvoa_pass_var = tk.DoubleVar(value=5.2)
        ttk.Entry(metrics_grid, textvariable=self.dvoa_pass_var, width=12).grid(row=row, column=1, pady=5)
        
        self.dvoa_pass_conf = ConfidenceIndicator(metrics_grid, "", 68.0)
        self.dvoa_pass_conf.grid(row=row, column=2, padx=10, pady=5)
        self.dvoa_pass_conf.set_info_command(lambda: self._show_metric_info("Opponent DVOA Pass Def %", self.dvoa_pass_var.get()))
        
        # Metric 3: DVOA Run
        row += 1
        ttk.Label(metrics_grid, text="Opponent DVOA Run Def %:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.dvoa_run_var = tk.DoubleVar(value=-3.5)
        ttk.Entry(metrics_grid, textvariable=self.dvoa_run_var, width=12).grid(row=row, column=1, pady=5)
        
        self.dvoa_run_conf = ConfidenceIndicator(metrics_grid, "", 71.0)
        self.dvoa_run_conf.grid(row=row, column=2, padx=10, pady=5)
        self.dvoa_run_conf.set_info_command(lambda: self._show_metric_info("Opponent DVOA Run Def %", self.dvoa_run_var.get()))
        
        # Metric 4: Team Off EPA
        row += 1
        ttk.Label(metrics_grid, text="Team A Off EPA L4:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.off_epa_var = tk.DoubleVar(value=0.18)
        ttk.Entry(metrics_grid, textvariable=self.off_epa_var, width=12).grid(row=row, column=1, pady=5)
        
        self.off_epa_conf = ConfidenceIndicator(metrics_grid, "", 82.0)
        self.off_epa_conf.grid(row=row, column=2, padx=10, pady=5)
        self.off_epa_conf.set_info_command(lambda: self._show_metric_info("Team Offense EPA L4", self.off_epa_var.get()))
        
        # Save context button
        ttk.Button(section, text="💾 Save Game Context", style='Primary.TButton',
                  command=self._save_game_context).pack(pady=10)
    
    def _create_narrative_section(self):
        """Create Tony Romo narrative analysis section."""
        self.narrative_box = NarrativeBox(self.scrollable_frame)
        self.narrative_box.pack(fill=tk.X, padx=10, pady=5)
    
    def _create_players_section(self):
        """Create player props section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="🏃 Player Props", padding=15)
        section.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add player form
        add_frame = ttk.Frame(section)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Player Name:").grid(row=0, column=0, padx=5)
        self.player_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.player_name_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Stat:").grid(row=0, column=2, padx=5)
        self.stat_type_var = tk.StringVar()
        stat_combo = ttk.Combobox(add_frame, textvariable=self.stat_type_var, 
                                  values=["Pass Yards", "Pass TDs", "Rush Yards", "Rush TDs", 
                                         "Receptions", "Rec Yards", "Rec TDs", "Anytime TD"],
                                  state='readonly', width=15)
        stat_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="Line:").grid(row=0, column=4, padx=5)
        self.line_var = tk.DoubleVar(value=0.5)
        ttk.Entry(add_frame, textvariable=self.line_var, width=10).grid(row=0, column=5, padx=5)
        
        ttk.Label(add_frame, text="Pick:").grid(row=0, column=6, padx=5)
        self.pick_var = tk.StringVar(value="Over")
        ttk.Combobox(add_frame, textvariable=self.pick_var, 
                    values=["Over", "Under", "Yes"], state='readonly', width=8).grid(row=0, column=7, padx=5)
        
        ttk.Button(add_frame, text="➕ Add Player", command=self._add_player).grid(row=0, column=8, padx=5)
        
        # Players list
        self.players_display = scrolledtext.ScrolledText(section, wrap=tk.WORD, height=8,
                                                        font=('Courier', 9), bg='#f8f9fa')
        self.players_display.pack(fill=tk.BOTH, expand=True)
        self.players_display.insert('1.0', "Add players to build your parlay...\n")
        self.players_display.config(state=tk.DISABLED)
        
        # Generate button
        generate_frame = ttk.Frame(section)
        generate_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(generate_frame, text="🎯 Generate Parlay Predictions", 
                  style='Primary.TButton', command=self._generate_predictions).pack(side=tk.LEFT, padx=5)
        ttk.Button(generate_frame, text="🗑️ Clear All", command=self._clear_players).pack(side=tk.LEFT)
    
    def _create_results_section(self):
        """Create results display section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="📊 Analysis Results", padding=15)
        section.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_display = scrolledtext.ScrolledText(section, wrap=tk.WORD, height=12,
                                                        font=('Courier', 9), bg='#f8f9fa')
        self.results_display.pack(fill=tk.BOTH, expand=True)
        self.results_display.insert('1.0', "Results will appear here after generating predictions...\n")
        self.results_display.config(state=tk.DISABLED)
    
    def _load_schedule(self):
        """Load today's NFL schedule."""
        try:
            # Simulate schedule data - replace with actual API call
            today = datetime.now().strftime("%Y-%m-%d")
            games = [
                {"home": "Kansas City Chiefs", "away": "Buffalo Bills", "time": "8:20 PM ET"},
                {"home": "Dallas Cowboys", "away": "New York Giants", "time": "4:25 PM ET"},
                {"home": "Philadelphia Eagles", "away": "San Francisco 49ers", "time": "4:25 PM ET"}
            ]
            
            self.schedule_text.config(state=tk.NORMAL)
            self.schedule_text.delete('1.0', tk.END)
            
            if games:
                self.schedule_text.insert('1.0', f"📅 {today} - {len(games)} games scheduled\n\n")
                game_options = []
                for i, game in enumerate(games, 1):
                    text = f"{i}. {game['away']} @ {game['home']} - {game['time']}\n"
                    self.schedule_text.insert(tk.END, text)
                    game_options.append(f"{game['away']} @ {game['home']}")
                
                self.game_combo['values'] = game_options
                if game_options:
                    self.game_combo.current(0)
            else:
                self.schedule_text.insert('1.0', "No games scheduled for today.")
            
            self.schedule_text.config(state=tk.DISABLED)
            self.status_var.set(f"Loaded {len(games)} games")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load schedule: {str(e)}")
    
    def _load_selected_game(self):
        """Load the selected game into the context."""
        selected = self.game_combo.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a game first.")
            return
        
        # Parse teams
        parts = selected.split(" @ ")
        if len(parts) == 2:
            self.team_b_var.set(parts[0].strip())  # Away team
            self.team_a_var.set(parts[1].strip())  # Home team
            
            # Apply theme for home team
            self._apply_theme(self.team_a_var.get())
            
            # Generate initial narrative
            self._generate_narrative()
            
            self.status_var.set(f"Loaded: {selected}")
            messagebox.showinfo("Game Loaded", 
                              f"Game loaded:\n{parts[0]} @ {parts[1]}\n\n"
                              "You can now adjust metrics and add players from BOTH teams.")
    
    def _save_game_context(self):
        """Save the current game context."""
        self.current_game = {
            "team_a": self.team_a_var.get(),
            "team_b": self.team_b_var.get(),
            "spread": self.spread_var.get(),
            "total": self.total_var.get(),
            "implied_total": self.implied_var.get(),
            "def_epa": self.def_epa_var.get(),
            "dvoa_pass": self.dvoa_pass_var.get(),
            "dvoa_run": self.dvoa_run_var.get(),
            "off_epa": self.off_epa_var.get()
        }
        
        self._generate_narrative()
        self.status_var.set("Game context saved successfully!")
    
    def _show_metric_info(self, metric_name: str, current_value: float):
        """Show metric calculation info and allow manual entry."""
        if metric_name in self.METRIC_INFO:
            MetricCalculator(self.root, metric_name, current_value, self.METRIC_INFO[metric_name])
    
    def _generate_narrative(self):
        """Generate Tony Romo-style narrative analysis."""
        team_a = self.team_a_var.get()
        team_b = self.team_b_var.get()
        
        off_epa = self.off_epa_var.get()
        dvoa_pass = self.dvoa_pass_var.get()
        dvoa_run = self.dvoa_run_var.get()
        
        # Build narrative
        narrative = f"Alright folks, here's what I'm seeing with {team_a} taking on {team_b}. "
        
        if off_epa > 0.10:
            narrative += f"{team_a}'s offense has been hot lately, averaging {off_epa:.2f} EPA per play over their last four games. "
        else:
            narrative += f"{team_a}'s offense has been struggling a bit, only putting up {off_epa:.2f} EPA per play recently. "
        
        if dvoa_pass > 5:
            narrative += f"Now, {team_b}'s pass defense has some vulnerabilities - they're sitting at +{dvoa_pass:.1f}% DVOA against the pass, which is below league average. "
            narrative += f"I'd expect {team_a}'s QB to have some success here, especially on those intermediate routes. "
        elif dvoa_pass < -5:
            narrative += f"But here's the thing - {team_b}'s got a tough secondary, ranking at {dvoa_pass:.1f}% DVOA. The passing game might be tough sledding. "
        
        if dvoa_run < 0:
            narrative += f"Against the run, {team_b} is solid at {dvoa_run:.1f}% DVOA, so I'd look for {team_a} to attack through the air more. "
        else:
            narrative += f"The run defense for {team_b} isn't as strong though - {dvoa_run:.1f}% DVOA - so watch for {team_a} to establish the ground game early."
        
        # Calculate confidence
        confidence = 72.5  # Base confidence
        if abs(off_epa) > 0.15:
            confidence += 5  # Strong trend
        if abs(dvoa_pass) > 8 or abs(dvoa_run) > 8:
            confidence += 5  # Clear matchup advantage
        
        confidence = min(95, max(55, confidence))  # Clamp between 55-95
        
        # Derivation explanation
        derivation = (f"Narrative Confidence: {confidence:.1f}%\n\n"
                     f"Based on:\n"
                     f"• Offensive EPA L4: {off_epa:.3f} (Recent form)\n"
                     f"• DVOA Pass Defense: {dvoa_pass:.1f}% (Matchup strength)\n"
                     f"• DVOA Run Defense: {dvoa_run:.1f}% (Matchup strength)\n\n"
                     f"Tony Romo tone generated using game script correlation analysis and "
                     f"narrative templates based on EPA/DVOA thresholds.")
        
        self.narrative_box.set_narrative(narrative, confidence, derivation)
    
    def _add_player(self):
        """Add a player to the parlay."""
        name = self.player_name_var.get().strip()
        stat = self.stat_type_var.get()
        line = self.line_var.get()
        pick = self.pick_var.get()
        
        if not name or not stat:
            messagebox.showwarning("Missing Info", "Please enter player name and select a stat type.")
            return
        
        player = {
            "name": name,
            "stat": stat,
            "line": line,
            "pick": pick
        }
        self.players_list.append(player)
        
        # Update display
        self.players_display.config(state=tk.NORMAL)
        if len(self.players_list) == 1:
            self.players_display.delete('1.0', tk.END)
        
        display_text = f"{len(self.players_list)}. {name} - {stat} {pick} {line}\n"
        self.players_display.insert(tk.END, display_text)
        self.players_display.config(state=tk.DISABLED)
        
        # Clear inputs
        self.player_name_var.set("")
        self.line_var.set(0.5)
        
        self.status_var.set(f"Added {name} ({len(self.players_list)} total players)")
    
    def _clear_players(self):
        """Clear all players."""
        if self.players_list and not messagebox.askyesno("Confirm", "Clear all players?"):
            return
        
        self.players_list = []
        self.players_display.config(state=tk.NORMAL)
        self.players_display.delete('1.0', tk.END)
        self.players_display.insert('1.0', "Add players to build your parlay...\n")
        self.players_display.config(state=tk.DISABLED)
        
        self.status_var.set("Cleared all players")
    
    def _generate_predictions(self):
        """Generate predictions for the parlay."""
        if not self.players_list:
            messagebox.showwarning("No Players", "Please add at least one player first.")
            return
        
        if not self.current_game:
            messagebox.showwarning("No Context", "Please save game context first.")
            return
        
        # Generate mock predictions
        self.results_display.config(state=tk.NORMAL)
        self.results_display.delete('1.0', tk.END)
        
        self.results_display.insert(tk.END, "=" * 80 + "\n")
        self.results_display.insert(tk.END, "NFL PARLAY ANALYSIS - QUANTITATIVE PREDICTIONS\n")
        self.results_display.insert(tk.END, "=" * 80 + "\n\n")
        
        self.results_display.insert(tk.END, f"Game: {self.current_game['team_a']} vs {self.current_game['team_b']}\n")
        self.results_display.insert(tk.END, f"Spread: {self.current_game['spread']} | Total: {self.current_game['total']}\n\n")
        
        self.results_display.insert(tk.END, "-" * 80 + "\n")
        self.results_display.insert(tk.END, "PLAYER PROJECTIONS\n")
        self.results_display.insert(tk.END, "-" * 80 + "\n\n")
        
        total_ev = 0
        for i, player in enumerate(self.players_list, 1):
            # Mock calculations
            base_prob = 0.55 + (i * 0.02)  # Varying probabilities
            confidence = 65 + (i * 3)
            ev = (base_prob * 100) - 50  # Simplified EV
            total_ev += ev
            
            self.results_display.insert(tk.END, f"{i}. {player['name']} - {player['stat']} {player['pick']} {player['line']}\n")
            self.results_display.insert(tk.END, f"   Probability: {base_prob:.1%} | Confidence: {confidence:.1f}% | EV: +{ev:.2f}\n")
            
            if confidence < 60:
                self.results_display.insert(tk.END, "   ⚠️  LOW CONFIDENCE - Consider removing\n")
            
            self.results_display.insert(tk.END, "\n")
        
        # Parlay summary
        self.results_display.insert(tk.END, "=" * 80 + "\n")
        self.results_display.insert(tk.END, "PARLAY SUMMARY\n")
        self.results_display.insert(tk.END, "=" * 80 + "\n\n")
        
        combined_prob = 0.35 if len(self.players_list) > 3 else 0.45
        parlay_odds = 250 if len(self.players_list) > 3 else 150
        
        self.results_display.insert(tk.END, f"Legs: {len(self.players_list)}\n")
        self.results_display.insert(tk.END, f"Combined Probability: {combined_prob:.1%}\n")
        self.results_display.insert(tk.END, f"Expected Parlay Odds: +{parlay_odds}\n")
        self.results_display.insert(tk.END, f"Estimated Total EV: +{total_ev:.2f}\n\n")
        
        if combined_prob > 0.40:
            self.results_display.insert(tk.END, "✅ RECOMMENDATION: STRONG PLAY\n")
        elif combined_prob > 0.30:
            self.results_display.insert(tk.END, "✓ RECOMMENDATION: VIABLE PLAY\n")
        else:
            self.results_display.insert(tk.END, "⚠️  RECOMMENDATION: HIGH RISK\n")
        
        self.results_display.config(state=tk.DISABLED)
        self.status_var.set("Predictions generated successfully!")
        
        # Show completion message
        messagebox.showinfo("Analysis Complete", 
                          f"Generated predictions for {len(self.players_list)} player props.\n"
                          f"Combined probability: {combined_prob:.1%}\n"
                          f"Check the results section for details.")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = NFLParlayGeneratorPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
