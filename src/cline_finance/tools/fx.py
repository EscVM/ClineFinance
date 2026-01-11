"""
FX Tools - Foreign exchange rate tools.
"""
import logging
from typing import Optional
from datetime import datetime

import yfinance as yf

logger = logging.getLogger(__name__)

# Cache for FX rates (simple in-memory cache)
_fx_cache: dict[str, tuple[float, datetime]] = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


def _get_fx_pair_symbol(from_currency: str, to_currency: str) -> str:
    """Get the yfinance symbol for a currency pair."""
    return f"{from_currency.upper()}{to_currency.upper()}=X"


def _get_cached_rate(cache_key: str) -> Optional[float]:
    """Get a cached rate if still valid."""
    if cache_key in _fx_cache:
        rate, timestamp = _fx_cache[cache_key]
        age = (datetime.utcnow() - timestamp).total_seconds()
        if age < _CACHE_TTL_SECONDS:
            return rate
    return None


def _cache_rate(cache_key: str, rate: float) -> None:
    """Cache a rate."""
    _fx_cache[cache_key] = (rate, datetime.utcnow())


def get_fx_rate(from_currency: str, to_currency: str) -> dict:
    """
    Get the current exchange rate between two currencies.
    
    Uses Yahoo Finance for live FX rates. Rates are cached for 5 minutes
    to avoid excessive API calls.
    
    Args:
        from_currency: Source currency code (e.g., "USD")
        to_currency: Target currency code (e.g., "EUR")
    
    Returns:
        Dictionary with exchange rate and conversion info.
    
    Example:
        >>> get_fx_rate("USD", "EUR")
        {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.92,
            "inverse_rate": 1.087,
            "example": "1 USD = 0.92 EUR"
        }
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Same currency
    if from_currency == to_currency:
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 1.0,
            "inverse_rate": 1.0,
            "example": f"1 {from_currency} = 1 {to_currency}",
            "cached": True,
        }
    
    # Check cache
    cache_key = f"{from_currency}_{to_currency}"
    cached_rate = _get_cached_rate(cache_key)
    if cached_rate is not None:
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": round(cached_rate, 6),
            "inverse_rate": round(1 / cached_rate, 6),
            "example": f"1 {from_currency} = {cached_rate:.4f} {to_currency}",
            "cached": True,
        }
    
    # Fetch from yfinance
    try:
        symbol = _get_fx_pair_symbol(from_currency, to_currency)
        ticker = yf.Ticker(symbol)
        
        # Try to get current price
        info = ticker.info
        rate = info.get("regularMarketPrice") or info.get("previousClose")
        
        if rate is None:
            # Fallback: try fast_info
            rate = ticker.fast_info.get("lastPrice")
        
        if rate is None:
            # Another fallback: try history
            hist = ticker.history(period="1d")
            if not hist.empty:
                rate = hist["Close"].iloc[-1]
        
        if rate is None:
            raise ValueError(f"Could not fetch rate for {symbol}")
        
        # Cache the rate
        _cache_rate(cache_key, rate)
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": round(rate, 6),
            "inverse_rate": round(1 / rate, 6),
            "example": f"1 {from_currency} = {rate:.4f} {to_currency}",
            "cached": False,
            "source": "yfinance",
        }
        
    except Exception as e:
        logger.error(f"Error fetching FX rate {from_currency}/{to_currency}: {e}")
        
        # Try inverse pair
        try:
            inverse_symbol = _get_fx_pair_symbol(to_currency, from_currency)
            ticker = yf.Ticker(inverse_symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                inverse_rate = hist["Close"].iloc[-1]
                rate = 1 / inverse_rate
                
                _cache_rate(cache_key, rate)
                
                return {
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "rate": round(rate, 6),
                    "inverse_rate": round(inverse_rate, 6),
                    "example": f"1 {from_currency} = {rate:.4f} {to_currency}",
                    "cached": False,
                    "source": "yfinance (inverse)",
                }
        except Exception:
            pass
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "error": f"Could not fetch exchange rate: {str(e)}",
            "rate": None,
        }


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict:
    """
    Convert an amount from one currency to another.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., "USD")
        to_currency: Target currency code (e.g., "EUR")
    
    Returns:
        Dictionary with conversion result.
    
    Example:
        >>> convert_currency(100, "USD", "EUR")
        {
            "original_amount": 100,
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.92,
            "converted_amount": 92.0
        }
    """
    rate_result = get_fx_rate(from_currency, to_currency)
    
    if rate_result.get("error") or rate_result.get("rate") is None:
        return {
            "original_amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "error": rate_result.get("error", "Could not fetch exchange rate"),
            "converted_amount": None,
        }
    
    rate = rate_result["rate"]
    converted = amount * rate
    
    return {
        "original_amount": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "rate": rate,
        "converted_amount": round(converted, 2),
        "formatted": f"{amount:,.2f} {from_currency.upper()} = {converted:,.2f} {to_currency.upper()}",
    }


def get_major_fx_rates(base_currency: str = "USD") -> dict:
    """
    Get exchange rates for major currencies against a base currency.
    
    Args:
        base_currency: The base currency to get rates for (default: USD)
    
    Returns:
        Dictionary with rates for major currencies.
    
    Example:
        >>> get_major_fx_rates("USD")
        {
            "base_currency": "USD",
            "rates": {"EUR": 0.92, "GBP": 0.79, ...}
        }
    """
    major_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"]
    base = base_currency.upper()
    
    # Remove base from list
    currencies_to_fetch = [c for c in major_currencies if c != base]
    
    rates = {}
    errors = []
    
    for currency in currencies_to_fetch:
        result = get_fx_rate(base, currency)
        if result.get("rate") is not None:
            rates[currency] = result["rate"]
        else:
            errors.append(currency)
    
    return {
        "base_currency": base,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rates": rates,
        "errors": errors if errors else None,
    }
