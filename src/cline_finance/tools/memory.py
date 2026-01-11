"""
Memory Tools - Interface for persistent storage operations.
Supports multi-owner functionality with separate memory per owner.
"""
import logging
from typing import Optional

from cline_finance.core.memory_manager import get_memory_manager

logger = logging.getLogger(__name__)


def save_insight(
    category: str,
    content: str,
    symbol: Optional[str] = None,
    tags: Optional[list[str]] = None,
    expiry_days: Optional[int] = None,
) -> dict:
    """
    Save a market or portfolio insight to memory.
    
    Insights are stored with automatic expiry dates based on category.
    Use this to record important observations for future reference.
    Memory is stored per owner - only the current owner's insights are affected.
    
    Args:
        category: Type of insight - one of:
            - "market": General market conditions
            - "portfolio": Portfolio-specific observations
            - "stock": Individual stock analysis
            - "sector": Sector trends
            - "economic": Macroeconomic observations
            - "earnings": Earnings-related notes
        content: The insight text to save
        symbol: Related stock symbol (optional)
        tags: Tags for filtering (optional, e.g., ["bullish", "tech"])
        expiry_days: Days until insight expires (optional, uses category default)
    
    Returns:
        Dictionary with saved insight details.
    
    Example:
        >>> save_insight("stock", "NVDA showing strong momentum ahead of earnings", 
        ...              symbol="NVDA", tags=["bullish", "earnings"])
    """
    mm = get_memory_manager()
    
    insight = mm.save_insight(
        category=category,
        content=content,
        symbol=symbol,
        tags=tags,
        expiry_days=expiry_days,
    )
    
    return {
        "status": "success",
        "insight": {
            "id": insight.id,
            "date": insight.date,
            "category": insight.category,
            "content": insight.content,
            "symbol": insight.symbol,
            "tags": insight.tags,
            "expires": insight.relevance_expires,
        },
    }


def get_insights(
    category: Optional[str] = None,
    symbol: Optional[str] = None,
    tags: Optional[list[str]] = None,
    limit: int = 20,
) -> dict:
    """
    Retrieve stored insights from memory.
    
    Returns insights matching the specified criteria, sorted by date
    (newest first). Expired insights are automatically excluded.
    Only returns insights for the current owner.
    
    Args:
        category: Filter by category (market, portfolio, stock, etc.)
        symbol: Filter by stock symbol
        tags: Filter by any matching tag
        limit: Maximum number of insights to return
    
    Returns:
        Dictionary with matching insights.
    
    Example:
        >>> get_insights(category="stock", symbol="AMZN")
        >>> get_insights(tags=["bullish"])
    """
    mm = get_memory_manager()
    
    insights = mm.get_insights(
        category=category,
        symbol=symbol,
        tags=tags,
        limit=limit,
    )
    
    return {
        "count": len(insights),
        "filters": {
            "category": category,
            "symbol": symbol,
            "tags": tags,
        },
        "insights": [
            {
                "id": i.id,
                "date": i.date,
                "category": i.category,
                "content": i.content,
                "symbol": i.symbol,
                "tags": i.tags,
            }
            for i in insights
        ],
    }


def track_decision(
    action: str,
    rationale: str,
    symbol: Optional[str] = None,
    shares: Optional[float] = None,
    price: Optional[float] = None,
    review_days: int = 30,
) -> dict:
    """
    Track an investment decision for future review.
    
    Records buy/sell/hold decisions with rationale for later evaluation.
    Decisions are automatically flagged for review after the specified period.
    Decisions are stored per owner.
    
    Args:
        action: Decision type - "buy", "sell", "hold", or "rebalance"
        rationale: Reasoning behind the decision
        symbol: Stock symbol (if applicable)
        shares: Number of shares (if applicable)
        price: Price at decision time (if applicable)
        review_days: Days until review reminder (default 30)
    
    Returns:
        Dictionary with tracked decision details.
    
    Example:
        >>> track_decision("buy", "Adding NVDA for AI exposure", 
        ...                symbol="NVDA", shares=10, price=130.00)
    """
    mm = get_memory_manager()
    
    decision = mm.track_decision(
        action=action,
        rationale=rationale,
        symbol=symbol,
        shares=shares,
        price=price,
        review_days=review_days,
    )
    
    return {
        "status": "success",
        "decision": {
            "id": decision.id,
            "date": decision.date,
            "action": decision.action,
            "symbol": decision.symbol,
            "shares": decision.shares,
            "price": decision.price,
            "rationale": decision.rationale,
            "review_date": decision.review_date,
        },
    }


def get_pending_reviews() -> dict:
    """
    Get investment decisions due for review.
    
    Returns decisions where the review date has passed and
    the outcome hasn't been recorded yet. Only returns decisions
    for the current owner.
    
    Returns:
        Dictionary with pending review decisions.
    """
    mm = get_memory_manager()
    
    pending = mm.get_pending_reviews()
    
    return {
        "count": len(pending),
        "decisions": [
            {
                "id": d.id,
                "date": d.date,
                "action": d.action,
                "symbol": d.symbol,
                "shares": d.shares,
                "price": d.price,
                "rationale": d.rationale,
                "review_date": d.review_date,
                "days_overdue": _days_overdue(d.review_date),
            }
            for d in pending
        ],
    }


def _days_overdue(review_date: Optional[str]) -> int:
    """Calculate days overdue for a review."""
    if not review_date:
        return 0
    from datetime import datetime
    try:
        review = datetime.strptime(review_date, "%Y-%m-%d")
        return (datetime.utcnow() - review).days
    except ValueError:
        return 0


def update_decision_outcome(
    decision_id: str,
    outcome: str,
    close: bool = False,
) -> dict:
    """
    Update a decision with its outcome.
    
    Records how a previous decision turned out. Use this to
    track learning from past investment decisions.
    
    Args:
        decision_id: The decision ID to update
        outcome: Description of the outcome
        close: Whether to close the decision (no more reviews)
    
    Returns:
        Dictionary with update status.
    """
    mm = get_memory_manager()
    
    status = "closed" if close else "reviewed"
    decision = mm.update_decision_outcome(decision_id, outcome, status)
    
    if decision:
        return {
            "status": "success",
            "decision": {
                "id": decision.id,
                "action": decision.action,
                "symbol": decision.symbol,
                "outcome": decision.outcome,
                "status": decision.status,
            },
        }
    else:
        return {
            "status": "error",
            "error": f"Decision {decision_id} not found",
        }


def get_decisions(
    symbol: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """
    Get tracked investment decisions.
    
    Only returns decisions for the current owner.
    
    Args:
        symbol: Filter by stock symbol
        action: Filter by action type (buy, sell, hold, rebalance)
        status: Filter by status (pending, reviewed, closed)
        limit: Maximum number to return
    
    Returns:
        Dictionary with matching decisions.
    """
    mm = get_memory_manager()
    
    decisions = mm.get_decisions(
        symbol=symbol,
        action=action,
        status=status,
        limit=limit,
    )
    
    return {
        "count": len(decisions),
        "filters": {
            "symbol": symbol,
            "action": action,
            "status": status,
        },
        "decisions": [
            {
                "id": d.id,
                "date": d.date,
                "action": d.action,
                "symbol": d.symbol,
                "shares": d.shares,
                "price": d.price,
                "rationale": d.rationale,
                "outcome": d.outcome,
                "status": d.status,
            }
            for d in decisions
        ],
    }


def get_portfolio_history(days: int = 30) -> dict:
    """
    Get historical portfolio values.
    
    Retrieves portfolio snapshots for performance tracking and charting.
    Only returns history for the current owner.
    
    Args:
        days: Number of days of history to retrieve
    
    Returns:
        Dictionary with portfolio history and performance metrics.
    """
    mm = get_memory_manager()
    
    history = mm.get_portfolio_history(days=days)
    metrics = mm.get_performance_metrics(days=days)
    
    return {
        "period_days": days,
        "snapshot_count": len(history),
        "history": [
            {
                "date": s.date,
                "total_value": s.total_value_eur,
                "cost_basis": s.total_cost_basis,
                "cash": s.cash,
            }
            for s in history
        ],
        "metrics": metrics,
    }


def cleanup_memory() -> dict:
    """
    Clean up expired insights from memory.
    
    Removes insights that have passed their expiry date.
    Call this periodically to keep memory manageable.
    Only cleans up current owner's memory.
    
    Returns:
        Dictionary with cleanup results.
    """
    mm = get_memory_manager()
    
    removed = mm.cleanup_expired_insights()
    
    return {
        "status": "success",
        "insights_removed": removed,
    }
