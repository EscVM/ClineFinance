# /economy Workflow

Display economic indicators dashboard with macroeconomic data from FRED.

## Prerequisites

This workflow requires a FRED API key. If not configured, inform the user:
- Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html
- Run `./install.sh` again to add the key

## Step 1: Fetch Economic Overview

```
economic_indicators()
```

Get comprehensive economic data including:
- Interest rates (Fed Funds, Treasury yields)
- Inflation (CPI, Core CPI, PCE)
- Employment (unemployment rate, jobless claims)
- Yield curve status
- GDP growth

## Step 2: Display Dashboard

If FRED data is available:

```
📊 ECONOMIC INDICATORS DASHBOARD
════════════════════════════════════════════════════════════

📈 INTEREST RATES
┌──────────────────────┬─────────┬──────────┐
│ Indicator            │ Rate    │ Change   │
├──────────────────────┼─────────┼──────────┤
│ Fed Funds Rate       │ X.XX%   │ +/-X.XX  │
│ 2-Year Treasury      │ X.XX%   │ +/-X.XX  │
│ 10-Year Treasury     │ X.XX%   │ +/-X.XX  │
│ 30-Year Treasury     │ X.XX%   │ +/-X.XX  │
└──────────────────────┴─────────┴──────────┘

────────────────────────────────────────────────────────────

📉 INFLATION (Year-over-Year)
┌──────────────────────┬─────────┬──────────────────────────┐
│ Metric               │ YoY %   │ Assessment               │
├──────────────────────┼─────────┼──────────────────────────┤
│ CPI                  │ X.X%    │ vs 2% Fed target         │
│ Core CPI             │ X.X%    │ (ex food & energy)       │
│ PCE                  │ X.X%    │ Fed's preferred measure  │
└──────────────────────┴─────────┴──────────────────────────┘

Level: [LOW/MODERATE/ELEVATED/HIGH] - [Assessment]

────────────────────────────────────────────────────────────

👷 EMPLOYMENT
┌──────────────────────┬─────────┬──────────────────────────┐
│ Indicator            │ Value   │ Assessment               │
├──────────────────────┼─────────┼──────────────────────────┤
│ Unemployment Rate    │ X.X%    │ [STRONG/HEALTHY/SOFT]    │
│ Initial Claims       │ XXX,XXX │ Weekly jobless claims    │
└──────────────────────┴─────────┴──────────────────────────┘

────────────────────────────────────────────────────────────

📐 YIELD CURVE
10Y-2Y Spread: [+/-X.XX%]
Status: [NORMAL/FLAT/INVERTED/DEEPLY INVERTED]

[🟢/🟡/🔴] [Warning message based on status]

Historical Note: Inverted yield curves have preceded every 
US recession since the 1950s, typically by 12-18 months.

────────────────────────────────────────────────────────────

📊 GDP GROWTH
Latest: X.X% (annualized)
Previous Quarter: X.X%
Assessment: [STRONG/MODERATE/SLOW/CONTRACTING]

────────────────────────────────────────────────────────────

🎯 OVERALL OUTLOOK: [FAVORABLE/MIXED/CAUTIOUS]
[Outlook summary based on risk factors]
```

## Step 3: Handle Missing API Key

If FRED API key is not configured:

```
⚠️ FRED API KEY NOT CONFIGURED

Economic indicators require a FRED API key.

To enable economic data:
1. Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html
2. Run `./install.sh` to add your key
3. Restart Cline

Available without FRED:
- Market indices and VIX (/market)
- Sector performance (/market)
- Portfolio analysis (/analysis)
```

## Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 | Favorable / Low risk |
| 🟡 | Caution / Monitor |
| 🔴 | Warning / High risk |

## Yield Curve Interpretation

| Spread | Status | Risk Level |
|--------|--------|------------|
| > 0.5% | NORMAL | 🟢 Low |
| 0 to 0.5% | FLAT | 🟡 Moderate |
| -0.5% to 0 | INVERTED | 🟡 Elevated |
| < -0.5% | DEEPLY INVERTED | 🔴 High |

## Inflation Level Interpretation

| CPI YoY | Level | Assessment |
|---------|-------|------------|
| < 2% | LOW | Below Fed target |
| 2-3% | MODERATE | Near target |
| 3-5% | ELEVATED | Above target |
| > 5% | HIGH | Significant concern |

## Investment Context

After displaying the dashboard, provide context for investment decisions:

1. **High Rates + Low Inflation**: Generally positive for bonds, may pressure growth stocks
2. **Inverted Yield Curve**: Historical recession indicator - consider defensive positioning
3. **Rising Inflation**: Favors real assets, TIPS, value stocks over growth
4. **Weak Employment**: May signal Fed rate cuts - positive for bonds and growth stocks

## Individual Tool Access

Users can also query specific indicators:

- `interest_rates()` - Just rates
- `inflation_data()` - Just inflation
- `employment_data()` - Just employment
- `yield_curve_status()` - Just yield curve
- `gdp_growth()` - Just GDP
