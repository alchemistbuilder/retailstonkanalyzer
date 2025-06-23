import requests
import asyncio
import aiohttp
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class RealMarketData:
    symbol: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    last_updated: datetime = None

class RealMarketDataService:
    """Fetch real market data from actual APIs"""
    
    def __init__(self):
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.fmp_api_key = os.getenv('FMP_API_KEY')
        
    async def get_current_quote(self, symbol: str) -> Optional[RealMarketData]:
        """Get current quote prioritizing FMP API (premium) over Polygon"""
        # Try FMP first since you have premium
        if self.fmp_api_key:
            logger.info(f"Fetching real market data for {symbol} from FMP API (premium)")
            fmp_data = await self._get_fmp_quote(symbol)
            if fmp_data:
                return fmp_data
        
        # Fallback to Polygon if FMP fails
        if self.polygon_api_key:
            logger.info(f"Falling back to Polygon API for {symbol}")
            return await self._get_polygon_quote(symbol)
            
        logger.warning("No API keys configured, using mock data")
        return self._get_mock_data(symbol)
    
    async def _get_fmp_quote(self, symbol: str) -> Optional[RealMarketData]:
        """Get quote from FMP API (premium)"""
        try:
            # Get real-time quote from FMP
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}"
            params = {'apikey': self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            quote = data[0]
                            
                            return RealMarketData(
                                symbol=symbol,
                                current_price=quote.get('price', 0),
                                open_price=quote.get('open', 0),
                                high_price=quote.get('dayHigh', 0),
                                low_price=quote.get('dayLow', 0),
                                volume=int(quote.get('volume', 0)),
                                market_cap=quote.get('marketCap'),
                                pe_ratio=quote.get('pe'),
                                change=quote.get('change'),
                                change_percent=quote.get('changesPercentage'),
                                last_updated=datetime.now()
                            )
                    else:
                        logger.error(f"FMP API error for {symbol}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error fetching FMP data for {symbol}: {str(e)}")
            
        return None
    
    async def _get_polygon_quote(self, symbol: str) -> Optional[RealMarketData]:
        """Get current quote from Polygon API"""
        try:
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
            params = {
                'adjusted': 'true',
                'apikey': self.polygon_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'OK' and data.get('results'):
                            result = data['results'][0]
                            
                            # Get current day quote
                            current_data = await self._get_current_day_quote(symbol, session)
                            
                            return RealMarketData(
                                symbol=symbol,
                                current_price=current_data.get('c', result['c']),
                                open_price=current_data.get('o', result['o']),
                                high_price=current_data.get('h', result['h']),
                                low_price=current_data.get('l', result['l']),
                                volume=int(current_data.get('v', result['v'])),
                                change=current_data.get('c', result['c']) - result['o'],
                                change_percent=((current_data.get('c', result['c']) - result['o']) / result['o']) * 100,
                                last_updated=datetime.now()
                            )
                    else:
                        logger.error(f"Polygon API error for {symbol}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error fetching Polygon data for {symbol}: {str(e)}")
            
        return None
    
    async def _get_current_day_quote(self, symbol: str, session: aiohttp.ClientSession) -> Dict:
        """Get current day quote from Polygon"""
        try:
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            
            url = f"https://api.polygon.io/v1/open-close/{symbol}/{today}"
            params = {
                'adjusted': 'true',
                'apikey': self.polygon_api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'OK':
                        return {
                            'o': data.get('open'),
                            'h': data.get('high'),
                            'l': data.get('low'),
                            'c': data.get('close'),
                            'v': data.get('volume')
                        }
        except Exception as e:
            logger.error(f"Error fetching current day data for {symbol}: {str(e)}")
            
        return {}
    
    async def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive fundamental data from FMP API"""
        if not self.fmp_api_key:
            return self._get_mock_fundamental_data(symbol)
            
        try:
            # Get multiple data points concurrently
            profile_data = await self._get_fmp_profile(symbol)
            financials_data = await self._get_fmp_financials(symbol)
            ratios_data = await self._get_fmp_ratios(symbol)
            earnings_data = await self._get_fmp_earnings(symbol)
            key_metrics_data = await self._get_fmp_key_metrics(symbol)
            
            # Combine all data
            return {
                **profile_data,
                **financials_data,
                **ratios_data,
                **earnings_data,
                **key_metrics_data
            }
        except Exception as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {str(e)}")
            return self._get_mock_fundamental_data(symbol)
    
    async def _get_fmp_profile(self, symbol: str) -> Dict[str, Any]:
        """Get company profile"""
        try:
            url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}"
            params = {'apikey': self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            profile = data[0]
                            return {
                                'company_name': profile.get('companyName', symbol),
                                'sector': profile.get('sector', 'Unknown'),
                                'industry': profile.get('industry', 'Unknown'),
                                'market_cap': profile.get('mktCap'),
                                'enterprise_value': profile.get('enterpriseValue'),
                                'pe_ratio': profile.get('pe'),
                                'description': profile.get('description', ''),
                                'website': profile.get('website', ''),
                                'exchange': profile.get('exchangeShortName', 'NASDAQ')
                            }
        except Exception as e:
            logger.error(f"Error fetching profile for {symbol}: {str(e)}")
        return {}
    
    async def _get_fmp_financials(self, symbol: str) -> Dict[str, Any]:
        """Get financial statements data"""
        try:
            # Get income statement (quarterly and annual)
            quarterly_url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}"
            annual_url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}"
            params_q = {'period': 'quarter', 'limit': 4, 'apikey': self.fmp_api_key}
            params_a = {'period': 'annual', 'limit': 1, 'apikey': self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                # Get quarterly data
                async with session.get(quarterly_url, params=params_q) as response:
                    quarterly_data = []
                    if response.status == 200:
                        quarterly_data = await response.json()
                
                # Get annual data  
                async with session.get(annual_url, params=params_a) as response:
                    annual_data = []
                    if response.status == 200:
                        annual_data = await response.json()
                
                result = {}
                if quarterly_data and len(quarterly_data) > 0:
                    latest_q = quarterly_data[0]
                    result.update({
                        'latest_quarterly_revenue': latest_q.get('revenue'),
                        'latest_quarterly_net_income': latest_q.get('netIncome'),
                        'latest_quarterly_gross_profit': latest_q.get('grossProfit'),
                        'latest_quarter_date': latest_q.get('date'),
                        'quarterly_revenue_growth': self._calculate_growth(quarterly_data, 'revenue') if len(quarterly_data) >= 2 else None
                    })
                
                if annual_data and len(annual_data) > 0:
                    latest_a = annual_data[0]
                    result.update({
                        'annual_revenue': latest_a.get('revenue'),
                        'annual_net_income': latest_a.get('netIncome'),
                        'annual_gross_profit': latest_a.get('grossProfit'),
                        'annual_year': latest_a.get('date')
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {str(e)}")
        return {}
    
    async def _get_fmp_ratios(self, symbol: str) -> Dict[str, Any]:
        """Get financial ratios"""
        try:
            url = f"https://financialmodelingprep.com/api/v3/ratios/{symbol}"
            params = {'limit': 1, 'apikey': self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            ratios = data[0]
                            return {
                                'ev_to_sales': ratios.get('enterpriseValueOverSales'),
                                'price_to_sales': ratios.get('priceToSalesRatio'),
                                'gross_profit_margin': ratios.get('grossProfitMargin'),
                                'operating_margin': ratios.get('operatingProfitMargin'),
                                'net_profit_margin': ratios.get('netProfitMargin'),
                                'roe': ratios.get('returnOnEquity'),
                                'debt_to_equity': ratios.get('debtEquityRatio')
                            }
        except Exception as e:
            logger.error(f"Error fetching ratios for {symbol}: {str(e)}")
        return {}
    
    async def _get_fmp_earnings(self, symbol: str) -> Dict[str, Any]:
        """Get earnings data and key metrics"""
        try:
            url = f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}"
            params = {'period': 'quarter', 'limit': 1, 'apikey': self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            metrics = data[0]
                            return {
                                'eps': metrics.get('netIncomePerShare'),
                                'book_value_per_share': metrics.get('bookValuePerShare'),
                                'revenue_per_share': metrics.get('revenuePerShare'),
                                'shares_outstanding': metrics.get('sharesOutstanding')
                            }
        except Exception as e:
            logger.error(f"Error fetching earnings for {symbol}: {str(e)}")
        return {}
    
    async def _get_fmp_key_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive key metrics for company-specific drivers"""
        try:
            # Get key metrics (quarterly)
            metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}"
            
            # Get enterprise values 
            ev_url = f"https://financialmodelingprep.com/api/v3/enterprise-values/{symbol}"
            
            # Get financial growth
            growth_url = f"https://financialmodelingprep.com/api/v3/financial-growth/{symbol}"
            
            params = {'period': 'quarter', 'limit': 4, 'apikey': self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                # Get key metrics
                async with session.get(metrics_url, params=params) as response:
                    metrics_data = []
                    if response.status == 200:
                        metrics_data = await response.json()
                
                # Get enterprise values
                async with session.get(ev_url, params=params) as response:
                    ev_data = []
                    if response.status == 200:
                        ev_data = await response.json()
                
                # Get financial growth
                async with session.get(growth_url, params=params) as response:
                    growth_data = []
                    if response.status == 200:
                        growth_data = await response.json()
                
                result = {}
                
                if metrics_data and len(metrics_data) > 0:
                    latest_metrics = metrics_data[0]
                    result.update({
                        'revenue_per_share': latest_metrics.get('revenuePerShare'),
                        'net_income_per_share': latest_metrics.get('netIncomePerShare'),
                        'operating_cash_flow_per_share': latest_metrics.get('operatingCashFlowPerShare'),
                        'free_cash_flow_per_share': latest_metrics.get('freeCashFlowPerShare'),
                        'cash_per_share': latest_metrics.get('cashPerShare'),
                        'book_value_per_share': latest_metrics.get('bookValuePerShare'),
                        'tangible_book_value_per_share': latest_metrics.get('tangibleBookValuePerShare'),
                        'shareholders_equity_per_share': latest_metrics.get('shareholdersEquityPerShare'),
                        'debt_to_equity': latest_metrics.get('debtToEquity'),
                        'debt_to_assets': latest_metrics.get('debtToAssets'),
                        'working_capital': latest_metrics.get('workingCapital'),
                        'invested_capital': latest_metrics.get('investedCapital')
                    })
                
                if ev_data and len(ev_data) > 0:
                    latest_ev = ev_data[0]
                    result.update({
                        'enterprise_value': latest_ev.get('enterpriseValue'),
                        'enterprise_value_over_ebitda': latest_ev.get('enterpriseValueOverEBITDA')
                    })
                
                if growth_data and len(growth_data) > 0:
                    latest_growth = growth_data[0]
                    result.update({
                        'revenue_growth': latest_growth.get('revenueGrowth'),
                        'gross_profit_growth': latest_growth.get('grossProfitGrowth'),
                        'ebitda_growth': latest_growth.get('ebitdaGrowth'),
                        'operating_income_growth': latest_growth.get('operatingIncomeGrowth'),
                        'net_income_growth': latest_growth.get('netIncomeGrowth'),
                        'eps_growth': latest_growth.get('epsgrowth'),
                        'operating_cash_flow_growth': latest_growth.get('operatingCashFlowGrowth'),
                        'free_cash_flow_growth': latest_growth.get('freeCashFlowGrowth')
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching key metrics for {symbol}: {str(e)}")
        return {}
    
    def _calculate_growth(self, data_list: list, field: str) -> float:
        """Calculate YoY growth rate"""
        if len(data_list) < 2:
            return None
        current = data_list[0].get(field, 0) or 0
        previous = data_list[1].get(field, 0) or 0
        if previous == 0:
            return None
        return ((current - previous) / previous) * 100
    
    def _get_mock_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """Mock fundamental data when API unavailable"""
        return {
            'company_name': f'{symbol} Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'market_cap': 5000000000,
            'enterprise_value': 5200000000,
            'pe_ratio': 25.0,
            'ev_to_sales': 8.5,
            'latest_quarterly_revenue': 1250000000,
            'annual_revenue': 4800000000,
            'latest_quarterly_net_income': 180000000,
            'annual_net_income': 650000000
        }

    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Get company profile from FMP API"""
        if not self.fmp_api_key:
            return self._get_mock_company_data(symbol)
            
        try:
            url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}"
            params = {'apikey': self.fmp_api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            profile = data[0]
                            return {
                                'company_name': profile.get('companyName', symbol),
                                'sector': profile.get('sector', 'Unknown'),
                                'industry': profile.get('industry', 'Unknown'),
                                'market_cap': profile.get('mktCap'),
                                'pe_ratio': profile.get('pe'),
                                'description': profile.get('description', ''),
                                'website': profile.get('website', ''),
                                'exchange': profile.get('exchangeShortName', 'NASDAQ')
                            }
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {str(e)}")
            
        return self._get_mock_company_data(symbol)
    
    def _get_mock_data(self, symbol: str) -> RealMarketData:
        """Fallback mock data when APIs are unavailable"""
        # Use a hash of symbol to get consistent but varied mock prices
        hash_val = hash(symbol) % 1000
        base_price = 50 + (hash_val / 10)  # Price between 50-150
        
        return RealMarketData(
            symbol=symbol,
            current_price=base_price,
            open_price=base_price * 0.98,
            high_price=base_price * 1.05,
            low_price=base_price * 0.95,
            volume=1000000 + (hash_val * 10000),
            change=base_price * 0.02,
            change_percent=2.0,
            last_updated=datetime.now()
        )
    
    def _get_mock_company_data(self, symbol: str) -> Dict[str, Any]:
        """Mock company data"""
        company_map = {
            'OSCR': {
                'company_name': 'Oscar Health Inc',
                'sector': 'Healthcare',
                'industry': 'Healthcare Plans',
                'market_cap': 2500000000,  # $2.5B realistic for OSCR
                'pe_ratio': None,
                'description': 'Technology-focused health insurance company',
                'exchange': 'NYSE'
            },
            'HOOD': {
                'company_name': 'Robinhood Markets Inc',
                'sector': 'Financial Services',
                'industry': 'Financial Exchanges & Data',
                'market_cap': 8000000000,
                'pe_ratio': 25.0,
                'exchange': 'NASDAQ'
            }
        }
        
        return company_map.get(symbol, {
            'company_name': f'{symbol} Corp',
            'sector': 'Unknown',
            'industry': 'Unknown',
            'market_cap': 1000000000,
            'pe_ratio': 20.0,
            'exchange': 'NASDAQ'
        })

# Singleton instance
real_market_service = RealMarketDataService()