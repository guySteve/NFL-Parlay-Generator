#!/usr/bin/env python3
"""
NFL Parlay Generator - Enhanced GUI with Confidence Scores
Modern NFL-themed interface with quantitative analytics
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple
import math

class ConfidenceWidget(ttk.Frame):
    """Widget that displays a metric with confidence score and info button."""
    
    def __init__(self, parent, label_text: str, variable: tk.Variable, 
                 confidence_calculator=None, info_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.variable = variable
        self.confidence_calc = confidence_calculator
        self.confidence_value = tk.DoubleVar(value=75.0)  # Default confidence
        
        # Main container
        container = ttk.Frame(self)
        container.pack(fill=tk.X, padx=2, pady=2)
        
        # Label with info button
        label_frame = ttk.Frame(container)
        label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(label_frame, text=label_text, width=25, anchor='w').pack(side=tk.LEFT)
        
        if info_callback:
            info_btn = ttk.Button(label_frame, text="ℹ️", width=3, 
                                 command=lambda: info_callback(label_text))
            info_btn.pack(side=tk.LEFT, padx=2)
        
        # Entry field
        entry = ttk.Entry(container, textvariable=variable, width=15)
        entry.pack(side=tk.LEFT, padx=5)
        entry.bind('<KeyRelease>', self._update_confidence)
        
        # Confidence indicator
        self.confidence_label = ttk.Label(container, text="", width=10)
        self.confidence_label.pack(side=tk.LEFT, padx=5)
        
        # Update initial confidence
        self._update_confidence()
        
    def _update_confidence(self, event=None):
        """Update confidence score and visual indicator."""
        if self.confidence_calc:
            confidence = self.confidence_calc(self.variable.get())
        else:
            # Default: assume 100% confidence for manually entered data
            try:
                float(self.variable.get())
                confidence = 85.0  # Manual entry = 85% confidence
            except:
                confidence = 0.0
        
        self.confidence_value.set(confidence)
        
        # Update visual indicator
        if confidence >= 75:
            color = '#28a745'  # Green
            symbol = '✓'
        elif confidence >= 60:
            color = '#ffc107'  # Yellow
            symbol = '⚠'
        else:
            color = '#fd7e14'  # Orange/Red
            symbol = '⚠'
            self.configure(relief='solid', borderwidth=2)
            self.configure(style='Warning.TFrame')
        
        self.confidence_label.configure(
            text=f"{symbol} {confidence:.0f}%",
            foreground=color,
            font=('Arial', 9, 'bold')
        )


def create_tooltip(widget, text):
    """Create a tooltip for a widget."""
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, background="#ffffe0", 
                        relief='solid', borderwidth=1, font=('Arial', 9),
                        wraplength=300, justify='left', padx=10, pady=5)
        label.pack()
        
        widget.tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
    
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


# Test window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Confidence Widget Test")
    root.geometry("600x400")
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Warning.TFrame', background='#fff3cd', bordercolor='#fd7e14')
    
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="EPA/DVOA Metrics with Confidence", 
             font=('Arial', 14, 'bold')).pack(pady=10)
    
    # Example metrics
    epa_var = tk.DoubleVar(value=-0.04)
    dvoa_pass_var = tk.DoubleVar(value=8.2)
    dvoa_run_var = tk.DoubleVar(value=-5.5)
    
    def show_calculation_info(metric_name):
        info_text = {
            "Opponent Def EPA/Play:": 
                "EPA (Expected Points Added) per play.\n\n"
                "Calculation: Average of (Points Scored - Expected Points)\n"
                "across all defensive plays.\n\n"
                "Negative = Good defense\n"
                "Positive = Bad defense\n\n"
                "Data Source: RBSDM.com or nfelo.com\n"
                "Confidence: 85% (manual entry)",
            
            "Opponent DVOA Pass Def %:":
                "Defense-adjusted Value Over Average vs Pass.\n\n"
                "Calculation: (Actual Success Rate - Expected) / Expected\n"
                "adjusted for opponent quality and situation.\n\n"
                "Negative % = Good pass defense\n"
                "Positive % = Bad pass defense\n\n"
                "Data Source: FootballOutsiders.com\n"
                "Confidence: 85% (manual entry)",
            
            "Opponent DVOA Run Def %:":
                "Defense-adjusted Value Over Average vs Run.\n\n"
                "Similar to Pass DVOA but for rushing plays only.\n\n"
                "Data Source: FootballOutsiders.com\n"
                "Confidence: 85% (manual entry)"
        }
        
        messagebox.showinfo(
            f"Calculation: {metric_name}",
            info_text.get(metric_name, "No information available")
        )
    
    # Create confidence widgets
    ConfidenceWidget(
        frame,
        "Opponent Def EPA/Play:",
        epa_var,
        info_callback=show_calculation_info
    ).pack(fill=tk.X, pady=5)
    
    ConfidenceWidget(
        frame,
        "Opponent DVOA Pass Def %:",
        dvoa_pass_var,
        info_callback=show_calculation_info
    ).pack(fill=tk.X, pady=5)
    
    ConfidenceWidget(
        frame,
        "Opponent DVOA Run Def %:",
        dvoa_run_var,
        confidence_calculator=lambda x: 60.0 if x else 0.0,  # Low confidence example
        info_callback=show_calculation_info
    ).pack(fill=tk.X, pady=5)
    
    ttk.Label(frame, text="\n💡 Orange border = Confidence < 60%",
             foreground='#fd7e14', font=('Arial', 9, 'italic')).pack(pady=10)
    
    root.mainloop()
