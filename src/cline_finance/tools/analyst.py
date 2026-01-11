"""
Analyst Ratings Tool - Fetches analyst recommendations and price targets.
"""
import logging
from datetime import datetime
from typing import Optional

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


def get_analyst_ratings(symbol: str) -> dict:
    """
    Get analyst ratings, price targets, and recommendations for a stock.
    
    Fetches professional analyst opinions including:
    - Consensus recommendation (buy/hold/sell)
    - Price targets (high, low, mean)
    - Recent upgrades/downgrades
    - Number of analysts covering
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Dictionary with analyst data and recommendations.
    
    Example:
        >>> get_analyst_ratings("AAPL")
        >>> get_analyst_ratings("AMZN")
    """
    symbol = symbol.upper()
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get recommendations history
        recommendations = ticker.recommendations
        upgrades_downgrades = ticker.upgrades_downgrades
        
        # Build result
        result = {
            "symbol": symbol,
            "company_name": info.get("longName") or info.get("shortName") or symbol,
            "current_price": info.get("regularMarketPrice"),
            "currency": info.get("currency", "USD"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        # Price targets
        target_mean = info.get("targetMeanPrice")
        target_high = info.get("targetHighPrice")
        target_low = info.get("targetLowPrice")
        current_price = result["current_price"]
        
        if target_mean and current_price:
            upside = ((target_mean - current_price) / current_price * 100)
        else:
            upside = None
        
        result["price_targets"] = {
            "mean": target_mean,
            "high": target_high,
            "low": target_low,
            "upside_percent": round(upside, 2) if upside else None,
        }
        
        # Consensus recommendation
        recommendation_key = info.get("recommendationKey")
        recommendation_map = {
            "strongBuy": "STRONG BUY",
            "buy": "BUY",
            "hold": "HOLD",
            "sell": "SELL",
            "strongSell": "STRONG SELL",
        }
        
        result["recommendation"] = {
            "consensus": recommendation_map.get(recommendation_key, recommendation_key),
            "number_of_analysts": info.get("numberOfAnalystOpinions"),
        }
        
        # Add sentiment interpretation
        if recommendation_key in ["strongBuy", "buy"]:
            result["recommendation"]["sentiment"] = "BULLISH"
        elif recommendation_key == "hold":
            result["recommendation"]["sentiment"] = "NEUTRAL"
        elif recommendation_key in ["sell", "strongSell"]:
            result["recommendation"]["sentiment"] = "BEARISH"
        else:
            result["recommendation"]["sentiment"] = "UNKNOWN"
        
        # Recent recommendations
        recent_recs = []
        if recommendations is not None and not recommendations.empty:
            for idx, rec in recommendations.tail(5).iterrows():
                rec_dict = {
                    "firm": rec.get("Firm", "Unknown"),
                    "to_grade": rec.get("To Grade", ""),
                    "from_grade": rec.get("From Grade", ""),
                    "action": rec.get("Action", ""),
                }
                # Handle date - could be in index or column
                if isinstance(idx, pd.Timestamp):
                    rec_dict["date"] = idx.strftime("%Y-%m-%d")
                recent_recs.append(rec_dict)
        
        result["recent_recommendations"] = recent_recs[::-1]  # Newest first
        
        # Recent upgrades/downgrades
        recent_changes = []
        if upgrades_downgrades is not None and not upgrades_downgrades.empty:
            for idx, change in upgrades_downgrades.tail(5).iterrows():
                change_dict = {
                    "firm": change.get("Firm", "Unknown"),
                    "to_grade": change.get("ToGrade", ""),
                    "from_grade": change.get("FromGrade", ""),
                    "action": change.get("Action", ""),
                }
                if isinstance(idx, pd.Timestamp):
                    change_dict["date"] = idx.strftime("%Y-%m-%d")
                recent_changes.append(change_dict)
        
        result["recent_changes"] = recent_changes[::-1]  # Newest first
        
        # Summary assessment
        result["summary"] = _generate_summary(result)
        
        logger.info(f"Fetched analyst data for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching analyst data for {symbol}: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


def _generate_summary(data: dict) -> str:
    """Generate a text summary of analyst data."""
    parts = []
    
    symbol = data["symbol"]
    company = data.get("company_name", symbol)
    
    # Recommendation
    rec = data.get("recommendation", {})
    consensus = rec.get("consensus")
    num_analysts = rec.get("number_of_analysts")
    
    if consensus and num_analysts:
        parts.append(f"{company} has a {consensus} consensus rating from {num_analysts} analysts.")
    elif consensus:
        parts.append(f"{company} has a {consensus} consensus rating.")
    
    # Price target
    targets = data.get("price_targets", {})
    target_mean = targets.get("mean")
    upside = targets.get("upside_percent")
    
    if target_mean and upside is not None:
        direction = "upside" if upside > 0 else "downside"
        parts.append(f"Mean price target is ${target_mean:.2f} ({upside:+.1f}% {direction}).")
    
    # Recent activity
    recent = data.get("recent_changes", [])
    if recent:
        latest = recent[0]
        action = latest.get("action", "").lower()
        firm = latest.get("firm", "An analyst")
        if action:
            parts.append(f"Most recent: {firm} {action}.")
    
    return " ".join(parts) if parts else "Limited analyst data available."


def get_multiple_analyst_ratings(symbols: list[str]) -> dict:
    """
    Get analyst ratings for multiple symbols.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Dictionary with ratings for each symbol.
    """
    results = {}
    
    for symbol in symbols:
        results[symbol.upper()] = get_analyst_ratings(symbol)
    
    # Sort by upside potential
    ranked = sorted(
        [(s, d) for s, d in results.items() if "error" not in d],
        key=lambda x: x[1].get("price_targets", {}).get("upside_percent") or 0,
        reverse=True
    )
    
    return {
        "ratings": results,
        "count": len(results),
        "ranked_by_upside": [s for s, _ in ranked],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def get_earnings_calendar(symbol: str) -> dict:
    """
    Get upcoming earnings information for a stock.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Dictionary with earnings date and estimates.
    """
    symbol = symbol.upper()
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        calendar = ticker.calendar
        
        result = {
            "symbol": symbol,
            "company_name": info.get("longName", symbol),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        # Calendar data
        if calendar is not None and not calendar.empty:
            if isinstance(calendar, pd.DataFrame):
                cal_dict = calendar.to_dict()
                result["earnings"] = {
                    "earnings_date": str(cal_dict.get("Earnings Date", [None])[0]) if cal_dict.get("Earnings Date") else None,
                    "earnings_high": cal_dict.get("Earnings High", [None])[0] if cal_dict.get("Earnings High") else None,
                    "earnings_low": cal_dict.get("Earnings Low", [None])[0] if cal_dict.get("Earnings Low") else None,
                    "earnings_average": cal_dict.get("Earnings Average", [None])[0] if cal_dict.get("Earnings Average") else None,
                    "revenue_average": cal_dict.get("Revenue Average", [None])[0] if cal_dict.get("Revenue Average") else None,
                }
        else:
            result["earnings"] = {"note": "No upcoming earnings data available"}
        
        # Historical earnings
        earnings_history = ticker.earnings_history
        if earnings_history is not None and not earnings_history.empty:
            history = []
            for idx, row in earnings_history.tail(4).iterrows():
                history.append({
                    "date": str(idx) if not pd.isna(idx) else None,
                    "eps_estimate": row.get("epsEstimate"),
                    "eps_actual": row.get("epsActual"),
                    "surprise_percent": row.get("surprisePercent"),
                })
            result["earnings_history"] = history[::-1]
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching earnings for {symbol}: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
        }
