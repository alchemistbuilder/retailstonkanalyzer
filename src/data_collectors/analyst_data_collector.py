import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..core.config import settings
from ..models.stock_data import AnalystCoverage, AnalystRating
from ..utils.rate_limiter import RateLimiter


class FinancialModelingPrepAnalystCollector:
    def __init__(self):
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.api_key = settings.fmp_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=250)
    
    async def get_price_target_consensus(self, symbol: str) -> Dict:
        """Get price target consensus data"""
        try:
            url = f"{self.base_url}/price-target-consensus"
            params = {'symbol': symbol, 'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            await self.rate_limiter.wait()
                            return data[0]
        except Exception as e:
            print(f"Error fetching price target consensus for {symbol}: {e}")
        
        return {}
    
    async def get_price_targets(self, symbol: str) -> List[Dict]:
        """Get individual analyst price targets"""
        try:
            url = f"{self.base_url}/price-target"
            params = {'symbol': symbol, 'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data[:20]  # Get recent 20 targets
        except Exception as e:
            print(f"Error fetching price targets for {symbol}: {e}")
        
        return []
    
    async def get_analyst_estimates(self, symbol: str) -> Dict:
        """Get analyst estimates for earnings"""
        try:
            url = f"{self.base_url}/analyst-estimates/{symbol}"
            params = {'apikey': self.api_key, 'limit': 4}  # Get quarterly estimates
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching analyst estimates for {symbol}: {e}")
        
        return []
    
    async def get_upgrades_downgrades(self, symbol: str) -> List[Dict]:
        """Get recent upgrades and downgrades"""
        try:
            url = f"{self.base_url}/upgrades-downgrades"
            params = {'symbol': symbol, 'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data[:30]  # Get recent 30 changes
        except Exception as e:
            print(f"Error fetching upgrades/downgrades for {symbol}: {e}")
        
        return []


class BenzingaAnalystCollector:
    def __init__(self):
        self.base_url = "https://api.benzinga.com/api/v2.1"
        self.api_key = settings.benzinga_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def get_analyst_ratings(self, symbol: str) -> List[Dict]:
        """Get analyst ratings from Benzinga"""
        try:
            url = f"{self.base_url}/calendar/ratings"
            params = {
                'token': self.api_key,
                'symbols': symbol,
                'pagesize': 50
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data.get('ratings', [])
        except Exception as e:
            print(f"Error fetching Benzinga ratings for {symbol}: {e}")
        
        return []
    
    async def get_price_targets(self, symbol: str) -> List[Dict]:
        """Get price targets from Benzinga"""
        try:
            url = f"{self.base_url}/calendar/price-targets"
            params = {
                'token': self.api_key,
                'symbols': symbol,
                'pagesize': 50
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data.get('price_targets', [])
        except Exception as e:
            print(f"Error fetching Benzinga price targets for {symbol}: {e}")
        
        return []


class FinnhubAnalystCollector:
    def __init__(self):
        self.base_url = "https://finnhub.io/api/v1"
        self.api_key = settings.finnhub_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def get_recommendation_trends(self, symbol: str) -> List[Dict]:
        """Get recommendation trends from Finnhub"""
        try:
            url = f"{self.base_url}/stock/recommendation"
            params = {'symbol': symbol, 'token': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching Finnhub recommendations for {symbol}: {e}")
        
        return []
    
    async def get_price_target(self, symbol: str) -> Dict:
        """Get price target from Finnhub"""
        try:
            url = f"{self.base_url}/stock/price-target"
            params = {'symbol': symbol, 'token': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.rate_limiter.wait()
                        return data
        except Exception as e:
            print(f"Error fetching Finnhub price target for {symbol}: {e}")
        
        return {}


class AnalystDataAnalyzer:
    def __init__(self):
        pass
    
    def parse_consensus_rating(self, consensus_data: Dict) -> AnalystRating:
        """Parse consensus rating from various data sources"""
        try:
            # FMP consensus data
            consensus = consensus_data.get('targetConsensus', '').lower()
            
            if 'strong buy' in consensus or 'strongbuy' in consensus:
                return AnalystRating.STRONG_BUY
            elif 'buy' in consensus:
                return AnalystRating.BUY
            elif 'hold' in consensus:
                return AnalystRating.HOLD
            elif 'sell' in consensus:
                return AnalystRating.SELL
            elif 'strong sell' in consensus or 'strongsell' in consensus:
                return AnalystRating.STRONG_SELL
            
            # Fallback: determine from numerical ratings if available
            avg_rating = consensus_data.get('targetMean')
            if avg_rating:
                if avg_rating <= 1.5:
                    return AnalystRating.STRONG_BUY
                elif avg_rating <= 2.5:
                    return AnalystRating.BUY
                elif avg_rating <= 3.5:
                    return AnalystRating.HOLD
                elif avg_rating <= 4.5:
                    return AnalystRating.SELL
                else:
                    return AnalystRating.STRONG_SELL
            
        except Exception as e:
            print(f"Error parsing consensus rating: {e}")
        
        return AnalystRating.HOLD  # Default to hold
    
    def analyze_rating_changes(self, upgrades_downgrades: List[Dict], days: int = 30) -> Dict:
        """Analyze recent rating changes"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_upgrades = 0
        recent_downgrades = 0
        rating_changes = []
        
        for change in upgrades_downgrades:
            try:
                # Parse date from various formats
                published_date = change.get('publishedDate') or change.get('date')
                if published_date:
                    if isinstance(published_date, str):
                        change_date = datetime.strptime(published_date.split('T')[0], '%Y-%m-%d')
                    else:
                        change_date = published_date
                    
                    if change_date >= cutoff_date:
                        grade = change.get('newGrade', '').lower()
                        action = change.get('gradingCompany', '')
                        
                        rating_changes.append({
                            'date': change_date,
                            'action': grade,
                            'company': action,
                            'new_rating': change.get('newGrade'),
                            'previous_rating': change.get('previousGrade')
                        })
                        
                        # Count upgrades/downgrades
                        if any(word in grade for word in ['buy', 'upgrade', 'outperform', 'overweight']):
                            recent_upgrades += 1
                        elif any(word in grade for word in ['sell', 'downgrade', 'underperform', 'underweight']):
                            recent_downgrades += 1
                            
            except Exception as e:
                print(f"Error processing rating change: {e}")
                continue
        
        return {
            'recent_upgrades': recent_upgrades,
            'recent_downgrades': recent_downgrades,
            'rating_changes_30d': rating_changes,
            'net_sentiment': recent_upgrades - recent_downgrades
        }
    
    def calculate_price_target_metrics(self, consensus: Dict, individual_targets: List[Dict], current_price: float) -> Dict:
        """Calculate price target metrics"""
        try:
            # Get consensus targets
            avg_target = consensus.get('targetMean') or consensus.get('targetMedian')
            high_target = consensus.get('targetHigh')
            low_target = consensus.get('targetLow')
            
            # If consensus data is missing, calculate from individual targets
            if not avg_target and individual_targets:
                recent_targets = []
                cutoff_date = datetime.now() - timedelta(days=90)  # Recent 90 days
                
                for target in individual_targets:
                    try:
                        published_date = target.get('publishedDate', '')
                        if published_date:
                            target_date = datetime.strptime(published_date.split('T')[0], '%Y-%m-%d')
                            if target_date >= cutoff_date:
                                price_target = target.get('priceTarget') or target.get('adjPriceTarget')
                                if price_target and price_target > 0:
                                    recent_targets.append(float(price_target))
                    except:
                        continue
                
                if recent_targets:
                    avg_target = sum(recent_targets) / len(recent_targets)
                    high_target = max(recent_targets)
                    low_target = min(recent_targets)
            
            # Calculate upside/downside
            upside = 0.0
            if avg_target and current_price > 0:
                upside = (avg_target - current_price) / current_price * 100
            
            return {
                'avg_price_target': float(avg_target) if avg_target else 0.0,
                'high_price_target': float(high_target) if high_target else 0.0,
                'low_price_target': float(low_target) if low_target else 0.0,
                'price_target_upside': upside,
                'num_price_targets': len(individual_targets)
            }
            
        except Exception as e:
            print(f"Error calculating price target metrics: {e}")
            return {
                'avg_price_target': 0.0,
                'high_price_target': 0.0,
                'low_price_target': 0.0,
                'price_target_upside': 0.0,
                'num_price_targets': 0
            }
    
    def extract_analyst_firms(self, upgrades_downgrades: List[Dict], price_targets: List[Dict]) -> List[str]:
        """Extract unique analyst firms covering the stock"""
        firms = set()
        
        for change in upgrades_downgrades:
            firm = change.get('gradingCompany') or change.get('analystFirm')
            if firm:
                firms.add(firm)
        
        for target in price_targets:
            firm = target.get('analystCompany') or target.get('analystFirm')
            if firm:
                firms.add(firm)
        
        return list(firms)


class AnalystDataCollector:
    def __init__(self):
        self.fmp = FinancialModelingPrepAnalystCollector()
        self.benzinga = BenzingaAnalystCollector()
        self.finnhub = FinnhubAnalystCollector()
        self.analyzer = AnalystDataAnalyzer()
    
    async def collect_analyst_coverage(self, symbol: str, current_price: float = 0.0) -> AnalystCoverage:
        """Collect comprehensive analyst coverage data"""
        try:
            # Collect data from multiple sources concurrently
            tasks = [
                self.fmp.get_price_target_consensus(symbol),
                self.fmp.get_price_targets(symbol),
                self.fmp.get_upgrades_downgrades(symbol),
                self.finnhub.get_recommendation_trends(symbol),
                self.finnhub.get_price_target(symbol)
            ]
            
            consensus, price_targets, upgrades_downgrades, finnhub_recs, finnhub_target = await asyncio.gather(*tasks)
            
            # Parse consensus rating
            consensus_rating = self.analyzer.parse_consensus_rating(consensus)
            
            # Analyze rating changes
            rating_analysis = self.analyzer.analyze_rating_changes(upgrades_downgrades)
            
            # Calculate price target metrics
            price_target_metrics = self.analyzer.calculate_price_target_metrics(
                consensus, price_targets, current_price
            )
            
            # Extract analyst firms
            analyst_firms = self.analyzer.extract_analyst_firms(upgrades_downgrades, price_targets)
            
            # Count number of analysts
            num_analysts = consensus.get('targetMean') and len(price_targets) or len(analyst_firms)
            if not num_analysts and finnhub_recs:
                # Use Finnhub recommendation data
                latest_rec = finnhub_recs[0] if finnhub_recs else {}
                num_analysts = (latest_rec.get('buy', 0) + 
                              latest_rec.get('hold', 0) + 
                              latest_rec.get('sell', 0) + 
                              latest_rec.get('strongBuy', 0) + 
                              latest_rec.get('strongSell', 0))
            
            return AnalystCoverage(
                consensus_rating=consensus_rating,
                num_analysts=num_analysts,
                avg_price_target=price_target_metrics['avg_price_target'],
                high_price_target=price_target_metrics['high_price_target'],
                low_price_target=price_target_metrics['low_price_target'],
                price_target_upside=price_target_metrics['price_target_upside'],
                recent_upgrades=rating_analysis['recent_upgrades'],
                recent_downgrades=rating_analysis['recent_downgrades'],
                rating_changes_30d=rating_analysis['rating_changes_30d'],
                analyst_firms=analyst_firms,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error collecting analyst coverage for {symbol}: {e}")
            
            # Return default analyst coverage
            return AnalystCoverage(
                consensus_rating=AnalystRating.HOLD,
                num_analysts=0,
                avg_price_target=0.0,
                high_price_target=0.0,
                low_price_target=0.0,
                price_target_upside=0.0,
                recent_upgrades=0,
                recent_downgrades=0,
                rating_changes_30d=[],
                analyst_firms=[],
                timestamp=datetime.now()
            )