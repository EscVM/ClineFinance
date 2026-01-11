"""
Financial News Tool - Fetches relevant financial news.
"""
import logging
from datetime import datetime
from typing import Optional

import requests

from cline_finance.constants import NEWS_API_KEY

logger = logging.getLogger(__name__)


def get_financial_news(
    query: str = "stock market",
    symbols: Optional[list[str]] = None,
    limit: int = 10,
) -> dict:
    """
    Get latest financial news relevant to query or portfolio holdings.
    
    Uses NewsAPI to fetch recent financial articles. If no API key is configured,
    falls back to yfinance news for specific symbols.
    
    Args:
        query: Search term for news (e.g., "Apple earnings", "market outlook")
        symbols: List of stock symbols to get news for (optional)
        limit: Maximum number of articles to return (1-20)
    
    Returns:
        Dictionary with news articles and metadata.
    
    Example:
        >>> get_financial_news("NVIDIA AI chips")
        >>> get_financial_news(symbols=["AMZN", "MSFT"])
    """
    limit = min(max(1, limit), 20)  # Clamp to 1-20
    
    # If symbols provided, try to get news from yfinance
    if symbols:
        return _get_symbol_news(symbols, limit)
    
    # Try NewsAPI if key is available
    if NEWS_API_KEY:
        return _get_newsapi_news(query, limit)
    
    # Fallback to general market news via yfinance
    return _get_market_news_fallback(limit)


def _get_newsapi_news(query: str, limit: int) -> dict:
    """Fetch news from NewsAPI."""
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": NEWS_API_KEY,
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            raise Exception(data.get("message", "NewsAPI error"))
        
        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "source": article.get("source", {}).get("name"),
                "published_at": article.get("publishedAt"),
                "author": article.get("author"),
            })
        
        return {
            "query": query,
            "source": "NewsAPI",
            "articles": articles,
            "count": len(articles),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
    except Exception as e:
        logger.error(f"NewsAPI error: {e}")
        return {
            "query": query,
            "error": str(e),
            "articles": [],
            "count": 0,
        }


def _get_symbol_news(symbols: list[str], limit: int) -> dict:
    """Get news for specific symbols using yfinance."""
    import yfinance as yf
    
    all_news = []
    seen_titles = set()
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol.upper())
            news = ticker.news
            
            if news:
                for item in news[:5]:  # Limit per symbol
                    title = item.get("title", "")
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        all_news.append({
                            "title": title,
                            "description": item.get("summary"),
                            "url": item.get("link"),
                            "source": item.get("publisher"),
                            "published_at": datetime.fromtimestamp(
                                item.get("providerPublishTime", 0)
                            ).isoformat() if item.get("providerPublishTime") else None,
                            "related_symbol": symbol.upper(),
                        })
        except Exception as e:
            logger.warning(f"Error fetching news for {symbol}: {e}")
    
    # Sort by published date (newest first)
    all_news.sort(
        key=lambda x: x.get("published_at") or "",
        reverse=True
    )
    
    return {
        "symbols": [s.upper() for s in symbols],
        "source": "yfinance",
        "articles": all_news[:limit],
        "count": len(all_news[:limit]),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def _get_market_news_fallback(limit: int) -> dict:
    """Fallback to general market news via major indices/ETFs."""
    import yfinance as yf
    
    # Get news from major market ETFs
    market_symbols = ["SPY", "QQQ", "DIA"]
    all_news = []
    seen_titles = set()
    
    for symbol in market_symbols:
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if news:
                for item in news[:5]:
                    title = item.get("title", "")
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        all_news.append({
                            "title": title,
                            "description": item.get("summary"),
                            "url": item.get("link"),
                            "source": item.get("publisher"),
                            "published_at": datetime.fromtimestamp(
                                item.get("providerPublishTime", 0)
                            ).isoformat() if item.get("providerPublishTime") else None,
                        })
        except Exception:
            continue
    
    # Sort by date
    all_news.sort(
        key=lambda x: x.get("published_at") or "",
        reverse=True
    )
    
    return {
        "query": "market news",
        "source": "yfinance (fallback)",
        "articles": all_news[:limit],
        "count": len(all_news[:limit]),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "note": "Set NEWS_API_KEY environment variable for broader news coverage",
    }


def get_portfolio_news(portfolio_symbols: list[str], limit: int = 10) -> dict:
    """
    Get news relevant to portfolio holdings.
    
    Filters and prioritizes news that may impact the given holdings.
    
    Args:
        portfolio_symbols: List of symbols in the portfolio
        limit: Maximum total articles to return
    
    Returns:
        Dictionary with portfolio-relevant news.
    """
    # Get news for all portfolio symbols
    result = _get_symbol_news(portfolio_symbols, limit * 2)
    
    # Add relevance scoring (simple implementation)
    for article in result.get("articles", []):
        relevance = 0
        title = (article.get("title") or "").lower()
        desc = (article.get("description") or "").lower()
        
        # Check for mentions of portfolio symbols
        for symbol in portfolio_symbols:
            if symbol.lower() in title:
                relevance += 3
            elif symbol.lower() in desc:
                relevance += 1
        
        # Boost for certain keywords
        important_keywords = [
            "earnings", "revenue", "guidance", "upgrade", "downgrade",
            "acquisition", "merger", "lawsuit", "recall", "dividend",
        ]
        for keyword in important_keywords:
            if keyword in title:
                relevance += 2
            elif keyword in desc:
                relevance += 1
        
        article["relevance_score"] = relevance
    
    # Sort by relevance, then by date
    articles = result.get("articles", [])
    articles.sort(
        key=lambda x: (x.get("relevance_score", 0), x.get("published_at") or ""),
        reverse=True
    )
    
    result["articles"] = articles[:limit]
    result["count"] = len(result["articles"])
    
    return result
