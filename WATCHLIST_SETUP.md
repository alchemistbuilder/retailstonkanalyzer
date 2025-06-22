# 📊 Watchlist System Setup Guide

## 🚀 Quick Start

### 1. Initialize the Database
```bash
python init_watchlist_db.py
```
This will:
- Create the SQLite database (`watchlist.db`)
- Set up all necessary tables
- Optionally add sample data (GME, AMC, TSLA, ETH, BTC)

### 2. Start the API Server
```bash
python main.py --server
```
The server will be available at: http://localhost:8000

### 3. Open the Dashboard
Open `watchlist_dashboard.html` in your browser to access the web interface.

## 📋 What You Get

### Database Features
- **Ticker Management**: Add/remove stocks and crypto
- **Price Targets**: Set entry, exit, and stop-loss levels  
- **Priority System**: High/Medium/Low priority classification
- **Alert System**: Price and technical indicator alerts
- **Historical Tracking**: Track performance over time
- **Notes & Reasons**: Document why you're watching each ticker

### API Endpoints
- `POST /api/watchlist/tickers` - Add ticker
- `GET /api/watchlist/tickers` - List all tickers
- `GET /api/watchlist/tickers/{symbol}` - Get specific ticker
- `DELETE /api/watchlist/tickers/{symbol}` - Remove ticker
- `POST /api/watchlist/alerts` - Add alert
- `GET /api/watchlist/summary` - Get watchlist summary
- `GET /api/watchlist/movers` - Get biggest movers
- `GET /api/watchlist/near-targets` - Get tickers near price targets

### Web Dashboard Features
- **Live Data**: Real-time price updates every 30 seconds
- **Filtering**: Filter by asset type, priority, or search
- **Visual Indicators**: Color-coded price changes and RSI levels
- **Alert Management**: Visual alerts for active notifications
- **Add/Edit Interface**: Modal forms for managing tickers

## 🔧 Configuration

### Database Configuration
By default, uses SQLite (`watchlist.db`). To use PostgreSQL:

1. Update the database URL in `get_database_session()`:
```python
# In src/database/watchlist_models.py
def get_database_session(database_url: str = "postgresql://user:pass@localhost/watchlist"):
```

2. Install PostgreSQL dependencies:
```bash
pip install psycopg2-binary
```

### API Integration
The watchlist integrates with your existing stock analysis APIs:
- Uses Polygon.io for price data
- Uses FMP for fundamentals
- Can be extended to use crypto APIs

## 📊 Daily Workflow

### 1. Morning Review
- Open dashboard to see overnight moves
- Check "Near Targets" section for entry opportunities
- Review any triggered alerts

### 2. Add New Tickers
- Research potential opportunities
- Add to watchlist with price targets and notes
- Set priority based on conviction level

### 3. Monitor Throughout Day
- Dashboard auto-refreshes every 30 seconds
- Check for alert notifications
- Update notes as new information emerges

### 4. End of Day Review
- Review performance vs targets
- Update stop losses if needed
- Plan next day's focus based on setups

## 🚨 Alert System

### Alert Types Available
- `price_above` - Trigger when price goes above level
- `price_below` - Trigger when price goes below level  
- `rsi_oversold` - Trigger when RSI drops below level
- `rsi_overbought` - Trigger when RSI rises above level
- `volume_spike` - Trigger on volume anomalies
- `breakout` - Trigger on technical breakouts
- `sentiment_spike` - Trigger on social sentiment spikes

### Setting Up Alerts
```python
# Via API
POST /api/watchlist/alerts
{
  "symbol": "GME",
  "alert_type": "price_above", 
  "alert_value": 25.0,
  "priority": "high",
  "message": "GME breakout above resistance"
}
```

## 📈 Integration with Analysis Tools

### Connect to Existing Analysis
Your watchlist automatically integrates with the existing stock analyzer:

```python
# Update market data for watchlist ticker
PUT /api/watchlist/tickers/GME/market-data
{
  "current_price": 23.45,
  "rsi_14": 67.2,
  "macd_signal": "bullish",
  "volume_24h": 15000000
}
```

### Bulk Updates
Update multiple tickers at once:
```python
POST /api/watchlist/bulk/update-market-data
[
  {"symbol": "GME", "current_price": 23.45, "rsi_14": 67.2},
  {"symbol": "AMC", "current_price": 8.90, "rsi_14": 45.1}
]
```

## 🔄 Data Refresh Strategy

### Automatic Updates
- Dashboard refreshes every 30 seconds
- Market data cached for performance
- Historical data recorded for trend analysis

### Manual Refresh
- Click "🔄 Refresh" button in dashboard
- Or call `/api/watchlist/tickers` endpoint

## 📱 Next Steps

Once the watchlist is working, consider adding:

1. **Mobile Notifications** - Push alerts to phone
2. **Email Alerts** - Daily/weekly summaries
3. **Integration with Trading APIs** - Auto-execute based on alerts
4. **Advanced Charts** - TradingView integration
5. **Portfolio Tracking** - Track actual positions vs watchlist
6. **Social Sentiment Integration** - Add Reddit/Twitter sentiment
7. **Backtesting** - Test strategies on historical data

## 🛠️ Troubleshooting

### Database Issues
```bash
# Reset database
rm watchlist.db
python init_watchlist_db.py
```

### API Connection Issues
- Check if server is running: http://localhost:8000/docs
- Verify CORS settings in `main.py`
- Check console for JavaScript errors

### Performance Issues
- Consider switching to PostgreSQL for large watchlists
- Implement Redis caching for market data
- Optimize database queries with indexes

## 🏗️ Architecture

```
watchlist_dashboard.html (Frontend)
        ↓ HTTP/JSON
src/api/watchlist_api.py (FastAPI Endpoints)  
        ↓ Python
src/services/watchlist_service.py (Business Logic)
        ↓ SQLAlchemy
src/database/watchlist_models.py (Database Models)
        ↓ SQL
watchlist.db (SQLite Database)
```

This gives you a solid foundation for daily stock monitoring and position management!