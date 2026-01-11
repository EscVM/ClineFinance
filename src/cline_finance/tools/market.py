"""
Market Overview Tool - Fetches market indices and sentiment data.
"""
import logging
from datetime import datetime
from typing import Optional

import yfinance as yf

from cline_finance.constants import DEFAULT_INDICES, INDEX_NAMES, VIX_THRESHOLDS

logger = logging.getLogger(__name__)


def get_market_overview(indices: Optional[list[str]] = None) -> dict:
    """
    Get current market overview with major indices and sentiment.
    
    Fetches real-time data for major market indices and calculates
    overall market sentiment based on VIX and price movements.
    
    Args:
        indices: List of index symbols to include. Defaults to major indices.
    
    Returns:
        Dictionary with index data, VIX level, and market sentiment.
    
    Example:
        >>> get_market_overview()
        >>> get_market_overview(["^GSPC", "^STOXX50E"])
    """
    if indices is None:
        indices = DEFAULT_INDICES
    
    market_data = []
    advancing = 0
    declining = 0
    
    for index_symbol in indices:
        try:
            ticker = yf.Ticker(index_symbol)
            hist = ticker.history(period="2d")
            
            if hist.empty:
                continue
            
            current_price = float(hist['Close'].iloc[-1])
            prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            # Track advancing/declining
            if change > 0:
                advancing += 1
            elif change < 0:
                declining += 1
            
            market_data.append({
                "symbol": index_symbol,
                "name": INDEX_NAMES.get(index_symbol, index_symbol),
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "status": "up" if change > 0 else "down" if change < 0 else "flat",
            })
            
        except Exception as e:
            logger.warning(f"Error fetching {index_symbol}: {e}")
            market_data.append({
                "symbol": index_symbol,
                "name": INDEX_NAMES.get(index_symbol, index_symbol),
                "error": str(e),
            })
    
    # Get VIX for sentiment
    vix_data = _get_vix_data()
    
    # Determine market sentiment
    sentiment = _calculate_sentiment(vix_data.get("value"), advancing, declining)
    
    # Determine market status (simplified - would need real market hours check)
    now = datetime.utcnow()
    weekday = now.weekday()
    hour = now.hour
    
    # Rough estimate: US markets open 14:30-21:00 UTC
    if weekday < 5 and 14 <= hour < 21:
        market_status = "OPEN"
    else:
        market_status = "CLOSED"
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "market_status": market_status,
        "indices": market_data,
        "vix": vix_data,
        "sentiment": sentiment,
        "breadth": {
            "advancing": advancing,
            "declining": declining,
            "unchanged": len(market_data) - advancing - declining,
        },
    }


def _get_vix_data() -> dict:
    """Get VIX (Volatility Index) data."""
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")
        
        if hist.empty:
            return {"error": "VIX data unavailable"}
        
        current = float(hist['Close'].iloc[-1])
        prev = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current
        change = current - prev
        change_pct = (change / prev * 100) if prev > 0 else 0
        
        # 5-day trend
        five_day_ago = float(hist['Close'].iloc[0])
        trend = "rising" if current > five_day_ago else "falling" if current < five_day_ago else "stable"
        
        # Determine level
        if current < VIX_THRESHOLDS["complacent"]:
            level = "LOW"
            description = "Low volatility - market complacent"
        elif current < VIX_THRESHOLDS["normal"]:
            level = "NORMAL"
            description = "Normal volatility levels"
        elif current < VIX_THRESHOLDS["elevated"]:
            level = "ELEVATED"
            description = "Elevated volatility - some caution"
        elif current < VIX_THRESHOLDS["fearful"]:
            level = "HIGH"
            description = "High volatility - market fearful"
        else:
            level = "EXTREME"
            description = "Extreme volatility - panic conditions"
        
        return {
            "value": round(current, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "level": level,
            "description": description,
            "trend": trend,
        }
        
    except Exception as e:
        logger.error(f"Error fetching VIX: {e}")
        return {"error": str(e)}


def _calculate_sentiment(vix_value: Optional[float], advancing: int, declining: int) -> dict:
    """Calculate overall market sentiment."""
    
    # Base sentiment from VIX
    if vix_value is None:
        vix_sentiment = "UNKNOWN"
        vix_score = 50
    elif vix_value < 15:
        vix_sentiment = "BULLISH"
        vix_score = 80
    elif vix_value < 20:
        vix_sentiment = "NEUTRAL"
        vix_score = 60
    elif vix_value < 25:
        vix_sentiment = "CAUTIOUS"
        vix_score = 45
    elif vix_value < 30:
        vix_sentiment = "FEARFUL"
        vix_score = 30
    else:
        vix_sentiment = "PANIC"
        vix_score = 15
    
    # Adjust based on breadth
    total = advancing + declining
    if total > 0:
        breadth_ratio = advancing / total
        if breadth_ratio > 0.7:
            breadth_sentiment = "BULLISH"
            breadth_score = 80
        elif breadth_ratio > 0.5:
            breadth_sentiment = "POSITIVE"
            breadth_score = 60
        elif breadth_ratio > 0.3:
            breadth_sentiment = "NEGATIVE"
            breadth_score = 40
        else:
            breadth_sentiment = "BEARISH"
            breadth_score = 20
    else:
        breadth_sentiment = "UNKNOWN"
        breadth_score = 50
    
    # Combined score (VIX weighted more heavily)
    combined_score = (vix_score * 0.6 + breadth_score * 0.4)
    
    if combined_score >= 70:
        overall = "BULLISH"
    elif combined_score >= 55:
        overall = "POSITIVE"
    elif combined_score >= 45:
        overall = "NEUTRAL"
    elif combined_score >= 30:
        overall = "CAUTIOUS"
    else:
        overall = "BEARISH"
    
    return {
        "overall": overall,
        "score": round(combined_score),
        "vix_sentiment": vix_sentiment,
        "breadth_sentiment": breadth_sentiment,
    }


def get_market_movers(count: int = 5) -> dict:
    """
    Get top market movers (gainers and losers).
    
    Uses a predefined list of popular stocks to find movers.
    
    Args:
        count: Number of movers to return in each category
    
    Returns:
        Dictionary with top gainers and losers.
    """
    # Popular stocks to check
    popular_stocks = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
        "JPM", "V", "JNJ", "WMT", "PG", "UNH", "HD", "BAC",
        "XOM", "CVX", "PFE", "ABBV", "KO", "PEP", "MRK", "CSCO",
    ]
    
    movers = []
    
    for symbol in popular_stocks:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current = info.get("regularMarketPrice")
            prev = info.get("regularMarketPreviousClose")
            
            if current and prev:
                change_pct = ((current - prev) / prev * 100)
                movers.append({
                    "symbol": symbol,
                    "name": info.get("shortName", symbol),
                    "price": round(current, 2),
                    "change_percent": round(change_pct, 2),
                })
        except Exception:
            continue
    
    # Sort by change percent
    movers.sort(key=lambda x: x["change_percent"], reverse=True)
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "gainers": movers[:count],
        "losers": movers[-count:][::-1],  # Reverse to show biggest loser first
    }


def get_sector_performance() -> dict:
    """
    Get performance of major market sectors.
    
    Uses sector ETFs as proxies for sector performance.
    
    Returns:
        Dictionary with sector performance data.
    """
    # Sector ETFs
    sector_etfs = {
        "XLK": "Technology",
        "XLF": "Financials",
        "XLV": "Healthcare",
        "XLY": "Consumer Discretionary",
        "XLP": "Consumer Staples",
        "XLE": "Energy",
        "XLI": "Industrials",
        "XLB": "Materials",
        "XLRE": "Real Estate",
        "XLU": "Utilities",
        "XLC": "Communication Services",
    }
    
    sectors = []
    
    for symbol, name in sector_etfs.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                continue
            
            current = float(hist['Close'].iloc[-1])
            prev_day = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current
            week_ago = float(hist['Close'].iloc[0])
            
            day_change = ((current - prev_day) / prev_day * 100) if prev_day > 0 else 0
            week_change = ((current - week_ago) / week_ago * 100) if week_ago > 0 else 0
            
            sectors.append({
                "sector": name,
                "etf": symbol,
                "price": round(current, 2),
                "day_change": round(day_change, 2),
                "week_change": round(week_change, 2),
            })
            
        except Exception as e:
            logger.warning(f"Error fetching {symbol}: {e}")
    
    # Sort by day change
    sectors.sort(key=lambda x: x["day_change"], reverse=True)
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sectors": sectors,
        "best_sector": sectors[0]["sector"] if sectors else None,
        "worst_sector": sectors[-1]["sector"] if sectors else None,
    }
