# Charts Dashboard Workflow

## Trigger: /charts

When this workflow is triggered, display a comprehensive visual dashboard with ASCII charts and generate a combined PNG dashboard.

## Steps

### Step 1: Get Portfolio Valuation
Use the `portfolio_valuation` tool to get current positions, values, and allocations.

### Step 2: Get Portfolio History
Use the `portfolio_history` tool with days=30 to get historical value data.

### Step 3: Get Market Overview (Optional)
Use the `market_overview` tool to get benchmark data for comparison.

### Step 4: Generate PNG Dashboard
Use the `generate_report` tool to create a combined 4-panel dashboard PNG.

### Step 5: Present ASCII Charts Dashboard

```
📊 PORTFOLIO CHARTS DASHBOARD
══════════════════════════════════════════════════════════════

Generated: [timestamp]
Base Currency: [base_currency]

────────────────────────────────────────────────────────────
📈 PORTFOLIO VALUE TREND (30 Days)
────────────────────────────────────────────────────────────

[currency_symbol]XX,XXX ┤                                    ▄█▀
[currency_symbol]XX,XXX ┤                              ▄▄▀▀▀▀
[currency_symbol]XX,XXX ┤                    ▄▄▄▄▀▀▀▀▀▀
[currency_symbol]XX,XXX ┤          ▄▄▄▀▀▀▀▀▀▀
[currency_symbol]XX,XXX ┼▀▀▀▀▀▀▀▀▀▀
          └──────────────────────────────────────────
           [Start Date]                    [End Date]

Peak: [currency_symbol]XX,XXX ([date])    Low: [currency_symbol]XX,XXX ([date])
Period Change: [currency_symbol]X,XXX (+X.X%)

Sparkline: ▁▂▃▄▅▆▇█▇▆▅▆▇█

────────────────────────────────────────────────────────────
🥧 ALLOCATION BREAKDOWN
────────────────────────────────────────────────────────────

[SYMBOL1]  ████████████████████░░░░░░░░░░░░░░░░░░░░  XX.X%  [currency_symbol]XX,XXX
[SYMBOL2]  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  XX.X%  [currency_symbol]XX,XXX
[SYMBOL3]  ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  XX.X%  [currency_symbol]XX,XXX
[...]

Total Value: [currency_symbol]XX,XXX.XX

────────────────────────────────────────────────────────────
📊 POSITION PERFORMANCE
────────────────────────────────────────────────────────────

[Best Performers at top, sorted by gain %]

[SYMBOL]  ████████████████████████████░░░░  +XX.X%  📈 [sparkline]
[SYMBOL]  █████████████████░░░░░░░░░░░░░░░  +XX.X%  📈 [sparkline]
[SYMBOL]  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░   +X.X%  🟢 [sparkline]
[SYMBOL]  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   -X.X%  🔴 [sparkline]
          ├──────────────────────────────────┤
         -30%       0%        +30%       +60%

Portfolio Total: +X.X% ([currency_symbol]+X,XXX.XX)

────────────────────────────────────────────────────────────
🏢 SECTOR EXPOSURE
────────────────────────────────────────────────────────────

[Sector 1]        ████████████████████░░░░░░░░░░░░░░░░░░░░  XX.X%
[Sector 2]        ████████████████░░░░░░░░░░░░░░░░░░░░░░░░  XX.X%
[Sector 3]        ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  XX.X%
[Diversified]     ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  XX.X%

────────────────────────────────────────────────────────────
💱 CURRENCY EXPOSURE
────────────────────────────────────────────────────────────

[CURRENCY1]  ███████████████████████████████░░░░░░░░░  XX%  [symbol]XX,XXX
[CURRENCY2]  ███████████████░░░░░░░░░░░░░░░░░░░░░░░░░  XX%  [symbol]XX,XXX
[CURRENCY3]  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  XX%  [symbol]XX,XXX

FX Impact Note: [If significant USD exposure, note potential impact]

────────────────────────────────────────────────────────────
📈 BENCHMARK COMPARISON (Period)
────────────────────────────────────────────────────────────

Your Portfolio  ████████████████████████████░░░  +XX.X%  [🏆 if best]
S&P 500 (^GSPC) ██████████████████████░░░░░░░░░  +XX.X%
MSCI World      ████████████████████░░░░░░░░░░░  +XX.X%
Euro Stoxx 50   █████████████░░░░░░░░░░░░░░░░░░  +XX.X%

────────────────────────────────────────────────────────────
📁 GENERATED CHARTS
────────────────────────────────────────────────────────────

Dashboard saved to: data/charts/dashboard_YYYYMMDD.png

This PNG includes:
✅ Portfolio Value Over Time (line chart)
✅ Asset Allocation (pie chart)  
✅ Position Performance (bar chart)
✅ Sector Exposure (pie chart)

══════════════════════════════════════════════════════════════
```

## ASCII Chart Generation Guidelines

### Value Trend Chart
Create a simple ASCII representation:
- Use 5 rows for the y-axis (min to max values)
- Use sparkline characters (▁▂▃▄▅▆▇█) for the trend line
- Show peak/low annotations
- Calculate period change

### Allocation Bars
For each position:
```
[SYMBOL]  [bar based on weight]  XX.X%  [currency_symbol]XX,XXX
```
- Bar width: 40 characters total
- Filled portion: ██████
- Empty portion: ░░░░░░

### Performance Bars
For each position, sorted by gain%:
```
[SYMBOL]  [bar from center at 0%]  +XX.X%  [emoji] [sparkline]
```
- Center represents 0%
- Positive gains extend right
- Negative losses extend left (if any)
- Emoji: 📈 for >+10%, 🟢 for +0-10%, 🔴 for negative

### Sector/Currency Bars
Simple horizontal bars:
```
[Label]  [████████████░░░░░░░░]  XX.X%
```

## Data Collection Logic

### Portfolio Data Needed
From `portfolio_valuation`:
- positions[].symbol
- positions[].current_value_base
- positions[].weight
- positions[].gain_loss_pct
- positions[].sector
- sector_allocation
- currency_allocation
- total_value
- total_gain_loss_pct

### History Data Needed
From `portfolio_history`:
- history[].date
- history[].total_value
- Calculate: peak, low, period change

### Benchmark Data Needed
From `market_overview`:
- indices performance (S&P 500, etc.)
Or calculate from price_history of benchmark ETFs

## Sparkline Generation

Use the sparkline helper function:
```
▁▂▃▄▅▆▇█  (8 levels of height)
```

Sample values to 8-10 characters for compact display.

## Color Coding (Emoji-based)

Since ASCII doesn't support colors, use emojis:
- 📈 Strong positive (>+10%)
- 🟢 Positive (0% to +10%)
- 🟡 Flat (-2% to +2%)
- 🔴 Negative (-10% to 0%)
- 📉 Strong negative (<-10%)
- 🏆 Best performer / beating benchmark

## Bar Characters

```
█ - Full block (filled)
░ - Light shade (empty)
▓ - Medium shade (partial)
│ - Vertical line (axis)
─ - Horizontal line (axis)
├ ┤ - T-connections
┼ - Cross (origin)
```

## Error Handling

- If no history data: Show "Insufficient data for trend chart"
- If benchmark fetch fails: Skip benchmark section
- If single position: Still show all charts but note limited diversification

## Best Practices

- Always show base currency values
- Sort positions by weight for allocation, by gain% for performance
- Include both absolute values and percentages
- Add period context (e.g., "30 Days", "YTD")
- Note the PNG location for users who want high-quality charts
- Use consistent bar widths (40 chars) for visual alignment
