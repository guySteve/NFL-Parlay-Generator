#!/usr/bin/env python3
"""
Enhanced GUI Demo - Confidence Scores + Narrative Analysis + Data Collection Guide

Demonstrates the complete enhanced interface with:
1. Confidence scores with visual indicators
2. Info buttons with step-by-step data collection instructions
3. Narrative analysis box with AI modifier
4. Orange borders for low confidence
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from data_collection_guide import DataCollectionGuide
from matchup_narrative import MatchupNarrator


class EnhancedMetricWidget(ttk.Frame):
    """Enhanced metric widget with confidence and data guide."""
    
    def __init__(self, parent, label_text: str, variable: tk.Variable, 
                 guide_key: str, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.variable = variable
        self.guide_key = guide_key
        self.confidence = tk.DoubleVar(value=0.0)
        
        # Container
        self.inner_frame = ttk.Frame(self, style='Metric.TFrame')
        self.inner_frame.pack(fill=tk.X, padx=3, pady=3)
        
        # Label
        ttk.Label(
            self.inner_frame,
            text=label_text,
            width=28,
            anchor='w',
            font=('Arial', 10)
        ).grid(row=0, column=0, sticky='w', padx=5)
        
        # Entry
        entry = ttk.Entry(
            self.inner_frame,
            textvariable=variable,
            width=12,
            font=('Arial', 10)
        )
        entry.grid(row=0, column=1, padx=5)
        entry.bind('<KeyRelease>', self._update_confidence)
        entry.bind('<FocusOut>', self._update_confidence)
        
        # Info button
        info_btn = ttk.Button(
            self.inner_frame,
            text="ℹ️",
            width=3,
            command=self._show_data_guide,
            style='Info.TButton'
        )
        info_btn.grid(row=0, column=2, padx=2)
        
        # Confidence indicator
        self.confidence_label = tk.Label(
            self.inner_frame,
            text="",
            width=10,
            font=('Arial', 9, 'bold'),
            bg='#f5f5f5'
        )
        self.confidence_label.grid(row=0, column=3, padx=5)
        
        # Initial update
        self._update_confidence()
    
    def _update_confidence(self, event=None):
        """Update confidence based on entry value."""
        try:
            value = self.variable.get()
            if value == "" or value is None:
                confidence = 0.0
                color = '#999999'
                symbol = '⚠'
                text = "Empty"
                border_color = '#fd7e14'  # Orange
            else:
                float(value)  # Validate it's a number
                confidence = 85.0  # Manual entry = 85%
                if confidence >= 75:
                    color = '#28a745'  # Green
                    symbol = '✓'
                    border_color = '#28a745'
                elif confidence >= 60:
                    color = '#ffc107'  # Yellow
                    symbol = '⚠'
                    border_color = '#ffc107'
                else:
                    color = '#fd7e14'  # Orange
                    symbol = '⚠'
                    border_color = '#fd7e14'
                
                text = f"{symbol} {confidence:.0f}%"
            
            self.confidence.set(confidence)
            self.confidence_label.configure(text=text, fg=color)
            
            # Update border for low confidence
            if confidence < 60:
                self.inner_frame.configure(style='Warning.TFrame')
                self.configure(
                    relief='solid',
                    borderwidth=2,
                    padding=2
                )
                # Can't set border color directly in ttk, use workaround
                self.configure(style='WarningBorder.TFrame')
            else:
                self.configure(relief='flat', borderwidth=0, padding=0)
                
        except ValueError:
            self.confidence.set(0.0)
            self.confidence_label.configure(text="⚠ Invalid", fg='#dc3545')
    
    def _show_data_guide(self):
        """Show step-by-step data collection guide."""
        guide = DataCollectionGuide.get_instructions(self.guide_key)
        
        # Create custom dialog
        dialog = tk.Toplevel()
        dialog.title(guide['title'])
        dialog.geometry("800x700")
        dialog.transient(self.winfo_toplevel())
        
        # Header
        header = tk.Frame(dialog, bg='#0066cc', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=guide['title'],
            font=('Arial', 14, 'bold'),
            bg='#0066cc',
            fg='white'
        ).pack(pady=15)
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg='white')
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content sections
        content_frame = ttk.Frame(scrollable_frame, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # What is it?
        ttk.Label(
            content_frame,
            text="📖 What is this metric?",
            font=('Arial', 12, 'bold'),
            foreground='#0066cc'
        ).pack(anchor='w', pady=(0, 5))
        
        what_label = tk.Text(
            content_frame,
            height=4,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#f0f8ff',
            relief='flat',
            padx=10,
            pady=10
        )
        what_label.insert('1.0', guide['what_is_it'])
        what_label.configure(state='disabled')
        what_label.pack(fill=tk.X, pady=(0, 15))
        
        # Step by step
        ttk.Label(
            content_frame,
            text="📝 Step-by-Step Instructions",
            font=('Arial', 12, 'bold'),
            foreground='#0066cc'
        ).pack(anchor='w', pady=(0, 5))
        
        steps_text = scrolledtext.ScrolledText(
            content_frame,
            height=20,
            wrap=tk.WORD,
            font=('Courier New', 9),
            bg='#ffffff',
            relief='solid',
            borderwidth=1,
            padx=15,
            pady=15
        )
        steps_text.insert('1.0', guide['step_by_step'])
        steps_text.configure(state='disabled')
        steps_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Example
        ttk.Label(
            content_frame,
            text="✓ Example",
            font=('Arial', 12, 'bold'),
            foreground='#28a745'
        ).pack(anchor='w', pady=(0, 5))
        
        example_label = tk.Text(
            content_frame,
            height=6,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#f0fff0',
            relief='flat',
            padx=10,
            pady=10
        )
        example_label.insert('1.0', guide['example'])
        example_label.configure(state='disabled')
        example_label.pack(fill=tk.X, pady=(0, 15))
        
        # Quick search
        search_frame = ttk.Frame(content_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            search_frame,
            text="🔍 Quick Google Search:",
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        search_entry = ttk.Entry(search_frame, width=50, font=('Arial', 9))
        search_entry.insert(0, guide['google_search'])
        search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(
            dialog,
            text="Got It!",
            command=dialog.destroy,
            style='Primary.TButton'
        ).pack(pady=10)
        
        dialog.focus()


class EnhancedGUIDemo:
    """Demo of enhanced GUI with all features."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏈 NFL Parlay Generator - Enhanced Interface")
        self.root.geometry("1000x900")
        
        # Variables
        self.team_var = tk.StringVar(value="Kansas City Chiefs")
        self.opponent_var = tk.StringVar(value="Denver Broncos")
        self.spread_var = tk.DoubleVar(value=-7.5)
        self.total_var = tk.DoubleVar(value=45.5)
        
        self.opp_def_epa_var = tk.DoubleVar(value=-0.08)
        self.opp_dvoa_pass_var = tk.DoubleVar(value=12.5)
        self.opp_dvoa_run_var = tk.DoubleVar(value=-8.2)
        self.team_off_epa_var = tk.DoubleVar(value=0.18)
        
        self.ai_modifier_var = tk.DoubleVar(value=1.0)
        
        self._setup_styles()
        self._create_widgets()
    
    def _setup_styles(self):
        """Setup visual styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        primary = '#E31837'  # Chiefs red
        secondary = '#FFB81C'  # Chiefs gold
        
        style.configure('TFrame', background='#f5f5f5')
        style.configure('Metric.TFrame', background='#ffffff')
        style.configure('Warning.TFrame', background='#fff3cd', bordercolor='#fd7e14')
        style.configure('WarningBorder.TFrame', background='#fff3cd', relief='solid', borderwidth=2)
        
        style.configure('TLabelframe', background='#ffffff', bordercolor=primary, borderwidth=2)
        style.configure('TLabelframe.Label', 
                       background='#ffffff', 
                       foreground=primary, 
                       font=('Arial', 11, 'bold'))
        
        style.configure('Primary.TButton',
                       font=('Arial', 10, 'bold'),
                       background=primary,
                       foreground='white')
        
        style.configure('Info.TButton',
                       font=('Arial', 12, 'bold'))
    
    def _create_widgets(self):
        """Create all widgets."""
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(
            main,
            text="🏈 NFL Parlay Generator - Enhanced Interface",
            font=('Arial', 16, 'bold'),
            bg='#f5f5f5',
            fg='#E31837'
        )
        title.pack(pady=(0, 15))
        
        # Game info frame
        game_frame = ttk.LabelFrame(main, text="Game Context", padding=15)
        game_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(game_frame, text="Team:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(game_frame, textvariable=self.team_var, width=25).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(game_frame, text="Opponent:", font=('Arial', 10)).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        ttk.Entry(game_frame, textvariable=self.opponent_var, width=25).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(game_frame, text="Spread:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(game_frame, textvariable=self.spread_var, width=10).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # EPA/DVOA Metrics frame
        metrics_frame = ttk.LabelFrame(main, text="📊 EPA/DVOA Metrics (Click ℹ️ for help)", padding=15)
        metrics_frame.pack(fill=tk.X, pady=(0, 15))
        
        EnhancedMetricWidget(
            metrics_frame,
            "Opponent Def EPA/Play:",
            self.opp_def_epa_var,
            "Opponent Def EPA/Play:"
        ).pack(fill=tk.X, pady=3)
        
        EnhancedMetricWidget(
            metrics_frame,
            "Opponent DVOA Pass Def %:",
            self.opp_dvoa_pass_var,
            "Opponent DVOA Pass Def %:"
        ).pack(fill=tk.X, pady=3)
        
        EnhancedMetricWidget(
            metrics_frame,
            "Opponent DVOA Run Def %:",
            self.opp_dvoa_run_var,
            "Opponent DVOA Run Def %:"
        ).pack(fill=tk.X, pady=3)
        
        EnhancedMetricWidget(
            metrics_frame,
            "Team Offensive EPA (L4):",
            self.team_off_epa_var,
            "Team Off EPA (L4):"
        ).pack(fill=tk.X, pady=3)
        
        # AI Modifier frame
        ai_frame = ttk.LabelFrame(main, text="🤖 AI Analysis Modifier", padding=15)
        ai_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            ai_frame,
            text="Adjust AI confidence level:",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        slider_frame = ttk.Frame(ai_frame)
        slider_frame.pack(fill=tk.X)
        
        tk.Scale(
            slider_frame,
            from_=0.5,
            to=1.5,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.ai_modifier_var,
            length=400,
            bg='#ffffff',
            font=('Arial', 9)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.ai_label = tk.Label(
            slider_frame,
            text="Standard (1.0x)",
            font=('Arial', 10, 'bold'),
            bg='#f5f5f5',
            width=20
        )
        self.ai_label.pack(side=tk.LEFT, padx=10)
        
        self.ai_modifier_var.trace('w', self._update_ai_label)
        
        # Generate button
        ttk.Button(
            main,
            text="🔮 Generate Narrative Analysis",
            command=self._generate_narrative,
            style='Primary.TButton'
        ).pack(pady=10)
        
        # Narrative output
        narrative_frame = ttk.LabelFrame(main, text="📝 Matchup Narrative Analysis", padding=15)
        narrative_frame.pack(fill=tk.BOTH, expand=True)
        
        self.narrative_text = scrolledtext.ScrolledText(
            narrative_frame,
            height=15,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#ffffff',
            padx=15,
            pady=15
        )
        self.narrative_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert default narrative
        self._generate_narrative()
    
    def _update_ai_label(self, *args):
        """Update AI modifier label."""
        value = self.ai_modifier_var.get()
        if value < 0.8:
            text = f"Conservative ({value:.1f}x)"
            color = '#ffc107'
        elif value > 1.2:
            text = f"Aggressive ({value:.1f}x)"
            color = '#E31837'
        else:
            text = f"Standard ({value:.1f}x)"
            color = '#28a745'
        
        self.ai_label.configure(text=text, fg=color)
    
    def _generate_narrative(self):
        """Generate and display narrative analysis."""
        narrator = MatchupNarrator(ai_modifier=self.ai_modifier_var.get())
        
        analysis = narrator.generate_narrative(
            team_name=self.team_var.get(),
            opponent_name=self.opponent_var.get(),
            spread=self.spread_var.get(),
            opponent_def_epa=self.opp_def_epa_var.get(),
            opponent_dvoa_pass=self.opp_dvoa_pass_var.get(),
            opponent_dvoa_run=self.opp_dvoa_run_var.get(),
            team_offense_epa_l4=self.team_off_epa_var.get()
        )
        
        self.narrative_text.delete('1.0', tk.END)
        self.narrative_text.insert('1.0', analysis.full_narrative)


if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedGUIDemo(root)
    root.mainloop()
