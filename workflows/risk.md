# Risk Dashboard Workflow

## Trigger: /risk

When this workflow is triggered, display a comprehensive risk assessment of the portfolio.

## Steps

### Step 1: Get Portfolio Valuation
Use the `portfolio_valuation` tool to get current positions and values.

### Step 2: Get Market Overview
Use the `market_overview` tool to get VIX and market sentiment.

### Step 3: Get Sector Performance
Use the `sector_performance` tool to analyze sector trends.

### Step 4: Recall Risk Insights
Use `recall_insights` with category "risk" to get previous risk observations.

### Step 5: Present Risk Dashboard

```
🛡️ PORTFOLIO RISK DASHBOARD
══════════════════════════════════════════════════════════════

Generated: [timestamp]

────────────────────────────────────────────────────────────
📊 OVERALL RISK SCORE
────────────────────────────────────────────────────────────

                    🟡 MODERATE RISK
                    
   LOW ───────────────●─────────── HIGH
        Safe        Balanced      Risky

────────────────────────────────────────────────────────────
🎯 CONCENTRATION RISK
────────────────────────────────────────────────────────────

Status: [🔴 HIGH / 🟡 MODERATE / 🟢 LOW]

Position Concentration:
AMZN:  [████████████████░░░░] 45.8%  ⚠️ >40% EXTREME
IWDA:  [██████████░░░░░░░░░░] 26.4%
CSPX:  [████████████░░░░░░░░] 27.8%

Risk Assessment:
• Single stock (AMZN) represents 45.8% of portfolio
• Top 1 position holds nearly half of value
• Recommendation: Consider trimming to <35%

────────────────────────────────────────────────────────────
📈 SECTOR RISK
────────────────────────────────────────────────────────────

Status: [🔴 HIGH / 🟡 MODERATE / 🟢 LOW]

Sector Exposure:
Consumer Discretionary: [████████████████░░░░] 45.8%
Diversified:           [██████████████░░░░░░] 54.2%

Analysis:
• Heavy exposure to Consumer Discretionary (AMZN)
• Diversified ETFs provide broad market exposure
• Recommendation: [sector-specific advice]

────────────────────────────────────────────────────────────
💱 CURRENCY RISK
────────────────────────────────────────────────────────────

Status: [🔴 HIGH / 🟡 MODERATE / 🟢 LOW]

Currency Exposure:
USD:  [████████████████░░░░] ~75%   [currency_symbol]53,000 exposed
[base_currency]:  [████░░░░░░░░░░░░░░░░] ~25%   [currency_symbol]17,800 hedged

[base_currency]/USD Rate: 1.08
Impact Analysis:
• A 5% USD decline → ~[currency_symbol]2,650 portfolio loss
• A 5% USD rise → ~[currency_symbol]2,650 portfolio gain

Recommendation: [currency risk advice]

────────────────────────────────────────────────────────────
🌊 MARKET/VOLATILITY RISK
────────────────────────────────────────────────────────────

Status: [🔴 HIGH / 🟡 MODERATE / 🟢 LOW]

VIX Level: XX.X
Market Sentiment: [BULLISH / NEUTRAL / BEARISH]

VIX Gauge:
CALM    [░░░░░░░░░░░░░░░░░░░░] PANIC
         ●                      
        14.2

Interpretation:
• VIX < 15: Low volatility, markets calm
• VIX 15-20: Normal conditions
• VIX 20-25: Elevated caution
• VIX 25-30: High volatility
• VIX > 30: Market stress/panic

Current Risk: [assessment based on VIX]

────────────────────────────────────────────────────────────
📉 DRAWDOWN RISK
────────────────────────────────────────────────────────────

Current Position:
• Portfolio Value: [currency_symbol]70,820
• Cost Basis: [currency_symbol]66,500
• Current P&L: +[currency_symbol]4,320 (+6.5%)

Stress Test Scenarios:
┌─────────────────────────┬─────────────┬─────────────┐
│ Scenario                │ Impact      │ New Value   │
├─────────────────────────┼─────────────┼─────────────┤
│ -10% Market Correction  │ -[currency_symbol]7,082     │ [currency_symbol]63,738     │
│ -20% Bear Market        │ -[currency_symbol]14,164    │ [currency_symbol]56,656     │
│ -30% Crash              │ -[currency_symbol]21,246    │ [currency_symbol]49,574     │
│ -50% Severe Crash       │ -[currency_symbol]35,410    │ [currency_symbol]35,410     │
└─────────────────────────┴─────────────┴─────────────┘

Recovery Time Estimates (at 8% annual return):
• From -10%: ~1.3 years
• From -20%: ~2.9 years
• From -30%: ~4.7 years

────────────────────────────────────────────────────────────
🔄 CORRELATION RISK
────────────────────────────────────────────────────────────

Portfolio Beta: ~1.1 (estimated)

Interpretation:
• Beta > 1.0: More volatile than market
• Your portfolio moves ~10% more than S&P 500

Correlation Analysis:
• AMZN highly correlated with NASDAQ
• IWDA/CSPX provide market exposure
• Limited diversification benefit between positions

────────────────────────────────────────────────────────────
🚨 RISK ALERTS
────────────────────────────────────────────────────────────

Active Alerts:
⚠️ [HIGH] AMZN concentration at 45.8% (threshold: 40%)
⚠️ [MEDIUM] High USD exposure without hedging
ℹ️ [LOW] No bond allocation for stability

────────────────────────────────────────────────────────────
💡 RISK MITIGATION RECOMMENDATIONS
────────────────────────────────────────────────────────────

Priority Actions:

1. **REDUCE CONCENTRATION** [HIGH]
   Trim AMZN to <35% of portfolio
   → Sell ~[currency_symbol]7,600 worth to bring to target

2. **ADD DIVERSIFICATION** [MEDIUM]
   Consider adding non-US exposure
   → European or EM ETFs for geographic spread

3. **CONSIDER HEDGING** [LOW]
   For major USD exposure
   → Currency-hedged ETFs or [base_currency]-denominated alternatives

══════════════════════════════════════════════════════════════
```

### Step 6: Store Risk Insights
Use `remember_insight` with category "risk" to store any new risk observations.

## Risk Calculation Logic

### Concentration Risk Levels
```
< 15% top position → LOW (🟢)
15-25% top position → MODERATE (🟡)
25-40% top position → HIGH (🟠)
> 40% top position → EXTREME (🔴)
```

### Sector Risk Levels
```
No sector > 30% → LOW (🟢)
One sector 30-50% → MODERATE (🟡)
One sector > 50% → HIGH (🔴)
```

### Currency Risk Levels
```
< 50% foreign currency → LOW (🟢)
50-75% foreign currency → MODERATE (🟡)
> 75% foreign currency → HIGH (🔴)
```

### Market Risk (VIX-based)
```
VIX < 15 → LOW (🟢) - Complacent
VIX 15-20 → LOW-MODERATE (🟢) - Normal
VIX 20-25 → MODERATE (🟡) - Elevated
VIX 25-30 → HIGH (🟠) - Fearful
VIX > 30 → EXTREME (🔴) - Panic
```

### Overall Risk Score
Weighted average of:
- Concentration: 35%
- Sector: 20%
- Currency: 15%
- Market: 30%

## Guidelines

- All risk assessments should be data-driven
- Provide specific numbers, not just labels
- Always include actionable recommendations
- Use progress bars for visual clarity
- Compare to thresholds for context
- Consider user's likely risk tolerance (moderate for most)

## European Investor Considerations

- [base_currency]/USD exposure is common and significant
- US stocks dominate most portfolios
- Consider UCITS ETF alternatives
- Tax implications of rebalancing
