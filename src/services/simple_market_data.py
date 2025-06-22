import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..core.config import settings
from .watchlist_service import WatchlistService
from ..database.watchlist_models import get_database_session, AssetType

logger = logging.getLogger(__name__)

class SimpleMarketDataService:
    """Simplified market data service using your configured APIs"""
    
    def __init__(self):
        self.polygon_api_key = settings.polygon_api_key
        self.fmp_api_key = settings.fmp_api_key
        
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
                    await asyncio.sleep(1)  # Be conservative with rate limits
                    
                except Exception as e:
                    logger.error(f"Error updating {ticker.symbol}: {e}")
                    results["failed"].append(ticker.symbol)
            
            db_session.close()
            
        except Exception as e:
            logger.error(f"Error in update_all_watchlist_data: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _update_stock_data(self, watchlist_service: WatchlistService, symbol: str) -> bool:
        """Update data for a stock ticker using FMP and Polygon APIs"""
        try:
            # Try FMP first (you have this configured)
            fmp_data = await self._fetch_fmp_quote(symbol)
            
            if fmp_data:
                # Extract data from FMP response
                current_price = fmp_data.get('price')
                market_cap = fmp_data.get('marketCap')
                volume = fmp_data.get('volume')
                change = fmp_data.get('change')
                change_percent = fmp_data.get('changesPercentage')
                
                # Calculate RSI using simple approximation (you can enhance this)
                rsi = self._calculate_simple_rsi(change_percent)
                
                # Update in database
                success = watchlist_service.update_ticker_market_data(
                    symbol=symbol,
                    current_price=current_price,
                    price_change_24h=change,
                    price_change_percent_24h=change_percent,
                    volume_24h=volume,
                    market_cap=market_cap,
                    rsi_14=rsi,
                    macd_signal=self._get_simple_macd_signal(change_percent)
                )
                
                return success
            
            # If FMP fails, try Polygon as backup
            if self.polygon_api_key:
                polygon_data = await self._fetch_polygon_quote(symbol)
                if polygon_data:
                    return await self._process_polygon_data(watchlist_service, symbol, polygon_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating stock data for {symbol}: {e}")
            return False
    
    async def _fetch_fmp_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current quote from Financial Modeling Prep"""
        try:
            if not self.fmp_api_key:
                return None
                
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}"
            params = {"apikey": self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            return data[0]  # FMP returns array
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching FMP quote for {symbol}: {e}")
            return None
    
    async def _fetch_polygon_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current quote from Polygon.io"""
        try:
            if not self.polygon_api_key:
                return None
                
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
            params = {"apikey": self.polygon_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'OK' and data.get('results'):
                            return data['results'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Polygon quote for {symbol}: {e}")
            return None
    
    async def _process_polygon_data(self, watchlist_service: WatchlistService, symbol: str, data: Dict) -> bool:
        """Process Polygon API data"""
        try:
            current_price = data.get('c')  # Close price
            volume = data.get('v')  # Volume
            
            # Calculate change (approximation)
            open_price = data.get('o', current_price)
            change = current_price - open_price if current_price and open_price else 0
            change_percent = (change / open_price * 100) if open_price else 0
            
            # Simple RSI approximation
            rsi = self._calculate_simple_rsi(change_percent)
            
            success = watchlist_service.update_ticker_market_data(
                symbol=symbol,
                current_price=current_price,
                price_change_24h=change,
                price_change_percent_24h=change_percent,
                volume_24h=volume,
                rsi_14=rsi,
                macd_signal=self._get_simple_macd_signal(change_percent)
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing Polygon data for {symbol}: {e}")
            return False
    
    async def _update_crypto_data(self, watchlist_service: WatchlistService, symbol: str) -> bool:
        """Update data for a crypto ticker using CoinGecko API (free)"""
        try:
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
                market_cap=crypto_data.get("market_cap"),
                rsi_14=self._calculate_simple_rsi(crypto_data.get("price_change_percent_24h", 0))
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
    
    def _calculate_simple_rsi(self, change_percent: float) -> float:
        """Simple RSI approximation based on price change"""
        if change_percent is None:
            return 50.0
        
        # Simple mapping: negative change -> lower RSI, positive -> higher RSI
        # This is a very basic approximation
        if change_percent > 5:
            return 80.0
        elif change_percent > 2:
            return 70.0
        elif change_percent > 0:
            return 60.0
        elif change_percent > -2:
            return 40.0
        elif change_percent > -5:
            return 30.0
        else:
            return 20.0
    
    def _get_simple_macd_signal(self, change_percent: float) -> str:
        """Simple MACD signal based on price change"""
        if change_percent is None:
            return "neutral"
        
        if change_percent > 1:
            return "bullish"
        elif change_percent < -1:
            return "bearish"
        else:
            return "neutral"
    
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