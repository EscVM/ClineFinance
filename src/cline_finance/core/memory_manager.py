"""
Memory Manager - Handles persistent storage of insights, decisions, and portfolio history.
Supports multi-owner functionality with separate memory files per owner.
"""
import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from cline_finance.constants import (
    DATA_DIR,
    RETENTION_PERIODS,
    INSIGHT_CATEGORIES,
)

logger = logging.getLogger(__name__)


@dataclass
class Insight:
    """Represents a stored market or portfolio insight."""
    
    id: str
    date: str
    category: str
    content: str
    symbol: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    relevance_expires: Optional[str] = None
    source: str = "analysis"
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> "Insight":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            date=data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
            category=data.get("category", "general"),
            content=data.get("content", ""),
            symbol=data.get("symbol"),
            tags=data.get("tags", []),
            relevance_expires=data.get("relevance_expires"),
            source=data.get("source", "analysis"),
        )
    
    def is_expired(self) -> bool:
        if not self.relevance_expires:
            return False
        try:
            expiry = datetime.strptime(self.relevance_expires, "%Y-%m-%d")
            return datetime.utcnow() > expiry
        except ValueError:
            return False


@dataclass
class Decision:
    """Represents an investment decision for tracking."""
    
    id: str
    date: str
    action: str  # buy, sell, hold, rebalance
    symbol: Optional[str]
    shares: Optional[float]
    price: Optional[float]
    rationale: str
    outcome: Optional[str] = None
    outcome_date: Optional[str] = None
    review_date: Optional[str] = None
    status: str = "pending"  # pending, reviewed, closed
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> "Decision":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            date=data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
            action=data.get("action", ""),
            symbol=data.get("symbol"),
            shares=data.get("shares"),
            price=data.get("price"),
            rationale=data.get("rationale", ""),
            outcome=data.get("outcome"),
            outcome_date=data.get("outcome_date"),
            review_date=data.get("review_date"),
            status=data.get("status", "pending"),
        )


@dataclass
class PortfolioSnapshot:
    """Represents a point-in-time portfolio snapshot."""
    
    date: str
    total_value_eur: float
    total_cost_basis: float
    cash: float
    positions: list[dict]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "PortfolioSnapshot":
        return cls(
            date=data.get("date", ""),
            total_value_eur=data.get("total_value_eur", 0.0),
            total_cost_basis=data.get("total_cost_basis", 0.0),
            cash=data.get("cash", 0.0),
            positions=data.get("positions", []),
        )


def _get_memory_path_for_owner(owner_slug: Optional[str] = None) -> Path:
    """
    Get the memory file path for an owner.
    
    Args:
        owner_slug: Owner slug. If None, uses current owner from settings.
    
    Returns:
        Path to memory.json file
    """
    # Import here to avoid circular imports
    from cline_finance.core.settings_manager import get_settings_manager
    
    sm = get_settings_manager()
    
    if owner_slug:
        owner_dir = DATA_DIR / owner_slug
    else:
        try:
            owner_dir = sm.get_owner_directory()
        except ValueError:
            # No owner configured yet, use legacy path
            return DATA_DIR / "memory.json"
    
    return owner_dir / "memory.json"


class MemoryManager:
    """
    Manages persistent memory for the financial advisor with multi-owner support.
    
    All data stored in owner-specific memory.json file with sections:
    - insights: Market and portfolio insights
    - decisions: Investment decisions with outcomes
    - snapshots: Portfolio history snapshots
    """
    
    def __init__(self, memory_file: Optional[Path] = None, owner_slug: Optional[str] = None):
        """
        Initialize the memory manager.
        
        Args:
            memory_file: Explicit path to memory file. If not provided, uses owner-specific path.
            owner_slug: Owner slug. If not provided, uses current owner from settings.
        """
        self._explicit_file = memory_file
        self._owner_slug = owner_slug
        self._data: Optional[dict] = None
        self._loaded_path: Optional[Path] = None
    
    @property
    def memory_file(self) -> Path:
        """Get the memory file path (owner-aware)."""
        if self._explicit_file:
            return self._explicit_file
        return _get_memory_path_for_owner(self._owner_slug)
    
    def _ensure_directory(self) -> None:
        """Ensure data directory exists."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _should_reload(self) -> bool:
        """Check if we need to reload due to owner change."""
        if self._data is None:
            return True
        current_path = self.memory_file
        return self._loaded_path != current_path
    
    def _load(self, force: bool = False) -> dict:
        """Load memory data from file."""
        if not force and not self._should_reload() and self._data is not None:
            return self._data
        
        current_path = self.memory_file
        
        if not current_path.exists():
            self._data = {"insights": [], "decisions": [], "snapshots": []}
            self._loaded_path = current_path
            return self._data
        
        try:
            with open(current_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            self._loaded_path = current_path
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error loading {current_path}: {e}")
            self._data = {"insights": [], "decisions": [], "snapshots": []}
            self._loaded_path = current_path
        
        return self._data
    
    def _save(self) -> None:
        """Save memory data to file."""
        if self._data is None:
            return
        
        self._ensure_directory()
        self._data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        current_path = self.memory_file
        with open(current_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        
        self._loaded_path = current_path
    
    def reload(self) -> dict:
        """Force reload memory from disk."""
        self._data = None
        self._loaded_path = None
        data = self._load(force=True)
        return data if data is not None else {"insights": [], "decisions": [], "snapshots": []}
    
    # -------------------------------------------------------------------------
    # Insights Management
    # -------------------------------------------------------------------------
    
    def save_insight(
        self,
        category: str,
        content: str,
        symbol: Optional[str] = None,
        tags: Optional[list[str]] = None,
        expiry_days: Optional[int] = None,
    ) -> Insight:
        """Save a new insight to memory."""
        if category not in INSIGHT_CATEGORIES:
            category = "market"
        
        if expiry_days is None:
            expiry_days = RETENTION_PERIODS.get("general_insights", 180)
        
        expiry_date = None
        if expiry_days:
            expiry_date = (datetime.utcnow() + timedelta(days=expiry_days)).strftime("%Y-%m-%d")
        
        insight = Insight(
            id=str(uuid.uuid4()),
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            category=category,
            content=content,
            symbol=symbol.upper() if symbol else None,
            tags=tags or [],
            relevance_expires=expiry_date,
        )
        
        data = self._load()
        data["insights"].append(insight.to_dict())
        self._save()
        
        logger.info(f"Saved insight: {category} - {content[:50]}...")
        return insight
    
    def get_insights(
        self,
        category: Optional[str] = None,
        symbol: Optional[str] = None,
        tags: Optional[list[str]] = None,
        include_expired: bool = False,
        limit: int = 20,
    ) -> list[Insight]:
        """Retrieve insights matching criteria."""
        data = self._load()
        insights = [Insight.from_dict(i) for i in data.get("insights", [])]
        
        filtered = []
        for insight in insights:
            if not include_expired and insight.is_expired():
                continue
            if category and insight.category != category:
                continue
            if symbol and insight.symbol != symbol.upper():
                continue
            if tags and not any(t in insight.tags for t in tags):
                continue
            filtered.append(insight)
        
        filtered.sort(key=lambda x: x.date, reverse=True)
        return filtered[:limit]
    
    def cleanup_expired_insights(self) -> int:
        """Remove expired insights from storage."""
        data = self._load()
        original_count = len(data.get("insights", []))
        insights = [Insight.from_dict(i) for i in data.get("insights", [])]
        valid_insights = [i for i in insights if not i.is_expired()]
        
        data["insights"] = [i.to_dict() for i in valid_insights]
        self._save()
        
        removed = original_count - len(valid_insights)
        logger.info(f"Cleaned up {removed} expired insights")
        return removed
    
    # -------------------------------------------------------------------------
    # Decisions Management
    # -------------------------------------------------------------------------
    
    def track_decision(
        self,
        action: str,
        rationale: str,
        symbol: Optional[str] = None,
        shares: Optional[float] = None,
        price: Optional[float] = None,
        review_days: int = 30,
    ) -> Decision:
        """Track an investment decision for future review."""
        review_date = (datetime.utcnow() + timedelta(days=review_days)).strftime("%Y-%m-%d")
        
        decision = Decision(
            id=str(uuid.uuid4()),
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            action=action,
            symbol=symbol.upper() if symbol else None,
            shares=shares,
            price=price,
            rationale=rationale,
            review_date=review_date,
        )
        
        data = self._load()
        data["decisions"].append(decision.to_dict())
        self._save()
        
        logger.info(f"Tracked decision: {action} {symbol or ''}")
        return decision
    
    def get_pending_reviews(self) -> list[Decision]:
        """Get decisions that are due for review."""
        data = self._load()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        pending = []
        
        for d in data.get("decisions", []):
            decision = Decision.from_dict(d)
            if decision.status == "pending" and decision.review_date and decision.review_date <= today:
                pending.append(decision)
        
        return pending
    
    def update_decision_outcome(
        self,
        decision_id: str,
        outcome: str,
        status: str = "reviewed",
    ) -> Optional[Decision]:
        """Update a decision with its outcome."""
        data = self._load()
        
        for i, d in enumerate(data.get("decisions", [])):
            if d.get("id") == decision_id:
                d["outcome"] = outcome
                d["outcome_date"] = datetime.utcnow().strftime("%Y-%m-%d")
                d["status"] = status
                data["decisions"][i] = d
                self._save()
                logger.info(f"Updated decision {decision_id} outcome")
                return Decision.from_dict(d)
        
        logger.warning(f"Decision {decision_id} not found")
        return None
    
    def get_decisions(
        self,
        symbol: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> list[Decision]:
        """Get decisions matching criteria."""
        data = self._load()
        decisions = [Decision.from_dict(d) for d in data.get("decisions", [])]
        
        filtered = []
        for d in decisions:
            if symbol and d.symbol != symbol.upper():
                continue
            if action and d.action != action:
                continue
            if status and d.status != status:
                continue
            filtered.append(d)
        
        filtered.sort(key=lambda x: x.date, reverse=True)
        return filtered[:limit]
    
    # -------------------------------------------------------------------------
    # Portfolio History Management
    # -------------------------------------------------------------------------
    
    def save_portfolio_snapshot(
        self,
        total_value_eur: float,
        total_cost_basis: float,
        cash: float,
        positions: list[dict],
    ) -> PortfolioSnapshot:
        """Save a portfolio snapshot."""
        snapshot = PortfolioSnapshot(
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            total_value_eur=total_value_eur,
            total_cost_basis=total_cost_basis,
            cash=cash,
            positions=positions,
        )
        
        data = self._load()
        today = snapshot.date
        
        # Check if we already have a snapshot for today
        existing_index = None
        for i, s in enumerate(data.get("snapshots", [])):
            if s.get("date") == today:
                existing_index = i
                break
        
        if existing_index is not None:
            data["snapshots"][existing_index] = snapshot.to_dict()
        else:
            data["snapshots"].append(snapshot.to_dict())
        
        self._save()
        logger.info(f"Saved portfolio snapshot: €{total_value_eur:,.2f}")
        return snapshot
    
    def get_portfolio_history(
        self,
        days: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[PortfolioSnapshot]:
        """Get portfolio history snapshots."""
        data = self._load()
        snapshots = [PortfolioSnapshot.from_dict(s) for s in data.get("snapshots", [])]
        
        if days:
            cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            snapshots = [s for s in snapshots if s.date >= cutoff]
        
        snapshots.sort(key=lambda x: x.date)
        
        if limit:
            snapshots = snapshots[-limit:]
        
        return snapshots
    
    def get_performance_metrics(self, days: int = 30) -> dict:
        """Calculate performance metrics from history."""
        snapshots = self.get_portfolio_history(days=days)
        
        if len(snapshots) < 2:
            return {
                "period_days": days,
                "snapshots_available": len(snapshots),
                "error": "Insufficient data for performance calculation",
            }
        
        first = snapshots[0]
        last = snapshots[-1]
        
        value_change = last.total_value_eur - first.total_value_eur
        value_change_pct = (value_change / first.total_value_eur * 100) if first.total_value_eur > 0 else 0
        
        values = [s.total_value_eur for s in snapshots]
        
        return {
            "period_days": days,
            "snapshots_available": len(snapshots),
            "start_date": first.date,
            "end_date": last.date,
            "start_value": first.total_value_eur,
            "end_value": last.total_value_eur,
            "value_change": round(value_change, 2),
            "value_change_percent": round(value_change_pct, 2),
            "period_high": max(values),
            "period_low": min(values),
        }


# Module-level instance cache (owner-aware)
_memory_managers: dict[str, MemoryManager] = {}


def get_memory_manager(owner_slug: Optional[str] = None) -> MemoryManager:
    """
    Get a memory manager instance for an owner.
    
    Args:
        owner_slug: Owner slug. If None, uses current owner from settings.
    
    Returns:
        MemoryManager instance
    """
    from cline_finance.core.settings_manager import get_settings_manager
    
    sm = get_settings_manager()
    
    if owner_slug is None:
        settings = sm.get_settings()
        owner_slug = settings.current_owner
    
    # Use empty string key for unconfigured state
    cache_key = owner_slug or ""
    
    if cache_key not in _memory_managers:
        _memory_managers[cache_key] = MemoryManager(owner_slug=owner_slug)
    
    return _memory_managers[cache_key]


def reset_memory_managers() -> None:
    """Reset all cached memory managers (for testing)."""
    global _memory_managers
    _memory_managers = {}
