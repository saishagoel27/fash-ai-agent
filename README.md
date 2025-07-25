# Clothing Search Agent

An intelligent AI-powered agent that searches for clothing items across multiple e-commerce platforms, helping users find the best deals and options based on their preferences.

## Features

- **Multi-Platform Search**: Searches across Amazon, eBay, Etsy, ASOS, and more
- **AI-Powered Filtering**: Uses OpenAI to understand natural language queries
- **Price Tracking**: Monitors price changes and sends alerts
- **Preference Learning**: Learns user preferences over time
- **Smart Notifications**: Email alerts for price drops and new matches
- **Data Persistence**: Stores search history and preferences

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd clothing-search-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration

## Configuration

### Required API Keys

- **OpenAI API Key**: For AI-powered search and filtering
- **SERP API Key**: For enhanced search capabilities
- **Email Credentials**: For notifications (optional)

### Environment Variables

See `.env` file for all configuration options.

## Usage

### Basic Usage

```python
from src.agents.clothing_agent import ClothingAgent

agent = ClothingAgent()

# Search for clothing items
results = agent.search("blue denim jacket under $100")

# Get filtered results based on preferences
filtered_results = agent.filter_results(results, preferences)
```

### Command Line Interface

```bash
# Run the agent with default settings
python scripts/run_agent.py

# Search for specific items
python scripts/run_agent.py --query "red summer dress size M"

# Set up user preferences
python src/main.py --setup-preferences
```

## Project Structure

```
clothing-search-agent/
├── src/                     # Main source code
│   ├── agents/             # AI agents
│   ├── scrapers/           # Web scrapers
│   ├── models/             # Data models
│   ├── services/           # Services (notifications, storage)
│   └── utils/              # Utilities
├── data/                   # Data storage
├── tests/                  # Test files
├── docs/                   # Documentation
├── notebooks/              # Jupyter notebooks
└── scripts/                # Utility scripts
```

## API Documentation

See `docs/api_docs.md` for detailed API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Testing

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_agents/
pytest tests/test_scrapers/

# Run with coverage
pytest --cov=src tests/
```

## Logging

Logs are stored in `logs/app.log`. Adjust log level in `.env` file.

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues, please open a GitHub issue.
