"""
Portfolio Manager - Handles CRUD operations for portfolio data with multi-owner support.
"""
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from cline_finance.constants import DATA_DIR

logger = logging.getLogger(__name__)


@dataclass
class Lot:
    """Represents a single purchase lot within a position."""
    
    date: str           # Purchase date (YYYY-MM-DD)
    shares: float       # Shares in this lot
    price: float        # Price per share at purchase
    currency: str       # Currency at purchase
    notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {
            "date": self.date,
            "shares": self.shares,
            "price": self.price,
            "currency": self.currency,
        }
        if self.notes:
            result["notes"] = self.notes
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "Lot":
        """Create Lot from dictionary."""
        return cls(
            date=data.get("date", "unknown"),
            shares=data.get("shares", 0),
            price=data.get("price", 0),
            currency=data.get("currency", "EUR"),
            notes=data.get("notes"),
        )


@dataclass
class Position:
    """Represents a single portfolio position with lot tracking."""
    
    symbol: str
    currency: str = "EUR"
    lots: list = field(default_factory=list)  # List of Lot objects
    sector: Optional[str] = None
    asset_type: str = "stock"
    isin: Optional[str] = None
    exchange: Optional[str] = None
    company_name: Optional[str] = None
    notes: Optional[str] = None
    
    @property
    def shares(self) -> float:
        """Total shares computed from all lots."""
        return sum(lot.shares for lot in self.lots) if self.lots else 0
    
    @property
    def avg_cost(self) -> float:
        """Weighted average cost computed from all lots."""
        if not self.lots:
            return 0
        total_cost = sum(lot.shares * lot.price for lot in self.lots)
        total_shares = sum(lot.shares for lot in self.lots)
        return total_cost / total_shares if total_shares > 0 else 0
    
    @property
    def first_purchase(self) -> Optional[str]:
        """Get the earliest lot date."""
        if self.lots:
            dates = [lot.date for lot in self.lots if lot.date != "unknown"]
            return min(dates) if dates else None
        return None
    
    @property
    def cost_basis(self) -> float:
        """Total cost basis of this position."""
        return sum(lot.shares * lot.price for lot in self.lots) if self.lots else 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "symbol": self.symbol,
            "currency": self.currency,
            "lots": [lot.to_dict() for lot in self.lots],
        }
        if self.sector:
            result["sector"] = self.sector
        if self.asset_type != "stock":
            result["asset_type"] = self.asset_type
        if self.isin:
            result["isin"] = self.isin
        if self.exchange:
            result["exchange"] = self.exchange
        if self.company_name:
            result["company_name"] = self.company_name
        if self.notes:
            result["notes"] = self.notes
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        """Create Position from dictionary, handling legacy formats."""
        symbol = data.get("symbol", "")
        currency = data.get("currency") or data.get("purchase_currency", "EUR")
        
        # Handle lots
        lots_data = data.get("lots", [])
        if lots_data:
            lots = [Lot.from_dict(lot) for lot in lots_data]
        else:
            # Legacy migration: create single lot from shares/avg_cost
            shares = data.get("shares", 0)
            avg_cost = data.get("avg_cost") or data.get("purchase_price", 0)
            first_purchase = data.get("first_purchase", "unknown")
            
            if shares > 0:
                lots = [Lot(
                    date=first_purchase or "unknown",
                    shares=shares,
                    price=avg_cost,
                    currency=currency,
                )]
            else:
                lots = []
        
        return cls(
            symbol=symbol,
            currency=currency,
            lots=lots,
            sector=data.get("sector"),
            asset_type=data.get("asset_type", "stock"),
            isin=data.get("isin"),
            exchange=data.get("exchange"),
            company_name=data.get("company_name"),
            notes=data.get("notes"),
        )


@dataclass
class Portfolio:
    """Represents the complete portfolio."""
    
    positions: list[Position] = field(default_factory=list)
    cash: float = 0.0
    base_currency: str = "EUR"
    owner: Optional[str] = None
    last_updated: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": "2.0",
            "base_currency": self.base_currency,
            "owner": self.owner,
            "last_updated": self.last_updated or datetime.utcnow().isoformat() + "Z",
            "cash": self.cash,
            "positions": [p.to_dict() for p in self.positions],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        """Create Portfolio from dictionary."""
        # Handle legacy format
        if "portfolio" in data:
            legacy = data["portfolio"]
            positions_data = legacy.get("holdings", [])
            return cls(
                positions=[Position.from_dict(p) for p in positions_data],
                cash=legacy.get("cash", 0.0),
                base_currency=legacy.get("base_currency", "EUR"),
                owner=legacy.get("owner"),
                last_updated=legacy.get("last_updated"),
            )
        
        # New format
        positions_data = data.get("positions", [])
        return cls(
            positions=[Position.from_dict(p) for p in positions_data],
            cash=data.get("cash", 0.0),
            base_currency=data.get("base_currency", "EUR"),
            owner=data.get("owner"),
            last_updated=data.get("last_updated"),
        )
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position by symbol."""
        symbol_upper = symbol.upper()
        for pos in self.positions:
            if pos.symbol.upper() == symbol_upper:
                return pos
        return None
    
    def total_cost_basis(self) -> float:
        """Calculate total cost basis of all positions."""
        return sum(p.shares * p.avg_cost for p in self.positions)


def _get_portfolio_path_for_owner(owner_slug: Optional[str] = None) -> Path:
    """
    Get the portfolio file path for an owner.
    
    Args:
        owner_slug: Owner slug. If None, uses current owner from settings.
    
    Returns:
        Path to portfolio.json file
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
            return DATA_DIR / "portfolio.json"
    
    return owner_dir / "portfolio.json"


class PortfolioManager:
    """
    Manages portfolio data with file persistence and multi-owner support.
    
    Provides CRUD operations for portfolio positions with automatic
    file synchronization and validation.
    """
    
    def __init__(self, portfolio_path: Optional[Path] = None, owner_slug: Optional[str] = None):
        """
        Initialize the portfolio manager.
        
        Args:
            portfolio_path: Path to portfolio JSON file. If not provided, 
                            uses owner-specific path.
            owner_slug: Owner slug to use. If not provided, uses current owner.
        """
        self._explicit_path = portfolio_path
        self._owner_slug = owner_slug
        self._portfolio: Optional[Portfolio] = None
        self._loaded_path: Optional[Path] = None
    
    @property
    def portfolio_path(self) -> Path:
        """Get the portfolio file path (owner-aware)."""
        if self._explicit_path:
            return self._explicit_path
        return _get_portfolio_path_for_owner(self._owner_slug)
    
    def _ensure_directory(self) -> None:
        """Ensure the data directory exists."""
        self.portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _should_reload(self) -> bool:
        """Check if we need to reload due to owner change."""
        if self._portfolio is None:
            return True
        current_path = self.portfolio_path
        return self._loaded_path != current_path
    
    def load(self, force: bool = False) -> Portfolio:
        """
        Load portfolio from file.
        
        Args:
            force: Force reload even if already loaded.
        
        Returns:
            Portfolio object with current holdings.
        """
        if not force and not self._should_reload() and self._portfolio is not None:
            return self._portfolio
        
        current_path = self.portfolio_path
        
        if not current_path.exists():
            logger.info(f"Portfolio file not found at {current_path}, creating empty portfolio")
            self._portfolio = Portfolio()
            self._loaded_path = current_path
            return self._portfolio
        
        with open(current_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._portfolio = Portfolio.from_dict(data)
        self._loaded_path = current_path
        logger.info(f"Loaded portfolio with {len(self._portfolio.positions)} positions from {current_path}")
        return self._portfolio
    
    def save(self) -> None:
        """
        Save portfolio to file.
        
        Updates the last_updated timestamp automatically.
        """
        if self._portfolio is None:
            raise ValueError("No portfolio loaded to save")
        
        self._ensure_directory()
        self._portfolio.last_updated = datetime.utcnow().isoformat() + "Z"
        
        # Sync owner name from settings if not set
        if not self._portfolio.owner:
            from cline_finance.core.settings_manager import get_settings_manager
            sm = get_settings_manager()
            owner = sm.get_current_owner()
            if owner:
                self._portfolio.owner = owner.name
        
        current_path = self.portfolio_path
        with open(current_path, "w", encoding="utf-8") as f:
            json.dump(self._portfolio.to_dict(), f, indent=2)
        
        self._loaded_path = current_path
        logger.info(f"Saved portfolio to {current_path}")
    
    def add_position(
        self,
        symbol: str,
        shares: float,
        avg_cost: float,
        currency: str = "EUR",
        sector: Optional[str] = None,
        asset_type: str = "stock",
        isin: Optional[str] = None,
        exchange: Optional[str] = None,
        company_name: Optional[str] = None,
        notes: Optional[str] = None,
        purchase_date: Optional[str] = None,
    ) -> Position:
        """
        Add a new position or add to existing one via lot tracking.
        
        If position already exists, adds a new lot and avg_cost is recomputed.
        
        Args:
            symbol: Stock/ETF ticker symbol
            shares: Number of shares to add
            avg_cost: Purchase price per share
            currency: Currency of the purchase price
            sector: Business sector
            asset_type: 'stock' or 'etf'
            isin: International Securities ID
            exchange: Exchange code
            company_name: Full company name
            notes: Personal notes about this purchase lot
            purchase_date: Date of purchase (YYYY-MM-DD), defaults to today
        
        Returns:
            The added or updated Position.
        """
        portfolio = self.load()
        existing = portfolio.get_position(symbol)
        
        # Create the new lot
        lot_date = purchase_date or datetime.utcnow().strftime("%Y-%m-%d")
        new_lot = Lot(
            date=lot_date,
            shares=shares,
            price=avg_cost,
            currency=currency,
            notes=notes,
        )
        
        if existing:
            # Append new lot to existing position
            existing.lots.append(new_lot)
            
            # Update optional fields if provided
            if sector:
                existing.sector = sector
            if company_name:
                existing.company_name = company_name
            # Position-level notes are separate from lot notes
            
            logger.info(f"Added lot to {symbol}: +{shares} shares @ {currency}{avg_cost:.2f} (total: {existing.shares} @ {existing.avg_cost:.2f})")
            self.save()
            return existing
        
        # Create new position with initial lot
        new_position = Position(
            symbol=symbol.upper(),
            currency=currency,
            lots=[new_lot],
            sector=sector,
            asset_type=asset_type,
            isin=isin,
            exchange=exchange,
            company_name=company_name,
        )
        portfolio.positions.append(new_position)
        logger.info(f"Added new position {symbol}: {shares} shares @ {currency}{avg_cost:.2f}")
        self.save()
        return new_position
    
    def update_position(
        self,
        symbol: str,
        shares: Optional[float] = None,
        avg_cost: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Position:
        """
        Update an existing position.
        
        Note: If shares or avg_cost are provided, this will consolidate all lots
        into a single lot with the new values (for manual corrections).
        
        Args:
            symbol: Stock ticker to update
            shares: New total share count (consolidates lots if provided)
            avg_cost: New average cost (consolidates lots if provided)
            notes: Updated position-level notes (if provided)
        
        Returns:
            Updated Position.
        
        Raises:
            ValueError: If position doesn't exist.
        """
        portfolio = self.load()
        position = portfolio.get_position(symbol)
        
        if not position:
            raise ValueError(f"Position {symbol} not found in portfolio")
        
        # If shares or avg_cost is being modified, consolidate lots
        if shares is not None or avg_cost is not None:
            # Use provided values or current computed values
            new_shares = shares if shares is not None else position.shares
            new_avg_cost = avg_cost if avg_cost is not None else position.avg_cost
            
            # Get earliest date from existing lots
            earliest_date = position.first_purchase or datetime.utcnow().strftime("%Y-%m-%d")
            
            # Replace all lots with a single consolidated lot
            position.lots = [Lot(
                date=earliest_date,
                shares=new_shares,
                price=new_avg_cost,
                currency=position.currency,
                notes="Consolidated from manual adjustment",
            )]
            logger.info(f"Consolidated {symbol} lots: {new_shares} shares @ {new_avg_cost:.2f}")
        
        if notes is not None:
            position.notes = notes
        
        logger.info(f"Updated position {symbol}")
        self.save()
        return position
    
    def remove_position(self, symbol: str) -> bool:
        """
        Remove a position from the portfolio.
        
        Args:
            symbol: Stock ticker to remove.
        
        Returns:
            True if position was removed, False if not found.
        """
        portfolio = self.load()
        symbol_upper = symbol.upper()
        
        for i, pos in enumerate(portfolio.positions):
            if pos.symbol.upper() == symbol_upper:
                removed = portfolio.positions.pop(i)
                logger.info(f"Removed position {removed.symbol}")
                self.save()
                return True
        
        logger.warning(f"Position {symbol} not found for removal")
        return False
    
    def get_portfolio(self) -> Portfolio:
        """
        Get the current portfolio.
        
        Returns:
            Current Portfolio object.
        """
        return self.load()
    
    def update_cash(self, amount: float) -> float:
        """
        Update cash balance.
        
        Args:
            amount: New cash balance (or amount to add if negative).
        
        Returns:
            New cash balance.
        """
        portfolio = self.load()
        portfolio.cash = amount
        self.save()
        return portfolio.cash
    
    def get_summary(self) -> dict:
        """
        Get a summary of the portfolio.
        
        Returns:
            Dictionary with portfolio summary stats.
        """
        portfolio = self.load()
        
        return {
            "owner": portfolio.owner,
            "base_currency": portfolio.base_currency,
            "last_updated": portfolio.last_updated,
            "total_positions": len(portfolio.positions),
            "cash": portfolio.cash,
            "total_cost_basis": portfolio.total_cost_basis(),
            "positions": [
                {
                    "symbol": p.symbol,
                    "shares": p.shares,
                    "avg_cost": p.avg_cost,
                    "cost_basis": p.shares * p.avg_cost,
                    "sector": p.sector,
                    "asset_type": p.asset_type,
                }
                for p in portfolio.positions
            ],
        }
    
    def reload(self) -> Portfolio:
        """Force reload portfolio from disk."""
        self._portfolio = None
        self._loaded_path = None
        return self.load(force=True)


# Module-level instance cache (owner-aware)
_portfolio_managers: dict[str, PortfolioManager] = {}


def get_portfolio_manager(owner_slug: Optional[str] = None) -> PortfolioManager:
    """
    Get a portfolio manager instance for an owner.
    
    Args:
        owner_slug: Owner slug. If None, uses current owner from settings.
    
    Returns:
        PortfolioManager instance
    """
    from cline_finance.core.settings_manager import get_settings_manager
    
    sm = get_settings_manager()
    
    if owner_slug is None:
        settings = sm.get_settings()
        owner_slug = settings.current_owner
    
    # Use empty string key for unconfigured state
    cache_key = owner_slug or ""
    
    if cache_key not in _portfolio_managers:
        _portfolio_managers[cache_key] = PortfolioManager(owner_slug=owner_slug)
    
    return _portfolio_managers[cache_key]


def reset_portfolio_managers() -> None:
    """Reset all cached portfolio managers (for testing)."""
    global _portfolio_managers
    _portfolio_managers = {}
