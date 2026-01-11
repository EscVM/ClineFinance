# Portfolio View Workflow

## Trigger: /portfolio

When this workflow is triggered, display the current portfolio state clearly and concisely.

## Steps

### Step 1: Check Settings
Use `get_settings` to verify user's base currency is configured.
- If not configured, ask user to set their base currency first

### Step 2: Get Portfolio Valuation
Use the `portfolio_valuation` tool to fetch real-time portfolio data.
- This returns values in both original currency AND base currency

### Step 3: Display ASCII Table
Use the `portfolio_table` tool to get a formatted table view.
- Multi-currency portfolios show both original and base currency values

### Step 4: Present Results

Display the following information (using user's base currency for totals):

```
📊 PORTFOLIO SUMMARY
═══════════════════════════════════════════════════

[Insert ASCII table from portfolio_table tool]

─────────────────────────────────────────────────
💰 Total Value: [base_currency_symbol]XX,XXX.XX
📈 Total P&L: [base_currency_symbol]X,XXX.XX (+X.X%)
💵 Cash: [base_currency_symbol]X,XXX.XX
─────────────────────────────────────────────────

📊 Allocation by Sector:
• [Sector]: XX.X%
• [Sector]: XX.X%

💱 Currency Exposure:
• USD: XX.X%
• EUR: XX.X%

⚠️ Concentration Risk: [LOW/MODERATE/HIGH]
   Max Position: [Symbol] at XX.X%

Last Updated: [timestamp]
```

## Guidelines

- Use the user's configured base currency for totals
- For multi-currency portfolios, show currency exposure breakdown
- Use clear formatting with box-drawing characters
- Highlight any positions with gains in context
- Flag any concentration risks (including currency risk)
- Keep it concise - this is a quick view

## Example Output (USD Base Currency)

```
📊 PORTFOLIO SUMMARY
═══════════════════════════════════════════════════

┌─────────┬─────────┬──────────────┬─────────────┬─────────┬─────────┐
│ Symbol  │ Shares  │ Value (Orig) │ Value (USD) │ P&L %   │ Weight  │
├─────────┼─────────┼──────────────┼─────────────┼─────────┼─────────┤
│ AAPL    │ 100.00  │ $17,550 USD  │ $17,550     │ +12.0%  │ 45.3%   │
│ ASML    │ 10.00   │ €8,500 EUR   │ $9,350      │ +8.2%   │ 24.1%   │
│ VOO     │ 25.00   │ $11,875 USD  │ $11,875     │ +5.5%   │ 30.6%   │
├─────────┼─────────┼──────────────┼─────────────┼─────────┼─────────┤
│ TOTAL   │         │ (mixed)      │ $38,775     │ +8.7%   │ 100%    │
└─────────┴─────────┴──────────────┴─────────────┴─────────┴─────────┘

─────────────────────────────────────────────────
💰 Total Value: $38,775.00
📈 Total P&L: $3,105.00 (+8.7%)
💵 Cash: $5,000.00
─────────────────────────────────────────────────

📊 Allocation by Sector:
• Technology: 69.4%
• Diversified: 30.6%

💱 Currency Exposure:
• USD: 75.9%
• EUR: 24.1%

⚠️ Concentration Risk: MODERATE
   Max Position: AAPL at 45.3%
```

## Example Output (Single Currency - EUR)

```
📊 PORTFOLIO SUMMARY
═══════════════════════════════════════════════════

┌─────────┬─────────┬──────────┬──────────┬─────────┬─────────┐
│ Symbol  │ Shares  │ Avg Cost │ Value    │ P&L     │ Weight  │
├─────────┼─────────┼──────────┼──────────┼─────────┼─────────┤
│ ASML    │ 15.00   │ €750.00  │ €12,750  │ +€1,500 │ 55.2%   │
│ IWDA    │ 120.00  │ €78.50   │ €10,320  │ +€900   │ 44.8%   │
├─────────┼─────────┼──────────┼──────────┼─────────┼─────────┤
│ TOTAL   │         │          │ €23,070  │ +€2,400 │ 100%    │
└─────────┴─────────┴──────────┴──────────┴─────────┴─────────┘

─────────────────────────────────────────────────
💰 Total Value: €23,070.00
📈 Total P&L: €2,400.00 (+11.6%)
💵 Cash: €2,000.00
─────────────────────────────────────────────────

📊 Allocation by Sector:
• Technology: 55.2%
• Diversified: 44.8%

⚠️ Concentration Risk: MODERATE
   Max Position: ASML at 55.2%
