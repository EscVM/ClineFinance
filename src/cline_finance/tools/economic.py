"""
Economic Data Tool - Fetches macroeconomic indicators from FRED.
"""
import logging
from datetime import datetime
from typing import Optional

from cline_finance.constants import FRED_API_KEY

logger = logging.getLogger(__name__)

# FRED Series IDs
FRED_SERIES = {
    # Interest Rates
    "fed_funds": "FEDFUNDS",          # Federal Funds Rate
    "treasury_2y": "DGS2",            # 2-Year Treasury
    "treasury_10y": "DGS10",          # 10-Year Treasury
    "treasury_30y": "DGS30",          # 30-Year Treasury
    
    # Inflation
    "cpi": "CPIAUCSL",                # Consumer Price Index
    "core_cpi": "CPILFESL",           # Core CPI (ex food & energy)
    "pce": "PCEPI",                   # PCE Price Index
    
    # Employment
    "unemployment": "UNRATE",          # Unemployment Rate
    "jobless_claims": "ICSA",         # Initial Jobless Claims
    
    # GDP
    "gdp": "GDP",                      # Gross Domestic Product
    "gdp_growth": "A191RL1Q225SBEA",  # Real GDP Growth Rate
}

# Human-readable names
SERIES_NAMES = {
    "FEDFUNDS": "Federal Funds Rate",
    "DGS2": "2-Year Treasury Yield",
    "DGS10": "10-Year Treasury Yield",
    "DGS30": "30-Year Treasury Yield",
    "CPIAUCSL": "Consumer Price Index",
    "CPILFESL": "Core CPI (ex Food & Energy)",
    "PCEPI": "PCE Price Index",
    "UNRATE": "Unemployment Rate",
    "ICSA": "Initial Jobless Claims",
    "GDP": "Gross Domestic Product",
    "A191RL1Q225SBEA": "Real GDP Growth Rate",
}


def _get_fred_client():
    """Get FRED API client if key is available."""
    if not FRED_API_KEY:
        return None
    
    try:
        from fredapi import Fred
        return Fred(api_key=FRED_API_KEY)
    except ImportError:
        logger.warning("fredapi not installed. Run: pip install fredapi")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize FRED client: {e}")
        return None


def _fetch_series(series_id: str, observations: int = 1) -> Optional[dict]:
    """Fetch a FRED series with the latest observations."""
    fred = _get_fred_client()
    if not fred:
        return None
    
    try:
        data = fred.get_series(series_id)
        if data is None or data.empty:
            return None
        
        # Get latest values
        latest = data.dropna().tail(observations)
        
        return {
            "series_id": series_id,
            "name": SERIES_NAMES.get(series_id, series_id),
            "value": float(latest.iloc[-1]),
            "date": latest.index[-1].strftime("%Y-%m-%d"),
            "previous": float(latest.iloc[-2]) if len(latest) >= 2 else None,
            "change": float(latest.iloc[-1] - latest.iloc[-2]) if len(latest) >= 2 else None,
        }
    except Exception as e:
        logger.error(f"Error fetching FRED series {series_id}: {e}")
        return None


def get_interest_rates() -> dict:
    """
    Get current interest rates from FRED.
    
    Includes Fed Funds Rate and Treasury yields (2Y, 10Y, 30Y).
    
    Returns:
        Dictionary with interest rate data or error if FRED unavailable.
    """
    if not FRED_API_KEY:
        return {
            "error": "FRED_API_KEY not configured",
            "note": "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
        }
    
    rates = {}
    series_to_fetch = ["fed_funds", "treasury_2y", "treasury_10y", "treasury_30y"]
    
    for key in series_to_fetch:
        series_id = FRED_SERIES[key]
        data = _fetch_series(series_id, observations=5)
        if data:
            rates[key] = data
    
    if not rates:
        return {"error": "Failed to fetch interest rate data"}
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rates": rates,
        "summary": _generate_rates_summary(rates),
    }


def _generate_rates_summary(rates: dict) -> str:
    """Generate a text summary of interest rates."""
    parts = []
    
    if "fed_funds" in rates:
        parts.append(f"Fed Funds Rate: {rates['fed_funds']['value']:.2f}%")
    
    if "treasury_10y" in rates:
        parts.append(f"10Y Treasury: {rates['treasury_10y']['value']:.2f}%")
    
    if "treasury_2y" in rates and "treasury_10y" in rates:
        spread = rates["treasury_10y"]["value"] - rates["treasury_2y"]["value"]
        spread_status = "INVERTED ⚠️" if spread < 0 else "normal"
        parts.append(f"2Y/10Y Spread: {spread:+.2f}% ({spread_status})")
    
    return " | ".join(parts)


def get_inflation_data() -> dict:
    """
    Get inflation indicators from FRED.
    
    Includes CPI, Core CPI, and PCE Price Index.
    
    Returns:
        Dictionary with inflation data.
    """
    if not FRED_API_KEY:
        return {
            "error": "FRED_API_KEY not configured",
            "note": "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
        }
    
    fred = _get_fred_client()
    if not fred:
        return {"error": "Failed to initialize FRED client"}
    
    inflation = {}
    
    try:
        # CPI - year-over-year change
        for key in ["cpi", "core_cpi", "pce"]:
            series_id = FRED_SERIES[key]
            data = fred.get_series(series_id)
            
            if data is not None and not data.empty:
                latest = data.dropna().tail(13)  # 13 months for YoY
                
                if len(latest) >= 13:
                    current = float(latest.iloc[-1])
                    year_ago = float(latest.iloc[0])
                    yoy_change = ((current - year_ago) / year_ago) * 100
                    
                    inflation[key] = {
                        "series_id": series_id,
                        "name": SERIES_NAMES.get(series_id, series_id),
                        "latest_value": current,
                        "date": latest.index[-1].strftime("%Y-%m-%d"),
                        "yoy_percent": round(yoy_change, 2),
                    }
    except Exception as e:
        logger.error(f"Error fetching inflation data: {e}")
        return {"error": str(e)}
    
    if not inflation:
        return {"error": "Failed to fetch inflation data"}
    
    # Determine inflation level
    cpi_yoy = inflation.get("cpi", {}).get("yoy_percent", 0)
    if cpi_yoy < 2:
        level = "LOW"
        assessment = "Below Fed target of 2%"
    elif cpi_yoy < 3:
        level = "MODERATE"
        assessment = "Near Fed target"
    elif cpi_yoy < 5:
        level = "ELEVATED"
        assessment = "Above target, may prompt Fed action"
    else:
        level = "HIGH"
        assessment = "Significantly above target"
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "inflation": inflation,
        "level": level,
        "assessment": assessment,
    }


def get_employment_data() -> dict:
    """
    Get employment indicators from FRED.
    
    Includes unemployment rate and initial jobless claims.
    
    Returns:
        Dictionary with employment data.
    """
    if not FRED_API_KEY:
        return {
            "error": "FRED_API_KEY not configured",
            "note": "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
        }
    
    employment = {}
    
    # Unemployment rate
    data = _fetch_series(FRED_SERIES["unemployment"], observations=5)
    if data:
        employment["unemployment_rate"] = data
    
    # Jobless claims
    data = _fetch_series(FRED_SERIES["jobless_claims"], observations=5)
    if data:
        employment["initial_claims"] = data
    
    if not employment:
        return {"error": "Failed to fetch employment data"}
    
    # Assessment
    unemp = employment.get("unemployment_rate", {}).get("value", 0)
    if unemp < 4:
        level = "STRONG"
        assessment = "Full employment conditions"
    elif unemp < 5:
        level = "HEALTHY"
        assessment = "Normal labor market"
    elif unemp < 7:
        level = "SOFT"
        assessment = "Some labor market weakness"
    else:
        level = "WEAK"
        assessment = "Elevated unemployment"
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "employment": employment,
        "level": level,
        "assessment": assessment,
    }


def get_yield_curve() -> dict:
    """
    Get yield curve data and inversion status.
    
    The 10Y-2Y spread is a key recession indicator.
    Inversions have preceded every recession since the 1950s.
    
    Returns:
        Dictionary with yield curve data and assessment.
    """
    if not FRED_API_KEY:
        return {
            "error": "FRED_API_KEY not configured",
            "note": "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
        }
    
    # Fetch treasury yields
    treasury_2y = _fetch_series(FRED_SERIES["treasury_2y"], observations=30)
    treasury_10y = _fetch_series(FRED_SERIES["treasury_10y"], observations=30)
    
    if not treasury_2y or not treasury_10y:
        return {"error": "Failed to fetch treasury yields"}
    
    # Calculate spread
    spread = treasury_10y["value"] - treasury_2y["value"]
    
    # Determine status
    if spread < -0.5:
        status = "DEEPLY INVERTED"
        warning = "🔴 Strong recession warning signal"
        risk_level = "HIGH"
    elif spread < 0:
        status = "INVERTED"
        warning = "🟡 Yield curve inverted - historically precedes recessions"
        risk_level = "ELEVATED"
    elif spread < 0.5:
        status = "FLAT"
        warning = "🟡 Yield curve flattening - monitor closely"
        risk_level = "MODERATE"
    else:
        status = "NORMAL"
        warning = "🟢 Normal yield curve - no recession signal"
        risk_level = "LOW"
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "treasury_2y": treasury_2y["value"],
        "treasury_10y": treasury_10y["value"],
        "spread_10y_2y": round(spread, 3),
        "status": status,
        "warning": warning,
        "risk_level": risk_level,
        "historical_note": "Inverted yield curves have preceded every US recession since the 1950s, typically by 12-18 months.",
    }


def get_gdp_data() -> dict:
    """
    Get GDP and growth data from FRED.
    
    Returns:
        Dictionary with GDP data.
    """
    if not FRED_API_KEY:
        return {
            "error": "FRED_API_KEY not configured",
            "note": "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
        }
    
    fred = _get_fred_client()
    if not fred:
        return {"error": "Failed to initialize FRED client"}
    
    try:
        # GDP Growth Rate
        growth_data = fred.get_series(FRED_SERIES["gdp_growth"])
        
        if growth_data is None or growth_data.empty:
            return {"error": "Failed to fetch GDP data"}
        
        latest = growth_data.dropna().tail(8)  # Last 2 years quarterly
        
        current_growth = float(latest.iloc[-1])
        prev_growth = float(latest.iloc[-2]) if len(latest) >= 2 else None
        
        # Assessment
        if current_growth < 0:
            level = "CONTRACTING"
            assessment = "Economy contracting - potential recession"
        elif current_growth < 1:
            level = "SLOW"
            assessment = "Below-trend growth"
        elif current_growth < 3:
            level = "MODERATE"
            assessment = "Healthy growth pace"
        else:
            level = "STRONG"
            assessment = "Above-trend growth"
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "gdp_growth": {
                "current": current_growth,
                "previous": prev_growth,
                "date": latest.index[-1].strftime("%Y-%m-%d"),
                "unit": "% change (annualized)",
            },
            "recent_quarters": [round(float(v), 2) for v in latest.values],
            "level": level,
            "assessment": assessment,
        }
        
    except Exception as e:
        logger.error(f"Error fetching GDP data: {e}")
        return {"error": str(e)}


def get_economic_summary() -> dict:
    """
    Get comprehensive economic summary with all major indicators.
    
    Provides a snapshot of:
    - Interest rates (Fed Funds, Treasury yields)
    - Inflation (CPI, Core CPI)
    - Employment (unemployment rate)
    - Yield curve status
    
    Returns:
        Dictionary with complete economic overview.
    """
    if not FRED_API_KEY:
        return {
            "error": "FRED_API_KEY not configured",
            "note": "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
            "available": False,
        }
    
    # Gather all data
    rates = get_interest_rates()
    inflation = get_inflation_data()
    employment = get_employment_data()
    yield_curve = get_yield_curve()
    gdp = get_gdp_data()
    
    # Build summary
    highlights = []
    
    # Rates highlight
    if "rates" in rates and "fed_funds" in rates["rates"]:
        fed_rate = rates["rates"]["fed_funds"]["value"]
        highlights.append(f"Fed Funds Rate at {fed_rate:.2f}%")
    
    # Inflation highlight
    if "inflation" in inflation and "cpi" in inflation["inflation"]:
        cpi_yoy = inflation["inflation"]["cpi"]["yoy_percent"]
        highlights.append(f"CPI inflation at {cpi_yoy:.1f}% YoY")
    
    # Employment highlight
    if "employment" in employment and "unemployment_rate" in employment["employment"]:
        unemp = employment["employment"]["unemployment_rate"]["value"]
        highlights.append(f"Unemployment at {unemp:.1f}%")
    
    # Yield curve highlight
    if "spread_10y_2y" in yield_curve:
        spread = yield_curve["spread_10y_2y"]
        status = yield_curve.get("status", "")
        highlights.append(f"Yield curve {status.lower()} (spread: {spread:+.2f}%)")
    
    # Overall assessment
    risk_factors = []
    if yield_curve.get("risk_level") in ["ELEVATED", "HIGH"]:
        risk_factors.append("inverted yield curve")
    if inflation.get("level") in ["ELEVATED", "HIGH"]:
        risk_factors.append("elevated inflation")
    if employment.get("level") in ["SOFT", "WEAK"]:
        risk_factors.append("weak employment")
    if gdp.get("level") in ["CONTRACTING", "SLOW"]:
        risk_factors.append("slowing growth")
    
    if len(risk_factors) >= 3:
        overall_outlook = "CAUTIOUS"
        outlook_note = f"Multiple concerns: {', '.join(risk_factors)}"
    elif len(risk_factors) >= 1:
        overall_outlook = "MIXED"
        outlook_note = f"Some concerns: {', '.join(risk_factors)}"
    else:
        overall_outlook = "FAVORABLE"
        outlook_note = "Economic conditions broadly supportive"
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "available": True,
        "interest_rates": rates.get("rates", {}),
        "inflation": inflation.get("inflation", {}),
        "employment": employment.get("employment", {}),
        "yield_curve": {
            "spread": yield_curve.get("spread_10y_2y"),
            "status": yield_curve.get("status"),
            "warning": yield_curve.get("warning"),
        },
        "gdp": gdp.get("gdp_growth", {}),
        "highlights": highlights,
        "outlook": overall_outlook,
        "outlook_note": outlook_note,
    }
