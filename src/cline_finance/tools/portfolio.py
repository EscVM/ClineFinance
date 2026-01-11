"""
Portfolio Tools - Portfolio management and valuation.
Supports multi-owner functionality with separate portfolio per owner.
"""
import json
import logging
from datetime import datetime
from typing import Optional

from cline_finance.core.portfolio_manager import get_portfolio_manager
from cline_finance.core.memory_manager import get_memory_manager
from cline_finance.core.chart_generator import ChartGenerator
from cline_finance.core.settings_manager import get_settings_manager, CURRENCY_SYMBOLS
from cline_finance.tools.quotes import get_stock_quote
from cline_finance.tools.fx import get_fx_rate

logger = logging.getLogger(__name__)

# Chart generator singleton (shared across owners)
_chart_generator: Optional[ChartGenerator] = None


def _get_chart_generator() -> ChartGenerator:
    """Get or create chart generator instance."""
    global _chart_generator
    if _chart_generator is None:
        _chart_generator = ChartGenerator()
    return _chart_generator


def _get_currency_symbol(currency: str) -> str:
    """Get the display symbol for a currency."""
    return CURRENCY_SYMBOLS.get(currency.upper(), currency)


def _convert_to_base(amount: float, from_currency: str, base_currency: str) -> tuple[float, float]:
    """
    Convert an amount to base currency.
    
    Returns:
        Tuple of (converted_amount, fx_rate)
    """
    if from_currency.upper() == base_currency.upper():
        return amount, 1.0
    
    fx_result = get_fx_rate(from_currency, base_currency)
    rate = fx_result.get("rate", 1.0) or 1.0
    return amount * rate, rate


def get_portfolio_valuation() -> dict:
    """
    Get current portfolio valuation with real-time prices.
    
    Fetches live quotes for all positions and calculates:
    - Current market value per position (in original currency AND base currency)
    - Gain/loss per position
    - Total portfolio value in base currency
    - Portfolio allocation percentages
    
    Values are displayed in both original currency and converted to base currency.
    Uses the current owner's portfolio.
    
    Returns:
        Dictionary with complete portfolio valuation.
    """
    pm = get_portfolio_manager()
    sm = get_settings_manager()
    portfolio = pm.get_portfolio()
    
    # Get owner info
    current_owner = sm.get_current_owner()
    if current_owner:
        base_currency = current_owner.base_currency
        owner_name = current_owner.name
    else:
        base_currency = "USD"
        owner_name = None
    
    base_symbol = _get_currency_symbol(base_currency)
    
    positions_data = []
    total_value_base = 0.0
    total_cost_basis_base = 0.0
    errors = []
    currency_exposure = {}  # Track exposure per currency
    
    for position in portfolio.positions:
        try:
            # Get current quote
            quote = get_stock_quote(position.symbol)
            current_price = quote["price"]
            position_currency = quote.get("currency", position.currency or "USD")
            
            # Calculate position value in original currency
            current_value_orig = position.shares * current_price
            cost_basis_orig = position.shares * position.avg_cost
            gain_loss_orig = current_value_orig - cost_basis_orig
            gain_loss_pct = (gain_loss_orig / cost_basis_orig * 100) if cost_basis_orig > 0 else 0
            
            # Convert to base currency
            current_value_base, fx_rate = _convert_to_base(current_value_orig, position_currency, base_currency)
            cost_basis_base, _ = _convert_to_base(cost_basis_orig, position_currency, base_currency)
            gain_loss_base = current_value_base - cost_basis_base
            
            # Track currency exposure
            currency_exposure[position_currency] = currency_exposure.get(position_currency, 0) + current_value_base
            
            position_data = {
                "symbol": position.symbol,
                "company_name": quote.get("company_name", position.company_name or position.symbol),
                "shares": position.shares,
                # Original currency values
                "avg_cost": round(position.avg_cost, 2),
                "current_price": current_price,
                "currency": position_currency,
                "currency_symbol": _get_currency_symbol(position_currency),
                "cost_basis": round(cost_basis_orig, 2),
                "current_value": round(current_value_orig, 2),
                "gain_loss": round(gain_loss_orig, 2),
                # Base currency values
                "current_value_base": round(current_value_base, 2),
                "cost_basis_base": round(cost_basis_base, 2),
                "gain_loss_base": round(gain_loss_base, 2),
                "fx_rate": round(fx_rate, 6) if position_currency != base_currency else None,
                # Common
                "gain_loss_pct": round(gain_loss_pct, 2),
                "sector": position.sector or quote.get("sector"),
                "asset_type": position.asset_type,
                "weight": 0,  # Calculated after total
            }
            
            positions_data.append(position_data)
            total_value_base += current_value_base
            total_cost_basis_base += cost_basis_base
            
        except Exception as e:
            logger.error(f"Error valuing {position.symbol}: {e}")
            errors.append({"symbol": position.symbol, "error": str(e)})
            
            # Use cost basis as fallback (assume same currency as base for simplicity)
            cost_basis = position.shares * position.avg_cost
            positions_data.append({
                "symbol": position.symbol,
                "shares": position.shares,
                "avg_cost": round(position.avg_cost, 2),
                "currency": position.currency or "USD",
                "currency_symbol": _get_currency_symbol(position.currency or "USD"),
                "cost_basis": round(cost_basis, 2),
                "current_value": round(cost_basis, 2),
                "current_value_base": round(cost_basis, 2),
                "cost_basis_base": round(cost_basis, 2),
                "gain_loss_base": 0,
                "error": str(e),
                "sector": position.sector,
                "asset_type": position.asset_type,
                "weight": 0,
            })
            total_value_base += cost_basis
            total_cost_basis_base += cost_basis
    
    # Calculate weights (based on base currency values)
    for pos in positions_data:
        if total_value_base > 0:
            pos["weight"] = round(pos["current_value_base"] / total_value_base * 100, 2)
    
    # Calculate portfolio totals
    total_gain_loss_base = total_value_base - total_cost_basis_base
    total_gain_loss_pct = (total_gain_loss_base / total_cost_basis_base * 100) if total_cost_basis_base > 0 else 0
    
    # Sector allocation (in base currency)
    sector_allocation = {}
    for pos in positions_data:
        sector = pos.get("sector") or "Other"
        sector_allocation[sector] = sector_allocation.get(sector, 0) + pos["current_value_base"]
    
    # Asset type allocation (in base currency)
    asset_allocation = {}
    for pos in positions_data:
        asset_type = pos.get("asset_type", "stock")
        asset_allocation[asset_type] = asset_allocation.get(asset_type, 0) + pos["current_value_base"]
    
    # Currency allocation
    currency_allocation = {}
    for curr, value in currency_exposure.items():
        pct = (value / total_value_base * 100) if total_value_base > 0 else 0
        currency_allocation[curr] = {
            "value": round(value, 2),
            "percentage": round(pct, 2),
        }
    
    # Calculate concentration risk
    max_weight = max((p["weight"] for p in positions_data), default=0)
    if max_weight > 40:
        concentration_risk = "HIGH"
    elif max_weight > 25:
        concentration_risk = "MODERATE"
    else:
        concentration_risk = "LOW"
    
    result = {
        "valuation_date": datetime.utcnow().isoformat() + "Z",
        "owner": owner_name,
        "base_currency": base_currency,
        "base_currency_symbol": base_symbol,
        "total_value": round(total_value_base, 2),
        "total_cost_basis": round(total_cost_basis_base, 2),
        "total_gain_loss": round(total_gain_loss_base, 2),
        "total_gain_loss_pct": round(total_gain_loss_pct, 2),
        "cash": portfolio.cash,
        "total_with_cash": round(total_value_base + portfolio.cash, 2),
        "positions": positions_data,
        "position_count": len(positions_data),
        "sector_allocation": {k: round(v, 2) for k, v in sector_allocation.items()},
        "asset_allocation": {k: round(v, 2) for k, v in asset_allocation.items()},
        "currency_allocation": currency_allocation,
        "concentration_risk": concentration_risk,
        "max_position_weight": round(max_weight, 2),
    }
    
    if errors:
        result["errors"] = errors
    
    # Save snapshot to memory
    try:
        mm = get_memory_manager()
        mm.save_portfolio_snapshot(
            total_value_eur=total_value_base,  # Note: field name is legacy, stores base currency value
            total_cost_basis=total_cost_basis_base,
            cash=portfolio.cash,
            positions=[
                {
                    "symbol": p["symbol"],
                    "shares": p["shares"],
                    "current_value": p["current_value_base"],
                    "gain_loss_pct": p.get("gain_loss_pct", 0),
                }
                for p in positions_data
            ],
        )
    except Exception as e:
        logger.warning(f"Failed to save portfolio snapshot: {e}")
    
    return result


def add_position(
    symbol: str,
    shares: float,
    price: float,
    currency: Optional[str] = None,
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    asset_type: str = "stock",
    notes: Optional[str] = None,
) -> dict:
    """
    Add a new position or add to existing position.
    
    If the position already exists, calculates new weighted average cost.
    Adds to the current owner's portfolio.
    
    Args:
        symbol: Stock/ETF ticker symbol
        shares: Number of shares purchased
        price: Purchase price per share
        currency: Currency of the purchase price (e.g., "USD", "EUR", "GBP")
                  If not provided, will be auto-detected from quote
        exchange: Exchange where purchased (e.g., "NYSE", "NASDAQ", "LSE")
        sector: Business sector (auto-detected if not provided)
        asset_type: 'stock' or 'etf'
        notes: Optional notes about the purchase
    
    Returns:
        Dictionary with the added/updated position details.
    
    Example:
        >>> add_position("AAPL", 10, 175.50, currency="USD", exchange="NASDAQ")
        >>> add_position("ASML", 5, 850.00, currency="EUR", exchange="AMS")
    """
    pm = get_portfolio_manager()
    sm = get_settings_manager()
    
    current_owner = sm.get_current_owner()
    if current_owner:
        base_currency = current_owner.base_currency
    else:
        base_currency = "USD"
    
    # Try to get sector and currency from quote if not provided
    if not sector or not currency:
        try:
            quote = get_stock_quote(symbol)
            if not sector:
                sector = quote.get("sector")
            if not currency:
                currency = quote.get("currency", "USD")
        except Exception:
            if not currency:
                currency = "USD"  # Default if we can't detect
    
    # Ensure currency is set
    position_currency = currency or "USD"
    
    position = pm.add_position(
        symbol=symbol,
        shares=shares,
        avg_cost=price,
        currency=position_currency,
        exchange=exchange,
        sector=sector,
        asset_type=asset_type,
        notes=notes,
    )
    
    # Calculate value in base currency
    cost_basis = position.shares * position.avg_cost
    cost_basis_base, fx_rate = _convert_to_base(cost_basis, position_currency, base_currency)
    
    # Track as decision
    try:
        mm = get_memory_manager()
        mm.track_decision(
            action="buy",
            symbol=symbol,
            shares=shares,
            price=price,
            rationale=notes or f"Added {shares} shares of {symbol} at {_get_currency_symbol(position_currency)}{price:.2f}",
        )
    except Exception as e:
        logger.warning(f"Failed to track decision: {e}")
    
    result = {
        "status": "success",
        "action": "added" if position.shares == shares else "updated",
        "position": {
            "symbol": position.symbol,
            "total_shares": position.shares,
            "avg_cost": round(position.avg_cost, 2),
            "currency": position_currency,
            "currency_symbol": _get_currency_symbol(position_currency),
            "exchange": exchange,
            "cost_basis": round(cost_basis, 2),
            "cost_basis_base": round(cost_basis_base, 2),
            "base_currency": base_currency,
            "sector": position.sector,
            "asset_type": position.asset_type,
            "notes": position.notes,
        },
    }
    
    if position_currency != base_currency:
        result["position"]["fx_rate"] = round(fx_rate, 6)
    
    return result


def update_position(
    symbol: str,
    shares: Optional[float] = None,
    avg_cost: Optional[float] = None,
    notes: Optional[str] = None,
) -> dict:
    """
    Update an existing position.
    
    Args:
        symbol: Stock ticker to update
        shares: New total share count (if changing)
        avg_cost: New average cost (if correcting)
        notes: Updated notes
    
    Returns:
        Dictionary with the updated position details.
    """
    pm = get_portfolio_manager()
    
    try:
        position = pm.update_position(
            symbol=symbol,
            shares=shares,
            avg_cost=avg_cost,
            notes=notes,
        )
        
        return {
            "status": "success",
            "position": {
                "symbol": position.symbol,
                "shares": position.shares,
                "avg_cost": round(position.avg_cost, 2),
                "currency": position.currency,
                "currency_symbol": _get_currency_symbol(position.currency),
                "cost_basis": round(position.shares * position.avg_cost, 2),
                "notes": position.notes,
            },
        }
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
        }


def remove_position(symbol: str, reason: Optional[str] = None) -> dict:
    """
    Remove a position from the portfolio (sell all shares).
    
    Args:
        symbol: Stock ticker to remove
        reason: Optional reason for selling
    
    Returns:
        Dictionary with removal status.
    """
    pm = get_portfolio_manager()
    
    # Get position info before removing
    portfolio = pm.get_portfolio()
    position = portfolio.get_position(symbol)
    
    if not position:
        return {
            "status": "error",
            "error": f"Position {symbol} not found",
        }
    
    removed = pm.remove_position(symbol)
    
    if removed:
        # Track as decision
        try:
            mm = get_memory_manager()
            mm.track_decision(
                action="sell",
                symbol=symbol,
                shares=position.shares,
                price=position.avg_cost,
                rationale=reason or f"Sold all {position.shares} shares of {symbol}",
            )
        except Exception as e:
            logger.warning(f"Failed to track decision: {e}")
        
        return {
            "status": "success",
            "message": f"Removed {position.shares} shares of {symbol}",
            "removed_position": {
                "symbol": position.symbol,
                "shares": position.shares,
                "avg_cost": round(position.avg_cost, 2),
                "currency": position.currency,
            },
        }
    else:
        return {
            "status": "error",
            "error": f"Failed to remove position {symbol}",
        }


def get_portfolio_table() -> str:
    """
    Get portfolio as a formatted ASCII table with dual currency display.
    
    Shows values in both original currency and base currency.
    Uses the current owner's portfolio.
    
    Returns:
        ASCII table string showing portfolio positions.
    """
    valuation = get_portfolio_valuation()
    cg = _get_chart_generator()
    base_currency = valuation["base_currency"]
    base_symbol = valuation["base_currency_symbol"]
    owner_name = valuation.get("owner")
    
    # Check if portfolio has multiple currencies
    currencies = set(p.get("currency", "USD") for p in valuation["positions"])
    is_multi_currency = len(currencies) > 1 or (len(currencies) == 1 and list(currencies)[0] != base_currency)
    
    # Header with owner info
    header_line = ""
    if owner_name:
        header_line = f"📊 {owner_name}'s Portfolio ({base_currency})\n"
        header_line += "─" * 60 + "\n\n"
    
    if is_multi_currency:
        # Multi-currency table with both original and base values
        headers = ["Symbol", "Shares", "Avg Cost", "Price", "Value (Orig)", f"Value ({base_currency})", "P&L %", "Weight"]
        rows = []
        
        for pos in valuation["positions"]:
            curr_symbol = pos.get("currency_symbol", "$")
            rows.append([
                pos["symbol"],
                f"{pos['shares']:.2f}",
                f"{curr_symbol}{pos.get('avg_cost', 0):,.2f}",
                f"{curr_symbol}{pos.get('current_price', pos.get('avg_cost', 0)):,.2f}",
                f"{curr_symbol}{pos['current_value']:,.2f}",
                f"{base_symbol}{pos['current_value_base']:,.2f}",
                f"{pos.get('gain_loss_pct', 0):+.1f}%",
                f"{pos['weight']:.1f}%",
            ])
        
        # Add total row
        rows.append([
            "TOTAL",
            "",
            "",
            "",
            "(mixed)",
            f"{base_symbol}{valuation['total_value']:,.2f}",
            f"{valuation['total_gain_loss_pct']:+.1f}%",
            "100%",
        ])
    else:
        # Single currency table (simpler display)
        curr_symbol = base_symbol
        headers = ["Symbol", "Shares", "Avg Cost", "Price", "Value", "P&L", "P&L %", "Weight"]
        rows = []
        
        for pos in valuation["positions"]:
            rows.append([
                pos["symbol"],
                f"{pos['shares']:.2f}",
                f"{curr_symbol}{pos.get('avg_cost', 0):,.2f}",
                f"{curr_symbol}{pos.get('current_price', pos.get('avg_cost', 0)):,.2f}",
                f"{curr_symbol}{pos['current_value']:,.2f}",
                f"{curr_symbol}{pos.get('gain_loss', 0):+,.2f}",
                f"{pos.get('gain_loss_pct', 0):+.1f}%",
                f"{pos['weight']:.1f}%",
            ])
        
        # Add total row
        rows.append([
            "TOTAL",
            "",
            "",
            "",
            f"{curr_symbol}{valuation['total_value']:,.2f}",
            f"{curr_symbol}{valuation['total_gain_loss']:+,.2f}",
            f"{valuation['total_gain_loss_pct']:+.1f}%",
            "100%",
        ])
    
    table = cg.format_ascii_table(
        headers,
        rows,
        alignments=['l', 'r', 'r', 'r', 'r', 'r', 'r', 'r']
    )
    
    return header_line + table


def get_portfolio_history(days: int = 30) -> dict:
    """
    Get portfolio value history.
    
    Args:
        days: Number of days of history to retrieve
    
    Returns:
        Dictionary with portfolio history and performance metrics.
    """
    mm = get_memory_manager()
    sm = get_settings_manager()
    
    current_owner = sm.get_current_owner()
    if current_owner:
        base_currency = current_owner.base_currency
    else:
        base_currency = "USD"
    
    history = mm.get_portfolio_history(days=days)
    metrics = mm.get_performance_metrics(days=days)
    
    return {
        "base_currency": base_currency,
        "history": [
            {
                "date": s.date,
                "total_value": s.total_value_eur,  # Legacy field name
                "cost_basis": s.total_cost_basis,
                "cash": s.cash,
            }
            for s in history
        ],
        "metrics": metrics,
    }


def generate_portfolio_report() -> dict:
    """
    Generate a comprehensive HTML report with charts.
    
    Returns:
        Dictionary with path to generated report and summary.
    """
    valuation = get_portfolio_valuation()
    mm = get_memory_manager()
    cg = _get_chart_generator()
    
    # Get history for charts
    history = mm.get_portfolio_history(days=90)
    
    # Prepare data for dashboard
    portfolio_data = {
        "total_value": valuation["total_value"],
        "positions": valuation["positions"],
    }
    
    history_data = None
    if len(history) > 1:
        history_data = {
            "dates": [s.date for s in history],
            "values": [s.total_value_eur for s in history],
        }
    
    # Generate dashboard
    dashboard_path = cg.combined_dashboard(portfolio_data, history_data)
    
    return {
        "status": "success",
        "report_path": str(dashboard_path),
        "owner": valuation.get("owner"),
        "base_currency": valuation["base_currency"],
        "summary": {
            "total_value": valuation["total_value"],
            "total_gain_loss": valuation["total_gain_loss"],
            "total_gain_loss_pct": valuation["total_gain_loss_pct"],
            "position_count": valuation["position_count"],
        },
        "message": f"Report generated at {dashboard_path}",
    }
