# Full Portfolio Analysis Workflow

## Trigger: /analysis

When this workflow is triggered, perform a comprehensive analysis of the portfolio including valuation, market context, news, and actionable insights.

## Steps

### Step 1: Get Portfolio Valuation
Use the `portfolio_valuation` tool to fetch current portfolio state.

### Step 2: Get Market Context
Use the `market_overview` tool to understand current market conditions.

### Step 3: Get Sector Performance
Use the `sector_performance` tool to see how relevant sectors are performing.

### Step 4: Get Portfolio News
Use the `news_for_portfolio` tool to fetch relevant news for holdings.

### Step 5: Get Analyst Ratings
For each major position (>10% weight), use `analyst_ratings` tool.

### Step 6: Check Earnings Calendar
Use the `earnings_calendar` tool to check upcoming earnings for holdings.

### Step 7: Recall Relevant Insights
Use the `recall_insights` tool with category "analysis" to get previous insights.

### Step 8: Present Analysis

```
📊 COMPREHENSIVE PORTFOLIO ANALYSIS
══════════════════════════════════════════════════════════════

Generated: [timestamp]

────────────────────────────────────────────────────────────
📈 PORTFOLIO OVERVIEW
────────────────────────────────────────────────────────────

[Insert portfolio valuation summary]

Total Value: [currency_symbol]XX,XXX.XX
Total P&L: [currency_symbol]X,XXX.XX (+X.X%)
Cash Available: [currency_symbol]X,XXX.XX

────────────────────────────────────────────────────────────
🌐 MARKET CONDITIONS
────────────────────────────────────────────────────────────

Market Sentiment: [BULLISH/NEUTRAL/BEARISH]
VIX Level: XX.X ([interpretation])

Index Performance (1D):
• S&P 500: +X.XX%
• NASDAQ: +X.XX%
• Euro Stoxx 50: +X.XX%

────────────────────────────────────────────────────────────
📊 SECTOR ANALYSIS
────────────────────────────────────────────────────────────

Your Sectors vs Market:
┌──────────────────────┬─────────────┬─────────────┬───────────┐
│ Sector               │ Your Weight │ 1W Perf     │ Status    │
├──────────────────────┼─────────────┼─────────────┼───────────┤
│ [Sector Name]        │ XX.X%       │ +X.XX%      │ [STATUS]  │
└──────────────────────┴─────────────┴─────────────┴───────────┘

────────────────────────────────────────────────────────────
🏢 POSITION ANALYSIS
────────────────────────────────────────────────────────────

[For each major position:]

**[SYMBOL] - [Company Name]**
• Your Position: XX shares @ [currency_symbol]XX.XX avg ([currency_symbol]XX,XXX value)
• Current P&L: [currency_symbol]X,XXX (+XX.X%)
• Weight: XX.X% of portfolio
• Analyst Consensus: [BUY/HOLD/SELL]
• Price Target: [currency_symbol]XXX (XX% upside/downside)
• Next Earnings: [Date]

────────────────────────────────────────────────────────────
📰 RELEVANT NEWS
────────────────────────────────────────────────────────────

[List key news items affecting portfolio]

• [Symbol]: [Headline] - [Source]
• [Symbol]: [Headline] - [Source]

────────────────────────────────────────────────────────────
⚠️ RISK ASSESSMENT
────────────────────────────────────────────────────────────

Concentration Risk: [LOW/MODERATE/HIGH]
• Largest position: [Symbol] at XX.X%
• Top 3 positions: XX.X% of portfolio

Sector Risk: [LOW/MODERATE/HIGH]
• [Assessment based on sector concentration]

Market Risk: [LOW/MODERATE/HIGH]
• VIX indicates [interpretation]
• Portfolio beta (estimated): X.XX

────────────────────────────────────────────────────────────
💡 ACTIONABLE INSIGHTS
────────────────────────────────────────────────────────────

Based on the analysis:

1. **[Insight Category]**: [Specific recommendation]
2. **[Insight Category]**: [Specific recommendation]
3. **[Insight Category]**: [Specific recommendation]

────────────────────────────────────────────────────────────
📋 PREVIOUS INSIGHTS REFERENCED
────────────────────────────────────────────────────────────

[Any relevant past insights that inform this analysis]

══════════════════════════════════════════════════════════════
```

### Step 9: Store Key Insights
Use the `remember_insight` tool to store any important new insights discovered.

## Guidelines

- All values MUST be in [base_currency]
- Provide context for all metrics (what does VIX at 20 mean?)
- Be specific with recommendations - avoid vague suggestions
- Reference historical context from memory when available
- Flag urgent items (earnings this week, significant news)
- Compare current state to previous analyses if available
- Focus on actionable insights, not just data dumps

## Analysis Framework

When generating insights, consider:

1. **Valuation**: Are positions overvalued/undervalued vs targets?
2. **Momentum**: Are positions trending up/down?
3. **Risk**: Any concentration, sector, or market risks?
4. **Events**: Upcoming earnings, ex-dividend dates?
5. **News**: Any material news affecting holdings?
6. **Rebalancing**: Should positions be trimmed/added?

## Example Insight Categories

- **Rebalancing Alert**: Position exceeds target allocation
- **Earnings Watch**: Upcoming earnings to monitor
- **News Impact**: Material news affecting position
- **Valuation Signal**: Price vs analyst target divergence
- **Risk Warning**: Elevated concentration or market risk
- **Opportunity**: Sector rotation or buying opportunity
