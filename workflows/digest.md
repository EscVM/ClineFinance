# Weekly Digest Workflow

## Trigger: /digest

When this workflow is triggered, generate a comprehensive weekly summary of portfolio performance and important events.

## Steps

### Step 1: Get Portfolio Valuation
Use the `portfolio_valuation` tool to get current state.

### Step 2: Get Portfolio History
Use the `portfolio_history` tool with days=7 to get weekly data.

### Step 3: Get Market Overview
Use the `market_overview` tool for market context.

### Step 4: Get Portfolio News
Use the `news_for_portfolio` tool for relevant news.

### Step 5: Get Pending Reviews
Use the `pending_reviews` tool to check for decisions needing review.

### Step 6: Get Upcoming Earnings
Use the `earnings_calendar` tool with portfolio symbols.

### Step 7: Present Weekly Digest

```
📬 WEEKLY PORTFOLIO DIGEST
══════════════════════════════════════════════════════════════

Week of [Start Date] - [End Date]

────────────────────────────────────────────────────────────
📊 WEEKLY PERFORMANCE
────────────────────────────────────────────────────────────

Total Value: [currency_symbol]XX,XXX.XX
Weekly Change: [currency_symbol]X,XXX.XX (+X.X%)

Trend: [sparkline] ▁▂▃▅▆▇█▆▅

Performance vs Benchmarks:
• Your Portfolio: +X.X%
• S&P 500:        +X.X%
• Euro Stoxx 50:  +X.X%

────────────────────────────────────────────────────────────
🏆 POSITION HIGHLIGHTS
────────────────────────────────────────────────────────────

📈 BEST PERFORMER:
   [SYMBOL] +X.X% (+[currency_symbol]XXX.XX)
   [Brief reason if news available]

📉 WORST PERFORMER:
   [SYMBOL] -X.X% (-[currency_symbol]XXX.XX)
   [Brief reason if news available]

Position Performance This Week:
┌──────────┬───────────┬────────────┬──────────────────┐
│ Symbol   │ Value     │ Change     │ Trend            │
├──────────┼───────────┼────────────┼──────────────────┤
│ AMZN     │ [currency_symbol]32,450   │ +[currency_symbol]1,285    │ ▁▂▃▅▆▇█  +4.1%  │
│ IWDA     │ [currency_symbol]18,720   │   -[currency_symbol]150    │ ▆▅▄▃▃▂▁  -0.8%  │
│ CSPX     │ [currency_symbol]19,650   │   +[currency_symbol]420    │ ▃▄▅▅▆▆▇  +2.2%  │
└──────────┴───────────┴────────────┴──────────────────┘

────────────────────────────────────────────────────────────
📰 KEY NEWS THIS WEEK
────────────────────────────────────────────────────────────

• [Symbol]: [Headline] - [Impact assessment]
• [Symbol]: [Headline] - [Impact assessment]
• Market: [Headline] - [Portfolio relevance]

────────────────────────────────────────────────────────────
📅 UPCOMING EVENTS
────────────────────────────────────────────────────────────

Earnings Next Week:
• [Symbol] reports [Date] [Before/After market]

Ex-Dividend Dates:
• [Symbol] - [Date] (Yield: X.X%)

────────────────────────────────────────────────────────────
⏰ PENDING REVIEWS
────────────────────────────────────────────────────────────

Decisions needing your attention:
• [Date]: [Action] [Symbol] - Review due [Date]
  Original rationale: "[Rationale]"
  Current P&L: +[currency_symbol]XXX (+X.X%)

────────────────────────────────────────────────────────────
💡 WEEKLY RECOMMENDATIONS
────────────────────────────────────────────────────────────

Based on this week's activity:

1. **[Priority]**: [Specific recommendation]
2. **[Priority]**: [Specific recommendation]

────────────────────────────────────────────────────────────
🎯 PORTFOLIO HEALTH CHECK
────────────────────────────────────────────────────────────

Concentration Risk:  [████████░░] HIGH
Sector Balance:      [██████░░░░] MODERATE  
Market Correlation:  [████░░░░░░] LOW
Overall Health:      🟡 FAIR

══════════════════════════════════════════════════════════════
```

### Step 8: Store Digest Insight
Use `remember_insight` to note any important observations from the digest.

## Guidelines

- Focus on actionable insights, not just data
- Highlight what changed, not just current state
- Compare performance to relevant benchmarks
- Flag items requiring attention
- Keep it scannable with clear sections
- Use visual indicators for quick reading

## Weekly Recommendations Logic

Generate recommendations based on:
1. **Concentration Alert**: If any position >40%
2. **Rebalancing**: If drift >5% from targets
3. **Earnings Watch**: Positions with upcoming earnings
4. **Review Reminders**: Pending decision reviews
5. **Performance Action**: Positions significantly up/down
6. **Market Context**: If VIX elevated, suggest caution

## Best Practices

- Run /digest every weekend or Monday morning
- Review pending decisions when flagged
- Consider rebalancing quarterly
- Store important insights for future reference
