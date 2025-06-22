import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..core.config import settings
from ..data_collectors.fundamental_data_collector import FundamentalDataCollector
from ..data_collectors.technical_data_collector import TechnicalDataCollector
from .watchlist_service import WatchlistService
from ..database.watchlist_models import get_database_session, AssetType

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service to fetch and update market data for watchlist tickers"""
    
    def __init__(self):
        self.fundamental_collector = FundamentalDataCollector()
        self.technical_collector = TechnicalDataCollector()
        
    async def update_all_watchlist_data(self) -> Dict[str, Any]:
        """Update market data for all active watchlist tickers"""
        results = {
            "updated": [],
            "failed": [],
            "timestamp": datetime.utcnow().isoformat(),
            "total_processed": 0
        }
        
        try:
            # Get database session
            db_session = next(get_database_session())
            watchlist_service = WatchlistService(db_session)
            
            # Get all active tickers
            tickers = watchlist_service.get_all_tickers(active_only=True)
            results["total_processed"] = len(tickers)
            
            logger.info(f"Updating market data for {len(tickers)} watchlist tickers")
            
            # Process each ticker
            for ticker in tickers:
                try:
                    if ticker.asset_type == AssetType.CRYPTO:
                        # Handle crypto data
                        success = await self._update_crypto_data(watchlist_service, ticker.symbol)
                    else:
                        # Handle stock data
                        success = await self._update_stock_data(watchlist_service, ticker.symbol)
                    
                    if success:
                        results["updated"].append(ticker.symbol)
                        logger.info(f"✅ Updated {ticker.symbol}")
                    else:
                        results["failed"].append(ticker.symbol)
                        logger.warning(f"❌ Failed to update {ticker.symbol}")
                        
                    # Small delay to respect rate limits
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error updating {ticker.symbol}: {e}")
                    results["failed"].append(ticker.symbol)
            
            db_session.close()
            
        except Exception as e:
            logger.error(f"Error in update_all_watchlist_data: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _update_stock_data(self, watchlist_service: WatchlistService, symbol: str) -> bool:
        """Update data for a stock ticker"""
        try:
            # Get fundamental data (price, market cap, etc.)
            fundamental_data = await self.fundamental_collector.get_fundamental_data(symbol)
            
            # Get technical data (RSI, etc.)
            technical_data = await self.technical_collector.get_technical_indicators(symbol)
            
            if not fundamental_data and not technical_data:
                return False
            
            # Prepare update data
            update_data = {}
            
            if fundamental_data:
                update_data.update({
                    "current_price": fundamental_data.current_price,
                    "market_cap": fundamental_data.market_cap,
                    "volume_24h": getattr(fundamental_data, 'volume', None),
                })
                
                # Calculate 24h change if we have previous price
                ticker = watchlist_service.get_ticker(symbol)
                if ticker and ticker.current_price and fundamental_data.current_price:
                    price_change = fundamental_data.current_price - ticker.current_price
                    price_change_percent = (price_change / ticker.current_price) * 100
                    update_data.update({
                        "price_change_24h": price_change,
                        "price_change_percent_24h": price_change_percent
                    })
            
            if technical_data:
                update_data.update({
                    "rsi_14": technical_data.rsi,
                    "macd_signal": self._get_macd_signal(technical_data)
                })
            
            # Update in database
            if update_data:
                success = watchlist_service.update_ticker_market_data(
                    symbol=symbol,
                    **update_data
                )
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating stock data for {symbol}: {e}")
            return False
    
    async def _update_crypto_data(self, watchlist_service: WatchlistService, symbol: str) -> bool:
        """Update data for a crypto ticker"""
        try:
            # For crypto, we'll use a simple price API (CoinGecko-style)
            crypto_data = await self._fetch_crypto_data(symbol)
            
            if not crypto_data:
                return False
            
            # Update in database
            success = watchlist_service.update_ticker_market_data(
                symbol=symbol,
                current_price=crypto_data.get("current_price"),
                price_change_24h=crypto_data.get("price_change_24h"),
                price_change_percent_24h=crypto_data.get("price_change_percent_24h"),
                volume_24h=crypto_data.get("volume_24h"),
                market_cap=crypto_data.get("market_cap")
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating crypto data for {symbol}: {e}")
            return False
    
    async def _fetch_crypto_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch crypto data from CoinGecko API (free tier)"""
        try:
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum", 
                "ADA": "cardano",
                "DOT": "polkadot",
                "LINK": "chainlink",
                "UNI": "uniswap",
                "AAVE": "aave",
                "SUSHI": "sushi"
            }
            
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if coin_id in data:
                            coin_data = data[coin_id]
                            return {
                                "current_price": coin_data.get("usd"),
                                "price_change_percent_24h": coin_data.get("usd_24h_change"),
                                "volume_24h": coin_data.get("usd_24h_vol"),
                                "market_cap": coin_data.get("usd_market_cap")
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return None
    
    async def update_single_ticker(self, symbol: str) -> bool:
        """Update market data for a single ticker"""
        try:
            db_session = next(get_database_session())
            watchlist_service = WatchlistService(db_session)
            
            ticker = watchlist_service.get_ticker(symbol)
            if not ticker:
                return False
            
            if ticker.asset_type == AssetType.CRYPTO:
                success = await self._update_crypto_data(watchlist_service, symbol)
            else:
                success = await self._update_stock_data(watchlist_service, symbol)
            
            db_session.close()
            return success
            
        except Exception as e:
            logger.error(f"Error updating single ticker {symbol}: {e}")
            return False
    
    def _get_macd_signal(self, technical_data) -> str:
        """Convert MACD data to simple signal"""
        try:
            if hasattr(technical_data, 'macd') and hasattr(technical_data, 'macd_signal'):
                if technical_data.macd > technical_data.macd_signal:
                    return "bullish"
                elif technical_data.macd < technical_data.macd_signal:
                    return "bearish"
            return "neutral"
        except:
            return "neutral"

class MarketDataScheduler:
    """Scheduler for automatic market data updates"""
    
    def __init__(self, update_interval_minutes: int = 10):
        self.update_interval = update_interval_minutes * 60  # Convert to seconds
        self.market_data_service = MarketDataService()
        self.running = False
        self.last_update = None
        
    async def start_scheduler(self):
        """Start the automatic update scheduler"""
        self.running = True
        logger.info(f"Starting market data scheduler (every {self.update_interval/60} minutes)")
        
        while self.running:
            try:
                logger.info("Starting scheduled market data update...")
                results = await self.market_data_service.update_all_watchlist_data()
                
                self.last_update = datetime.utcnow()
                
                logger.info(f"Scheduled update completed: {len(results['updated'])} updated, {len(results['failed'])} failed")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in scheduled update: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_scheduler(self):
        """Stop the automatic update scheduler"""
        self.running = False
        logger.info("Market data scheduler stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.running,
            "update_interval_minutes": self.update_interval / 60,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "next_update": (self.last_update + timedelta(seconds=self.update_interval)).isoformat() if self.last_update else None
        }

# Global scheduler instance
market_data_scheduler = MarketDataScheduler(update_interval_minutes=10)