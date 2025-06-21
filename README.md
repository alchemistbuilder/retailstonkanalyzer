# 🎯 Retail Meme Stock Analyzer

A comprehensive stock analysis system that combines **social sentiment**, **technical analysis**, **fundamental data**, **analyst coverage**, and **stock structure** to identify retail meme stock opportunities and detect institutional vs retail sentiment divergences.

## ✨ Features

### 📊 Multi-Factor Analysis
- **Social Sentiment**: Reddit, Twitter/X, StockTwits monitoring
- **Technical Analysis**: Chart patterns, indicators, trend analysis
- **Fundamental Analysis**: Financial metrics, valuation ratios
- **Analyst Coverage**: Ratings, price targets, consensus data
- **Stock Structure**: Short interest, float, institutional ownership

### 🔍 Advanced Detection
- **Short Squeeze Identification**: High short interest + positive sentiment
- **Sentiment Divergence**: Retail vs institutional sentiment gaps
- **Momentum Analysis**: Chart patterns and breakout detection
- **Value Opportunities**: Undervalued stocks with analyst support
- **Risk Assessment**: Multi-factor risk scoring

### 🚀 API & Interface
- **RESTful API**: FastAPI-powered backend
- **Real-time Analysis**: Async data collection and processing
- **Alerting System**: Priority-based opportunity alerts
- **Batch Processing**: Watchlist scanning and monitoring

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- API keys for data sources (see Configuration section)

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd retailstonkanalyzer

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## ⚙️ Configuration

### Required API Keys

Create a `.env` file with the following API keys:

#### 📈 Financial Data APIs
```bash
# Alpha Vantage (Free tier: 5 calls/minute)
ALPHA_VANTAGE_API_KEY=your_key_here

# Polygon.io (Free tier: 5 calls/minute)
POLYGON_API_KEY=your_key_here

# Financial Modeling Prep (Free tier: 250 calls/day)
FMP_API_KEY=your_key_here

# Finnhub (Free tier: 60 calls/minute)
FINNHUB_API_KEY=your_key_here
```

#### 📊 Stock Structure APIs
```bash
# ORTEX (Premium service for short interest data)
ORTEX_API_KEY=your_key_here

# Benzinga (Analyst ratings and news)
BENZINGA_API_KEY=your_key_here
```

#### 📱 Social Media APIs
```bash
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Twitter API v2
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# StockTwits
STOCKTWITS_ACCESS_TOKEN=your_token_here
```

### 🔑 Getting API Keys

#### Free APIs (Recommended to start)
1. **Alpha Vantage**: [alphavantage.co](https://www.alphavantage.co/support/#api-key) - Free
2. **Financial Modeling Prep**: [financialmodelingprep.com](https://financialmodelingprep.com/developer/docs) - Free tier
3. **Polygon.io**: [polygon.io](https://polygon.io/) - Free tier
4. **Reddit**: [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) - Free
5. **Twitter**: [developer.twitter.com](https://developer.twitter.com/) - Free tier

#### Premium APIs (Optional for enhanced features)
1. **ORTEX**: [ortex.com](https://public.ortex.com/ortex-apis) - Premium short interest data
2. **Benzinga**: [benzinga.com/apis](https://www.benzinga.com/apis/) - Premium analyst data

## 🚀 Usage

### Command Line Interface

```bash
# Check configuration
python main.py --config

# Analyze a single stock
python main.py --symbol GME

# Analyze multiple stocks
python main.py --symbols GME AMC TSLA NVDA

# Analyze entire watchlist
python main.py --watchlist

# Start API server
python main.py --server
```

### API Server

Start the API server:
```bash
python main.py --server
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### API Endpoints

#### Core Analysis
```bash
# Analyze specific stocks
POST /analyze
{
  "symbols": ["GME", "AMC", "TSLA"]
}

# Get detailed stock analysis
GET /stock/{symbol}

# Scan watchlist (background task)
POST /scan
```

#### Data Retrieval
```bash
# Get watchlist summary
GET /watchlist

# Get top opportunities
GET /top-opportunities?limit=10&min_score=70

# Get alerts
GET /alerts?priority=high

# Get system status
GET /status
```

## 📊 Analysis Components

### 1. Social Sentiment (25% weight)
- **Reddit**: Mentions, sentiment, subreddit analysis
- **Twitter**: Tweet volume, engagement, sentiment
- **StockTwits**: Bullish/bearish sentiment, user following
- **Scoring**: Volume-weighted sentiment with trend analysis

### 2. Technical Analysis (25% weight)
- **Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Patterns**: Chart pattern recognition with confidence scores
- **Volume**: Spike detection and trend confirmation
- **Trend**: Multi-timeframe trend analysis

### 3. Fundamental Analysis (20% weight)
- **Valuation**: P/E, P/S, P/B ratios vs industry
- **Growth**: Revenue growth, earnings growth trends
- **Profitability**: Margins, ROE, ROA analysis
- **Health**: Debt ratios, liquidity metrics

### 4. Analyst Coverage (15% weight)
- **Consensus**: Buy/Hold/Sell ratings distribution
- **Price Targets**: Average, high, low targets with upside
- **Changes**: Recent upgrades/downgrades tracking
- **Firm Quality**: Coverage from top-tier analysts

### 5. Stock Structure (15% weight)
- **Short Interest**: Percentage of float shorted
- **Float**: Free-trading shares availability
- **Ownership**: Institutional vs retail distribution
- **Squeeze Potential**: Multi-factor squeeze scoring

## 🎯 Scoring System

### Composite Score (0-100)
The system generates a weighted composite score combining all five factors:

- **90-100**: Exceptional opportunity
- **80-89**: Strong buy signal
- **70-79**: Good opportunity
- **60-69**: Moderate interest
- **50-59**: Neutral/Hold
- **Below 50**: Weak/Avoid

### Risk Assessment
- **Low Risk**: Established companies, strong fundamentals
- **Medium Risk**: Growth stocks, moderate volatility
- **High Risk**: Meme stocks, high volatility, speculative

### Opportunity Types
- **Short Squeeze**: High short interest + positive sentiment
- **Momentum**: Strong technical + social momentum
- **Value**: Undervalued with analyst support
- **Growth**: Strong fundamentals + growth metrics
- **Contrarian**: Negative sentiment + positive fundamentals

## 🚨 Alert System

### Divergence Detection
The system identifies key divergences:

1. **Retail Bullish vs Institutional Bearish**
   - High social sentiment + analyst downgrades
   - Warning: Potential bubble formation

2. **Retail Bearish vs Institutional Bullish**
   - Low social interest + strong analyst ratings
   - Opportunity: Institutional accumulation

3. **Short Squeeze Setup**
   - High short interest + positive retail sentiment
   - High volatility potential

4. **Hidden Gems**
   - Strong fundamentals + low social attention
   - Long-term value opportunities

5. **Value Traps**
   - Cheap valuation + deteriorating fundamentals
   - Risk warning signals

### Alert Priorities
- **High**: Score >80, strong divergence signals
- **Medium**: Score 60-80, moderate signals
- **Low**: Score <60, weak signals

## 📈 Example Analysis Output

```
🔍 Analyzing GME...
==================================================
📊 GME - GameStop Corp.
🎯 Composite Score: 78.5/100
🏷️  Opportunity Type: short_squeeze
⚠️  Risk Level: high
🔒 Confidence: 0.75

📈 Component Scores:
  📱 Social Sentiment: 85.2
  📊 Technical Analysis: 72.1
  💰 Fundamental Analysis: 45.8
  👥 Analyst Coverage: 38.4
  🏗️  Stock Structure: 92.3

💬 Social Sentiment:
  Mentions: 1,247
  Sentiment Score: 0.734
  Trend: bullish
  Top Keywords: squeeze, diamond, hands, moon, rocket

🚨 Alerts (3):
  HIGH: Short squeeze setup detected
  MEDIUM: Strong social momentum vs weak analyst support
  LOW: High volatility expected
```

## 🔧 Development

### Project Structure
```
retailstonkanalyzer/
├── src/
│   ├── analyzers/          # Scoring and analysis logic
│   ├── data_collectors/    # API integrations
│   ├── core/              # Main orchestration
│   ├── models/            # Data models
│   ├── api/               # FastAPI endpoints
│   ├── dashboard/         # UI components (future)
│   └── utils/             # Utilities and helpers
├── tests/                 # Test suite
├── config/               # Configuration files
├── requirements.txt      # Dependencies
├── main.py              # CLI entry point
└── README.md           # This file
```

### Adding New Data Sources
1. Create collector in `src/data_collectors/`
2. Implement data models in `src/models/`
3. Add scoring logic in `src/analyzers/`
4. Update composite scorer weights in `src/core/config.py`

### Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 📊 Performance & Limits

### Rate Limits (Free Tiers)
- **Alpha Vantage**: 5 calls/minute
- **Polygon**: 5 calls/minute  
- **FMP**: 250 calls/day
- **Reddit**: 60 calls/minute
- **Twitter**: 300 calls/15min window

### Recommended Usage
- **Single Stock**: ~2-3 seconds
- **Watchlist (20 stocks)**: ~2-3 minutes
- **API Response**: <1 second (cached data)

### Scaling Considerations
- Use Redis for caching in production
- Implement PostgreSQL for data persistence
- Add Celery for background processing
- Deploy with Docker containers

## 🛡️ Risk Disclaimers

⚠️ **IMPORTANT DISCLAIMERS**

- **Not Financial Advice**: This tool is for educational and research purposes only
- **High Risk**: Meme stocks are highly volatile and speculative
- **Do Your Research**: Always perform additional due diligence
- **Risk Management**: Never invest more than you can afford to lose
- **Market Volatility**: Past performance does not predict future results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or feature requests:
1. Check the [Issues](https://github.com/yourusername/retailstonkanalyzer/issues) page
2. Create a new issue with detailed description
3. Include relevant logs and configuration details

---

**Happy Trading! 🚀📈**

*Remember: This tool helps identify opportunities, but successful trading requires discipline, risk management, and continuous learning.*