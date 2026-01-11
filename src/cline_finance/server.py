"""
ClineFinance MCP Server - Main entry point.

A FastMCP server that transforms Cline into a personal financial advisor.
"""
import logging

from fastmcp import FastMCP

from cline_finance.constants import SERVER_NAME, SERVER_VERSION

# Import tool implementations
from cline_finance.tools.quotes import get_stock_quote, get_historical_data, get_multiple_quotes
from cline_finance.tools.settings import (
    get_user_settings,
    set_user_settings,
    get_currency_symbol,
    create_owner as create_owner_impl,
    switch_owner as switch_owner_impl,
    list_owners as list_owners_impl,
    delete_owner as delete_owner_impl,
)
from cline_finance.tools.fx import get_fx_rate, convert_currency, get_major_fx_rates
from cline_finance.tools.portfolio import (
    get_portfolio_valuation,
    add_position,
    update_position,
    remove_position,
    get_portfolio_table,
    get_portfolio_history,
    generate_portfolio_report,
)
from cline_finance.tools.market import (
    get_market_overview,
    get_market_movers,
    get_sector_performance,
)
from cline_finance.tools.news import get_financial_news, get_portfolio_news
from cline_finance.tools.analyst import get_analyst_ratings, get_earnings_calendar
from cline_finance.tools.memory import (
    save_insight,
    get_insights,
    track_decision,
    get_pending_reviews,
    update_decision_outcome,
    get_decisions,
    get_portfolio_history as get_memory_history,
    cleanup_memory,
)
from cline_finance.tools.economic import (
    get_interest_rates,
    get_inflation_data,
    get_employment_data,
    get_yield_curve,
    get_gdp_data,
    get_economic_summary,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(SERVER_NAME)

# Create FastMCP server instance
mcp = FastMCP(SERVER_NAME)


# =============================================================================
# Settings & Owner Management Tools
# =============================================================================

@mcp.tool()
def get_settings() -> dict:
    """
    Get current user settings including base currency and owner info.
    
    Call this on first interaction to check if settings are configured.
    If not configured, prompt the user to create an owner first.
    
    Returns:
        Current settings including owner_name, base_currency, is_configured status
    """
    return get_user_settings()


@mcp.tool()
def set_settings(base_currency: str) -> dict:
    """
    Set user preferences including base currency for the current owner.
    
    The base currency is used for portfolio totals and conversions.
    
    Supported currencies:
        USD ($), EUR (€), GBP (£), JPY (¥), CHF, CAD (C$), AUD (A$),
        CNY (¥), HKD (HK$), SGD (S$), SEK (kr), NOK (kr), DKK (kr),
        INR (₹), BRL (R$), MXN (MX$), KRW (₩), TWD (NT$), PLN (zł), CZK (Kč)
    
    Args:
        base_currency: 3-letter currency code (e.g., "USD", "EUR", "GBP")
    
    Returns:
        Updated settings confirmation
    """
    return set_user_settings(base_currency=base_currency)


@mcp.tool()
def create_owner(name: str, base_currency: str = "USD") -> dict:
    """
    Create a new portfolio owner.
    
    Each owner has their own separate portfolio and memory (insights, decisions, history).
    This enables managing multiple people's investments independently.
    
    On first-time setup, call this to create the initial owner.
    
    Args:
        name: Display name for the owner (e.g., "John", "Jane", "Family")
        base_currency: Base currency for portfolio totals (e.g., "USD", "EUR", "GBP")
    
    Returns:
        Created owner details including slug and base currency
    
    Example:
        create_owner("John", "EUR") → Creates portfolio for John with EUR base currency
    """
    return create_owner_impl(name=name, base_currency=base_currency)


@mcp.tool()
def switch_owner(name: str) -> dict:
    """
    Switch to a different portfolio owner.
    
    Changes the active context so all subsequent portfolio and memory
    operations use the selected owner's data.
    
    Args:
        name: Owner name or slug to switch to (e.g., "John" or "john")
    
    Returns:
        Switched owner details
    
    Example:
        switch_owner("Jane") → Switches to Jane's portfolio
    """
    return switch_owner_impl(name_or_slug=name)


@mcp.tool()
def list_owners() -> dict:
    """
    List all registered portfolio owners.
    
    Shows all owners with their base currency and indicates which is currently active.
    
    Returns:
        List of all owners with their details
    """
    return list_owners_impl()


@mcp.tool()
def delete_owner(name: str, confirm: bool = False) -> dict:
    """
    Delete an owner and all their data.
    
    ⚠️ WARNING: This permanently deletes the owner's portfolio, memory, and all history!
    Cannot delete the only remaining owner.
    
    Args:
        name: Owner name or slug to delete
        confirm: Must be True to actually delete (safety check)
    
    Returns:
        Deletion result
    """
    return delete_owner_impl(name_or_slug=name, confirm=confirm)


# =============================================================================
# FX (Foreign Exchange) Tools
# =============================================================================

@mcp.tool()
def fx_rate(from_currency: str, to_currency: str) -> dict:
    """
    Get the current exchange rate between two currencies.
    
    Uses live FX rates from Yahoo Finance.
    
    Args:
        from_currency: Source currency code (e.g., "USD")
        to_currency: Target currency code (e.g., "EUR")
    
    Returns:
        Exchange rate and conversion example
    """
    return get_fx_rate(from_currency, to_currency)


@mcp.tool()
def convert_amount(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    Convert an amount from one currency to another.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency (e.g., "USD")
        to_currency: Target currency (e.g., "EUR")
    
    Returns:
        Converted amount with rate used
    """
    return convert_currency(amount, from_currency, to_currency)


# =============================================================================
# Stock Quote Tools
# =============================================================================

@mcp.tool()
def get_quote(symbol: str) -> dict:
    """
    Get real-time stock/ETF quote with price, change, and company info.
    
    Supports various exchanges via suffixes:
    - No suffix: US exchanges (AAPL, MSFT)
    - .AS: Amsterdam (IWDA.AS)
    - .DE: Frankfurt/XETRA (AMZN.DE)
    - .L: London (RDSA.L)
    - .MI: Milan (ENI.MI)
    
    Args:
        symbol: Stock ticker with optional exchange suffix
    
    Returns:
        Quote data including price, change percent, volume, P/E ratio
    """
    return get_stock_quote(symbol)


@mcp.tool()
def get_price_history(symbol: str, period: str = "1mo", interval: str = "1d") -> dict:
    """
    Get historical price data for charting and analysis.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, ytd, max)
        interval: Data interval (1d, 1wk, 1mo)
    
    Returns:
        Historical prices, volumes, and summary statistics
    """
    return get_historical_data(symbol, period, interval)


# =============================================================================
# Portfolio Tools
# =============================================================================

@mcp.tool()
def portfolio_valuation() -> dict:
    """
    Get complete portfolio valuation with real-time prices.
    
    Calculates current value, gain/loss, and allocation for all positions.
    Values are shown in original currency AND converted to base currency.
    
    Returns:
        Portfolio summary with positions, total value, P&L, sector/currency allocation
    """
    return get_portfolio_valuation()


@mcp.tool()
def portfolio_table() -> str:
    """
    Get portfolio as a formatted ASCII table for display.
    
    Returns:
        Formatted table showing all positions with P&L
    """
    return get_portfolio_table()


@mcp.tool()
def buy_stock(
    symbol: str, 
    shares: float, 
    price: float,
    currency: str = None,
    exchange: str = None,
    sector: str = None,
    asset_type: str = "stock",
    notes: str = None,
) -> dict:
    """
    Add a new position or add to existing position.
    
    Automatically calculates weighted average cost if position exists.
    
    Args:
        symbol: Stock/ETF ticker symbol
        shares: Number of shares purchased
        price: Purchase price per share
        currency: Currency of purchase (e.g., "USD", "EUR", "GBP") - auto-detected if not provided
        exchange: Exchange where purchased (e.g., "NYSE", "NASDAQ", "LSE")
        sector: Business sector (auto-detected if not provided)
        asset_type: 'stock' or 'etf'
        notes: Optional notes about the purchase
    
    Returns:
        Added/updated position details with values in original and base currency
    
    Example:
        buy_stock("AAPL", 10, 175.50, currency="USD", exchange="NASDAQ")
    """
    return add_position(symbol, shares, price, currency, exchange, sector, asset_type, notes)


@mcp.tool()
def sell_stock(symbol: str, reason: str = None) -> dict:
    """
    Remove a position from portfolio (sell all shares).
    
    Args:
        symbol: Stock ticker to remove
        reason: Optional reason for selling
    
    Returns:
        Removal confirmation with position details
    """
    return remove_position(symbol, reason)


@mcp.tool()
def modify_position(
    symbol: str,
    shares: float = None,
    avg_cost: float = None,
    notes: str = None,
) -> dict:
    """
    Update an existing portfolio position.
    
    Args:
        symbol: Stock ticker to update
        shares: New total share count (if changing)
        avg_cost: New average cost (if correcting)
        notes: Updated notes
    
    Returns:
        Updated position details
    """
    return update_position(symbol, shares, avg_cost, notes)


@mcp.tool()
def portfolio_history(days: int = 30) -> dict:
    """
    Get portfolio value history for performance tracking.
    
    Args:
        days: Number of days of history
    
    Returns:
        Historical values and performance metrics
    """
    return get_portfolio_history(days)


@mcp.tool()
def generate_report() -> dict:
    """
    Generate a visual portfolio report with charts.
    
    Creates PNG dashboard with allocation pie chart, performance bars,
    and value history (if available).
    
    Returns:
        Path to generated report and summary
    """
    return generate_portfolio_report()


# =============================================================================
# Market Tools
# =============================================================================

@mcp.tool()
def market_overview(indices: list = None) -> dict:
    """
    Get market overview with major indices and sentiment.
    
    Args:
        indices: List of index symbols (default: major US & EU indices)
    
    Returns:
        Index data, VIX level, and market sentiment
    """
    return get_market_overview(indices)


@mcp.tool()
def market_movers(count: int = 5) -> dict:
    """
    Get top market gainers and losers.
    
    Args:
        count: Number of movers in each category
    
    Returns:
        Top gainers and losers with price changes
    """
    return get_market_movers(count)


@mcp.tool()
def sector_performance() -> dict:
    """
    Get performance of market sectors.
    
    Uses sector ETFs to show daily and weekly sector performance.
    
    Returns:
        Sector performance data sorted by daily change
    """
    return get_sector_performance()


# =============================================================================
# News Tools
# =============================================================================

@mcp.tool()
def financial_news(query: str = "stock market", symbols: list = None, limit: int = 10) -> dict:
    """
    Get latest financial news.
    
    Args:
        query: Search term for news
        symbols: List of stock symbols to get news for (alternative to query)
        limit: Maximum articles to return (1-20)
    
    Returns:
        News articles with titles, descriptions, and sources
    """
    return get_financial_news(query, symbols, limit)


@mcp.tool()
def news_for_portfolio(limit: int = 10) -> dict:
    """
    Get news relevant to current portfolio holdings.
    
    Fetches and scores news based on relevance to your positions.
    
    Args:
        limit: Maximum articles to return
    
    Returns:
        Portfolio-relevant news sorted by relevance
    """
    # Get portfolio symbols
    valuation = get_portfolio_valuation()
    symbols = [p["symbol"] for p in valuation.get("positions", [])]
    
    if not symbols:
        return {"error": "No positions in portfolio", "articles": []}
    
    return get_portfolio_news(symbols, limit)


# =============================================================================
# Analyst Tools
# =============================================================================

@mcp.tool()
def analyst_ratings(symbol: str) -> dict:
    """
    Get analyst ratings and price targets for a stock.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Consensus rating, price targets, recent upgrades/downgrades
    """
    return get_analyst_ratings(symbol)


@mcp.tool()
def earnings_calendar(symbol: str) -> dict:
    """
    Get upcoming earnings information for a stock.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Earnings date, estimates, and historical surprise data
    """
    return get_earnings_calendar(symbol)


# =============================================================================
# Memory Tools
# =============================================================================

@mcp.tool()
def remember_insight(
    category: str,
    content: str,
    symbol: str = None,
    tags: list = None,
) -> dict:
    """
    Save a market or portfolio insight for future reference.
    
    Categories: market, portfolio, stock, sector, economic, earnings
    
    Args:
        category: Type of insight
        content: The insight text
        symbol: Related stock symbol (optional)
        tags: Tags for filtering (optional)
    
    Returns:
        Saved insight details
    """
    return save_insight(category, content, symbol, tags)


@mcp.tool()
def recall_insights(
    category: str = None,
    symbol: str = None,
    tags: list = None,
    limit: int = 10,
) -> dict:
    """
    Retrieve stored insights from memory.
    
    Args:
        category: Filter by category
        symbol: Filter by stock symbol
        tags: Filter by tags
        limit: Maximum insights to return
    
    Returns:
        Matching insights sorted by date
    """
    return get_insights(category, symbol, tags, limit)


@mcp.tool()
def record_decision(
    action: str,
    rationale: str,
    symbol: str = None,
    shares: float = None,
    price: float = None,
) -> dict:
    """
    Track an investment decision for future review.
    
    Args:
        action: buy, sell, hold, or rebalance
        rationale: Reasoning behind the decision
        symbol: Stock symbol (if applicable)
        shares: Number of shares (if applicable)
        price: Price at decision (if applicable)
    
    Returns:
        Tracked decision details
    """
    return track_decision(action, rationale, symbol, shares, price)


@mcp.tool()
def pending_reviews() -> dict:
    """
    Get investment decisions due for review.
    
    Returns:
        Decisions where review date has passed
    """
    return get_pending_reviews()


@mcp.tool()
def decision_outcome(decision_id: str, outcome: str, close: bool = False) -> dict:
    """
    Update a decision with its outcome.
    
    Args:
        decision_id: The decision ID
        outcome: Description of the outcome
        close: Whether to close (no more reviews)
    
    Returns:
        Updated decision
    """
    return update_decision_outcome(decision_id, outcome, close)


@mcp.tool()
def decision_history(symbol: str = None, action: str = None, limit: int = 20) -> dict:
    """
    Get tracked investment decisions.
    
    Args:
        symbol: Filter by stock symbol
        action: Filter by action type
        limit: Maximum to return
    
    Returns:
        Matching decisions
    """
    return get_decisions(symbol, action, limit=limit)


# =============================================================================
# Economic Tools (FRED)
# =============================================================================

@mcp.tool()
def economic_indicators() -> dict:
    """
    Get key economic indicators from FRED (Federal Reserve Economic Data).
    
    Returns interest rates (Fed Funds, Treasury yields), inflation (CPI),
    and employment data (unemployment rate).
    
    Requires FRED_API_KEY to be configured (free at fred.stlouisfed.org).
    
    Returns:
        Economic indicators with Fed Funds Rate, Treasury yields,
        CPI inflation, and unemployment rate
    """
    return get_economic_summary()


@mcp.tool()
def yield_curve_status() -> dict:
    """
    Get yield curve status with recession warning indicator.
    
    The 10Y-2Y Treasury spread is a key recession predictor.
    Inversions have preceded every US recession since the 1950s.
    
    Requires FRED_API_KEY to be configured.
    
    Returns:
        Yield curve spread, inversion status, and risk assessment
    """
    return get_yield_curve()


@mcp.tool()
def interest_rates() -> dict:
    """
    Get current interest rates from FRED.
    
    Includes Fed Funds Rate and Treasury yields (2Y, 10Y, 30Y).
    
    Requires FRED_API_KEY to be configured.
    
    Returns:
        Current interest rates with recent changes
    """
    return get_interest_rates()


@mcp.tool()
def inflation_data() -> dict:
    """
    Get inflation indicators from FRED.
    
    Includes CPI, Core CPI, and PCE Price Index with year-over-year changes.
    
    Requires FRED_API_KEY to be configured.
    
    Returns:
        Inflation metrics with assessment vs Fed's 2% target
    """
    return get_inflation_data()


@mcp.tool()
def employment_data() -> dict:
    """
    Get employment indicators from FRED.
    
    Includes unemployment rate and initial jobless claims.
    
    Requires FRED_API_KEY to be configured.
    
    Returns:
        Employment data with labor market assessment
    """
    return get_employment_data()


@mcp.tool()
def gdp_growth() -> dict:
    """
    Get GDP growth data from FRED.
    
    Shows real GDP growth rate with recent quarters.
    
    Requires FRED_API_KEY to be configured.
    
    Returns:
        GDP growth rate with economic assessment
    """
    return get_gdp_data()


# =============================================================================
# Server Entry Point
# =============================================================================

def main():
    """Main entry point for the ClineFinance MCP server."""
    print(f"🚀 Starting {SERVER_NAME} v{SERVER_VERSION}")
    print("📊 Financial Advisor for Cline")
    print("=" * 40)
    
    # List available tools
    print("\nAvailable tools:")
    tools = [
        # Settings & Owner
        "get_settings", "set_settings", "create_owner", "switch_owner", "list_owners", "delete_owner",
        # FX
        "fx_rate", "convert_amount",
        # Quotes
        "get_quote", "get_price_history",
        # Portfolio
        "portfolio_valuation", "portfolio_table", "buy_stock", "sell_stock",
        "modify_position", "portfolio_history", "generate_report",
        # Market
        "market_overview", "market_movers", "sector_performance",
        # News
        "financial_news", "news_for_portfolio",
        # Analyst
        "analyst_ratings", "earnings_calendar",
        # Memory
        "remember_insight", "recall_insights", "record_decision",
        "pending_reviews", "decision_outcome", "decision_history",
        # Economic
        "economic_indicators", "yield_curve_status", "interest_rates",
        "inflation_data", "employment_data", "gdp_growth",
    ]
    for tool in tools:
        print(f"  • {tool}")
    
    print("\n" + "=" * 40)
    
    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
