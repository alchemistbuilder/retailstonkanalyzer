import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Optional

from ..core.config import settings
from ..models.stock_data import FundamentalData
from ..utils.rate_limiter import RateLimiter


class FinancialModelingPrepCollector:
    def __init__(self):
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.api_key = settings.fmp_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=250)  # FMP free tier
    
    async def get_company_profile(self, symbol: str) -> Dict:
        """Get company profile data"""
        try:
            url = f"{self.base_url}/profile/{symbol}"
            params = {'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            await self.rate_limiter.wait()
                            return data[0]
        except Exception as e:
            print(f"Error fetching company profile for {symbol}: {e}")
        
        return {}
    
    async def get_key_metrics(self, symbol: str) -> Dict:
        """Get key financial metrics"""
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
            print(f"Error fetching key metrics for {symbol}: {e}")
        
        return {}
    
    async def get_financial_ratios(self, symbol: str) -> Dict:
        """Get financial ratios"""
        try:
            url = f"{self.base_url}/ratios/{symbol}"
            params = {'apikey': self.api_key, 'limit': 1}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            await self.rate_limiter.wait()
                            return data[0]
        except Exception as e:
            print(f"Error fetching financial ratios for {symbol}: {e}")
        
        return {}
    
    async def get_income_statement(self, symbol: str) -> Dict:
        """Get latest income statement"""
        try:
            url = f"{self.base_url}/income-statement/{symbol}"
            params = {'apikey': self.api_key, 'limit': 1}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            await self.rate_limiter.wait()
                            return data[0]
        except Exception as e:
            print(f"Error fetching income statement for {symbol}: {e}")
        
        return {}
    
    async def get_balance_sheet(self, symbol: str) -> Dict:
        """Get latest balance sheet"""
        try:
            url = f"{self.base_url}/balance-sheet-statement/{symbol}"
            params = {'apikey': self.api_key, 'limit': 1}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            await self.rate_limiter.wait()
                            return data[0]
        except Exception as e:
            print(f"Error fetching balance sheet for {symbol}: {e}")
        
        return {}
    
    async def get_cash_flow(self, symbol: str) -> Dict:
        """Get latest cash flow statement"""
        try:
            url = f"{self.base_url}/cash-flow-statement/{symbol}"
            params = {'apikey': self.api_key, 'limit': 1}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            await self.rate_limiter.wait()
                            return data[0]
        except Exception as e:
            print(f"Error fetching cash flow for {symbol}: {e}")
        
        return {}


class AlphaVantageFundamentalCollector:
    def __init__(self):
        self.base_url = "https://www.alphavantage.co/query"
        self.api_key = settings.alpha_vantage_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=5)
    
    async def get_company_overview(self, symbol: str) -> Dict:
        """Get company overview from Alpha Vantage"""
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


class FinnhubFundamentalCollector:
    def __init__(self):
        self.base_url = "https://finnhub.io/api/v1"
        self.api_key = settings.finnhub_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def get_company_profile(self, symbol: str) -> Dict:
        """Get company profile from Finnhub"""
        try:
            url = f"{self.base_url}/stock/profile2"
            params = {'symbol': symbol, 'token': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching Finnhub profile for {symbol}: {e}")
        
        return {}
    
    async def get_basic_financials(self, symbol: str) -> Dict:
        """Get basic financial metrics from Finnhub"""
        try:
            url = f"{self.base_url}/stock/metric"
            params = {'symbol': symbol, 'metric': 'all', 'token': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching Finnhub financials for {symbol}: {e}")
        
        return {}


class FundamentalAnalyzer:
    def __init__(self):
        pass
    
    def calculate_valuation_metrics(self, profile: Dict, metrics: Dict, ratios: Dict) -> Dict:
        """Calculate valuation metrics and scores"""
        valuation = {}
        
        try:
            # Market cap
            market_cap = profile.get('mktCap') or metrics.get('marketCapitalizationTTM')
            if market_cap:
                valuation['market_cap'] = float(market_cap)
            
            # P/E ratio
            pe_ratio = ratios.get('priceEarningsRatio') or metrics.get('peRatioTTM')
            if pe_ratio and pe_ratio != 0:
                valuation['pe_ratio'] = float(pe_ratio)
                valuation['pe_score'] = self._score_pe_ratio(pe_ratio)
            
            # P/S ratio
            ps_ratio = ratios.get('priceToSalesRatio') or metrics.get('priceToSalesRatioTTM')
            if ps_ratio and ps_ratio != 0:
                valuation['ps_ratio'] = float(ps_ratio)
                valuation['ps_score'] = self._score_ps_ratio(ps_ratio)
            
            # P/B ratio
            pb_ratio = ratios.get('priceToBookRatio') or metrics.get('pbRatioTTM')
            if pb_ratio and pb_ratio != 0:
                valuation['pb_ratio'] = float(pb_ratio)
                valuation['pb_score'] = self._score_pb_ratio(pb_ratio)
            
            # Calculate composite valuation score
            scores = [
                valuation.get('pe_score', 5),
                valuation.get('ps_score', 5),
                valuation.get('pb_score', 5)
            ]
            valuation['composite_score'] = sum(scores) / len(scores)
            
        except Exception as e:
            print(f"Error calculating valuation metrics: {e}")
        
        return valuation
    
    def _score_pe_ratio(self, pe_ratio: float) -> float:
        """Score P/E ratio (1-10, higher is better)"""
        if pe_ratio < 0:
            return 1  # Negative earnings
        elif pe_ratio < 15:
            return 9  # Very attractive
        elif pe_ratio < 25:
            return 7  # Reasonable
        elif pe_ratio < 40:
            return 5  # Fair
        elif pe_ratio < 60:
            return 3  # Expensive
        else:
            return 1  # Very expensive
    
    def _score_ps_ratio(self, ps_ratio: float) -> float:
        """Score P/S ratio (1-10, higher is better)"""
        if ps_ratio < 2:
            return 9  # Very attractive
        elif ps_ratio < 5:
            return 7  # Reasonable
        elif ps_ratio < 10:
            return 5  # Fair
        elif ps_ratio < 20:
            return 3  # Expensive
        else:
            return 1  # Very expensive
    
    def _score_pb_ratio(self, pb_ratio: float) -> float:
        """Score P/B ratio (1-10, higher is better)"""
        if pb_ratio < 1:
            return 9  # Trading below book value
        elif pb_ratio < 2:
            return 7  # Reasonable
        elif pb_ratio < 3:
            return 5  # Fair
        elif pb_ratio < 5:
            return 3  # Expensive
        else:
            return 1  # Very expensive
    
    def calculate_growth_metrics(self, income: Dict, metrics: Dict) -> Dict:
        """Calculate growth metrics"""
        growth = {}
        
        try:
            # Revenue growth
            revenue_growth = metrics.get('revenueGrowthTTM')
            if revenue_growth:
                growth['revenue_growth_yoy'] = float(revenue_growth) * 100
                growth['revenue_growth_score'] = self._score_growth(revenue_growth * 100)
            
            # Earnings growth
            earnings_growth = metrics.get('epsgrowthTTM')
            if earnings_growth:
                growth['earnings_growth_yoy'] = float(earnings_growth) * 100
                growth['earnings_growth_score'] = self._score_growth(earnings_growth * 100)
            
            # Calculate composite growth score
            growth_scores = []
            if 'revenue_growth_score' in growth:
                growth_scores.append(growth['revenue_growth_score'])
            if 'earnings_growth_score' in growth:
                growth_scores.append(growth['earnings_growth_score'])
            
            if growth_scores:
                growth['composite_growth_score'] = sum(growth_scores) / len(growth_scores)
            
        except Exception as e:
            print(f"Error calculating growth metrics: {e}")
        
        return growth
    
    def _score_growth(self, growth_rate: float) -> float:
        """Score growth rate (1-10, higher is better)"""
        if growth_rate > 50:
            return 10  # Exceptional growth
        elif growth_rate > 25:
            return 8   # High growth
        elif growth_rate > 15:
            return 6   # Good growth
        elif growth_rate > 5:
            return 5   # Modest growth
        elif growth_rate > 0:
            return 3   # Slow growth
        else:
            return 1   # Declining
    
    def calculate_financial_health(self, balance: Dict, ratios: Dict) -> Dict:
        """Calculate financial health metrics"""
        health = {}
        
        try:
            # Debt to equity
            debt_to_equity = ratios.get('debtEquityRatio')
            if debt_to_equity:
                health['debt_to_equity'] = float(debt_to_equity)
                health['debt_score'] = self._score_debt_ratio(debt_to_equity)
            
            # Current ratio
            current_ratio = ratios.get('currentRatio')
            if current_ratio:
                health['current_ratio'] = float(current_ratio)
                health['liquidity_score'] = self._score_current_ratio(current_ratio)
            
            # ROE
            roe = ratios.get('returnOnEquityTTM')
            if roe:
                health['roe'] = float(roe) * 100
                health['roe_score'] = self._score_roe(roe * 100)
            
            # Profit margin
            profit_margin = ratios.get('netProfitMarginTTM')
            if profit_margin:
                health['profit_margin'] = float(profit_margin) * 100
                health['margin_score'] = self._score_profit_margin(profit_margin * 100)
            
            # Calculate composite health score
            health_scores = []
            for score_key in ['debt_score', 'liquidity_score', 'roe_score', 'margin_score']:
                if score_key in health:
                    health_scores.append(health[score_key])
            
            if health_scores:
                health['composite_health_score'] = sum(health_scores) / len(health_scores)
            
        except Exception as e:
            print(f"Error calculating financial health: {e}")
        
        return health
    
    def _score_debt_ratio(self, debt_ratio: float) -> float:
        """Score debt to equity ratio (1-10, higher is better)"""
        if debt_ratio < 0.3:
            return 9   # Very low debt
        elif debt_ratio < 0.6:
            return 7   # Reasonable debt
        elif debt_ratio < 1.0:
            return 5   # Moderate debt
        elif debt_ratio < 2.0:
            return 3   # High debt
        else:
            return 1   # Very high debt
    
    def _score_current_ratio(self, current_ratio: float) -> float:
        """Score current ratio (1-10, higher is better)"""
        if current_ratio > 2.5:
            return 9   # Excellent liquidity
        elif current_ratio > 1.5:
            return 7   # Good liquidity
        elif current_ratio > 1.0:
            return 5   # Adequate liquidity
        elif current_ratio > 0.5:
            return 3   # Poor liquidity
        else:
            return 1   # Very poor liquidity
    
    def _score_roe(self, roe: float) -> float:
        """Score return on equity (1-10, higher is better)"""
        if roe > 20:
            return 10  # Excellent returns
        elif roe > 15:
            return 8   # Very good returns
        elif roe > 10:
            return 6   # Good returns
        elif roe > 5:
            return 4   # Modest returns
        elif roe > 0:
            return 2   # Poor returns
        else:
            return 1   # Negative returns
    
    def _score_profit_margin(self, margin: float) -> float:
        """Score profit margin (1-10, higher is better)"""
        if margin > 20:
            return 10  # Excellent margins
        elif margin > 15:
            return 8   # Very good margins
        elif margin > 10:
            return 6   # Good margins
        elif margin > 5:
            return 4   # Modest margins
        elif margin > 0:
            return 2   # Poor margins
        else:
            return 1   # Negative margins


class FundamentalDataCollector:
    def __init__(self):
        self.fmp = FinancialModelingPrepCollector()
        self.alpha_vantage = AlphaVantageFundamentalCollector()
        self.finnhub = FinnhubFundamentalCollector()
        self.analyzer = FundamentalAnalyzer()
    
    async def collect_fundamental_data(self, symbol: str) -> FundamentalData:
        """Collect comprehensive fundamental data for a symbol"""
        try:
            # Collect data from multiple sources concurrently
            tasks = [
                self.fmp.get_company_profile(symbol),
                self.fmp.get_key_metrics(symbol),
                self.fmp.get_financial_ratios(symbol),
                self.fmp.get_income_statement(symbol),
                self.fmp.get_balance_sheet(symbol),
                self.fmp.get_cash_flow(symbol)
            ]
            
            profile, metrics, ratios, income, balance, cash_flow = await asyncio.gather(*tasks)
            
            # Calculate various metrics
            valuation = self.analyzer.calculate_valuation_metrics(profile, metrics, ratios)
            growth = self.analyzer.calculate_growth_metrics(income, metrics)
            health = self.analyzer.calculate_financial_health(balance, ratios)
            
            # Extract key values
            market_cap = valuation.get('market_cap', 0)
            pe_ratio = valuation.get('pe_ratio')
            ps_ratio = valuation.get('ps_ratio')
            revenue_growth = growth.get('revenue_growth_yoy')
            profit_margin = health.get('profit_margin')
            debt_to_equity = health.get('debt_to_equity')
            current_ratio = health.get('current_ratio')
            roe = health.get('roe')
            
            # Free cash flow
            free_cash_flow = cash_flow.get('freeCashFlow')
            
            # Enterprise value
            enterprise_value = metrics.get('enterpriseValueTTM')
            
            # Book value
            book_value = balance.get('totalStockholdersEquity')
            
            return FundamentalData(
                market_cap=market_cap,
                pe_ratio=pe_ratio,
                ps_ratio=ps_ratio,
                revenue_growth_yoy=revenue_growth,
                profit_margin=profit_margin,
                debt_to_equity=debt_to_equity,
                current_ratio=current_ratio,
                roe=roe,
                free_cash_flow=free_cash_flow,
                enterprise_value=enterprise_value,
                book_value=book_value,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error collecting fundamental data for {symbol}: {e}")
            
            # Return default fundamental data
            return FundamentalData(
                market_cap=0.0,
                pe_ratio=None,
                ps_ratio=None,
                revenue_growth_yoy=None,
                profit_margin=None,
                debt_to_equity=None,
                current_ratio=None,
                roe=None,
                free_cash_flow=None,
                enterprise_value=None,
                book_value=None,
                timestamp=datetime.now()
            )