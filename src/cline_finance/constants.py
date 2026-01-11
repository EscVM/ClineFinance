"""
Constants and configuration for ClineFinance.
"""
import os
from pathlib import Path

# Server identification
SERVER_NAME = "cline-finance"
SERVER_VERSION = "1.0.0"

# Base paths
_PACKAGE_DIR = Path(__file__).parent
_REPO_ROOT = _PACKAGE_DIR.parent.parent

# Data directory - can be set via DATA_DIR environment variable (set by install.sh)
DATA_DIR = Path(os.getenv("DATA_DIR", os.getenv("CLINE_FINANCE_DATA_DIR", _REPO_ROOT / "data")))
CHARTS_DIR = DATA_DIR / "charts"

# File paths - all data in single directory
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
MEMORY_FILE = DATA_DIR / "memory.json"

# API Keys (loaded from environment variables)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# Default currency for portfolio valuation
DEFAULT_CURRENCY = "EUR"

# Market indices for overview
DEFAULT_INDICES = [
    "^GSPC",   # S&P 500
    "^DJI",    # Dow Jones
    "^IXIC",   # NASDAQ
    "^STOXX50E",  # Euro Stoxx 50
    "^FTSE",   # FTSE 100
]

# Index display names
INDEX_NAMES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones Industrial Average",
    "^IXIC": "NASDAQ Composite",
    "^STOXX50E": "Euro Stoxx 50",
    "^FTSE": "FTSE 100",
    "^VIX": "VIX (Volatility Index)",
    "^RUT": "Russell 2000",
    "^GDAXI": "DAX",
    "^FCHI": "CAC 40",
}

# Memory retention periods (in days)
RETENTION_PERIODS = {
    "portfolio_snapshots": None,  # Keep forever
    "decisions": None,            # Keep forever
    "price_alerts": 30,
    "earnings_notes": 365,
    "market_events": 730,         # 2 years
    "general_insights": 180,      # 6 months
}

# Insight categories
INSIGHT_CATEGORIES = [
    "market",      # General market conditions
    "portfolio",   # Portfolio-specific insights
    "stock",       # Individual stock analysis
    "sector",      # Sector trends
    "economic",    # Macroeconomic observations
    "earnings",    # Earnings-related notes
]

# Risk thresholds
CONCENTRATION_THRESHOLDS = {
    "low": 15,       # < 15% in single position = low risk
    "moderate": 25,  # 15-25% = moderate
    "high": 40,      # 25-40% = high
    "extreme": 100,  # > 40% = extreme
}

# VIX sentiment thresholds
VIX_THRESHOLDS = {
    "complacent": 15,
    "normal": 20,
    "elevated": 25,
    "fearful": 30,
    "panic": 40,
}

# Chart colors (for matplotlib)
CHART_COLORS = {
    "primary": "#2563eb",    # Blue
    "secondary": "#16a34a",  # Green
    "accent": "#dc2626",     # Red
    "neutral": "#6b7280",    # Gray
    "background": "#ffffff",
    "text": "#1f2937",
}

# Sector colors for pie charts
SECTOR_COLORS = {
    "Technology": "#3b82f6",
    "Consumer Discretionary": "#f59e0b",
    "Healthcare": "#10b981",
    "Financials": "#6366f1",
    "Communication Services": "#ec4899",
    "Industrials": "#8b5cf6",
    "Consumer Staples": "#14b8a6",
    "Energy": "#f97316",
    "Utilities": "#06b6d4",
    "Real Estate": "#84cc16",
    "Materials": "#a855f7",
    "Diversified": "#64748b",
    "US Large Cap": "#2563eb",
    "Other": "#9ca3af",
}
