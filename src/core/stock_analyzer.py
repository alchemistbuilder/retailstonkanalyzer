import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from ..models.stock_data import StockAnalysis, StockAlert
from ..data_collectors.social_media_collector import SocialMediaCollector
from ..data_collectors.technical_data_collector import TechnicalDataCollector
from ..data_collectors.fundamental_data_collector import FundamentalDataCollector
from ..data_collectors.analyst_data_collector import AnalystDataCollector
from ..data_collectors.stock_structure_collector import StockStructureCollector
from ..analyzers.composite_scorer import CompositeScorer
from ..analyzers.divergence_detector import DivergenceDetector
from ..utils.rate_limiter import global_rate_limiter
from .config import settings


class StockAnalyzer:
    def __init__(self):
        # Initialize all data collectors
        self.social_collector = SocialMediaCollector()
        self.technical_collector = TechnicalDataCollector()
        self.fundamental_collector = FundamentalDataCollector()
        self.analyst_collector = AnalystDataCollector()
        self.structure_collector = StockStructureCollector()
        
        # Initialize analyzers
        self.scorer = CompositeScorer()
        self.divergence_detector = DivergenceDetector()
    
    async def analyze_stock(self, symbol: str, company_name: str = "") -> Optional[StockAnalysis]:
        """Perform comprehensive analysis of a single stock"""
        try:
            print(f"Starting analysis for {symbol}...")
            
            # Collect all data concurrently
            print(f"Collecting data for {symbol}...")
            tasks = [
                self._collect_social_data(symbol),
                self._collect_technical_data(symbol),
                self._collect_fundamental_data(symbol),
                self._collect_analyst_data(symbol),
                self._collect_structure_data(symbol)
            ]
            
            (social_sentiment, technical_analysis, fundamental_data, 
             analyst_coverage, stock_structure) = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions from data collection
            if isinstance(social_sentiment, Exception):
                print(f"Error collecting social data for {symbol}: {social_sentiment}")
                social_sentiment = self._get_default_social_sentiment()
            
            if isinstance(technical_analysis, Exception):
                print(f"Error collecting technical data for {symbol}: {technical_analysis}")
                technical_analysis = self._get_default_technical_analysis()
            
            if isinstance(fundamental_data, Exception):
                print(f"Error collecting fundamental data for {symbol}: {fundamental_data}")
                fundamental_data = self._get_default_fundamental_data()
            
            if isinstance(analyst_coverage, Exception):
                print(f"Error collecting analyst data for {symbol}: {analyst_coverage}")
                analyst_coverage = self._get_default_analyst_coverage()
            
            if isinstance(stock_structure, Exception):
                print(f"Error collecting structure data for {symbol}: {stock_structure}")
                stock_structure = self._get_default_stock_structure()
            
            # Determine sector and industry (placeholder for now)
            sector = "Unknown"
            industry = "Unknown"
            
            # Create stock analysis object
            analysis = StockAnalysis(
                symbol=symbol,
                company_name=company_name or symbol,
                sector=sector,
                industry=industry,
                social_sentiment=social_sentiment,
                technical_analysis=technical_analysis,
                fundamental_data=fundamental_data,
                analyst_coverage=analyst_coverage,
                stock_structure=stock_structure,
                composite_score=None,  # Will be calculated next
                alerts=[],
                last_updated=datetime.now()
            )
            
            # Calculate composite score
            print(f"Calculating composite score for {symbol}...")
            composite_score = self.scorer.calculate_composite_score(analysis)
            analysis.composite_score = composite_score
            
            # Detect divergences and generate alerts
            print(f"Detecting divergences for {symbol}...")
            divergence_signals = self.divergence_detector.detect_all_divergences(analysis)
            
            # Convert divergence signals to alerts
            alerts = self._convert_signals_to_alerts(symbol, divergence_signals, composite_score.total_score)
            analysis.alerts = alerts
            
            print(f"Analysis complete for {symbol}. Score: {composite_score.total_score:.1f}")
            return analysis
            
        except Exception as e:
            print(f"Error analyzing stock {symbol}: {e}")
            return None
    
    async def analyze_multiple_stocks(self, symbols: List[str]) -> Dict[str, Optional[StockAnalysis]]:
        """Analyze multiple stocks with rate limiting"""
        results = {}
        
        # Analyze stocks with controlled concurrency to respect rate limits
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent analyses
        
        async def analyze_with_semaphore(symbol: str):
            async with semaphore:
                return await self.analyze_stock(symbol)
        
        tasks = [analyze_with_semaphore(symbol) for symbol in symbols]
        analyses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, analysis in zip(symbols, analyses):
            if isinstance(analysis, Exception):
                print(f"Error analyzing {symbol}: {analysis}")
                results[symbol] = None
            else:
                results[symbol] = analysis
        
        return results
    
    async def _collect_social_data(self, symbol: str):
        """Collect social media sentiment data"""
        return await self.social_collector.collect_sentiment(symbol)
    
    async def _collect_technical_data(self, symbol: str):
        """Collect technical analysis data"""
        return await self.technical_collector.collect_technical_analysis(symbol)
    
    async def _collect_fundamental_data(self, symbol: str):
        """Collect fundamental data"""
        return await self.fundamental_collector.collect_fundamental_data(symbol)
    
    async def _collect_analyst_data(self, symbol: str):
        """Collect analyst coverage data"""
        # Get current price for price target calculations
        technical_data = await self.technical_collector.collect_technical_analysis(symbol)
        current_price = technical_data.price if technical_data else 0.0
        
        return await self.analyst_collector.collect_analyst_coverage(symbol, current_price)
    
    async def _collect_structure_data(self, symbol: str):
        """Collect stock structure data"""
        return await self.structure_collector.collect_stock_structure(symbol)
    
    def _get_default_social_sentiment(self):
        """Get default social sentiment when collection fails"""
        from ..models.stock_data import SocialSentiment, TrendDirection
        return SocialSentiment(
            platform="aggregated",
            mentions=0,
            sentiment_score=0.0,
            volume_trend=TrendDirection.NEUTRAL,
            top_keywords=[],
            influencer_mentions=0,
            timestamp=datetime.now()
        )
    
    def _get_default_technical_analysis(self):
        """Get default technical analysis when collection fails"""
        from ..models.stock_data import TechnicalAnalysis, TrendDirection
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
            timestamp=datetime.now()
        )
    
    def _get_default_fundamental_data(self):
        """Get default fundamental data when collection fails"""
        from ..models.stock_data import FundamentalData
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
    
    def _get_default_analyst_coverage(self):
        """Get default analyst coverage when collection fails"""
        from ..models.stock_data import AnalystCoverage, AnalystRating
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
    
    def _get_default_stock_structure(self):
        """Get default stock structure when collection fails"""
        from ..models.stock_data import StockStructure
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
    
    def _convert_signals_to_alerts(self, symbol: str, signals, total_score: float) -> List[StockAlert]:
        """Convert divergence signals to stock alerts"""
        alerts = []
        
        # Import chart collector here to avoid circular imports
        from ..data_collectors.chart_image_collector import ChartImageCollector
        chart_collector = ChartImageCollector()
        
        for signal in signals:
            # Determine priority based on signal strength and total score
            if signal.strength > 0.8 and total_score > 70:
                priority = "high"
            elif signal.strength > 0.6 and total_score > 50:
                priority = "medium"
            else:
                priority = "low"
            
            # Get alert-specific chart image
            try:
                chart_image_url = asyncio.run(chart_collector.get_alert_chart(symbol, signal.divergence_type.value))
            except:
                chart_image_url = f"https://chart-img.com/chart/{symbol.upper()}"
            
            # Create alert
            alert = StockAlert(
                symbol=symbol,
                alert_type=signal.divergence_type.value,
                score=total_score,
                trigger_reason=signal.description,
                priority=priority,
                social_catalyst=signal.catalyst if "social" in signal.catalyst.lower() else None,
                technical_catalyst=signal.catalyst if "technical" in signal.catalyst.lower() else None,
                fundamental_catalyst=signal.catalyst if "fundamental" in signal.catalyst.lower() else None,
                analyst_catalyst=signal.catalyst if "analyst" in signal.catalyst.lower() else None,
                structure_catalyst=signal.catalyst if "short" in signal.catalyst.lower() else None,
                timestamp=datetime.now(),
                chart_image_url=chart_image_url
            )
            
            alerts.append(alert)
        
        return alerts


class WatchlistAnalyzer:
    def __init__(self):
        self.analyzer = StockAnalyzer()
    
    async def analyze_watchlist(self, symbols: List[str] = None) -> Dict[str, Optional[StockAnalysis]]:
        """Analyze the entire watchlist"""
        if symbols is None:
            symbols = settings.default_watchlist
        
        print(f"Analyzing watchlist: {symbols}")
        results = await self.analyzer.analyze_multiple_stocks(symbols)
        
        # Filter out failed analyses and sort by score
        successful_analyses = {
            symbol: analysis for symbol, analysis in results.items() 
            if analysis is not None
        }
        
        # Sort by composite score
        sorted_analyses = dict(sorted(
            successful_analyses.items(),
            key=lambda x: x[1].composite_score.total_score if x[1].composite_score else 0,
            reverse=True
        ))
        
        print(f"Successfully analyzed {len(sorted_analyses)} out of {len(symbols)} stocks")
        
        return sorted_analyses
    
    def get_top_opportunities(self, analyses: Dict[str, StockAnalysis], 
                            min_score: float = 70.0, limit: int = 10) -> List[StockAnalysis]:
        """Get top opportunities from analyses"""
        opportunities = []
        
        for symbol, analysis in analyses.items():
            if analysis and analysis.composite_score and analysis.composite_score.total_score >= min_score:
                opportunities.append(analysis)
        
        # Sort by score and return top N
        opportunities.sort(key=lambda x: x.composite_score.total_score, reverse=True)
        return opportunities[:limit]
    
    def get_alerts_summary(self, analyses: Dict[str, StockAnalysis]) -> Dict[str, List[StockAlert]]:
        """Get summary of all alerts by priority"""
        alerts_by_priority = {"high": [], "medium": [], "low": []}
        
        for symbol, analysis in analyses.items():
            if analysis and analysis.alerts:
                for alert in analysis.alerts:
                    alerts_by_priority[alert.priority].append(alert)
        
        # Sort alerts by score within each priority
        for priority in alerts_by_priority:
            alerts_by_priority[priority].sort(key=lambda x: x.score, reverse=True)
        
        return alerts_by_priority