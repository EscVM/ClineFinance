#!/bin/bash
set -e

# ClineFinance Installation Script
# Automatically configures MCP server for Cline

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PATH="$SCRIPT_DIR/src/cline_finance/server.py"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  💰 ClineFinance - Personal Financial Advisor for Cline  💰  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${BLUE}📦 Checking Python installation...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "✅ Python $PYTHON_VERSION found"
    else
        echo -e "${RED}❌ Python 3.10+ required (found $PYTHON_VERSION)${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}📦 Setting up virtual environment...${NC}"
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"
pip install -q --upgrade pip
pip install -q -e "$SCRIPT_DIR"
echo "✅ Dependencies installed"

# Create data directories
echo -e "${BLUE}📁 Creating data directories...${NC}"
mkdir -p "$SCRIPT_DIR/data/charts"
echo "✅ Data directories ready"

# Function to configure MCP
configure_mcp() {
    local config="$1"
    local name="$2"
    
    [[ ! -f "$config" ]] && { mkdir -p "$(dirname "$config")"; echo '{"mcpServers":{}}' > "$config"; }
    
    "$VENV_PYTHON" -c "
import json
with open('$config', 'r+') as f:
    c = json.load(f)
    c.setdefault('mcpServers', {})['cline-finance'] = {
        'command': '$VENV_PYTHON',
        'args': ['$SERVER_PATH'],
        'env': {
            'PYTHONPATH': '$SCRIPT_DIR/src',
            'DATA_DIR': '$SCRIPT_DIR/data'
        },
        'autoApprove': [
            'get_settings', 'set_settings',
            'fx_rate', 'convert_amount',
            'get_quote', 'get_price_history',
            'portfolio_valuation', 'portfolio_table', 'buy_stock', 'sell_stock',
            'modify_position', 'portfolio_history', 'generate_report',
            'market_overview', 'market_movers', 'sector_performance',
            'financial_news', 'news_for_portfolio',
            'analyst_ratings', 'earnings_calendar',
            'remember_insight', 'recall_insights', 'record_decision',
            'pending_reviews', 'decision_outcome', 'decision_history',
            'economic_indicators', 'yield_curve_status', 'interest_rates',
            'inflation_data', 'employment_data', 'gdp_growth'
        ]
    }
    f.seek(0)
    json.dump(c, f, indent=2)
    f.truncate()
"
    echo "✅ Configured $name at $config (all tools pre-approved)"
}

# Configure MCP server for Cline
echo ""
echo -e "${BLUE}📝 Configuring Cline MCP server...${NC}"

# Check known Cline config locations (fast, no find needed)
CLINE_CONFIG=""
CLINE_CONFIGS=(
    # macOS paths
    "$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    "$HOME/Library/Application Support/Code/User/globalStorage/asbx.amzn-cline/settings/cline_mcp_settings.json"
    # Linux paths
    "$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    "$HOME/.config/Code/User/globalStorage/asbx.amzn-cline/settings/cline_mcp_settings.json"
    # VS Code Insiders
    "$HOME/Library/Application Support/Code - Insiders/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    "$HOME/Library/Application Support/Code - Insiders/User/globalStorage/asbx.amzn-cline/settings/cline_mcp_settings.json"
)

for config in "${CLINE_CONFIGS[@]}"; do
    if [[ -f "$config" ]]; then
        CLINE_CONFIG="$config"
        break
    fi
done

if [[ -n "$CLINE_CONFIG" ]]; then
    configure_mcp "$CLINE_CONFIG" "Cline"
else
    echo -e "${YELLOW}⚠️  Cline MCP config not found - will show manual instructions${NC}"
fi

# Copy workflows to Cline
echo ""
echo -e "${BLUE}📁 Installing workflows...${NC}"

# Check known Cline workflow directories (fast, no find needed)
WORKFLOW_DIR=""
WORKFLOW_DIRS=(
    "$HOME/Documents/Cline/Workflows"
    "$HOME/Cline/Workflows"
    "$HOME/Desktop/Cline/Workflows"
)

for dir in "${WORKFLOW_DIRS[@]}"; do
    parent_dir=$(dirname "$dir")
    if [[ -d "$parent_dir" ]]; then
        WORKFLOW_DIR="$dir"
        break
    fi
done

# Default to ~/Cline/Workflows if no existing Cline directory found
WORKFLOW_DIR="${WORKFLOW_DIR:-$HOME/Cline/Workflows}"

if mkdir -p "$WORKFLOW_DIR" 2>/dev/null; then
    cp "$SCRIPT_DIR/workflows"/*.md "$WORKFLOW_DIR"/ 2>/dev/null && echo "✅ Copied workflows to $WORKFLOW_DIR" || echo "⚠️  Failed to copy workflows"
fi

# Optional: NewsAPI key
echo ""
echo -e "${BLUE}🔑 API Key Configuration (Optional)${NC}"
echo ""
echo "NewsAPI provides enhanced financial news."
echo "Get a free key at: https://newsapi.org/register"
echo ""

ENV_FILE="$SCRIPT_DIR/.env"
read -p "Enter NewsAPI key (or press Enter to skip): " NEWS_API_KEY

if [[ -n "$NEWS_API_KEY" ]]; then
    echo "NEWS_API_KEY=$NEWS_API_KEY" > "$ENV_FILE"
    echo "✅ NewsAPI key saved"
    
    # Update Cline MCP config with NEWS_API_KEY
    if [[ -f "$CLINE_CONFIG" ]]; then
        "$VENV_PYTHON" -c "
import json
with open('$CLINE_CONFIG', 'r+') as f:
    c = json.load(f)
    if 'cline-finance' in c.get('mcpServers', {}):
        c['mcpServers']['cline-finance']['env']['NEWS_API_KEY'] = '$NEWS_API_KEY'
        f.seek(0)
        json.dump(c, f, indent=2)
        f.truncate()
" 2>/dev/null
    fi
else
    echo -e "${YELLOW}⚠️  Skipped - will use yfinance fallback for news${NC}"
fi

# Optional: FRED API key
echo ""
echo "FRED (Federal Reserve) provides macroeconomic data:"
echo "  • Interest rates (Fed Funds, Treasury yields)"
echo "  • Inflation (CPI, PCE)"
echo "  • Employment (unemployment rate)"
echo "  • GDP growth"
echo "Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html"
echo ""

read -p "Enter FRED API key (or press Enter to skip): " FRED_API_KEY

if [[ -n "$FRED_API_KEY" ]]; then
    echo "FRED_API_KEY=$FRED_API_KEY" >> "$ENV_FILE"
    echo "✅ FRED API key saved"
    
    # Update Cline MCP config with FRED_API_KEY
    if [[ -f "$CLINE_CONFIG" ]]; then
        "$VENV_PYTHON" -c "
import json
with open('$CLINE_CONFIG', 'r+') as f:
    c = json.load(f)
    if 'cline-finance' in c.get('mcpServers', {}):
        c['mcpServers']['cline-finance']['env']['FRED_API_KEY'] = '$FRED_API_KEY'
        f.seek(0)
        json.dump(c, f, indent=2)
        f.truncate()
" 2>/dev/null
    fi
else
    echo -e "${YELLOW}⚠️  Skipped - economic indicators will not be available${NC}"
fi

# Show manual config if needed
if [[ -z "$CLINE_CONFIG" ]]; then
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}                    MANUAL CONFIGURATION                        ${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Add this to your cline_mcp_settings.json:"
    echo ""
    cat << EOF
{
  "mcpServers": {
    "cline-finance": {
      "command": "$VENV_PYTHON",
      "args": ["$SERVER_PATH"],
      "env": {
        "PYTHONPATH": "$SCRIPT_DIR/src",
        "DATA_DIR": "$SCRIPT_DIR/data"
      }
    }
  }
}
EOF
fi

# Final summary
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    ✅ INSTALLATION COMPLETE                    ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Available commands:"
echo "  /portfolio  - View your portfolio"
echo "  /analysis   - Full portfolio analysis"
echo "  /market     - Market overview"
echo "  /economy    - Economic indicators (requires FRED API key)"
echo "  /charts     - Visual dashboard with charts"
echo "  /ask        - Ask financial questions"
echo "  /rebalance  - Rebalancing recommendations"
echo ""
echo -e "${YELLOW}⚠️  Please restart VS Code / reload your agents${NC}"
echo ""

deactivate 2>/dev/null || true
exit 0
