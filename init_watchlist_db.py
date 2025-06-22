#!/usr/bin/env python3
"""
Initialize the Watchlist Database

This script creates the SQLite database and tables for the watchlist feature.
Run this once before starting the API server.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.watchlist_models import init_watchlist_database, WatchlistDatabase
from src.services.watchlist_service import WatchlistService
from src.database.watchlist_models import AssetType, Priority

def create_sample_data(db: WatchlistDatabase):
    """Create some sample watchlist entries for testing"""
    service = WatchlistService(db.get_session())
    
    try:
        # Add some sample stocks
        sample_tickers = [
            {
                "symbol": "GME",
                "asset_type": AssetType.STOCK,
                "priority": Priority.HIGH,
                "reason_added": "Reddit meme stock momentum",
                "entry_price_target": 20.0,
                "exit_price_target": 50.0,
                "stop_loss": 15.0,
                "company_name": "GameStop Corp",
                "sector": "Consumer Discretionary"
            },
            {
                "symbol": "AMC",
                "asset_type": AssetType.STOCK,
                "priority": Priority.HIGH,
                "reason_added": "Short squeeze potential",
                "entry_price_target": 8.0,
                "exit_price_target": 25.0,
                "stop_loss": 6.0,
                "company_name": "AMC Entertainment Holdings Inc",
                "sector": "Communication Services"
            },
            {
                "symbol": "TSLA",
                "asset_type": AssetType.STOCK,
                "priority": Priority.MEDIUM,
                "reason_added": "EV growth and innovation",
                "entry_price_target": 200.0,
                "exit_price_target": 300.0,
                "stop_loss": 180.0,
                "company_name": "Tesla Inc",
                "sector": "Consumer Discretionary"
            },
            {
                "symbol": "ETH",
                "asset_type": AssetType.CRYPTO,
                "priority": Priority.MEDIUM,
                "reason_added": "Crypto DeFi ecosystem growth",
                "entry_price_target": 2000.0,
                "exit_price_target": 3000.0,
                "stop_loss": 1800.0,
                "company_name": "Ethereum",
                "sector": "Cryptocurrency"
            },
            {
                "symbol": "BTC",
                "asset_type": AssetType.CRYPTO,
                "priority": Priority.LOW,
                "reason_added": "Digital gold hedge",
                "entry_price_target": 40000.0,
                "exit_price_target": 60000.0,
                "stop_loss": 35000.0,
                "company_name": "Bitcoin",
                "sector": "Cryptocurrency"
            }
        ]
        
        for ticker_data in sample_tickers:
            try:
                service.add_ticker(**ticker_data)
                print(f"✅ Added {ticker_data['symbol']} to watchlist")
            except ValueError as e:
                print(f"⚠️  {ticker_data['symbol']} already exists: {e}")
                
        print(f"✅ Sample data creation completed")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
    finally:
        service.db.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing Watchlist Database")
    print("=" * 50)
    
    # Database file path
    db_path = "watchlist.db"
    database_url = f"sqlite:///{db_path}"
    
    try:
        # Initialize database
        print("📦 Creating database tables...")
        db = init_watchlist_database(database_url)
        print(f"✅ Database initialized at: {db_path}")
        
        # Add sample data by default for demo
        print("\n📝 Creating sample watchlist entries...")
        create_sample_data(db)
        
        print("\n🎉 Watchlist database initialization complete!")
        print("\nNext steps:")
        print("1. Start the API server: python main.py --server")
        print("2. Open the watchlist dashboard: watchlist_dashboard.html")
        print("3. Add your tickers via the web interface or API")
        
        # Display current database info
        service = WatchlistService(db.get_session())
        summary = service.get_watchlist_summary()
        print(f"\n📊 Current watchlist stats:")
        print(f"   Total tickers: {summary['total_tickers']}")
        print(f"   High priority: {summary['high_priority_tickers']}")
        
        service.db.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())