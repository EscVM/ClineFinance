[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<h1 align="center"> ClineFinance 💰 </h1>

**Personal Financial Advisor MCP Server for Cline**

Transform Cline into your personal financial advisor with portfolio management, market analysis, and investment insights.

## 📝 Context

Nowadays, since investing is becoming more and more accessible for common users, financial advisors are popping up like mushrooms. However, their interests are not always aligned with yours, and unless you have Aladdin's Genie as your financial advisor, no one really has the key to make you rich. However, at the time of writing (2026), we already have very powerful models which, with the correct context, can be the best financial expert you could hope for—much cheaper and much more aligned and helpful for you. So, what are you waiting for? Clone this repository and start making your own personal agent powered by your favourite model!

## ✨ Features

- **Multi-Owner Support**: Manage portfolios for multiple people (yourself, spouse, family members)
- **Multi-Currency Support**: Track positions in any currency (USD, EUR, GBP, etc.) with automatic FX conversion
- **Portfolio Management**: Track positions with individual lot history, cost basis, P&L with weighted average calculations
- **Market Analysis**: Real-time quotes, market sentiment, sector performance, VIX tracking
- **Memory System**: Store insights, track decisions, review outcomes over time (per owner)
- **News Integration**: Financial news for your holdings (NewsAPI or yfinance fallback)
- **Analyst Data**: Consensus ratings, price targets, earnings calendar
- **Chart Generation**: Matplotlib visualizations and ASCII tables
- **Slash Commands**: Quick access to common workflows

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ClineFinance

# Run the installation script
chmod +x install.sh
./install.sh
```

The installer will:
1. ✅ Check Python 3.10+ installation
2. ✅ Create a virtual environment
3. ✅ Install all dependencies
4. ✅ **Auto-configure Cline MCP settings**
5. ✅ Create data directories
6. ✅ Prompt for optional NewsAPI key

**No manual configuration required!** Just run `./install.sh` and restart Cline.

## 📖 Getting Started

After installation, restart Cline and start chatting! Here's how to build your portfolio:

### 1️⃣ First Time Setup - Create Your Portfolio

The easiest way to get started is to ask Cline directly:

```
You: "Hi! Can you setup an account for Vittorio with EUR as base currency?"
```
```
Cline: ✅ Portfolio created for Vittorio with EUR (€) base currency!
       You're all set. What would you like to do?
```

Or you can be guided through the setup:

```
You: "Hi!"
```
```
Cline: Welcome! Let's set up your portfolio.
       What's your name?

You: "John"

Cline: Great! What base currency do you prefer? (e.g., USD, EUR, GBP)

You: "EUR"

Cline: ✅ Portfolio created for John with EUR (€) base currency!
       You're all set. What would you like to do?
```

### 2️⃣ Adding Your First Position

Tell Cline about your stock purchases in natural language:

```
You: "I bought 50 shares of AAPL at $175 on NASDAQ"
```
```
Cline: ✅ Added AAPL to John's portfolio
       • 50 shares @ $175.00 USD
       • Cost basis: $8,750.00 (€8,094 EUR)
       • Sector: Technology
```

You can add positions in **any currency**:

```
You: "Add 10 shares of ASML at €850, bought on Amsterdam exchange"
```
```
Cline: ✅ Added ASML to portfolio
       • 10 shares @ €850.00 EUR
       • Cost basis: €8,500.00
       • Sector: Technology
```

### 3️⃣ Viewing Your Portfolio

Use the `/portfolio` command to see everything:

```
You: "/portfolio"
```
```
Cline: 📊 John's Portfolio (EUR)
       ────────────────────────────────────────────────────────────
       
       ┌─────────┬─────────┬──────────────┬─────────────┬─────────┐
       │ Symbol  │ Shares  │ Value (Orig) │ Value (EUR) │ P&L %   │
       ├─────────┼─────────┼──────────────┼─────────────┼─────────┤
       │ AAPL    │ 50.00   │ $9,125 USD   │ €8,445      │ +4.3%   │
       │ ASML    │ 10.00   │ €8,900 EUR   │ €8,900      │ +4.7%   │
       ├─────────┼─────────┼──────────────┼─────────────┼─────────┤
       │ TOTAL   │         │ (mixed)      │ €17,345     │ +4.5%   │
       └─────────┴─────────┴──────────────┴─────────────┴─────────┘
       
       💰 Total Value: €17,345
       📈 Total P&L: €745 (+4.5%)
```

### 4️⃣ Buying More Shares (Lot Tracking)

When you buy more of an existing position, ClineFinance creates a new **lot** and tracks each purchase separately while computing a weighted average:

```
You: "I bought 20 more shares of AAPL at $180"
```
```
Cline: ✅ Added lot to AAPL
       • New lot: 20 shares @ $180.00 (2026-01-11)
       • Total shares: 70 (was 50)
       • Avg cost: $176.43 (weighted average)
       
       📋 Purchase History:
       Lot 1: 50 @ $175.00 on 2026-01-10
       Lot 2: 20 @ $180.00 on 2026-01-11
```

**How lot tracking works:**
- Each purchase is recorded as a separate lot with date, shares, and price
- Total shares = sum of all lot shares
- Average cost = weighted average computed from all lots
- First purchase date = earliest lot date (preserved)

### 5️⃣ Selling Positions

To sell all shares of a position:

```
You: "I sold all my ASML shares"
```
```
Cline: ✅ Removed ASML from portfolio
       • Sold 10 shares
       • Original cost: €850.00/share
```

### 6️⃣ Getting Market Analysis

Ask questions or use slash commands:

```
You: "/analysis"           # Full portfolio analysis
You: "/market"             # Market overview with indices
You: "/risk"               # Risk dashboard
You: "How is NVDA doing?"  # Any financial question
You: "What's the news on my portfolio?"
```

---

## 👥 Multi-Owner Support

ClineFinance supports multiple portfolio owners, perfect for managing:
- Your own portfolio and your spouse's
- Family member investments
- Different investment strategies (e.g., "Growth Portfolio", "Dividend Portfolio")

### Creating Additional Owners

```
You: "Create a portfolio for my wife Jane with USD as base currency"
```
```
Cline: ✅ Created portfolio for Jane with USD ($) base currency
       I've switched to Jane's portfolio.
```

### Switching Between Owners

```
You: "Switch to John's portfolio"
```
```
Cline: ✅ Switched to John's portfolio (EUR)
```

### Listing All Owners

```
You: "Who has portfolios?"
```
```
Cline: 📋 Registered Portfolios:
       • John (EUR) ← current
       • Jane (USD)
```

### Data Separation

Each owner has completely separate:
- Portfolio positions
- Memory (insights, decisions, history)
- Data files (stored in `data/{owner_slug}/`)

---

## 💡 Quick Tips

- **Natural language works**: Just describe what you did, Cline understands
- **Currency auto-detection**: If you don't specify, it detects from the stock exchange
- **Slash commands**: Use `/portfolio`, `/market`, `/analysis` for quick views
- **Ask anything**: "Should I rebalance?", "What's my tech exposure?", etc.
- **Switch owners anytime**: "Switch to Jane's portfolio", "Go back to my portfolio"

---

### Optional API Keys

The installer will prompt you for optional API keys:

#### NewsAPI (Enhanced News)
For broader financial news coverage, get a free API key at: https://newsapi.org/register

Without it, news falls back to yfinance (works fine for most use cases).

#### FRED (Economic Data)
For macroeconomic indicators (interest rates, inflation, GDP, unemployment), get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html

Without it, economic indicator tools will not be available.

## 📋 Slash Commands

| Command | Description |
|---------|-------------|
| `/portfolio` | View portfolio summary with P&L and allocation |
| `/analysis` | Full portfolio analysis with market context |
| `/market` | Market overview with indices and sentiment |
| `/economy` | Economic indicators dashboard (requires FRED API key) |
| `/ask [question]` | Ask any financial question |
| `/rebalance` | Get rebalancing recommendations |
| `/charts` | Visual dashboard with ASCII charts and PNG export |
| `/digest` | Weekly digest with sparklines, highlights, and pending reviews |
| `/risk` | Risk dashboard with concentration, sector, and stress analysis |

## 🛠️ Available Tools

### Owner Management Tools
| Tool | Description |
|------|-------------|
| `get_settings` | Get current owner and preferences |
| `set_settings` | Set base currency for current owner |
| `create_owner` | Create a new portfolio owner |
| `switch_owner` | Switch to another owner's portfolio |
| `list_owners` | List all registered owners |
| `delete_owner` | Delete an owner and all their data |

### FX Tools
| Tool | Description |
|------|-------------|
| `fx_rate` | Get exchange rate between two currencies |
| `convert_amount` | Convert amount between currencies |

### Quote & Price Tools
| Tool | Description |
|------|-------------|
| `get_quote` | Get real-time quote for a symbol |
| `get_price_history` | Get historical prices (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, ytd, max) |

### Portfolio Tools
| Tool | Description |
|------|-------------|
| `portfolio_valuation` | Get full portfolio valuation |
| `portfolio_table` | Get ASCII-formatted portfolio table |
| `buy_stock` | Record a stock purchase |
| `sell_stock` | Record a stock sale |
| `modify_position` | Modify existing position |
| `portfolio_history` | Get historical snapshots |
| `generate_report` | Generate report with optional chart |

### Market Tools
| Tool | Description |
|------|-------------|
| `market_overview` | Get indices, VIX, and sentiment |
| `market_movers` | Get top gainers and losers |
| `sector_performance` | Get sector ETF performance |

### News Tools
| Tool | Description |
|------|-------------|
| `financial_news` | Search financial news by query |
| `news_for_portfolio` | Get news for all holdings |

### Analyst Tools
| Tool | Description |
|------|-------------|
| `analyst_ratings` | Get analyst recommendations |
| `earnings_calendar` | Get upcoming earnings dates |

### Memory Tools (per owner)
| Tool | Description |
|------|-------------|
| `remember_insight` | Store an important insight |
| `recall_insights` | Recall insights by category/symbol |
| `record_decision` | Record a trading decision |
| `pending_reviews` | Get decisions pending review |
| `decision_outcome` | Record decision outcome |
| `decision_history` | Get decision history for symbol |

### Economic Tools (requires FRED API key)
| Tool | Description |
|------|-------------|
| `economic_indicators` | Get comprehensive economic overview |
| `interest_rates` | Get Fed Funds Rate and Treasury yields |
| `inflation_data` | Get CPI, Core CPI, PCE inflation metrics |
| `employment_data` | Get unemployment rate and jobless claims |
| `yield_curve_status` | Get yield curve with recession indicator |
| `gdp_growth` | Get GDP growth rate |

## 📁 Project Structure

```
ClineFinance/
├── src/cline_finance/
│   ├── __init__.py
│   ├── server.py           # FastMCP server with all tools
│   ├── constants.py        # Configuration constants
│   ├── core/
│   │   ├── portfolio_manager.py  # Portfolio CRUD operations
│   │   ├── memory_manager.py     # Insights & decisions
│   │   ├── settings_manager.py   # User & owner preferences
│   │   └── chart_generator.py    # Visualizations
│   └── tools/
│       ├── settings.py     # Settings & owner management tools
│       ├── fx.py           # Foreign exchange tools
│       ├── quotes.py       # Price & quote tools
│       ├── portfolio.py    # Portfolio tools
│       ├── market.py       # Market analysis tools
│       ├── news.py         # News tools
│       ├── analyst.py      # Analyst data tools
│       ├── memory.py       # Memory tools
│       └── economic.py     # Economic indicators (FRED)
├── workflows/
│   ├── portfolio.md        # /portfolio workflow
│   ├── analysis.md         # /analysis workflow
│   ├── market.md           # /market workflow
│   ├── economy.md          # /economy workflow
│   ├── ask.md              # /ask workflow
│   ├── rebalance.md        # /rebalance workflow
│   ├── charts.md           # /charts workflow
│   ├── digest.md           # /digest workflow
│   └── risk.md             # /risk workflow
├── data/
│   ├── settings.json       # Global settings + owner registry
│   ├── john/               # John's data directory
│   │   ├── portfolio.json  # John's portfolio
│   │   └── memory.json     # John's insights & decisions
│   ├── jane/               # Jane's data directory
│   │   ├── portfolio.json  # Jane's portfolio
│   │   └── memory.json     # Jane's insights & decisions
│   └── charts/             # Generated charts (shared)
├── .clinerules             # Cline behavior rules
├── install.sh              # Installation script
├── pyproject.toml          # Package configuration
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## 📊 Data Format

### Settings (data/settings.json)

The settings file now includes owner registry:

```json
{
  "version": "2.0",
  "current_owner": "john",
  "date_format": "YYYY-MM-DD",
  "owners": {
    "john": {
      "name": "John",
      "base_currency": "EUR",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "jane": {
      "name": "Jane",
      "base_currency": "USD",
      "created_at": "2024-01-16T14:00:00Z",
      "updated_at": "2024-01-16T14:00:00Z"
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T14:00:00Z"
}
```

### Portfolio (data/{owner}/portfolio.json)

Positions track individual purchase **lots** for complete history:

```json
{
  "version": "2.0",
  "owner": "John",
  "base_currency": "EUR",
  "cash": 5000.0,
  "positions": [
    {
      "symbol": "AAPL",
      "currency": "USD",
      "lots": [
        {
          "date": "2024-01-15",
          "shares": 50.0,
          "price": 175.00,
          "currency": "USD"
        },
        {
          "date": "2024-02-01",
          "shares": 20.0,
          "price": 180.00,
          "currency": "USD",
          "notes": "Added on dip"
        }
      ],
      "exchange": "NASDAQ",
      "sector": "Technology"
    },
    {
      "symbol": "ASML",
      "currency": "EUR",
      "lots": [
        {
          "date": "2024-02-01",
          "shares": 10.0,
          "price": 850.00,
          "currency": "EUR"
        }
      ],
      "exchange": "AMS",
      "sector": "Technology"
    }
  ]
}
```

**Computed properties** (not stored, calculated on-the-fly):
- `shares` = sum of all lot shares
- `avg_cost` = weighted average of lot prices
- `first_purchase` = earliest lot date
- `cost_basis` = total cost of all lots

### Memory (data/{owner}/memory.json)

Each owner has their own memory file:

```json
{
  "insights": [
    {
      "id": "uuid",
      "content": "Tech sector showing strength",
      "category": "market",
      "symbols": ["AAPL", "MSFT"],
      "created_at": "2024-01-15T10:30:00",
      "expires_at": "2024-04-15T10:30:00"
    }
  ],
  "decisions": [
    {
      "id": "uuid",
      "action": "BUY",
      "symbol": "AMZN",
      "shares": 50,
      "price": 145.50,
      "rationale": "AWS growth, AI tailwinds",
      "created_at": "2024-01-15T10:30:00",
      "review_at": "2024-04-15T10:30:00",
      "outcome": null
    }
  ],
  "snapshots": []
}
```

## 🌍 Multi-Currency Support

ClineFinance supports investors worldwide:

- **Set your base currency** on first use (USD, EUR, GBP, JPY, etc.)
- **Track positions in any currency** - each position stores its purchase currency
- **Automatic FX conversion** using live exchange rates
- **Dual currency display** - see values in original currency AND base currency
- **Currency risk analysis** - monitor exposure across currencies

### Supported Currencies
USD ($), EUR (€), GBP (£), JPY (¥), CHF, CAD (C$), AUD (A$), CNY (¥), HKD (HK$), SGD (S$), SEK (kr), NOK (kr), DKK (kr), INR (₹), BRL (R$), and more.

### Example: Multi-Currency Portfolio Display
```
│ Symbol │ Value (Orig) │ Value (USD) │ P&L % │ Weight │
├────────┼──────────────┼─────────────┼───────┼────────┤
│ AAPL   │ $17,550 USD  │ $17,550     │ +12%  │ 45%    │
│ ASML   │ €8,500 EUR   │ $9,350      │ +8%   │ 24%    │
│ HSBA   │ £2,100 GBP   │ $2,730      │ -3%   │ 7%     │
├────────┼──────────────┼─────────────┼───────┼────────┤
│ TOTAL  │ (mixed)      │ $38,700     │ +7%   │ 100%   │
```

## 🔒 Privacy

- All data stored locally in `data/` directory
- Each owner's data is completely separate
- No data sent to external servers (except market data APIs)
- Portfolio and decisions are confidential

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

---

**Built with ❤️ for investors worldwide using Cline**
