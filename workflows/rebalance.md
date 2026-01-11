# Portfolio Rebalancing Workflow

## Trigger: /rebalance

When this workflow is triggered, analyze the portfolio for rebalancing opportunities and provide actionable recommendations.

## Steps

### Step 1: Get Portfolio State
Use the `portfolio_valuation` tool to get current allocation.

### Step 2: Check Portfolio History
Use the `portfolio_history` tool to see allocation drift over time.

### Step 3: Recall Target Allocation
Use `recall_insights` with category "strategy" to find target allocation.

### Step 4: Get Market Context
Use the `market_overview` tool to understand current conditions.

### Step 5: Check Analyst Views
For positions that may need adjustment, use `analyst_ratings`.

### Step 6: Present Rebalancing Analysis

```
⚖️ PORTFOLIO REBALANCING ANALYSIS
══════════════════════════════════════════════════════════════

Generated: [timestamp]

────────────────────────────────────────────────────────────
📊 CURRENT ALLOCATION
────────────────────────────────────────────────────────────

┌─────────┬───────────┬────────────┬────────────┬───────────┐
│ Symbol  │ Value     │ Current %  │ Target %   │ Drift     │
├─────────┼───────────┼────────────┼────────────┼───────────┤
│ AMZN    │ [currency_symbol]32,450   │ 45.8%      │ 35.0%      │ +10.8%  ⚠️│
│ IWDA    │ [currency_symbol]18,720   │ 26.4%      │ 35.0%      │ -8.6%   ⚠️│
│ CSPX    │ [currency_symbol]19,650   │ 27.8%      │ 30.0%      │ -2.2%     │
├─────────┼───────────┼────────────┼────────────┼───────────┤
│ TOTAL   │ [currency_symbol]70,820   │ 100%       │ 100%       │           │
│ CASH    │ [currency_symbol]5,000    │            │            │           │
└─────────┴───────────┴────────────┴────────────┴───────────┘

⚠️ = Drift exceeds 5% threshold

────────────────────────────────────────────────────────────
📈 ALLOCATION DRIFT OVER TIME
────────────────────────────────────────────────────────────

[Visual representation of allocation drift]

AMZN:  [██████████████████████████░░░░░░░░░░] 45.8% (target: 35%)
IWDA:  [██████████████░░░░░░░░░░░░░░░░░░░░░░] 26.4% (target: 35%)
CSPX:  [████████████████░░░░░░░░░░░░░░░░░░░░] 27.8% (target: 30%)

────────────────────────────────────────────────────────────
🎯 REBALANCING RECOMMENDATIONS
────────────────────────────────────────────────────────────

To restore target allocation:

1. **SELL AMZN** - Trim overweight position
   • Current: [currency_symbol]32,450 (45.8%)
   • Target: [currency_symbol]24,787 (35.0%)
   • Action: Sell [currency_symbol]7,663 worth (~36 shares)
   • Rationale: Position has grown beyond target due to outperformance

2. **BUY IWDA** - Build underweight position
   • Current: [currency_symbol]18,720 (26.4%)
   • Target: [currency_symbol]24,787 (35.0%)
   • Action: Buy [currency_symbol]6,067 worth (~58 shares)
   • Rationale: Diversified ETF underweight vs target

3. **BUY CSPX** - Minor top-up
   • Current: [currency_symbol]19,650 (27.8%)
   • Target: [currency_symbol]21,246 (30.0%)
   • Action: Buy [currency_symbol]1,596 worth (~4 shares)
   • Rationale: Minor drift, low priority

────────────────────────────────────────────────────────────
💰 EXECUTION PLAN
────────────────────────────────────────────────────────────

If you want to proceed with full rebalancing:

Step 1: Sell 36 shares of AMZN at ~[currency_symbol]210.XX
        → Generates ~[currency_symbol]7,663 + existing [currency_symbol]5,000 cash

Step 2: Buy 58 shares of IWDA at ~[currency_symbol]104.XX
        → Uses ~[currency_symbol]6,067

Step 3: Buy 4 shares of CSPX at ~[currency_symbol]401.XX
        → Uses ~[currency_symbol]1,596

Estimated Remaining Cash: [currency_symbol]5,000 (unchanged buffer)

────────────────────────────────────────────────────────────
📊 MARKET CONTEXT CHECK
────────────────────────────────────────────────────────────

Before rebalancing, consider:

• Market Sentiment: [BULLISH/NEUTRAL/BEARISH]
• VIX Level: XX.X - [interpretation]
• AMZN Analyst View: [consensus and price target]

Timing Consideration: [Assessment of whether now is good time]

────────────────────────────────────────────────────────────
⚠️ IMPORTANT CONSIDERATIONS
────────────────────────────────────────────────────────────

Tax Implications:
• Selling AMZN at profit will realize capital gains
• Estimated gain: [currency_symbol]7,663 (if all shares are profitable)
• Consider tax-loss harvesting opportunities

Transaction Costs:
• Broker commissions (if applicable)
• Bid-ask spreads

Alternative Approaches:
1. **Partial Rebalance**: Only address positions >5% drift
2. **Cash Flow Rebalance**: Use new contributions to underweight positions
3. **Threshold Rebalance**: Wait until drift exceeds 10%

────────────────────────────────────────────────────────────
✅ RECOMMENDED ACTIONS
────────────────────────────────────────────────────────────

Based on analysis:

☐ [HIGH PRIORITY] Trim AMZN - concentration risk elevated
☐ [MEDIUM PRIORITY] Add to IWDA - restore diversification
☐ [LOW PRIORITY] Minor CSPX top-up when convenient

Would you like me to:
1. Record a decision to rebalance?
2. Execute specific buy/sell orders?
3. Set a reminder to review in X weeks?

══════════════════════════════════════════════════════════════
```

### Step 7: Record Decision (if requested)
If user decides to rebalance, use `record_decision` to log the decision with rationale.

## Rebalancing Rules

### When to Rebalance
- **Time-based**: Quarterly review at minimum
- **Threshold-based**: When any position drifts >5% from target
- **Cash flow**: When adding new money to portfolio
- **Major event**: After significant market moves (>10%)

### Rebalancing Methods

#### 1. Full Rebalancing
Restore all positions to exact target weights.
- Pro: Clean allocation
- Con: More transactions, potential tax events

#### 2. Partial Rebalancing
Only address positions with significant drift (>5%).
- Pro: Fewer transactions
- Con: May leave minor imbalances

#### 3. Cash Flow Rebalancing
Direct new contributions to underweight positions.
- Pro: No selling required, tax efficient
- Con: Slower correction, requires ongoing contributions

#### 4. Threshold Bands
Only rebalance when drift exceeds set threshold.
- Pro: Reduces overtrading
- Con: May allow larger drift

## Target Allocation Framework

### Core-Satellite Approach
```
Core Holdings (70-80%):
├── Broad Market ETFs (IWDA, CSPX)
└── Target: Stable, diversified foundation

Satellite Holdings (20-30%):
├── Individual Stocks (AMZN, etc.)
└── Target: Alpha generation potential
```

### Risk-Based Allocation
```
Conservative: 60% Bonds, 40% Equities
Moderate: 40% Bonds, 60% Equities
Aggressive: 20% Bonds, 80% Equities
Very Aggressive: 0% Bonds, 100% Equities
```

### Geographic Diversification
```
US Equities: 50-60%
European Equities: 20-30%
Emerging Markets: 10-15%
Other: 5-10%
```

## Guidelines

- All values in [base_currency]
- Always show drift clearly (current vs target)
- Consider tax implications of selling winners
- Provide multiple approaches (not just one option)
- Factor in transaction costs for small rebalances
- Consider market timing (avoid rebalancing into falling knives)
- Log all rebalancing decisions in memory

## Tax Efficiency Tips

For European investors:
- Consider accumulating ETFs to defer tax events
- Time sales strategically around tax year
- Use capital losses to offset gains
- Be aware of country-specific holding periods for favorable rates
