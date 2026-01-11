"""
Settings Tools - User preferences and owner management.
"""
import logging
from typing import Optional

from cline_finance.core.settings_manager import (
    get_settings_manager,
    CURRENCY_SYMBOLS,
)

logger = logging.getLogger(__name__)


def get_user_settings() -> dict:
    """
    Get current user settings and preferences.
    
    Returns the user's configured preferences including base currency and owner info.
    If no owners have been configured, returns defaults and indicates
    that the user should create an owner first.
    
    Returns:
        Dictionary with current settings and configuration status.
    
    Example:
        >>> get_user_settings()
        {
            "is_configured": True,
            "current_owner": "john",
            "owner_name": "John",
            "base_currency": "EUR",
            "base_currency_symbol": "€",
            ...
        }
    """
    sm = get_settings_manager()
    settings = sm.get_settings()
    is_configured = sm.is_configured()
    current_owner = sm.get_current_owner()
    
    result = {
        "is_configured": is_configured,
        "current_owner": settings.current_owner,
        "owner_name": current_owner.name if current_owner else None,
        "base_currency": current_owner.base_currency if current_owner else "USD",
        "base_currency_symbol": current_owner.get_currency_symbol() if current_owner else "$",
        "date_format": settings.date_format,
        "owners_count": len(settings.owners),
        "supported_currencies": list(CURRENCY_SYMBOLS.keys()),
    }
    
    if not is_configured:
        result["message"] = "No portfolio owner configured. Please create one using create_owner."
    elif current_owner:
        result["message"] = f"Active portfolio: {current_owner.name} ({current_owner.base_currency})"
    
    return result


def set_user_settings(
    base_currency: Optional[str] = None,
) -> dict:
    """
    Update settings for the current owner.
    
    Use this to change the base currency for portfolio valuation and display.
    
    Args:
        base_currency: 3-letter currency code (e.g., "USD", "EUR", "GBP")
    
    Returns:
        Dictionary with updated settings.
    
    Example:
        >>> set_user_settings(base_currency="EUR")
        {
            "status": "success",
            "base_currency": "EUR",
            "message": "Base currency set to EUR (€)"
        }
    """
    sm = get_settings_manager()
    
    if not sm.is_configured():
        return {
            "status": "error",
            "error": "No owner configured. Please create an owner first using create_owner.",
        }
    
    try:
        owner = sm.update_owner_settings(base_currency=base_currency)
        
        result = {
            "status": "success",
            "owner_name": owner.name,
            "base_currency": owner.base_currency,
            "base_currency_symbol": owner.get_currency_symbol(),
            "updated_at": owner.updated_at,
        }
        
        if base_currency:
            symbol = CURRENCY_SYMBOLS.get(base_currency.upper(), base_currency)
            result["message"] = f"Base currency set to {owner.base_currency} ({symbol})"
        else:
            result["message"] = "Settings updated successfully"
        
        return result
        
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
            "supported_currencies": list(CURRENCY_SYMBOLS.keys()),
        }


def create_owner(
    name: str,
    base_currency: str = "USD",
) -> dict:
    """
    Create a new portfolio owner.
    
    Each owner has their own portfolio and memory (insights, decisions, history).
    This is useful for managing multiple people's investments.
    
    Args:
        name: Display name for the owner (e.g., "John", "Jane")
        base_currency: Base currency for this owner's portfolio (e.g., "USD", "EUR")
    
    Returns:
        Dictionary with created owner details.
    
    Example:
        >>> create_owner("John", "EUR")
        {
            "status": "success",
            "owner_name": "John",
            "owner_slug": "john",
            "base_currency": "EUR",
            "message": "✅ Created portfolio for John with EUR (€) base currency"
        }
    """
    sm = get_settings_manager()
    
    try:
        owner = sm.create_owner(name=name, base_currency=base_currency)
        symbol = CURRENCY_SYMBOLS.get(owner.base_currency, owner.base_currency)
        
        return {
            "status": "success",
            "owner_name": owner.name,
            "owner_slug": sm.get_settings().current_owner,
            "base_currency": owner.base_currency,
            "base_currency_symbol": symbol,
            "created_at": owner.created_at,
            "message": f"✅ Created portfolio for {owner.name} with {owner.base_currency} ({symbol}) base currency",
        }
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
        }


def switch_owner(name_or_slug: str) -> dict:
    """
    Switch to a different portfolio owner.
    
    Changes the active owner context. All subsequent portfolio and memory
    operations will use this owner's data.
    
    Args:
        name_or_slug: Owner name or slug (e.g., "John" or "john")
    
    Returns:
        Dictionary with switched owner details.
    
    Example:
        >>> switch_owner("Jane")
        {
            "status": "success",
            "owner_name": "Jane",
            "base_currency": "USD",
            "message": "✅ Switched to Jane's portfolio (USD)"
        }
    """
    sm = get_settings_manager()
    
    try:
        owner = sm.switch_owner(name_or_slug)
        symbol = CURRENCY_SYMBOLS.get(owner.base_currency, owner.base_currency)
        
        # Reset cached managers to pick up new owner
        from cline_finance.core.portfolio_manager import reset_portfolio_managers
        from cline_finance.core.memory_manager import reset_memory_managers
        reset_portfolio_managers()
        reset_memory_managers()
        
        return {
            "status": "success",
            "owner_name": owner.name,
            "base_currency": owner.base_currency,
            "base_currency_symbol": symbol,
            "message": f"✅ Switched to {owner.name}'s portfolio ({owner.base_currency})",
        }
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
        }


def list_owners() -> dict:
    """
    List all registered portfolio owners.
    
    Returns:
        Dictionary with list of all owners and their details.
    
    Example:
        >>> list_owners()
        {
            "owners": [
                {"name": "John", "base_currency": "EUR", "is_current": True},
                {"name": "Jane", "base_currency": "USD", "is_current": False}
            ],
            "total": 2,
            "current_owner": "john"
        }
    """
    sm = get_settings_manager()
    owners = sm.list_owners()
    settings = sm.get_settings()
    
    # Enrich with currency symbols
    for owner in owners:
        owner["currency_symbol"] = CURRENCY_SYMBOLS.get(owner["base_currency"], owner["base_currency"])
    
    return {
        "owners": owners,
        "total": len(owners),
        "current_owner": settings.current_owner,
    }


def delete_owner(name_or_slug: str, confirm: bool = False) -> dict:
    """
    Delete an owner and all their data.
    
    ⚠️ WARNING: This permanently deletes the owner's portfolio and memory!
    
    Args:
        name_or_slug: Owner name or slug to delete
        confirm: Must be True to actually delete (safety check)
    
    Returns:
        Dictionary with deletion result.
    
    Example:
        >>> delete_owner("Jane", confirm=True)
        {
            "status": "success",
            "message": "✅ Deleted owner Jane and all their data"
        }
    """
    sm = get_settings_manager()
    
    if not confirm:
        return {
            "status": "error",
            "error": "Must set confirm=True to delete owner data. This action is irreversible!",
            "warning": "⚠️ This will permanently delete all portfolio and memory data for this owner.",
        }
    
    try:
        sm.delete_owner(name_or_slug, confirm=True)
        
        return {
            "status": "success",
            "message": f"✅ Deleted owner {name_or_slug} and all their data",
        }
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
        }


def get_currency_symbol(currency: str) -> dict:
    """
    Get the symbol for a currency code.
    
    Args:
        currency: 3-letter currency code (e.g., "USD", "EUR", "GBP")
    
    Returns:
        Dictionary with currency code and its symbol.
    
    Example:
        >>> get_currency_symbol("EUR")
        {"currency": "EUR", "symbol": "€"}
    """
    currency_upper = currency.upper()
    symbol = CURRENCY_SYMBOLS.get(currency_upper, currency_upper)
    
    return {
        "currency": currency_upper,
        "symbol": symbol,
        "is_known": currency_upper in CURRENCY_SYMBOLS,
    }
