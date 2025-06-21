import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Optional

from ..core.config import settings
from ..models.stock_data import StockStructure
from ..utils.rate_limiter import RateLimiter


class ORTEXCollector:
    def __init__(self):
        self.base_url = "https://api.ortex.com/v1"
        self.api_key = settings.ortex_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def get_short_interest_data(self, symbol: str) -> Dict:
        """Get short interest data from ORTEX"""
        try:
            url = f"{self.base_url}/securities/{symbol}/short-interest"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
                    elif response.status == 401:
                        print("ORTEX API key invalid or expired")
                    elif response.status == 403:
                        print("ORTEX API access forbidden - check subscription")
                    
        except Exception as e:
            print(f"Error fetching ORTEX short interest for {symbol}: {e}")
        
        return {}
    
    async def get_utilization_data(self, symbol: str) -> Dict:
        """Get utilization rate data from ORTEX"""
        try:
            url = f"{self.base_url}/securities/{symbol}/utilization"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
                    
        except Exception as e:
            print(f"Error fetching ORTEX utilization for {symbol}: {e}")
        
        return {}
    
    async def get_cost_to_borrow(self, symbol: str) -> Dict:
        """Get cost to borrow data from ORTEX"""
        try:
            url = f"{self.base_url}/securities/{symbol}/cost-to-borrow"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
                    
        except Exception as e:
            print(f"Error fetching ORTEX cost to borrow for {symbol}: {e}")
        
        return {}


class FinancialModelingPrepStructureCollector:
    def __init__(self):
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.api_key = settings.fmp_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=250)
    
    async def get_key_metrics(self, symbol: str) -> Dict:
        """Get key metrics including shares outstanding"""
        try:
            url = f"{self.base_url}/key-metrics/{symbol}"
            params = {'apikey': self.api_key, 'limit': 1}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            await self.rate_limiter.wait()
                            return data[0]
        except Exception as e:
            print(f"Error fetching FMP key metrics for {symbol}: {e}")
        
        return {}
    
    async def get_institutional_ownership(self, symbol: str) -> Dict:
        """Get institutional ownership data"""
        try:
            url = f"{self.base_url}/institutional-holder/{symbol}"
            params = {'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching institutional ownership for {symbol}: {e}")
        
        return []
    
    async def get_insider_trading(self, symbol: str) -> Dict:
        """Get insider trading data"""
        try:
            url = f"{self.base_url}/insider-trading"
            params = {'symbol': symbol, 'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching insider trading for {symbol}: {e}")
        
        return []


class AlphaVantageStructureCollector:
    def __init__(self):
        self.base_url = "https://www.alphavantage.co/query"
        self.api_key = settings.alpha_vantage_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=5)
    
    async def get_company_overview(self, symbol: str) -> Dict:
        """Get company overview with shares outstanding"""
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching Alpha Vantage overview for {symbol}: {e}")
        
        return {}


class YahooFinanceStructureCollector:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def get_key_statistics(self, symbol: str) -> Dict:
        """Get key statistics from Yahoo Finance (fallback)"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            await self.rate_limiter.wait()
            return info
            
        except Exception as e:
            print(f"Error fetching Yahoo Finance data for {symbol}: {e}")
        
        return {}


class StockStructureAnalyzer:
    def __init__(self):
        pass
    
    def calculate_short_squeeze_score(self, 
                                    short_interest: float, 
                                    utilization: float, 
                                    cost_to_borrow: float, 
                                    days_to_cover: float) -> float:
        """Calculate short squeeze potential score (0-100)"""
        score = 0.0
        
        try:
            # Short interest component (0-40 points)
            if short_interest > 30:
                score += 40
            elif short_interest > 20:
                score += 30
            elif short_interest > 15:
                score += 20
            elif short_interest > 10:
                score += 10
            
            # Utilization component (0-25 points)
            if utilization > 90:
                score += 25
            elif utilization > 80:
                score += 20
            elif utilization > 70:
                score += 15
            elif utilization > 60:
                score += 10
            
            # Cost to borrow component (0-20 points)
            if cost_to_borrow > 50:
                score += 20
            elif cost_to_borrow > 25:
                score += 15
            elif cost_to_borrow > 10:
                score += 10
            elif cost_to_borrow > 5:
                score += 5
            
            # Days to cover component (0-15 points)
            if days_to_cover > 10:
                score += 15
            elif days_to_cover > 5:
                score += 10
            elif days_to_cover > 3:
                score += 5
            
        except Exception as e:
            print(f"Error calculating short squeeze score: {e}")
        
        return min(score, 100.0)
    
    def calculate_institutional_ownership(self, institutional_data: list) -> float:
        """Calculate total institutional ownership percentage"""
        try:
            if not institutional_data:
                return 0.0
            
            total_shares_held = 0
            shares_outstanding = 0
            
            for holder in institutional_data:
                shares = holder.get('sharesHeld') or holder.get('shares', 0)
                if shares:
                    total_shares_held += shares
                
                # Try to get shares outstanding from the data
                if not shares_outstanding:
                    shares_outstanding = holder.get('sharesOutstanding', 0)
            
            if shares_outstanding > 0:
                return (total_shares_held / shares_outstanding) * 100
            
        except Exception as e:
            print(f"Error calculating institutional ownership: {e}")
        
        return 0.0
    
    def calculate_insider_ownership(self, insider_data: list, shares_outstanding: float) -> float:
        """Calculate insider ownership percentage"""
        try:
            if not insider_data or not shares_outstanding:
                return 0.0
            
            total_insider_shares = 0
            
            for trade in insider_data:
                # Look for beneficial ownership data
                shares = trade.get('sharesOwned') or trade.get('beneficialOwnership', 0)
                if shares:
                    total_insider_shares += shares
            
            if total_insider_shares > 0:
                return (total_insider_shares / shares_outstanding) * 100
            
        except Exception as e:
            print(f"Error calculating insider ownership: {e}")
        
        return 0.0
    
    def calculate_float(self, shares_outstanding: float, 
                       institutional_ownership_pct: float, 
                       insider_ownership_pct: float) -> float:
        """Calculate free float shares"""
        try:
            if shares_outstanding <= 0:
                return 0.0
            
            # Float = Outstanding - (Institutional + Insider holdings)
            restricted_pct = institutional_ownership_pct + insider_ownership_pct
            float_pct = max(0, 100 - restricted_pct)
            
            return shares_outstanding * (float_pct / 100)
            
        except Exception as e:
            print(f"Error calculating float: {e}")
            return shares_outstanding * 0.5  # Estimate 50% float


class StockStructureCollector:
    def __init__(self):
        self.ortex = ORTEXCollector()
        self.fmp = FinancialModelingPrepStructureCollector()
        self.alpha_vantage = AlphaVantageStructureCollector()
        self.yahoo = YahooFinanceStructureCollector()
        self.analyzer = StockStructureAnalyzer()
    
    async def collect_stock_structure(self, symbol: str) -> StockStructure:
        """Collect comprehensive stock structure data"""
        try:
            # Collect data from multiple sources concurrently
            tasks = [
                self.fmp.get_key_metrics(symbol),
                self.fmp.get_institutional_ownership(symbol),
                self.fmp.get_insider_trading(symbol),
                self.alpha_vantage.get_company_overview(symbol),
                self.ortex.get_short_interest_data(symbol),
                self.ortex.get_utilization_data(symbol),
                self.ortex.get_cost_to_borrow(symbol)
            ]
            
            (fmp_metrics, institutional_data, insider_data, 
             av_overview, short_data, utilization_data, ctb_data) = await asyncio.gather(*tasks)
            
            # Extract shares outstanding (try multiple sources)
            shares_outstanding = 0.0
            sources = [
                fmp_metrics.get('numberOfShares'),
                av_overview.get('SharesOutstanding'),
                short_data.get('sharesOutstanding')
            ]
            
            for shares in sources:
                if shares and shares > 0:
                    shares_outstanding = float(shares)
                    break
            
            # If still no data, try Yahoo Finance as fallback
            if shares_outstanding == 0:
                yahoo_data = await self.yahoo.get_key_statistics(symbol)
                shares_outstanding = float(yahoo_data.get('sharesOutstanding', 0))
            
            # Extract short interest data
            short_interest_pct = 0.0
            short_ratio = 0.0
            cost_to_borrow = 0.0
            utilization_rate = 0.0
            days_to_cover = 0.0
            
            if short_data:
                short_interest_pct = float(short_data.get('shortInterestPercent', 0))
                short_ratio = float(short_data.get('shortRatio', 0))
                days_to_cover = float(short_data.get('daysToCover', 0))
            
            if ctb_data:
                cost_to_borrow = float(ctb_data.get('costToBorrow', 0))
            
            if utilization_data:
                utilization_rate = float(utilization_data.get('utilization', 0))
            
            # Calculate ownership percentages
            institutional_ownership = self.analyzer.calculate_institutional_ownership(institutional_data)
            insider_ownership = self.analyzer.calculate_insider_ownership(insider_data, shares_outstanding)
            
            # Calculate float
            float_shares = self.analyzer.calculate_float(
                shares_outstanding, institutional_ownership, insider_ownership
            )
            
            # Calculate short squeeze score
            short_squeeze_score = self.analyzer.calculate_short_squeeze_score(
                short_interest_pct, utilization_rate, cost_to_borrow, days_to_cover
            )
            
            return StockStructure(
                shares_outstanding=shares_outstanding,
                float_shares=float_shares,
                short_interest=short_interest_pct,
                short_ratio=short_ratio,
                cost_to_borrow=cost_to_borrow if cost_to_borrow > 0 else None,
                utilization_rate=utilization_rate if utilization_rate > 0 else None,
                institutional_ownership=institutional_ownership,
                insider_ownership=insider_ownership,
                days_to_cover=days_to_cover if days_to_cover > 0 else None,
                short_squeeze_score=short_squeeze_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error collecting stock structure for {symbol}: {e}")
            
            # Return default stock structure
            return StockStructure(
                shares_outstanding=0.0,
                float_shares=0.0,
                short_interest=0.0,
                short_ratio=0.0,
                cost_to_borrow=None,
                utilization_rate=None,
                institutional_ownership=0.0,
                insider_ownership=0.0,
                days_to_cover=None,
                short_squeeze_score=0.0,
                timestamp=datetime.now()
            )