# Contributing to ClineFinance

Thank you for your interest in contributing to ClineFinance! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/EscVM/ClineFinance/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain how it benefits ClineFinance users

### Pull Requests

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Make your changes** following the code style below
4. **Test** your changes locally
5. **Commit** with clear messages: `git commit -m "Add: description of change"`
6. **Push** and open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ClineFinance.git
cd ClineFinance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .

# Run the server locally
python src/cline_finance/server.py
```

## Code Style

- **Python 3.10+** required
- Use **type hints** for function signatures
- Follow **PEP 8** conventions
- Use **docstrings** for public functions
- Keep functions focused and small

### Example

```python
def get_portfolio_value(symbol: str, shares: float) -> dict:
    """
    Calculate the current value of a position.
    
    Args:
        symbol: Stock ticker symbol
        shares: Number of shares held
    
    Returns:
        Dictionary with value, currency, and timestamp
    """
    # Implementation here
    pass
```

## Project Structure

```
src/cline_finance/
├── server.py           # Main MCP server (add tools here)
├── constants.py        # Configuration
├── core/               # Core business logic
│   ├── portfolio_manager.py
│   ├── memory_manager.py
│   ├── settings_manager.py
│   └── chart_generator.py
└── tools/              # MCP tool implementations
    ├── portfolio.py
    ├── quotes.py
    ├── market.py
    └── ...
```

## Adding a New Tool

1. Create or update a file in `src/cline_finance/tools/`
2. Import and register in `server.py`:

```python
@mcp.tool()
def my_new_tool(param: str) -> dict:
    """Tool description for Cline to understand."""
    return {"result": "value"}
```

3. Update `.clinerules` if needed
4. Add workflow in `workflows/` if applicable

## Adding a New Workflow

1. Create `workflows/my_workflow.md`
2. Add command to `.clinerules` under "Available Slash Commands"
3. Follow the existing workflow structure

## Testing

Currently, manual testing is the primary method:

```bash
# Run the server
python src/cline_finance/server.py

# Test with Cline in VS Code
# Use the tools and verify output
```

## Questions?

- Open an issue for questions
- Tag with `question` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make ClineFinance better! 💰
