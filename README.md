# Fash AI Agent - Social Media Fashion Trends Integration

An intelligent AI-powered agent that searches for clothing items across multiple e-commerce platforms and social media sources, providing personalized fashion recommendations with trend-driven insights from Pinterest and Instagram.

## 🌟 New Features (Issue #10)

- **Social Media Integration**: Real-time fashion trends from Pinterest and Instagram
- **Personalized Recommendation Loop**: AI learns from user feedback (likes, dislikes, saves)
- **Trend Analysis**: Seasonal trends, brand popularity, and fashion inspiration
- **User Feedback System**: Interactive feedback collection and preference learning
- **Enhanced Search**: Combines e-commerce results with social media content
- **Web Interface**: Beautiful UI for exploring trends and providing feedback

## Features

- **Multi-Platform Search**: Searches across Amazon, eBay, Etsy, ASOS, Pinterest, and Instagram
- **Social Media Trends**: Real-time fashion content from Pinterest and Instagram
- **AI-Powered Filtering**: Uses OpenAI to understand natural language queries
- **Personalized Recommendations**: Learns from user interactions and preferences
- **User Feedback Loop**: Like, dislike, and save items to improve recommendations
- **Trend Analysis**: Discover seasonal trends and fashion inspiration
- **Price Tracking**: Monitors price changes and sends alerts
- **Smart Notifications**: Email alerts for price drops and new matches
- **Data Persistence**: Stores search history, preferences, and feedback
- **Web Interface**: Modern UI for exploring fashion trends and providing feedback

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
python main.py

# Search for specific items
python main.py --query "red summer dress size M"

# Enhanced search with social media trends
python main.py --query "summer dress" --social-media

# Get trending fashion content
python main.py --trending

# Get fashion inspiration
python main.py --inspiration "vintage,bohemian,minimalist"

# Get seasonal trends
python main.py --season summer

# Set up user preferences
python main.py --setup-preferences

# Use personalized recommendations
python main.py --query "jeans" --user-session "your-session-id"
```

### Web Interface

```bash
# Start the web interface
python web_interface.py

# Access the interface at http://localhost:5000
```

### Interactive Mode

```bash
python main.py

# Available commands:
# - Type any clothing search query
# - 'trending' - Get trending fashion content
# - 'inspiration: [keywords]' - Get fashion inspiration
# - 'help' - Show help
# - 'quit' - Exit
```

## Project Structure

```
fash-ai-agent/
├── main.py                 # Main entry point
├── clothing_agent.py       # Main clothing search agent
├── clothing_item.py        # Clothing item data model
├── preferences.py          # User preferences model
├── filter_agent.py         # Filtering and ranking agent
├── base_agent.py           # Base agent class
├── settings.py             # Settings and configuration
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── web_interface.py        # Flask web interface
├── templates/              # HTML templates
│   └── index.html          # Main web interface
├── pinterest_scraper.py    # Pinterest fashion scraper
├── instagram_scraper.py    # Instagram fashion scraper
├── social_media_manager.py # Social media trends manager
├── user_feedback.py        # User feedback system
├── README.md               # Project documentation
├── LICENSE                 # License file
└── user_feedback.db        # User feedback database (created automatically)
```

## Social Media Integration

### Pinterest Integration
- **Trending Fashion**: Get real-time fashion trends from Pinterest
- **Style Inspiration**: Search for fashion inspiration based on keywords
- **User Feeds**: Access fashion content from specific Pinterest users
- **Hashtag Search**: Find content by fashion-related hashtags

### Instagram Integration
- **Fashion Hashtags**: Search popular fashion hashtags (#fashion, #style, #ootd)
- **Influencer Content**: Get fashion content from popular influencers
- **Brand Trends**: Discover trending content for specific brands
- **Seasonal Trends**: Find seasonal fashion content

### User Feedback System
- **Like/Dislike**: Rate items to improve recommendations
- **Save Items**: Bookmark items for later reference
- **View Tracking**: Automatic tracking of viewed items
- **Preference Learning**: AI learns from user interactions
- **Personalized Scores**: Items ranked based on user preferences

### Enhanced Search Features
- **Combined Results**: E-commerce + social media content
- **Trending Integration**: Include trending content in searches
- **Personalized Ranking**: Results ranked by user preferences
- **Seasonal Trends**: Get seasonal fashion recommendations
- **Brand Analysis**: Discover trending brands and styles

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
