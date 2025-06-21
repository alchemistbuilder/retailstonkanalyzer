import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import ta
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator

from ..core.config import settings
from ..models.stock_data import TechnicalAnalysis, TrendDirection
from ..utils.rate_limiter import RateLimiter


class AlphaVantageCollector:
    def __init__(self):
        self.base_url = "https://www.alphavantage.co/query"
        self.api_key = settings.alpha_vantage_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=5)  # Alpha Vantage free tier
    
    async def get_daily_data(self, symbol: str, days: int = 100) -> Optional[pd.DataFrame]:
        """Get daily OHLCV data from Alpha Vantage"""
        try:
            params = {
                'function': 'TIME_SERIES_DAILY_ADJUSTED',
                'symbol': symbol,
                'apikey': self.api_key,
                'outputsize': 'compact'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'Time Series (Daily)' in data:
                            df = pd.DataFrame(data['Time Series (Daily)']).T
                            df.index = pd.to_datetime(df.index)
                            df = df.astype(float)
                            
                            # Rename columns
                            df.columns = ['open', 'high', 'low', 'close', 'adjusted_close', 'volume', 'dividend', 'split']
                            
                            # Sort by date and get recent data
                            df = df.sort_index(ascending=False).head(days)
                            df = df.sort_index()  # Sort chronologically for indicators
                            
                            await self.rate_limiter.wait()
                            return df
                        
        except Exception as e:
            print(f"Error fetching Alpha Vantage data for {symbol}: {e}")
        
        return None
    
    async def get_technical_indicators(self, symbol: str) -> Dict:
        """Get technical indicators from Alpha Vantage"""
        indicators = {}
        
        try:
            # RSI
            rsi_params = {
                'function': 'RSI',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 14,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=rsi_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'Technical Analysis: RSI' in data:
                            rsi_data = data['Technical Analysis: RSI']
                            latest_date = max(rsi_data.keys())
                            indicators['rsi'] = float(rsi_data[latest_date]['RSI'])
                
                await self.rate_limiter.wait()
                
                # MACD
                macd_params = {
                    'function': 'MACD',
                    'symbol': symbol,
                    'interval': 'daily',
                    'series_type': 'close',
                    'apikey': self.api_key
                }
                
                async with session.get(self.base_url, params=macd_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'Technical Analysis: MACD' in data:
                            macd_data = data['Technical Analysis: MACD']
                            latest_date = max(macd_data.keys())
                            macd_line = float(macd_data[latest_date]['MACD'])
                            signal_line = float(macd_data[latest_date]['MACD_Signal'])
                            
                            indicators['macd'] = {
                                'macd': macd_line,
                                'signal': signal_line,
                                'histogram': macd_line - signal_line,
                                'signal_direction': 'bullish' if macd_line > signal_line else 'bearish'
                            }
                
                await self.rate_limiter.wait()
                
        except Exception as e:
            print(f"Error fetching technical indicators for {symbol}: {e}")
        
        return indicators


class PolygonCollector:
    def __init__(self):
        self.base_url = "https://api.polygon.io"
        self.api_key = settings.polygon_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=5)  # Free tier limit
    
    async def get_daily_data(self, symbol: str, days: int = 100) -> Optional[pd.DataFrame]:
        """Get daily OHLCV data from Polygon"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
            params = {'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'results' in data and data['results']:
                            results = data['results']
                            
                            df = pd.DataFrame(results)
                            df['date'] = pd.to_datetime(df['t'], unit='ms')
                            df.set_index('date', inplace=True)
                            
                            # Rename columns to standard format
                            df.rename(columns={
                                'o': 'open',
                                'h': 'high',
                                'l': 'low',
                                'c': 'close',
                                'v': 'volume'
                            }, inplace=True)
                            
                            await self.rate_limiter.wait()
                            return df[['open', 'high', 'low', 'close', 'volume']]
                        
        except Exception as e:
            print(f"Error fetching Polygon data for {symbol}: {e}")
        
        return None
    
    async def get_real_time_data(self, symbol: str) -> Optional[Dict]:
        """Get real-time price data from Polygon"""
        try:
            url = f"{self.base_url}/v2/last/trade/{symbol}"
            params = {'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'results' in data:
                            result = data['results']
                            return {
                                'price': result.get('p'),
                                'size': result.get('s'),
                                'timestamp': datetime.fromtimestamp(result.get('t', 0) / 1000)
                            }
                        
        except Exception as e:
            print(f"Error fetching real-time data for {symbol}: {e}")
        
        return None


class TechnicalAnalyzer:
    def __init__(self):
        pass
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate various technical indicators"""
        if df is None or len(df) < 20:
            return {}
        
        indicators = {}
        
        try:
            # RSI
            rsi = RSIIndicator(df['close'])
            indicators['rsi'] = float(rsi.rsi().iloc[-1])
            
            # MACD
            macd = MACD(df['close'])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            
            indicators['macd'] = {
                'macd': float(macd_line),
                'signal': float(signal_line),
                'histogram': float(macd_line - signal_line),
                'signal_direction': 'bullish' if macd_line > signal_line else 'bearish'
            }
            
            # Bollinger Bands
            bollinger = BollingerBands(df['close'])
            bb_upper = bollinger.bollinger_hband().iloc[-1]
            bb_lower = bollinger.bollinger_lband().iloc[-1]
            bb_middle = bollinger.bollinger_mavg().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Bollinger position (0 = at lower band, 1 = at upper band)
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            indicators['bollinger_position'] = float(bb_position)
            
            # Moving Averages
            sma_20 = SMAIndicator(df['close'], window=20).sma_indicator().iloc[-1]
            sma_50 = SMAIndicator(df['close'], window=50).sma_indicator().iloc[-1]
            ema_12 = EMAIndicator(df['close'], window=12).ema_indicator().iloc[-1]
            ema_26 = EMAIndicator(df['close'], window=26).ema_indicator().iloc[-1]
            
            indicators['moving_averages'] = {
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'ema_12': float(ema_12),
                'ema_26': float(ema_26)
            }
            
            # Support and Resistance
            indicators['support_resistance'] = self._calculate_support_resistance(df)
            
            # Volume analysis
            indicators['volume_spike'] = self._detect_volume_spike(df)
            
            # Trend direction
            indicators['trend_direction'] = self._determine_trend(df, indicators)
            
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
        
        return indicators
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        try:
            # Use recent highs and lows
            recent_data = df.tail(20)
            
            # Resistance: recent highs
            resistance = float(recent_data['high'].max())
            
            # Support: recent lows
            support = float(recent_data['low'].min())
            
            return {
                'support': support,
                'resistance': resistance,
                'current_price': float(df['close'].iloc[-1])
            }
        except:
            return {'support': 0, 'resistance': 0, 'current_price': 0}
    
    def _detect_volume_spike(self, df: pd.DataFrame) -> bool:
        """Detect if current volume is significantly higher than average"""
        try:
            if len(df) < 20:
                return False
            
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].tail(20).mean()
            
            # Volume spike if current volume is 2x average
            return current_volume > (avg_volume * 2)
        except:
            return False
    
    def _determine_trend(self, df: pd.DataFrame, indicators: Dict) -> TrendDirection:
        """Determine overall trend direction"""
        try:
            current_price = df['close'].iloc[-1]
            ma_data = indicators.get('moving_averages', {})
            
            sma_20 = ma_data.get('sma_20', current_price)
            sma_50 = ma_data.get('sma_50', current_price)
            
            # Bullish: price above both MAs and 20 MA > 50 MA
            if current_price > sma_20 > sma_50:
                return TrendDirection.BULLISH
            # Bearish: price below both MAs and 20 MA < 50 MA
            elif current_price < sma_20 < sma_50:
                return TrendDirection.BEARISH
            else:
                return TrendDirection.NEUTRAL
                
        except:
            return TrendDirection.NEUTRAL


class PatternDetector:
    def __init__(self):
        pass
    
    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, float]:
        """Detect chart patterns and return confidence scores"""
        if df is None or len(df) < 20:
            return {'pattern': None, 'confidence': 0.0}
        
        patterns = {}
        
        try:
            # Double bottom pattern
            patterns['double_bottom'] = self._detect_double_bottom(df)
            
            # Double top pattern
            patterns['double_top'] = self._detect_double_top(df)
            
            # Breakout pattern
            patterns['breakout'] = self._detect_breakout(df)
            
            # Cup and handle
            patterns['cup_and_handle'] = self._detect_cup_and_handle(df)
            
            # Find the pattern with highest confidence
            best_pattern = max(patterns.items(), key=lambda x: x[1])
            
            return {
                'pattern': best_pattern[0] if best_pattern[1] > 0.6 else None,
                'confidence': best_pattern[1],
                'all_patterns': patterns
            }
            
        except Exception as e:
            print(f"Error detecting patterns: {e}")
            return {'pattern': None, 'confidence': 0.0}
    
    def _detect_double_bottom(self, df: pd.DataFrame) -> float:
        """Detect double bottom pattern"""
        # Simplified double bottom detection
        try:
            recent_data = df.tail(40)
            lows = recent_data['low']
            
            # Find two significant lows
            min_idx = lows.idxmin()
            
            # Look for another low before and after
            before_low = lows.loc[:min_idx].min() if len(lows.loc[:min_idx]) > 5 else float('inf')
            after_low = lows.loc[min_idx:].min() if len(lows.loc[min_idx:]) > 5 else float('inf')
            
            current_low = lows.min()
            
            # Check if we have two similar lows
            if abs(before_low - current_low) / current_low < 0.02:  # Within 2%
                return 0.7
            elif abs(after_low - current_low) / current_low < 0.02:
                return 0.7
            
            return 0.0
        except:
            return 0.0
    
    def _detect_double_top(self, df: pd.DataFrame) -> float:
        """Detect double top pattern"""
        try:
            recent_data = df.tail(40)
            highs = recent_data['high']
            
            max_idx = highs.idxmax()
            
            before_high = highs.loc[:max_idx].max() if len(highs.loc[:max_idx]) > 5 else 0
            after_high = highs.loc[max_idx:].max() if len(highs.loc[max_idx:]) > 5 else 0
            
            current_high = highs.max()
            
            if abs(before_high - current_high) / current_high < 0.02:
                return 0.7
            elif abs(after_high - current_high) / current_high < 0.02:
                return 0.7
            
            return 0.0
        except:
            return 0.0
    
    def _detect_breakout(self, df: pd.DataFrame) -> float:
        """Detect breakout pattern"""
        try:
            recent_data = df.tail(20)
            current_price = df['close'].iloc[-1]
            
            # Check if price is breaking resistance
            resistance = recent_data['high'].max()
            
            if current_price > resistance * 1.02:  # 2% above resistance
                return 0.8
            
            return 0.0
        except:
            return 0.0
    
    def _detect_cup_and_handle(self, df: pd.DataFrame) -> float:
        """Detect cup and handle pattern"""
        # Simplified cup and handle detection
        try:
            if len(df) < 50:
                return 0.0
            
            data = df.tail(50)
            prices = data['close']
            
            # Look for U-shape (cup) followed by small decline (handle)
            first_third = prices.iloc[:17]
            middle_third = prices.iloc[17:34]
            last_third = prices.iloc[34:]
            
            # Cup: high -> low -> high
            if (first_third.iloc[-1] > first_third.iloc[0] and 
                middle_third.min() < first_third.iloc[0] * 0.85 and
                last_third.iloc[-1] > middle_third.min() * 1.1):
                return 0.6
            
            return 0.0
        except:
            return 0.0


class TechnicalDataCollector:
    def __init__(self):
        self.alpha_vantage = AlphaVantageCollector()
        self.polygon = PolygonCollector()
        self.analyzer = TechnicalAnalyzer()
        self.pattern_detector = PatternDetector()
        # Import chart collector here to avoid circular imports
        from .chart_image_collector import ChartImageCollector
        self.chart_collector = ChartImageCollector()
    
    async def collect_technical_analysis(self, symbol: str) -> TechnicalAnalysis:
        """Collect comprehensive technical analysis for a symbol"""
        try:
            # Try Polygon first, fallback to Alpha Vantage
            df = await self.polygon.get_daily_data(symbol)
            if df is None:
                df = await self.alpha_vantage.get_daily_data(symbol)
            
            if df is None or len(df) == 0:
                raise Exception(f"No price data available for {symbol}")
            
            # Calculate technical indicators
            indicators = self.analyzer.calculate_technical_indicators(df)
            
            # Detect patterns
            pattern_data = self.pattern_detector.detect_patterns(df)
            
            # Get current price and volume
            current_price = float(df['close'].iloc[-1])
            current_volume = int(df['volume'].iloc[-1])
            
            # Generate chart images
            chart_images = await self.chart_collector.get_comprehensive_chart_package(symbol)
            
            # Build technical analysis object
            return TechnicalAnalysis(
                price=current_price,
                volume=current_volume,
                rsi=indicators.get('rsi', 50.0),
                macd_signal=indicators.get('macd', {}).get('signal_direction', 'neutral'),
                bollinger_position=indicators.get('bollinger_position', 0.5),
                moving_averages=indicators.get('moving_averages', {}),
                support_resistance=indicators.get('support_resistance', {}),
                pattern_detected=pattern_data.get('pattern'),
                pattern_confidence=pattern_data.get('confidence', 0.0),
                trend_direction=indicators.get('trend_direction', TrendDirection.NEUTRAL),
                volume_spike=indicators.get('volume_spike', False),
                timestamp=datetime.now(),
                chart_images=chart_images
            )
            
        except Exception as e:
            print(f"Error collecting technical analysis for {symbol}: {e}")
            
            # Return default technical analysis
            return TechnicalAnalysis(
                price=0.0,
                volume=0,
                rsi=50.0,
                macd_signal='neutral',
                bollinger_position=0.5,
                moving_averages={},
                support_resistance={},
                pattern_detected=None,
                pattern_confidence=0.0,
                trend_direction=TrendDirection.NEUTRAL,
                volume_spike=False,
                timestamp=datetime.now(),
                chart_images={}
            )