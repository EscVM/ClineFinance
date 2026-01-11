"""
Stock Quote Tool - Fetches real-time stock/ETF prices.
"""
import logging
from dataclasses import dataclass
from typing import Optional

import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class StockQuote:
    """Represents a stock/ETF quote."""
    
    symbol: str
    price: float
    currency: str
    change: float
    change_percent: float
    volume: Optional[int]
    market_cap: Optional[int]
    pe_ratio: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    company_name: str
    sector: Optional[str]
    exchange: Optional[str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "symbol": self.symbol,
            "price": self.price,
            "currency": self.currency,
            "change": self.change,
            "change_percent": self.change_percent,
            "volume": self.volume,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "52_week_high": self.fifty_two_week_high,
            "52_week_low": self.fifty_two_week_low,
            "company_name": self.company_name,
            "sector": self.sector,
            "exchange": self.exchange,
        }


def get_stock_quote(symbol: str) -> dict:
    """
    Fetch current stock/ETF quote.
    
    Supports various exchanges via suffixes:
    - No suffix: US exchanges (NYSE, NASDAQ)
    - .AS: Amsterdam (Euronext)
    - .DE: Frankfurt (XETRA)
    - .L: London Stock Exchange
    - .MI: Milan (Borsa Italiana)
    - .PA: Paris (Euronext)
    
    For European-listed US stocks (like AMZN on TDG), prices are in EUR.
    
    Args:
        symbol: Stock ticker symbol with optional exchange suffix
    
    Returns:
        Dictionary with quote data including price, change, and company info.
    
    Raises:
        ValueError: If symbol not found or data unavailable.
    
    Examples:
        >>> get_stock_quote("AAPL")          # US Apple
        >>> get_stock_quote("AMZN.DE")       # Amazon on Frankfurt
        >>> get_stock_quote("IWDA.AS")       # iShares World ETF Amsterdam
    """
    symbol = symbol.upper()
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if we got valid data
        if not info or info.get("regularMarketPrice") is None:
            # Try to get from history as fallback
            hist = ticker.history(period="2d")
            if hist.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
            
            current_price = float(hist['Close'].iloc[-1])
            prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "currency": info.get("currency", "USD"),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else None,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "company_name": info.get("longName", symbol),
                "sector": info.get("sector"),
                "exchange": info.get("exchange"),
            }
        
        # Use info data
        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
        
        if current_price is None:
            raise ValueError(f"Price data unavailable for: {symbol}")
        
        change = current_price - prev_close if prev_close else 0
        change_percent = (change / prev_close * 100) if prev_close and prev_close > 0 else 0
        
        quote = StockQuote(
            symbol=symbol,
            price=round(float(current_price), 2),
            currency=info.get("currency", "USD"),
            change=round(float(change), 2),
            change_percent=round(float(change_percent), 2),
            volume=info.get("regularMarketVolume"),
            market_cap=info.get("marketCap"),
            pe_ratio=round(float(info["trailingPE"]), 2) if info.get("trailingPE") else None,
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            company_name=info.get("longName") or info.get("shortName") or symbol,
            sector=info.get("sector"),
            exchange=info.get("exchange"),
        )
        
        logger.info(f"Fetched quote for {symbol}: {quote.price} {quote.currency}")
        return quote.to_dict()
        
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise ValueError(f"Failed to fetch quote for {symbol}: {str(e)}")


def get_historical_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
) -> dict:
    """
    Fetch historical price data for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: Data interval - 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo
    
    Returns:
        Dictionary with dates, prices, volumes, and summary statistics.
    """
    symbol = symbol.upper()
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise ValueError(f"No historical data for {symbol}")
        
        # Convert to lists for JSON serialization
        dates = [d.strftime("%Y-%m-%d") for d in hist.index]
        closes = [round(float(p), 2) for p in hist['Close']]
        volumes = [int(v) for v in hist['Volume']] if 'Volume' in hist.columns else []
        
        # Calculate summary stats
        start_price = closes[0]
        end_price = closes[-1]
        high_price = max(closes)
        low_price = min(closes)
        total_return = ((end_price - start_price) / start_price * 100) if start_price > 0 else 0
        
        # Volatility (standard deviation of returns)
        returns = hist['Close'].pct_change().dropna()
        volatility = float(returns.std() * 100) if len(returns) > 0 else 0
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(dates),
            "dates": dates,
            "prices": closes,
            "volumes": volumes,
            "summary": {
                "start_price": start_price,
                "end_price": end_price,
                "high": high_price,
                "low": low_price,
                "total_return_percent": round(total_return, 2),
                "volatility_percent": round(volatility, 2),
                "avg_volume": round(sum(volumes) / len(volumes)) if volumes else None,
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        raise ValueError(f"Failed to fetch historical data: {str(e)}")


def get_multiple_quotes(symbols: list[str]) -> dict:
    """
    Fetch quotes for multiple symbols at once.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Dictionary with quotes for each symbol (or error message if failed).
    """
    results = {}
    
    for symbol in symbols:
        try:
            results[symbol.upper()] = get_stock_quote(symbol)
        except Exception as e:
            results[symbol.upper()] = {"error": str(e)}
    
    return {
        "quotes": results,
        "success_count": sum(1 for r in results.values() if "error" not in r),
        "error_count": sum(1 for r in results.values() if "error" in r),
    }
