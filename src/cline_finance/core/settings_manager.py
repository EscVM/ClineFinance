"""
Settings Manager - Handles user preferences persistence with multi-owner support.
"""
import json
import logging
import shutil
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from cline_finance.constants import DATA_DIR

logger = logging.getLogger(__name__)

SETTINGS_FILE = DATA_DIR / "settings.json"

# Currency symbols mapping
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CHF": "CHF",
    "CAD": "C$",
    "AUD": "A$",
    "CNY": "¥",
    "HKD": "HK$",
    "SGD": "S$",
    "SEK": "kr",
    "NOK": "kr",
    "DKK": "kr",
    "INR": "₹",
    "BRL": "R$",
    "MXN": "MX$",
    "KRW": "₩",
    "TWD": "NT$",
    "PLN": "zł",
    "CZK": "Kč",
}


def slugify(name: str) -> str:
    """Convert owner name to a safe directory slug."""
    return name.lower().strip().replace(" ", "_").replace("-", "_")


@dataclass
class OwnerSettings:
    """Settings specific to an owner."""
    
    name: str  # Display name
    base_currency: str = "USD"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "OwnerSettings":
        return cls(
            name=data.get("name", "Unknown"),
            base_currency=data.get("base_currency", "USD"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    def get_currency_symbol(self, currency: Optional[str] = None) -> str:
        """Get the symbol for a currency code."""
        curr = currency or self.base_currency
        return CURRENCY_SYMBOLS.get(curr.upper(), curr)


@dataclass
class GlobalSettings:
    """Global application settings with multi-owner support."""
    
    current_owner: Optional[str] = None  # Slug of current owner
    date_format: str = "YYYY-MM-DD"
    owners: Dict[str, OwnerSettings] = field(default_factory=dict)
    version: str = "2.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    _legacy_currency: Optional[str] = field(default=None, repr=False)  # For migration
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "current_owner": self.current_owner,
            "date_format": self.date_format,
            "owners": {k: v.to_dict() for k, v in self.owners.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GlobalSettings":
        owners = {}
        owners_data = data.get("owners", {})
        for slug, owner_data in owners_data.items():
            owners[slug] = OwnerSettings.from_dict(owner_data)
        
        return cls(
            current_owner=data.get("current_owner"),
            date_format=data.get("date_format", "YYYY-MM-DD"),
            owners=owners,
            version=data.get("version", "2.0"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    def get_current_owner_settings(self) -> Optional[OwnerSettings]:
        """Get settings for the current owner."""
        if self.current_owner and self.current_owner in self.owners:
            return self.owners[self.current_owner]
        return None


class SettingsManager:
    """
    Manages user settings with file persistence and multi-owner support.
    
    Settings are stored in data/settings.json.
    Each owner has their own subdirectory: data/{owner_slug}/
    """
    
    def __init__(self, settings_path: Optional[Path] = None):
        """
        Initialize the settings manager.
        
        Args:
            settings_path: Path to settings JSON file. Defaults to SETTINGS_FILE.
        """
        self.settings_path = settings_path or SETTINGS_FILE
        self._settings: Optional[GlobalSettings] = None
        self._migration_done = False
    
    def _ensure_directory(self) -> None:
        """Ensure the data directory exists."""
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _migrate_legacy_data(self) -> Optional[str]:
        """
        Migrate legacy single-owner data to multi-owner structure.
        
        Returns:
            Owner slug if migration was performed, None otherwise.
        """
        if self._migration_done:
            return None
        
        self._migration_done = True
        legacy_portfolio = DATA_DIR / "portfolio.json"
        legacy_memory = DATA_DIR / "memory.json"
        legacy_settings = DATA_DIR / "settings.json"
        
        # Check if legacy files exist (not in subdirectory)
        has_legacy_portfolio = legacy_portfolio.exists()
        has_legacy_memory = legacy_memory.exists()
        
        if not has_legacy_portfolio and not has_legacy_memory:
            return None
        
        # Check if there's a legacy settings file with old format
        legacy_owner_name = None
        legacy_base_currency = "EUR"
        
        if legacy_settings.exists():
            try:
                with open(legacy_settings, "r", encoding="utf-8") as f:
                    old_settings = json.load(f)
                
                # Check if it's old format (no "owners" key)
                if "owners" not in old_settings:
                    legacy_base_currency = old_settings.get("base_currency", "EUR")
                    logger.info(f"Found legacy settings with base_currency: {legacy_base_currency}")
            except Exception as e:
                logger.warning(f"Could not read legacy settings: {e}")
        
        # Try to get owner from legacy portfolio
        if has_legacy_portfolio:
            try:
                with open(legacy_portfolio, "r", encoding="utf-8") as f:
                    portfolio_data = json.load(f)
                legacy_owner_name = portfolio_data.get("owner")
                if not legacy_owner_name:
                    # Check legacy format with "portfolio" key
                    if "portfolio" in portfolio_data:
                        legacy_owner_name = portfolio_data["portfolio"].get("owner")
            except Exception as e:
                logger.warning(f"Could not read legacy portfolio: {e}")
        
        if not legacy_owner_name:
            # Will be set during first interaction
            return None
        
        # Create owner directory and migrate files
        owner_slug = slugify(legacy_owner_name)
        owner_dir = DATA_DIR / owner_slug
        owner_dir.mkdir(parents=True, exist_ok=True)
        
        # Move portfolio
        if has_legacy_portfolio:
            dest_portfolio = owner_dir / "portfolio.json"
            if not dest_portfolio.exists():
                shutil.move(str(legacy_portfolio), str(dest_portfolio))
                logger.info(f"Migrated portfolio to {dest_portfolio}")
        
        # Move memory
        if has_legacy_memory:
            dest_memory = owner_dir / "memory.json"
            if not dest_memory.exists():
                shutil.move(str(legacy_memory), str(dest_memory))
                logger.info(f"Migrated memory to {dest_memory}")
        
        return owner_slug
    
    def load(self) -> GlobalSettings:
        """
        Load settings from file.
        
        Returns:
            GlobalSettings object with current preferences.
        """
        if self._settings is not None:
            return self._settings
        
        # Check for migration first
        migrated_owner = self._migrate_legacy_data()
        
        if not self.settings_path.exists():
            logger.info(f"Settings file not found at {self.settings_path}, creating new")
            self._settings = GlobalSettings()
            
            # If we migrated data, we need to wait for owner name
            if migrated_owner:
                # Create owner entry for migrated data
                self._settings.current_owner = migrated_owner
                # Owner settings will be created when user confirms
            
            return self._settings
        
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if it's old format (no "owners" key)
            if "owners" not in data and "base_currency" in data:
                # Old format - need migration
                logger.info("Detected legacy settings format, will migrate on owner creation")
                self._settings = GlobalSettings(
                    date_format=data.get("date_format", "YYYY-MM-DD"),
                )
                # Store legacy currency to use when owner is created
                self._settings._legacy_currency = data.get("base_currency", "EUR")
                return self._settings
            
            self._settings = GlobalSettings.from_dict(data)
            
            if migrated_owner and migrated_owner not in self._settings.owners:
                # Need to add migrated owner
                self._settings.current_owner = migrated_owner
            
            logger.info(f"Loaded settings: current_owner={self._settings.current_owner}")
            return self._settings
        except Exception as e:
            logger.error(f"Error loading settings: {e}, using defaults")
            self._settings = GlobalSettings()
            return self._settings
    
    def save(self) -> None:
        """
        Save settings to file.
        
        Updates the updated_at timestamp automatically.
        """
        if self._settings is None:
            self._settings = GlobalSettings()
        
        self._ensure_directory()
        
        now = datetime.utcnow().isoformat() + "Z"
        if self._settings.created_at is None:
            self._settings.created_at = now
        self._settings.updated_at = now
        
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self._settings.to_dict(), f, indent=2)
        
        logger.info(f"Saved settings to {self.settings_path}")
    
    def get_settings(self) -> GlobalSettings:
        """Get current global settings."""
        return self.load()
    
    def get_current_owner(self) -> Optional[OwnerSettings]:
        """Get the current owner's settings."""
        settings = self.load()
        return settings.get_current_owner_settings()
    
    def get_owner_directory(self, owner_slug: Optional[str] = None) -> Path:
        """Get the data directory for an owner."""
        settings = self.load()
        slug = owner_slug or settings.current_owner
        if not slug:
            raise ValueError("No owner specified and no current owner set")
        return DATA_DIR / slug
    
    def create_owner(
        self,
        name: str,
        base_currency: str = "USD",
        set_as_current: bool = True,
    ) -> OwnerSettings:
        """
        Create a new owner with their own portfolio.
        
        Args:
            name: Display name for the owner
            base_currency: Base currency code
            set_as_current: Whether to switch to this owner
        
        Returns:
            Created OwnerSettings
        """
        settings = self.load()
        slug = slugify(name)
        
        if slug in settings.owners:
            raise ValueError(f"Owner '{name}' already exists")
        
        # Validate currency
        base_currency = base_currency.upper()
        if len(base_currency) != 3:
            raise ValueError(f"Invalid currency code: {base_currency}")
        
        now = datetime.utcnow().isoformat() + "Z"
        owner = OwnerSettings(
            name=name,
            base_currency=base_currency,
            created_at=now,
            updated_at=now,
        )
        
        settings.owners[slug] = owner
        
        if set_as_current:
            settings.current_owner = slug
        
        # Create owner directory
        owner_dir = DATA_DIR / slug
        owner_dir.mkdir(parents=True, exist_ok=True)
        
        self.save()
        logger.info(f"Created owner '{name}' with slug '{slug}'")
        return owner
    
    def switch_owner(self, name_or_slug: str) -> OwnerSettings:
        """
        Switch to a different owner.
        
        Args:
            name_or_slug: Owner name or slug
        
        Returns:
            OwnerSettings for the switched owner
        """
        settings = self.load()
        slug = slugify(name_or_slug)
        
        if slug not in settings.owners:
            # Try to find by name
            for s, owner in settings.owners.items():
                if slugify(owner.name) == slug or owner.name.lower() == name_or_slug.lower():
                    slug = s
                    break
            else:
                available = [o.name for o in settings.owners.values()]
                raise ValueError(f"Owner '{name_or_slug}' not found. Available: {available}")
        
        settings.current_owner = slug
        self.save()
        
        logger.info(f"Switched to owner '{slug}'")
        return settings.owners[slug]
    
    def list_owners(self) -> list[dict]:
        """
        List all registered owners.
        
        Returns:
            List of owner info dicts
        """
        settings = self.load()
        owners = []
        
        for slug, owner in settings.owners.items():
            owners.append({
                "slug": slug,
                "name": owner.name,
                "base_currency": owner.base_currency,
                "is_current": slug == settings.current_owner,
                "created_at": owner.created_at,
            })
        
        return owners
    
    def delete_owner(self, name_or_slug: str, confirm: bool = False) -> bool:
        """
        Delete an owner and all their data.
        
        Args:
            name_or_slug: Owner name or slug
            confirm: Must be True to actually delete
        
        Returns:
            True if deleted
        """
        if not confirm:
            raise ValueError("Must set confirm=True to delete owner data")
        
        settings = self.load()
        slug = slugify(name_or_slug)
        
        if slug not in settings.owners:
            # Try to find by name
            for s, owner in settings.owners.items():
                if slugify(owner.name) == slug or owner.name.lower() == name_or_slug.lower():
                    slug = s
                    break
            else:
                raise ValueError(f"Owner '{name_or_slug}' not found")
        
        # Don't allow deleting the only owner
        if len(settings.owners) <= 1:
            raise ValueError("Cannot delete the only owner")
        
        # Remove owner directory
        owner_dir = DATA_DIR / slug
        if owner_dir.exists():
            shutil.rmtree(owner_dir)
            logger.info(f"Deleted owner directory: {owner_dir}")
        
        # Remove from settings
        del settings.owners[slug]
        
        # Switch to another owner if this was current
        if settings.current_owner == slug:
            settings.current_owner = list(settings.owners.keys())[0]
        
        self.save()
        logger.info(f"Deleted owner '{slug}'")
        return True
    
    def update_owner_settings(
        self,
        base_currency: Optional[str] = None,
        owner_slug: Optional[str] = None,
    ) -> OwnerSettings:
        """
        Update settings for an owner.
        
        Args:
            base_currency: New base currency code
            owner_slug: Owner to update (defaults to current)
        
        Returns:
            Updated OwnerSettings
        """
        settings = self.load()
        slug = owner_slug or settings.current_owner
        
        if not slug or slug not in settings.owners:
            raise ValueError("No owner specified or owner not found")
        
        owner = settings.owners[slug]
        
        if base_currency is not None:
            base_currency = base_currency.upper()
            if len(base_currency) != 3:
                raise ValueError(f"Invalid currency code: {base_currency}")
            owner.base_currency = base_currency
        
        owner.updated_at = datetime.utcnow().isoformat() + "Z"
        self.save()
        
        logger.info(f"Updated owner '{slug}' settings")
        return owner
    
    def is_configured(self) -> bool:
        """
        Check if settings have been configured (has at least one owner).
        
        Returns:
            True if at least one owner exists
        """
        settings = self.load()
        return len(settings.owners) > 0
    
    def get_currency_symbol(self, currency: Optional[str] = None) -> str:
        """
        Get the symbol for a currency.
        
        Args:
            currency: Currency code. If None, uses current owner's base_currency.
        
        Returns:
            Currency symbol (e.g., "$", "€", "£")
        """
        if currency:
            return CURRENCY_SYMBOLS.get(currency.upper(), currency)
        
        owner = self.get_current_owner()
        if owner:
            return owner.get_currency_symbol()
        
        return "$"  # Default


# Singleton instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get the singleton settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def reset_settings_manager() -> None:
    """Reset the singleton instance (for testing)."""
    global _settings_manager
    _settings_manager = None
