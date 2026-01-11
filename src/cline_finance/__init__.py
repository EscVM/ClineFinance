"""
ClineFinance - A high-quality MCP server for personal financial advisory.

This package transforms Cline into a sophisticated financial advisor that can:
- Track and analyze your investment portfolio
- Provide real-time market data and insights
- Remember past analysis and decisions
- Generate visual reports with charts
"""

__version__ = "1.0.0"
__author__ = "Vittorio"

from cline_finance.server import mcp

__all__ = ["mcp", "__version__"]
