import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Optional, List
from urllib.parse import urlencode

from ..core.config import settings
from ..utils.rate_limiter import RateLimiter


class ChartImageCollector:
    def __init__(self):
        self.base_url = "https://chart-img.com/chart"
        self.api_key = getattr(settings, 'chart_img_api_key', None)
        self.rate_limiter = RateLimiter(requests_per_minute=60)  # Conservative limit
    
    async def get_chart_image(self, symbol: str, timeframe: str = "daily", 
                            indicators: List[str] = None, width: int = 800, 
                            height: int = 600) -> str:
        """Get chart image URL for a specific symbol and timeframe"""
        try:
            # Build URL parameters
            params = {
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'width': width,
                'height': height
            }
            
            # Add indicators if specified
            if indicators:
                params['indicators'] = ','.join(indicators)
            
            # Add API key if available
            if self.api_key:
                params['api_key'] = self.api_key
            
            # Build full URL
            if params:
                url = f"{self.base_url}/{symbol.upper()}?{urlencode(params)}"
            else:
                url = f"{self.base_url}/{symbol.upper()}"
            
            await self.rate_limiter.wait()
            return url
            
        except Exception as e:
            print(f"Error generating chart URL for {symbol}: {e}")
            # Return a fallback URL
            return f"{self.base_url}/{symbol.upper()}"
    
    async def get_technical_chart(self, symbol: str, timeframe: str = "daily") -> str:
        """Get chart with common technical indicators"""
        indicators = [
            'ema8', 'ema13', 'ema21', 'sma50', 'sma100', 'sma200', 'rsi', 'macd', 'bollinger_bands', 'volume'
        ]
        return await self.get_chart_image(
            symbol=symbol, 
            timeframe=timeframe, 
            indicators=indicators,
            width=1000,
            height=700
        )
    
    async def get_multiple_timeframes(self, symbol: str) -> Dict[str, str]:
        """Get charts for multiple timeframes"""
        timeframes = {
            "intraday_1h": "1h",
            "intraday_4h": "4h", 
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly"
        }
        
        charts = {}
        for name, timeframe in timeframes.items():
            try:
                charts[name] = await self.get_technical_chart(symbol, timeframe)
                await asyncio.sleep(0.1)  # Small delay between requests
            except Exception as e:
                print(f"Error getting {timeframe} chart for {symbol}: {e}")
                charts[name] = f"{self.base_url}/{symbol.upper()}"
        
        return charts
    
    async def get_pattern_analysis_chart(self, symbol: str) -> str:
        """Get chart optimized for pattern recognition"""
        indicators = [
            'support_resistance', 'trend_lines', 'volume', 'pattern_recognition'
        ]
        return await self.get_chart_image(
            symbol=symbol,
            timeframe="daily",
            indicators=indicators,
            width=1200,
            height=800
        )
    
    async def get_squeeze_analysis_chart(self, symbol: str) -> str:
        """Get chart optimized for short squeeze analysis"""
        indicators = [
            'volume', 'short_volume', 'bollinger_bands', 'rsi', 'macd'
        ]
        return await self.get_chart_image(
            symbol=symbol,
            timeframe="daily", 
            indicators=indicators,
            width=1000,
            height=700
        )
    
    async def get_social_sentiment_chart(self, symbol: str) -> str:
        """Get chart with social sentiment overlay if available"""
        indicators = [
            'price', 'volume', 'social_sentiment', 'mentions_volume'
        ]
        return await self.get_chart_image(
            symbol=symbol,
            timeframe="daily",
            indicators=indicators,
            width=1000,
            height=700
        )
    
    async def get_comprehensive_chart_package(self, symbol: str) -> Dict[str, str]:
        """Get a comprehensive package of charts for analysis"""
        try:
            # Run chart generation concurrently
            tasks = {
                "technical_daily": self.get_technical_chart(symbol, "daily"),
                "technical_weekly": self.get_technical_chart(symbol, "weekly"),
                "pattern_analysis": self.get_pattern_analysis_chart(symbol),
                "squeeze_analysis": self.get_squeeze_analysis_chart(symbol),
                "intraday_1h": self.get_technical_chart(symbol, "1h"),
                "social_sentiment": self.get_social_sentiment_chart(symbol)
            }
            
            # Execute all tasks concurrently
            results = {}
            for name, task in tasks.items():
                try:
                    results[name] = await task
                except Exception as e:
                    print(f"Error generating {name} chart for {symbol}: {e}")
                    results[name] = f"{self.base_url}/{symbol.upper()}"
                
                # Small delay to be respectful to the API
                await asyncio.sleep(0.2)
            
            return results
            
        except Exception as e:
            print(f"Error generating comprehensive charts for {symbol}: {e}")
            
            # Return basic charts as fallback
            return {
                "technical_daily": f"{self.base_url}/{symbol.upper()}",
                "technical_weekly": f"{self.base_url}/{symbol.upper()}",
                "pattern_analysis": f"{self.base_url}/{symbol.upper()}",
                "squeeze_analysis": f"{self.base_url}/{symbol.upper()}",
                "intraday_1h": f"{self.base_url}/{symbol.upper()}",
                "social_sentiment": f"{self.base_url}/{symbol.upper()}"
            }
    
    async def get_alert_chart(self, symbol: str, alert_type: str) -> str:
        """Get chart optimized for specific alert type"""
        chart_configs = {
            "short_squeeze": {
                "indicators": ['volume', 'short_interest', 'bollinger_bands', 'rsi'],
                "timeframe": "daily"
            },
            "momentum": {
                "indicators": ['sma20', 'sma50', 'volume', 'rsi', 'macd'],
                "timeframe": "daily"
            },
            "breakout": {
                "indicators": ['support_resistance', 'volume', 'bollinger_bands'],
                "timeframe": "daily"
            },
            "value": {
                "indicators": ['price', 'volume', 'sma200'],
                "timeframe": "weekly"
            },
            "divergence": {
                "indicators": ['rsi', 'macd', 'volume', 'price'],
                "timeframe": "daily"
            }
        }
        
        config = chart_configs.get(alert_type, {
            "indicators": ['sma20', 'sma50', 'volume', 'rsi'],
            "timeframe": "daily"
        })
        
        return await self.get_chart_image(
            symbol=symbol,
            timeframe=config["timeframe"],
            indicators=config["indicators"],
            width=1000,
            height=600
        )
    
    def get_tradingview_backup_url(self, symbol: str) -> str:
        """Get TradingView backup chart URL if chart-img.com fails"""
        return f"https://www.tradingview.com/chart/?symbol={symbol.upper()}"
    
    def get_yahoo_backup_url(self, symbol: str) -> str:
        """Get Yahoo Finance backup chart URL"""
        return f"https://finance.yahoo.com/chart/{symbol.upper()}"
    
    async def validate_chart_availability(self, symbol: str) -> Dict[str, bool]:
        """Check if charts are available for a symbol"""
        try:
            # Try to get a basic chart
            chart_url = await self.get_chart_image(symbol)
            
            # In a real implementation, you might want to make an HTTP request
            # to verify the chart actually exists
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.head(chart_url, timeout=5) as response:
                        chart_available = response.status == 200
                except:
                    chart_available = False
            
            return {
                "charts_available": chart_available,
                "chart_url": chart_url,
                "backup_tradingview": self.get_tradingview_backup_url(symbol),
                "backup_yahoo": self.get_yahoo_backup_url(symbol)
            }
            
        except Exception as e:
            print(f"Error validating chart availability for {symbol}: {e}")
            return {
                "charts_available": False,
                "chart_url": None,
                "backup_tradingview": self.get_tradingview_backup_url(symbol),
                "backup_yahoo": self.get_yahoo_backup_url(symbol)
            }