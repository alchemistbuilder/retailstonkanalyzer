from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import enum
from typing import Optional, List, Dict, Any

Base = declarative_base()

class AssetType(enum.Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    ETF = "etf"
    INDEX = "index"

class AlertType(enum.Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    VOLUME_SPIKE = "volume_spike"
    RSI_OVERSOLD = "rsi_oversold"
    RSI_OVERBOUGHT = "rsi_overbought"
    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"
    SENTIMENT_SPIKE = "sentiment_spike"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class WatchlistTicker(Base):
    __tablename__ = 'watchlist_tickers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(SQLEnum(AssetType), nullable=False, default=AssetType.STOCK)
    
    # Basic Info
    company_name = Column(String(200))
    sector = Column(String(100))
    exchange = Column(String(50))
    
    # Watchlist Metadata
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_last_checked = Column(DateTime)
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.MEDIUM)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # User Notes
    reason_added = Column(Text)  # Why was this added to watchlist
    notes = Column(Text)  # General notes
    entry_price_target = Column(Float)  # Target entry price
    exit_price_target = Column(Float)   # Target exit price
    stop_loss = Column(Float)  # Stop loss level
    
    # Current Market Data (cached for quick display)
    current_price = Column(Float)
    price_change_24h = Column(Float)
    price_change_percent_24h = Column(Float)
    volume_24h = Column(Float)
    market_cap = Column(Float)
    
    # Technical Indicators (cached)
    rsi_14 = Column(Float)
    macd_signal = Column(String(20))  # bullish/bearish/neutral
    
    # Alert Status
    has_active_alerts = Column(Boolean, default=False)
    last_alert_triggered = Column(DateTime)
    
    # Performance Tracking
    times_alerted = Column(Integer, default=0)
    max_price_since_added = Column(Float)
    min_price_since_added = Column(Float)
    
    def __repr__(self):
        return f"<WatchlistTicker(symbol='{self.symbol}', priority='{self.priority.value}', active={self.is_active})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'asset_type': self.asset_type.value if self.asset_type else None,
            'company_name': self.company_name,
            'sector': self.sector,
            'exchange': self.exchange,
            'date_added': self.date_added.isoformat() if self.date_added else None,
            'date_last_checked': self.date_last_checked.isoformat() if self.date_last_checked else None,
            'priority': self.priority.value if self.priority else None,
            'is_active': self.is_active,
            'reason_added': self.reason_added,
            'notes': self.notes,
            'entry_price_target': self.entry_price_target,
            'exit_price_target': self.exit_price_target,
            'stop_loss': self.stop_loss,
            'current_price': self.current_price,
            'price_change_24h': self.price_change_24h,
            'price_change_percent_24h': self.price_change_percent_24h,
            'volume_24h': self.volume_24h,
            'market_cap': self.market_cap,
            'rsi_14': self.rsi_14,
            'macd_signal': self.macd_signal,
            'has_active_alerts': self.has_active_alerts,
            'last_alert_triggered': self.last_alert_triggered.isoformat() if self.last_alert_triggered else None,
            'times_alerted': self.times_alerted,
            'max_price_since_added': self.max_price_since_added,
            'min_price_since_added': self.min_price_since_added
        }

class WatchlistAlert(Base):
    __tablename__ = 'watchlist_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, nullable=False, index=True)  # Foreign key to WatchlistTicker
    symbol = Column(String(20), nullable=False, index=True)
    
    # Alert Configuration
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    alert_value = Column(Float)  # The threshold value (price, RSI level, etc.)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Alert Status
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_triggered = Column(DateTime)
    times_triggered = Column(Integer, default=0)
    
    # Alert Details
    message = Column(Text)  # Custom alert message
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.MEDIUM)
    
    def __repr__(self):
        return f"<WatchlistAlert(symbol='{self.symbol}', type='{self.alert_type.value}', value={self.alert_value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'ticker_id': self.ticker_id,
            'symbol': self.symbol,
            'alert_type': self.alert_type.value if self.alert_type else None,
            'alert_value': self.alert_value,
            'is_active': self.is_active,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_triggered': self.date_triggered.isoformat() if self.date_triggered else None,
            'times_triggered': self.times_triggered,
            'message': self.message,
            'priority': self.priority.value if self.priority else None
        }

class WatchlistHistory(Base):
    __tablename__ = 'watchlist_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Historical Data Point
    date_recorded = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    price = Column(Float)
    volume = Column(Float)
    rsi_14 = Column(Float)
    
    # Performance vs Targets
    distance_to_entry = Column(Float)  # % away from entry target
    distance_to_exit = Column(Float)   # % away from exit target
    distance_to_stop = Column(Float)   # % away from stop loss
    
    def __repr__(self):
        return f"<WatchlistHistory(symbol='{self.symbol}', date='{self.date_recorded}', price={self.price})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'ticker_id': self.ticker_id,
            'symbol': self.symbol,
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None,
            'price': self.price,
            'volume': self.volume,
            'rsi_14': self.rsi_14,
            'distance_to_entry': self.distance_to_entry,
            'distance_to_exit': self.distance_to_exit,
            'distance_to_stop': self.distance_to_stop
        }

# Database Configuration
class WatchlistDatabase:
    def __init__(self, database_url: str = "sqlite:///watchlist.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()

# Utility Functions
def init_watchlist_database(database_url: str = "sqlite:///watchlist.db") -> WatchlistDatabase:
    """Initialize the watchlist database"""
    db = WatchlistDatabase(database_url)
    db.create_tables()
    return db

def get_database_session(database_url: str = "sqlite:///watchlist.db"):
    """Get a database session - use this in your API endpoints"""
    db = WatchlistDatabase(database_url)
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()