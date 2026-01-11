"""
Chart Generator - Creates visualizations for portfolio analysis.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from cline_finance.constants import CHARTS_DIR, CHART_COLORS, SECTOR_COLORS

logger = logging.getLogger(__name__)


def generate_sparkline(values: list[float], width: int = 10) -> str:
    """
    Generate ASCII sparkline from values.
    
    Args:
        values: List of numeric values
        width: Number of characters in sparkline
    
    Returns:
        Sparkline string like "▁▂▃▅▆▇█▆▅"
    """
    if not values or len(values) < 2:
        return "─" * width
    
    blocks = "▁▂▃▄▅▆▇█"
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val
    
    if val_range == 0:
        return blocks[4] * width
    
    # Sample values to fit width
    if len(values) > width:
        step = len(values) / width
        sampled = [values[int(i * step)] for i in range(width)]
    else:
        sampled = values
    
    sparkline = ""
    for val in sampled:
        normalized = (val - min_val) / val_range
        index = min(int(normalized * (len(blocks) - 1)), len(blocks) - 1)
        sparkline += blocks[index]
    
    return sparkline


def generate_progress_bar(
    value: float,
    max_value: float = 100,
    width: int = 10,
    filled_char: str = "█",
    empty_char: str = "░",
) -> str:
    """
    Generate ASCII progress bar.
    
    Args:
        value: Current value
        max_value: Maximum value (100 for percentages)
        width: Width of bar in characters
        filled_char: Character for filled portion
        empty_char: Character for empty portion
    
    Returns:
        Progress bar string like "[████████░░]"
    """
    ratio = min(max(value / max_value, 0), 1)
    filled = int(ratio * width)
    empty = width - filled
    return f"[{filled_char * filled}{empty_char * empty}]"


def generate_allocation_bar(
    current_pct: float,
    target_pct: float = None,
    width: int = 16,
) -> tuple[str, str]:
    """
    Generate allocation bar with optional target comparison.
    
    Args:
        current_pct: Current allocation percentage
        target_pct: Target allocation percentage (optional)
        width: Width of bar
    
    Returns:
        Tuple of (bar_string, status_string)
    """
    bar = generate_progress_bar(current_pct, 100, width)
    
    if target_pct is None:
        return bar, ""
    
    diff = current_pct - target_pct
    if abs(diff) < 3:
        status = "✅ ON TARGET"
    elif diff > 0:
        status = f"⚠️ +{diff:.1f}% OVER"
    else:
        status = f"📉 {diff:.1f}% UNDER"
    
    return bar, status


def format_pnl_indicator(gain_pct: float, value: float) -> str:
    """
    Format P&L with visual indicator.
    
    Args:
        gain_pct: Gain/loss percentage
        value: Absolute gain/loss value
    
    Returns:
        Formatted string with emoji indicator
    """
    if gain_pct >= 10:
        emoji = "🚀"
    elif gain_pct >= 5:
        emoji = "📈"
    elif gain_pct >= 0:
        emoji = "🟢"
    elif gain_pct >= -5:
        emoji = "🔴"
    elif gain_pct >= -10:
        emoji = "📉"
    else:
        emoji = "💥"
    
    sign = "+" if value >= 0 else ""
    return f"{emoji} {sign}€{value:,.2f} ({sign}{gain_pct:.1f}%)"


def format_trend_indicator(change_pct: float) -> str:
    """Format trend indicator with arrow."""
    if change_pct > 2:
        return f"▲▲ +{change_pct:.2f}%"
    elif change_pct > 0:
        return f"▲ +{change_pct:.2f}%"
    elif change_pct > -2:
        return f"▼ {change_pct:.2f}%"
    else:
        return f"▼▼ {change_pct:.2f}%"


class ChartGenerator:
    """
    Generates charts for portfolio visualization.
    
    Supports:
    - Portfolio value over time (line chart)
    - Asset allocation (pie chart)
    - Sector exposure (pie chart)
    - Performance comparison (bar chart)
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the chart generator.
        
        Args:
            output_dir: Directory for saving charts. Defaults to CHARTS_DIR.
        """
        self.output_dir = output_dir or CHARTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 13
        plt.rcParams['figure.titlesize'] = 14
    
    def _save_figure(self, fig: plt.Figure, filename: str) -> Path:
        """Save figure and return path."""
        filepath = self.output_dir / filename
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        logger.info(f"Saved chart: {filepath}")
        return filepath
    
    def portfolio_value_chart(
        self,
        dates: list[str],
        values: list[float],
        cost_basis: Optional[list[float]] = None,
        title: str = "Portfolio Value Over Time",
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate portfolio value line chart.
        
        Args:
            dates: List of dates (YYYY-MM-DD format)
            values: Portfolio values corresponding to dates
            cost_basis: Optional cost basis line for comparison
            title: Chart title
            filename: Output filename (auto-generated if not provided)
        
        Returns:
            Path to the saved chart image.
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Parse dates
        date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
        
        # Plot portfolio value
        ax.plot(
            date_objects, 
            values, 
            color=CHART_COLORS["primary"],
            linewidth=2,
            label="Portfolio Value",
            marker='o',
            markersize=4,
        )
        
        # Fill area under curve
        ax.fill_between(
            date_objects, 
            values, 
            alpha=0.2, 
            color=CHART_COLORS["primary"]
        )
        
        # Add cost basis line if provided
        if cost_basis:
            ax.plot(
                date_objects,
                cost_basis,
                color=CHART_COLORS["neutral"],
                linewidth=1.5,
                linestyle='--',
                label="Cost Basis",
            )
        
        # Formatting
        ax.set_xlabel("Date")
        ax.set_ylabel("Value (EUR)")
        ax.set_title(title, fontweight='bold')
        ax.legend(loc='upper left')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45)
        
        # Format y-axis with EUR
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add min/max annotations
        max_val = max(values)
        min_val = min(values)
        max_idx = values.index(max_val)
        min_idx = values.index(min_val)
        
        ax.annotate(
            f'High: €{max_val:,.0f}',
            xy=(date_objects[max_idx], max_val),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=9,
            color=CHART_COLORS["secondary"],
        )
        
        if min_idx != max_idx:
            ax.annotate(
                f'Low: €{min_val:,.0f}',
                xy=(date_objects[min_idx], min_val),
                xytext=(10, -15),
                textcoords='offset points',
                fontsize=9,
                color=CHART_COLORS["accent"],
            )
        
        plt.tight_layout()
        
        if not filename:
            filename = f"portfolio_value_{datetime.now().strftime('%Y%m%d')}.png"
        
        return self._save_figure(fig, filename)
    
    def allocation_pie_chart(
        self,
        symbols: list[str],
        values: list[float],
        title: str = "Portfolio Allocation",
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate portfolio allocation pie chart.
        
        Args:
            symbols: List of stock symbols
            values: Market values for each position
            title: Chart title
            filename: Output filename
        
        Returns:
            Path to the saved chart image.
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Calculate percentages
        total = sum(values)
        percentages = [v / total * 100 for v in values]
        
        # Colors - use a colormap
        colors = plt.cm.Set3(np.linspace(0, 1, len(symbols)))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=symbols,
            autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
            colors=colors,
            startangle=90,
            explode=[0.02] * len(symbols),
        )
        
        # Style
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontweight='bold', pad=20)
        
        # Add legend with values
        legend_labels = [f'{s}: €{v:,.0f}' for s, v in zip(symbols, values)]
        ax.legend(
            wedges, 
            legend_labels,
            title="Holdings",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
        )
        
        plt.tight_layout()
        
        if not filename:
            filename = f"allocation_{datetime.now().strftime('%Y%m%d')}.png"
        
        return self._save_figure(fig, filename)
    
    def sector_pie_chart(
        self,
        sectors: list[str],
        values: list[float],
        title: str = "Sector Exposure",
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate sector exposure pie chart.
        
        Args:
            sectors: List of sector names
            values: Total exposure per sector
            title: Chart title
            filename: Output filename
        
        Returns:
            Path to the saved chart image.
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Get colors from sector color map
        colors = [SECTOR_COLORS.get(s, SECTOR_COLORS["Other"]) for s in sectors]
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=sectors,
            autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
            colors=colors,
            startangle=90,
            explode=[0.02] * len(sectors),
        )
        
        # Style
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
            autotext.set_color('white')
        
        ax.set_title(title, fontweight='bold', pad=20)
        
        # Legend
        legend_labels = [f'{s}: €{v:,.0f}' for s, v in zip(sectors, values)]
        ax.legend(
            wedges,
            legend_labels,
            title="Sectors",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
        )
        
        plt.tight_layout()
        
        if not filename:
            filename = f"sectors_{datetime.now().strftime('%Y%m%d')}.png"
        
        return self._save_figure(fig, filename)
    
    def performance_bar_chart(
        self,
        symbols: list[str],
        gains_pct: list[float],
        title: str = "Position Performance",
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate performance comparison bar chart.
        
        Args:
            symbols: List of stock symbols
            gains_pct: Gain/loss percentage for each position
            title: Chart title
            filename: Output filename
        
        Returns:
            Path to the saved chart image.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sort by performance
        sorted_data = sorted(zip(symbols, gains_pct), key=lambda x: x[1], reverse=True)
        sorted_symbols = [d[0] for d in sorted_data]
        sorted_gains = [d[1] for d in sorted_data]
        
        # Color based on positive/negative
        colors = [
            CHART_COLORS["secondary"] if g >= 0 else CHART_COLORS["accent"] 
            for g in sorted_gains
        ]
        
        # Create bars
        bars = ax.barh(sorted_symbols, sorted_gains, color=colors, edgecolor='white')
        
        # Add value labels
        for bar, gain in zip(bars, sorted_gains):
            width = bar.get_width()
            label_x = width + 0.5 if width >= 0 else width - 0.5
            ha = 'left' if width >= 0 else 'right'
            ax.text(
                label_x, 
                bar.get_y() + bar.get_height()/2,
                f'{gain:+.1f}%',
                va='center',
                ha=ha,
                fontsize=10,
                fontweight='bold',
            )
        
        # Add zero line
        ax.axvline(x=0, color=CHART_COLORS["neutral"], linewidth=1)
        
        # Formatting
        ax.set_xlabel("Gain/Loss (%)")
        ax.set_title(title, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        
        # Adjust x limits for labels
        max_abs = max(abs(min(sorted_gains)), abs(max(sorted_gains)))
        ax.set_xlim(-max_abs - 5, max_abs + 5)
        
        plt.tight_layout()
        
        if not filename:
            filename = f"performance_{datetime.now().strftime('%Y%m%d')}.png"
        
        return self._save_figure(fig, filename)
    
    def combined_dashboard(
        self,
        portfolio_data: dict,
        history_data: Optional[dict] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate a combined dashboard with multiple charts.
        
        Args:
            portfolio_data: Dictionary with current portfolio state
            history_data: Optional historical data for value chart
            filename: Output filename
        
        Returns:
            Path to the saved dashboard image.
        """
        fig = plt.figure(figsize=(16, 12))
        
        # Create grid for subplots
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. Portfolio Value Over Time (top left) or Total Value Summary
        ax1 = fig.add_subplot(gs[0, 0])
        if history_data and len(history_data.get("dates", [])) > 1:
            dates = [datetime.strptime(d, "%Y-%m-%d") for d in history_data["dates"]]
            ax1.plot(dates, history_data["values"], color=CHART_COLORS["primary"], linewidth=2)
            ax1.fill_between(dates, history_data["values"], alpha=0.2, color=CHART_COLORS["primary"])
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax1.set_ylabel("Value (EUR)")
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        else:
            # Show summary text if no history
            ax1.text(
                0.5, 0.5,
                f"Total Value\n€{portfolio_data.get('total_value', 0):,.2f}",
                ha='center', va='center',
                fontsize=24, fontweight='bold',
                color=CHART_COLORS["primary"]
            )
            ax1.axis('off')
        ax1.set_title("Portfolio Value", fontweight='bold')
        
        # 2. Allocation Pie (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        positions = portfolio_data.get("positions", [])
        if positions:
            symbols = [p["symbol"] for p in positions]
            values = [p.get("current_value", p.get("cost_basis", 0)) for p in positions]
            colors = plt.cm.Set3(np.linspace(0, 1, len(symbols)))
            ax2.pie(
                values, labels=symbols, autopct='%1.1f%%',
                colors=colors, startangle=90
            )
        ax2.set_title("Asset Allocation", fontweight='bold')
        
        # 3. Performance Bar (bottom left)
        ax3 = fig.add_subplot(gs[1, 0])
        if positions:
            symbols = [p["symbol"] for p in positions]
            gains = [p.get("gain_loss_pct", 0) for p in positions]
            colors = [CHART_COLORS["secondary"] if g >= 0 else CHART_COLORS["accent"] for g in gains]
            ax3.barh(symbols, gains, color=colors)
            ax3.axvline(x=0, color=CHART_COLORS["neutral"], linewidth=1)
            ax3.set_xlabel("Gain/Loss (%)")
        ax3.set_title("Position Performance", fontweight='bold')
        
        # 4. Sector Exposure (bottom right)
        ax4 = fig.add_subplot(gs[1, 1])
        if positions:
            sector_values = {}
            for p in positions:
                sector = p.get("sector", "Other")
                value = p.get("current_value", p.get("cost_basis", 0))
                sector_values[sector] = sector_values.get(sector, 0) + value
            
            sectors = list(sector_values.keys())
            values = list(sector_values.values())
            colors = [SECTOR_COLORS.get(s, SECTOR_COLORS["Other"]) for s in sectors]
            ax4.pie(values, labels=sectors, autopct='%1.1f%%', colors=colors, startangle=90)
        ax4.set_title("Sector Exposure", fontweight='bold')
        
        # Main title
        fig.suptitle(
            f"Portfolio Dashboard - {datetime.now().strftime('%B %d, %Y')}",
            fontsize=16, fontweight='bold', y=0.98
        )
        
        if not filename:
            filename = f"dashboard_{datetime.now().strftime('%Y%m%d')}.png"
        
        return self._save_figure(fig, filename)
    
    def format_ascii_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        alignments: Optional[list[str]] = None,
    ) -> str:
        """
        Generate an ASCII table for terminal display.
        
        Args:
            headers: Column headers
            rows: Table rows (list of lists)
            alignments: Column alignments ('l', 'c', 'r')
        
        Returns:
            Formatted ASCII table string.
        """
        if not alignments:
            alignments = ['l'] * len(headers)
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))
        
        # Build table
        def format_row(cells: list[str], widths: list[int], alignments: list[str]) -> str:
            formatted = []
            for cell, width, align in zip(cells, widths, alignments):
                if align == 'r':
                    formatted.append(str(cell).rjust(width))
                elif align == 'c':
                    formatted.append(str(cell).center(width))
                else:
                    formatted.append(str(cell).ljust(width))
            return "│ " + " │ ".join(formatted) + " │"
        
        # Build separator lines
        top_line = "┌─" + "─┬─".join("─" * w for w in widths) + "─┐"
        mid_line = "├─" + "─┼─".join("─" * w for w in widths) + "─┤"
        bot_line = "└─" + "─┴─".join("─" * w for w in widths) + "─┘"
        
        # Assemble table
        lines = [top_line]
        lines.append(format_row(headers, widths, alignments))
        lines.append(mid_line)
        for row in rows:
            lines.append(format_row(row, widths, alignments))
        lines.append(bot_line)
        
        return "\n".join(lines)
