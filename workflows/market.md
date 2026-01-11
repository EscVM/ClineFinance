# Market Deep Analysis Workflow

## Trigger: /market

When this workflow is triggered, provide a **comprehensive deep-dive into market conditions** with pattern analysis, trend detection, and actionable insights. This is NOT a simple snapshot—dig deep.

**Key Differentiation from /digest**: This workflow analyzes the MARKET itself (macro conditions, patterns, regime). `/digest` focuses on YOUR PORTFOLIO's weekly performance.

## Steps

### Step 1: Get Market Overview
Use the `market_overview` tool to fetch index performance and VIX.

### Step 2: Get Historical Context for VIX
Use `get_price_history` on `^VIX` with period="3mo" to analyze VIX trends.
Calculate:
- Current VIX vs 30-day average
- Current VIX vs 90-day average  
- Percentile ranking (where does current VIX sit in 3-month range?)

### Step 3: Analyze Index Trends vs Moving Averages
For each major index (^GSPC, ^IXIC, ^DJI, ^STOXX50E):
Use `get_price_history` with period="6mo" and interval="1d"
Determine:
- Price vs 50-day moving average (above/below, % distance)
- Price vs 200-day moving average (above/below, % distance)
- Trend direction (uptrend/downtrend/sideways)
- Golden cross / death cross signals

### Step 4: Get Sector Performance with Momentum Analysis
Use `sector_performance` tool.
Then use `get_price_history` on top 3 and bottom 3 sector ETFs with period="1mo"
Analyze:
- Week-over-week momentum shifts
- Sector leadership changes vs last month
- Identify sector rotation phase (early/mid/late cycle/recession)

### Step 5: Cross-Asset Correlation Check
Get price data for:
- `^TNX` (10-Year Treasury Yield) - period="1mo"
- `GLD` (Gold ETF) - period="1mo"
- `DX-Y.NYB` or `UUP` (US Dollar) - period="1mo"

Analyze relationships:
- Yields rising + stocks rising = risk-on
- Yields falling + stocks falling = flight to safety
- Gold rising + VIX rising = fear trade
- Dollar strengthening impact on international holdings

### Step 6: Get Market Movers with Context
Use `market_movers` tool.
For top 3 gainers and losers, use `financial_news` with those symbols to understand WHY they moved.

### Step 7: Get Broad Market News
Use `financial_news` with query="market economy fed" for macro context.

### Step 8: Economic Context (if FRED API configured)
Use `economic_indicators` to get interest rates, inflation, employment context.
Use `yield_curve_status` to check recession indicators.

### Step 9: Pattern Recognition & Regime Identification
Based on all collected data, identify:
- Current market regime (bull/bear/transition)
- Similarity to historical periods
- Key risks and opportunities

### Step 10: Present Deep Market Analysis

```
🔬 DEEP MARKET ANALYSIS
══════════════════════════════════════════════════════════════

Generated: [timestamp]
Analysis Depth: COMPREHENSIVE

────────────────────────────────────────────────────────────
🎯 EXECUTIVE SUMMARY
────────────────────────────────────────────────────────────

Market Regime: [🟢 BULL MARKET / 🟡 TRANSITIONAL / 🔴 BEAR MARKET]
Trend Strength: [Strong / Moderate / Weak]
Risk Level: [Low / Elevated / High]

Key Finding: [One-sentence summary of most important insight]

────────────────────────────────────────────────────────────
📊 VOLATILITY DEEP-DIVE
────────────────────────────────────────────────────────────

VIX Current: XX.X
VIX 30-Day Avg: XX.X  [Current vs avg: +X.X% / -X.X%]
VIX 90-Day Avg: XX.X  [Current vs avg: +X.X% / -X.X%]
VIX Percentile (90-day): XXth percentile

VIX Trend: [Rising / Falling / Stable] over past 2 weeks

Interpretation:
[🟢/🟡/🔴] [Detailed interpretation based on percentile and trend]

Historical Context:
• VIX at this level has historically preceded [observation]
• Similar VIX patterns occurred during [period], when markets [outcome]

────────────────────────────────────────────────────────────
📈 TREND ANALYSIS (vs Moving Averages)
────────────────────────────────────────────────────────────

┌─────────────────┬───────────┬────────────┬────────────┬──────────────┐
│ Index           │ Price     │ vs 50-DMA  │ vs 200-DMA │ Signal       │
├─────────────────┼───────────┼────────────┼────────────┼──────────────┤
│ S&P 500         │ X,XXX.XX  │ +X.X%      │ +X.X%      │ 🟢 BULLISH   │
│ NASDAQ          │ XX,XXX.XX │ +X.X%      │ +X.X%      │ 🟢 BULLISH   │
│ DOW JONES       │ XX,XXX.XX │ -X.X%      │ +X.X%      │ 🟡 CAUTION   │
│ Euro Stoxx 50   │ X,XXX.XX  │ +X.X%      │ +X.X%      │ 🟢 BULLISH   │
└─────────────────┴───────────┴────────────┴────────────┴──────────────┘

Trend Signals:
• Golden Cross: [None / Index approaching / Index confirmed]
• Death Cross: [None / Index approaching / Index confirmed]
• Overall Trend: [Strong uptrend / Weakening uptrend / Sideways / Weakening downtrend / Strong downtrend]

────────────────────────────────────────────────────────────
🔄 SECTOR ROTATION ANALYSIS
────────────────────────────────────────────────────────────

Current Leaders (1 Week):
┌─────────────────────────┬───────────┬───────────┬────────────────┐
│ Sector                  │ 1W Chg    │ 1M Chg    │ Momentum       │
├─────────────────────────┼───────────┼───────────┼────────────────┤
│ [Top Sector]            │ +X.X%     │ +X.X%     │ 🔼 Accelerating│
│ [2nd Sector]            │ +X.X%     │ +X.X%     │ ➡️  Steady     │
│ [3rd Sector]            │ +X.X%     │ -X.X%     │ 🔼 Reversing   │
└─────────────────────────┴───────────┴───────────┴────────────────┘

Current Laggards (1 Week):
┌─────────────────────────┬───────────┬───────────┬────────────────┐
│ Sector                  │ 1W Chg    │ 1M Chg    │ Momentum       │
├─────────────────────────┼───────────┼───────────┼────────────────┤
│ [Bottom Sector]         │ -X.X%     │ -X.X%     │ 🔽 Weakening   │
│ [2nd Bottom]            │ -X.X%     │ +X.X%     │ 🔽 Reversing   │
│ [3rd Bottom]            │ -X.X%     │ -X.X%     │ ➡️  Steady     │
└─────────────────────────┴───────────┴───────────┴────────────────┘

Rotation Phase: [EARLY CYCLE / MID CYCLE / LATE CYCLE / RECESSION]

Evidence:
• [Observation supporting phase identification]
• [Observation supporting phase identification]

Sector Rotation Implications:
• Favored sectors for this phase: [List]
• Sectors to underweight: [List]
• Watch for: [What would signal phase transition]

────────────────────────────────────────────────────────────
🔗 CROSS-ASSET SIGNALS
────────────────────────────────────────────────────────────

┌─────────────────────────┬───────────┬────────────────────────────┐
│ Asset                   │ Trend     │ Interpretation             │
├─────────────────────────┼───────────┼────────────────────────────┤
│ 10Y Treasury Yield      │ [↑↓→]     │ [What this means]          │
│ Gold (GLD)              │ [↑↓→]     │ [What this means]          │
│ US Dollar (DXY)         │ [↑↓→]     │ [What this means]          │
└─────────────────────────┴───────────┴────────────────────────────┘

Correlation Analysis:
• Stocks vs Bonds: [Positive / Negative / Decoupled]
• Risk Appetite: [RISK-ON / RISK-OFF / MIXED]
• Flight to Safety: [Active / Inactive]

Key Insight: [What cross-asset relationships are telling us]

────────────────────────────────────────────────────────────
🔥 MARKET MOVERS EXPLAINED
────────────────────────────────────────────────────────────

📈 TOP GAINERS:
│ [SYMBOL] +X.X%
│ └─ WHY: [News/catalyst explanation]
│
│ [SYMBOL] +X.X%
│ └─ WHY: [News/catalyst explanation]

📉 TOP LOSERS:
│ [SYMBOL] -X.X%
│ └─ WHY: [News/catalyst explanation]
│
│ [SYMBOL] -X.X%
│ └─ WHY: [News/catalyst explanation]

Pattern Observation: [Any theme in movers? Sector concentration?]

────────────────────────────────────────────────────────────
🏛️ ECONOMIC BACKDROP
────────────────────────────────────────────────────────────

Key Indicators:
• Fed Funds Rate: X.XX% [Stable / Hiking / Cutting]
• 10Y-2Y Spread: X.XX% [Normal / Flat / INVERTED ⚠️]
• CPI Inflation: X.X% YoY [Above / At / Below target]
• Unemployment: X.X% [Low / Normal / Elevated]

Economic Assessment: [Expansion / Slowdown / Recession Risk]

Fed Watch:
• Next meeting: [Date]
• Market expectation: [Hold / Hike / Cut] at X% probability
• Key factors: [What Fed is watching]

────────────────────────────────────────────────────────────
📰 MACRO NEWS CONTEXT
────────────────────────────────────────────────────────────

• [Headline] - [Market implication]
• [Headline] - [Market implication]
• [Headline] - [Market implication]

────────────────────────────────────────────────────────────
🔮 PATTERN RECOGNITION
────────────────────────────────────────────────────────────

Current Market Pattern: [Name/description of pattern]

Historical Comparison:
This environment most resembles [time period], characterized by:
• [Similarity 1]
• [Similarity 2]
• [Similarity 3]

What happened next historically: [Outcome with timeframe]

Confidence in pattern match: [High / Medium / Low]

────────────────────────────────────────────────────────────
⚠️ KEY RISKS TO MONITOR
────────────────────────────────────────────────────────────

1. [Risk 1]: [Description and trigger to watch]
2. [Risk 2]: [Description and trigger to watch]
3. [Risk 3]: [Description and trigger to watch]

────────────────────────────────────────────────────────────
💡 ACTIONABLE INSIGHTS
────────────────────────────────────────────────────────────

FOR YOUR PORTFOLIO:

Based on this analysis:

1. **Sector Positioning**: [Specific recommendation based on rotation]
2. **Risk Management**: [Action based on VIX and trend analysis]
3. **Opportunities**: [What to watch for entry points]
4. **Cautions**: [What to avoid or reduce]

MARKET TIMING SIGNAL: [🟢 FAVORABLE / 🟡 NEUTRAL / 🔴 UNFAVORABLE]

══════════════════════════════════════════════════════════════
```

### Step 11: Store Key Market Insights
Use `remember_insight` with category="market" to store:
- Current market regime assessment
- Any unusual patterns detected
- Key risks identified

## Analysis Guidelines

### VIX Interpretation Framework
- **<12**: Extreme complacency, possible blow-off top forming
- **12-15**: Low volatility, stable conditions, good for trend-following
- **15-20**: Normal volatility range, healthy market
- **20-25**: Elevated caution, consider hedging, reduce position sizes
- **25-30**: High volatility, potential capitulation, look for reversal signs
- **>30**: Extreme fear, historically good contrarian buy zone

### Moving Average Signals
- Price > 50 DMA > 200 DMA: Strong uptrend
- Price > 200 DMA but < 50 DMA: Weakening uptrend, caution
- Price < 50 DMA but > 200 DMA: Pullback in uptrend, possible entry
- Price < 50 DMA < 200 DMA: Strong downtrend
- 50 DMA crosses above 200 DMA: Golden Cross (bullish)
- 50 DMA crosses below 200 DMA: Death Cross (bearish)

### Sector Rotation by Economic Cycle
| Phase | Leading Sectors | Lagging Sectors |
|-------|-----------------|-----------------|
| Early Cycle | Financials, Consumer Discretionary, Industrials | Utilities, Healthcare |
| Mid Cycle | Technology, Communication Services, Industrials | Energy, Materials |
| Late Cycle | Energy, Materials, Healthcare | Technology, Consumer Discretionary |
| Recession | Utilities, Healthcare, Consumer Staples | Financials, Industrials |

### Cross-Asset Relationship Guide
| Scenario | Stocks | Bonds | Gold | Dollar | Interpretation |
|----------|--------|-------|------|--------|----------------|
| Risk-On | ↑ | ↓ | ↓ | ↓ | Growth optimism |
| Risk-Off | ↓ | ↑ | ↑ | ↑ | Flight to safety |
| Inflation Fear | ↓ | ↓ | ↑ | ↓ | Stagflation risk |
| Growth + Inflation | ↑ | ↓ | ↑ | Mixed | Goldilocks ending |
| Deflation Fear | ↓ | ↑ | ↑ | ↑ | Recession coming |

### Pattern Recognition Checklist
Look for these patterns:
1. **Breadth Divergence**: Index making new highs but fewer stocks participating
2. **Volume Confirmation**: Moves on high volume more significant
3. **VIX-Stock Divergence**: VIX rising while stocks rise = warning
4. **Sector Divergence**: Defensive outperforming cyclicals = late cycle
5. **Yield Curve Inversion**: 10Y-2Y negative = recession signal (12-18 month lead)

## When to Use /market vs /digest

| Use Case | Command |
|----------|---------|
| Sunday weekly review | /digest |
| Before making a trade | /market |
| During high volatility | /market |
| After major news event | /market |
| Monthly check-in | /digest |
| Planning asset allocation | /market |

## Best Practices

- Run /market before significant portfolio decisions
- Use during periods of uncertainty or volatility
- Compare current regime to stored insights from previous analyses
- Don't trade against the trend without strong conviction
- Remember: markets can stay irrational longer than you can stay solvent
