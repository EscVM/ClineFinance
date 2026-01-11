# Financial Q&A Workflow

## Trigger: /ask [question]

When this workflow is triggered, answer the user's financial question using available tools and financial knowledge.

## Steps

### Step 1: Parse the Question
Identify the type of question:
- **Quote/Price**: Questions about current prices → use `get_quote`
- **Historical**: Questions about price history → use `get_price_history`
- **Portfolio**: Questions about holdings → use `portfolio_valuation`
- **News**: Questions about what's happening → use `financial_news`
- **Analyst**: Questions about recommendations → use `analyst_ratings`
- **Market**: Questions about market conditions → use `market_overview`
- **Memory**: Questions about past decisions → use `recall_insights` or `decision_history`
- **General**: Financial concepts → use knowledge base

### Step 2: Gather Information
Use relevant tools based on question type. May need multiple tools.

### Step 3: Recall Context
Use `recall_insights` to check if this question relates to previous insights.

### Step 4: Formulate Answer

```
💬 FINANCIAL Q&A
══════════════════════════════════════════════════════════════

❓ Question: [User's question]

────────────────────────────────────────────────────────────
📝 ANSWER
────────────────────────────────────────────────────────────

[Clear, concise answer to the question]

[Include relevant data/numbers if applicable]

────────────────────────────────────────────────────────────
📊 SUPPORTING DATA
────────────────────────────────────────────────────────────

[Any relevant data retrieved from tools]

────────────────────────────────────────────────────────────
💡 ADDITIONAL CONTEXT
────────────────────────────────────────────────────────────

[Related information that might be helpful]

────────────────────────────────────────────────────────────
📚 SOURCES
────────────────────────────────────────────────────────────

• [Tool/source used]
• [Tool/source used]

══════════════════════════════════════════════════════════════
```

### Step 5: Store Insight (if applicable)
If the answer reveals something important, use `remember_insight` to store it.

## Question Categories & Tool Mapping

### Price & Quote Questions
**Examples:**
- "What's AAPL trading at?"
- "How much is my AMZN worth?"
- "What's the current price of MSFT?"

**Tools:** `get_quote`

### Historical Questions
**Examples:**
- "How has TSLA performed this year?"
- "Show me NVDA's 3-month chart"
- "What was AMZN's price last month?"

**Tools:** `get_price_history`

### Portfolio Questions
**Examples:**
- "What's my total portfolio value?"
- "How much am I up/down?"
- "What's my biggest position?"

**Tools:** `portfolio_valuation`, `portfolio_table`

### News Questions
**Examples:**
- "Any news on AMZN?"
- "What's happening in tech?"
- "Why is NVDA up today?"

**Tools:** `financial_news`, `news_for_portfolio`

### Analyst Questions
**Examples:**
- "What do analysts think of AAPL?"
- "Is MSFT a buy or sell?"
- "What's the price target for GOOGL?"

**Tools:** `analyst_ratings`

### Market Questions
**Examples:**
- "How's the market doing?"
- "Is it a good time to buy?"
- "What's the VIX at?"

**Tools:** `market_overview`, `sector_performance`

### Memory Questions
**Examples:**
- "Why did I buy AMZN?"
- "What insights did we have about tech?"
- "What decisions are pending review?"

**Tools:** `recall_insights`, `decision_history`, `pending_reviews`

### Earnings Questions
**Examples:**
- "When does AAPL report?"
- "Any earnings coming up?"
- "What's the earnings schedule?"

**Tools:** `earnings_calendar`

## Guidelines

- Always provide [base_currency] values when discussing money
- Be specific and data-driven in answers
- Don't speculate without data - use tools to verify
- Reference historical context from memory when relevant
- For complex questions, break down the answer into parts
- If uncertain, explain limitations and suggest follow-up

## Example Interactions

### Example 1: Price Question
**Q:** "What's AAPL trading at?"

**A:**
```
💬 FINANCIAL Q&A
══════════════════════════════════════════════════════════════

❓ Question: What's AAPL trading at?

────────────────────────────────────────────────────────────
📝 ANSWER
────────────────────────────────────────────────────────────

Apple (AAPL) is currently trading at [currency_symbol]185.42.

Today's Change: +[currency_symbol]2.15 (+1.17%)
52-Week Range: [currency_symbol]142.00 - [currency_symbol]199.62

────────────────────────────────────────────────────────────
📊 SUPPORTING DATA
────────────────────────────────────────────────────────────

• Open: [currency_symbol]183.50
• High: [currency_symbol]186.20
• Low: [currency_symbol]183.10
• Volume: 52.3M
• Avg Volume: 58.1M

────────────────────────────────────────────────────────────
📚 SOURCES
────────────────────────────────────────────────────────────

• get_quote tool (real-time data)

══════════════════════════════════════════════════════════════
```

### Example 2: Memory Question
**Q:** "Why did I buy AMZN?"

**A:**
```
💬 FINANCIAL Q&A
══════════════════════════════════════════════════════════════

❓ Question: Why did I buy AMZN?

────────────────────────────────────────────────────────────
📝 ANSWER
────────────────────────────────────────────────────────────

Based on recorded decisions, you bought AMZN on 2024-01-15:

Decision: BUY 50 shares of AMZN
Rationale: "AWS growth acceleration, AI tailwinds, reasonable 
          valuation after 2023 recovery"
Price at time: [currency_symbol]145.50

────────────────────────────────────────────────────────────
📊 CURRENT STATUS
────────────────────────────────────────────────────────────

• Current Price: [currency_symbol]210.75
• Your Cost Basis: [currency_symbol]145.50
• P&L: +[currency_symbol]3,262.50 (+44.8%)

────────────────────────────────────────────────────────────
📚 SOURCES
────────────────────────────────────────────────────────────

• decision_history tool (recorded decisions)
• get_quote tool (current price)

══════════════════════════════════════════════════════════════
```

## Financial Knowledge Base

For general financial questions, provide educational answers on:

### Investment Concepts
- Dollar-cost averaging
- Diversification
- Asset allocation
- Rebalancing
- Tax-loss harvesting

### Valuation Metrics
- P/E Ratio
- P/S Ratio
- EV/EBITDA
- Free Cash Flow Yield
- Dividend Yield

### Technical Concepts
- Support/Resistance
- Moving Averages
- RSI (overbought/oversold)
- Volume analysis

### Market Concepts
- Bull/Bear markets
- Sector rotation
- Risk-on/Risk-off
- VIX interpretation
- Yield curve

### European Investor Specifics
- [base_currency]/USD impact
- US withholding tax on dividends
- Accumulating vs Distributing ETFs
- UCITS regulations
