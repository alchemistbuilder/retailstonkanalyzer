from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np

from ..models.stock_data import (
    StockAnalysis, CompositeScore, SocialSentiment, TechnicalAnalysis,
    FundamentalData, AnalystCoverage, StockStructure, TrendDirection, AnalystRating
)
from ..core.config import settings


class SocialSentimentScorer:
    def __init__(self):
        self.max_score = 100.0
    
    def score_sentiment(self, social: SocialSentiment) -> float:
        """Score social sentiment (0-100)"""
        score = 0.0
        
        try:
            # Base sentiment score (0-40 points)
            sentiment_points = (social.sentiment_score + 1) * 20  # Convert -1,1 to 0-40
            score += min(sentiment_points, 40)
            
            # Volume/mentions score (0-30 points)
            if social.mentions > 1000:
                score += 30
            elif social.mentions > 500:
                score += 25
            elif social.mentions > 200:
                score += 20
            elif social.mentions > 100:
                score += 15
            elif social.mentions > 50:
                score += 10
            elif social.mentions > 10:
                score += 5
            
            # Trend direction bonus (0-15 points)
            if social.volume_trend == TrendDirection.BULLISH:
                score += 15
            elif social.volume_trend == TrendDirection.NEUTRAL:
                score += 7
            
            # Influencer mentions bonus (0-15 points)
            if social.influencer_mentions > 20:
                score += 15
            elif social.influencer_mentions > 10:
                score += 10
            elif social.influencer_mentions > 5:
                score += 5
            
            # Keyword quality bonus/penalty (0-10 points)
            bullish_keywords = ['moon', 'rocket', 'diamond', 'hodl', 'squeeze', 'buy', 'calls']
            bearish_keywords = ['sell', 'puts', 'crash', 'dump']
            
            keyword_score = 0
            for keyword in social.top_keywords:
                if keyword.lower() in bullish_keywords:
                    keyword_score += 2
                elif keyword.lower() in bearish_keywords:
                    keyword_score -= 2
            
            score += max(-10, min(keyword_score, 10))
            
        except Exception as e:
            print(f"Error scoring social sentiment: {e}")
        
        return max(0, min(score, self.max_score))


class TechnicalAnalysisScorer:
    def __init__(self):
        self.max_score = 100.0
    
    def score_technical(self, technical: TechnicalAnalysis) -> float:
        """Score technical analysis (0-100)"""
        score = 0.0
        
        try:
            # RSI score (0-20 points)
            rsi = technical.rsi
            if 30 <= rsi <= 70:
                score += 20  # Neutral RSI is good
            elif 20 <= rsi < 30 or 70 < rsi <= 80:
                score += 15  # Slightly oversold/overbought
            elif rsi < 20:
                score += 25  # Very oversold (potential bounce)
            elif rsi > 80:
                score += 5   # Very overbought (risky)
            
            # MACD signal (0-15 points)
            if technical.macd_signal == 'bullish':
                score += 15
            elif technical.macd_signal == 'neutral':
                score += 7
            
            # Bollinger Bands position (0-15 points)
            bb_pos = technical.bollinger_position
            if bb_pos < 0.2:
                score += 15  # Near lower band (oversold)
            elif 0.2 <= bb_pos <= 0.8:
                score += 10  # In the middle
            elif bb_pos > 0.8:
                score += 5   # Near upper band (overbought)
            
            # Trend direction (0-20 points)
            if technical.trend_direction == TrendDirection.BULLISH:
                score += 20
            elif technical.trend_direction == TrendDirection.NEUTRAL:
                score += 10
            
            # Pattern detection bonus (0-15 points)
            if technical.pattern_detected:
                score += technical.pattern_confidence * 15
            
            # Volume spike bonus (0-10 points)
            if technical.volume_spike:
                score += 10
            
            # Moving average alignment (0-5 points)
            ma_data = technical.moving_averages
            if ma_data:
                current_price = technical.price
                sma_20 = ma_data.get('sma_20', current_price)
                sma_50 = ma_data.get('sma_50', current_price)
                
                if current_price > sma_20 > sma_50:
                    score += 5  # Bullish alignment
                elif current_price > sma_20:
                    score += 2  # Partial bullish
            
        except Exception as e:
            print(f"Error scoring technical analysis: {e}")
        
        return max(0, min(score, self.max_score))


class FundamentalAnalysisScorer:
    def __init__(self):
        self.max_score = 100.0
    
    def score_fundamental(self, fundamental: FundamentalData) -> float:
        """Score fundamental analysis (0-100)"""
        score = 0.0
        
        try:
            # Valuation score (0-30 points)
            pe_score = self._score_pe_ratio(fundamental.pe_ratio)
            ps_score = self._score_ps_ratio(fundamental.ps_ratio)
            valuation_score = (pe_score + ps_score) / 2 * 3  # Scale to 30 points
            score += valuation_score
            
            # Growth score (0-25 points)
            if fundamental.revenue_growth_yoy is not None:
                growth_score = self._score_growth(fundamental.revenue_growth_yoy)
                score += growth_score * 25 / 10  # Scale to 25 points
            
            # Profitability score (0-25 points)
            if fundamental.profit_margin is not None:
                profit_score = self._score_profit_margin(fundamental.profit_margin)
                score += profit_score * 25 / 10  # Scale to 25 points
            
            # Financial health score (0-20 points)
            health_score = 0
            if fundamental.debt_to_equity is not None:
                health_score += self._score_debt_ratio(fundamental.debt_to_equity)
            if fundamental.current_ratio is not None:
                health_score += self._score_current_ratio(fundamental.current_ratio)
            if fundamental.roe is not None:
                health_score += self._score_roe(fundamental.roe)
            
            # Average health scores
            health_components = sum([1 for x in [fundamental.debt_to_equity, 
                                               fundamental.current_ratio, 
                                               fundamental.roe] if x is not None])
            if health_components > 0:
                score += (health_score / health_components) * 20 / 10  # Scale to 20 points
            
        except Exception as e:
            print(f"Error scoring fundamental analysis: {e}")
        
        return max(0, min(score, self.max_score))
    
    def _score_pe_ratio(self, pe_ratio: float) -> float:
        """Score P/E ratio (0-10)"""
        if pe_ratio is None or pe_ratio < 0:
            return 1
        elif pe_ratio < 15:
            return 9
        elif pe_ratio < 25:
            return 7
        elif pe_ratio < 40:
            return 5
        elif pe_ratio < 60:
            return 3
        else:
            return 1
    
    def _score_ps_ratio(self, ps_ratio: float) -> float:
        """Score P/S ratio (0-10)"""
        if ps_ratio is None:
            return 5
        elif ps_ratio < 2:
            return 9
        elif ps_ratio < 5:
            return 7
        elif ps_ratio < 10:
            return 5
        elif ps_ratio < 20:
            return 3
        else:
            return 1
    
    def _score_growth(self, growth_rate: float) -> float:
        """Score growth rate (0-10)"""
        if growth_rate > 50:
            return 10
        elif growth_rate > 25:
            return 8
        elif growth_rate > 15:
            return 6
        elif growth_rate > 5:
            return 5
        elif growth_rate > 0:
            return 3
        else:
            return 1
    
    def _score_profit_margin(self, margin: float) -> float:
        """Score profit margin (0-10)"""
        if margin > 20:
            return 10
        elif margin > 15:
            return 8
        elif margin > 10:
            return 6
        elif margin > 5:
            return 4
        elif margin > 0:
            return 2
        else:
            return 1
    
    def _score_debt_ratio(self, debt_ratio: float) -> float:
        """Score debt to equity ratio (0-10)"""
        if debt_ratio < 0.3:
            return 9
        elif debt_ratio < 0.6:
            return 7
        elif debt_ratio < 1.0:
            return 5
        elif debt_ratio < 2.0:
            return 3
        else:
            return 1
    
    def _score_current_ratio(self, current_ratio: float) -> float:
        """Score current ratio (0-10)"""
        if current_ratio > 2.5:
            return 9
        elif current_ratio > 1.5:
            return 7
        elif current_ratio > 1.0:
            return 5
        elif current_ratio > 0.5:
            return 3
        else:
            return 1
    
    def _score_roe(self, roe: float) -> float:
        """Score ROE (0-10)"""
        if roe > 20:
            return 10
        elif roe > 15:
            return 8
        elif roe > 10:
            return 6
        elif roe > 5:
            return 4
        elif roe > 0:
            return 2
        else:
            return 1


class AnalystCoverageScorer:
    def __init__(self):
        self.max_score = 100.0
    
    def score_analyst_coverage(self, analyst: AnalystCoverage) -> float:
        """Score analyst coverage (0-100)"""
        score = 0.0
        
        try:
            # Consensus rating score (0-40 points)
            rating_scores = {
                AnalystRating.STRONG_BUY: 40,
                AnalystRating.BUY: 30,
                AnalystRating.HOLD: 15,
                AnalystRating.SELL: 5,
                AnalystRating.STRONG_SELL: 0
            }
            score += rating_scores.get(analyst.consensus_rating, 15)
            
            # Price target upside (0-30 points)
            upside = analyst.price_target_upside
            if upside > 50:
                score += 30
            elif upside > 25:
                score += 25
            elif upside > 15:
                score += 20
            elif upside > 5:
                score += 15
            elif upside > 0:
                score += 10
            elif upside > -10:
                score += 5
            
            # Analyst coverage breadth (0-15 points)
            if analyst.num_analysts > 20:
                score += 15
            elif analyst.num_analysts > 15:
                score += 12
            elif analyst.num_analysts > 10:
                score += 10
            elif analyst.num_analysts > 5:
                score += 7
            elif analyst.num_analysts > 2:
                score += 5
            
            # Recent rating changes (0-15 points)
            net_changes = analyst.recent_upgrades - analyst.recent_downgrades
            if net_changes > 3:
                score += 15
            elif net_changes > 1:
                score += 10
            elif net_changes == 1:
                score += 5
            elif net_changes == 0:
                score += 3
            elif net_changes < -1:
                score -= 5  # Penalty for downgrades
            
        except Exception as e:
            print(f"Error scoring analyst coverage: {e}")
        
        return max(0, min(score, self.max_score))


class StockStructureScorer:
    def __init__(self):
        self.max_score = 100.0
    
    def score_stock_structure(self, structure: StockStructure) -> float:
        """Score stock structure (0-100)"""
        score = 0.0
        
        try:
            # Short squeeze potential (0-40 points)
            score += structure.short_squeeze_score * 0.4
            
            # Short interest (0-25 points)
            if structure.short_interest > 30:
                score += 25
            elif structure.short_interest > 20:
                score += 20
            elif structure.short_interest > 15:
                score += 15
            elif structure.short_interest > 10:
                score += 10
            elif structure.short_interest > 5:
                score += 5
            
            # Float size (0-15 points) - smaller float can be more volatile
            if structure.shares_outstanding > 0 and structure.float_shares > 0:
                float_ratio = structure.float_shares / structure.shares_outstanding
                if float_ratio < 0.3:
                    score += 15  # Very small float
                elif float_ratio < 0.5:
                    score += 12  # Small float
                elif float_ratio < 0.7:
                    score += 8   # Medium float
                else:
                    score += 5   # Large float
            
            # Utilization rate (0-10 points)
            if structure.utilization_rate:
                if structure.utilization_rate > 90:
                    score += 10
                elif structure.utilization_rate > 80:
                    score += 8
                elif structure.utilization_rate > 70:
                    score += 6
                elif structure.utilization_rate > 60:
                    score += 4
            
            # Cost to borrow (0-10 points)
            if structure.cost_to_borrow:
                if structure.cost_to_borrow > 50:
                    score += 10
                elif structure.cost_to_borrow > 25:
                    score += 8
                elif structure.cost_to_borrow > 10:
                    score += 6
                elif structure.cost_to_borrow > 5:
                    score += 4
            
        except Exception as e:
            print(f"Error scoring stock structure: {e}")
        
        return max(0, min(score, self.max_score))


class DivergenceAnalyzer:
    def __init__(self):
        pass
    
    def analyze_retail_vs_institutional(self, 
                                      social: SocialSentiment,
                                      analyst: AnalystCoverage,
                                      structure: StockStructure) -> Dict[str, float]:
        """Analyze divergence between retail and institutional sentiment"""
        divergences = {}
        
        try:
            # Retail sentiment vs analyst rating divergence
            retail_bullish = social.sentiment_score > 0.3
            analyst_bullish = analyst.consensus_rating in [AnalystRating.BUY, AnalystRating.STRONG_BUY]
            
            if retail_bullish and not analyst_bullish:
                divergences['retail_vs_analyst'] = 0.8  # Strong retail, weak institutional
            elif not retail_bullish and analyst_bullish:
                divergences['retail_vs_analyst'] = -0.8  # Weak retail, strong institutional
            else:
                divergences['retail_vs_analyst'] = 0.0
            
            # Short squeeze setup detection
            high_short_interest = structure.short_interest > 15
            positive_retail_sentiment = social.sentiment_score > 0.2
            high_social_volume = social.mentions > 100
            
            if high_short_interest and positive_retail_sentiment and high_social_volume:
                divergences['squeeze_potential'] = min(structure.short_squeeze_score / 100, 1.0)
            else:
                divergences['squeeze_potential'] = 0.0
            
            # Institutional vs retail ownership imbalance
            if structure.institutional_ownership > 80:
                divergences['institutional_dominated'] = 0.7
            elif structure.institutional_ownership < 20:
                divergences['retail_dominated'] = 0.7
            else:
                divergences['balanced_ownership'] = 0.0
            
        except Exception as e:
            print(f"Error analyzing divergences: {e}")
        
        return divergences


class CompositeScorer:
    def __init__(self):
        self.social_scorer = SocialSentimentScorer()
        self.technical_scorer = TechnicalAnalysisScorer()
        self.fundamental_scorer = FundamentalAnalysisScorer()
        self.analyst_scorer = AnalystCoverageScorer()
        self.structure_scorer = StockStructureScorer()
        self.divergence_analyzer = DivergenceAnalyzer()
        
        # Get weights from config
        self.weights = {
            'social': settings.social_sentiment_weight,
            'technical': settings.technical_analysis_weight,
            'fundamental': settings.fundamental_analysis_weight,
            'analyst': settings.analyst_coverage_weight,
            'structure': settings.stock_structure_weight
        }
    
    def calculate_composite_score(self, analysis: StockAnalysis) -> CompositeScore:
        """Calculate composite score from all analysis factors"""
        try:
            # Calculate individual scores
            social_score = self.social_scorer.score_sentiment(analysis.social_sentiment)
            technical_score = self.technical_scorer.score_technical(analysis.technical_analysis)
            fundamental_score = self.fundamental_scorer.score_fundamental(analysis.fundamental_data)
            analyst_score = self.analyst_scorer.score_analyst_coverage(analysis.analyst_coverage)
            structure_score = self.structure_scorer.score_stock_structure(analysis.stock_structure)
            
            # Calculate weighted total score
            total_score = (
                social_score * self.weights['social'] +
                technical_score * self.weights['technical'] +
                fundamental_score * self.weights['fundamental'] +
                analyst_score * self.weights['analyst'] +
                structure_score * self.weights['structure']
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(analysis, total_score)
            
            # Determine opportunity type
            opportunity_type = self._determine_opportunity_type(analysis)
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence(analysis)
            
            return CompositeScore(
                total_score=total_score,
                social_score=social_score,
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                analyst_score=analyst_score,
                structure_score=structure_score,
                risk_level=risk_level,
                opportunity_type=opportunity_type,
                confidence_level=confidence_level,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error calculating composite score: {e}")
            
            # Return default score
            return CompositeScore(
                total_score=0.0,
                social_score=0.0,
                technical_score=0.0,
                fundamental_score=0.0,
                analyst_score=0.0,
                structure_score=0.0,
                risk_level="unknown",
                opportunity_type="unknown",
                confidence_level=0.0,
                timestamp=datetime.now()
            )
    
    def _determine_risk_level(self, analysis: StockAnalysis, total_score: float) -> str:
        """Determine risk level based on various factors"""
        risk_factors = 0
        
        # High volatility indicators
        if analysis.technical_analysis.rsi > 80 or analysis.technical_analysis.rsi < 20:
            risk_factors += 1
        
        # High valuation
        if analysis.fundamental_data.pe_ratio and analysis.fundamental_data.pe_ratio > 50:
            risk_factors += 1
        
        # High social hype
        if analysis.social_sentiment.sentiment_score > 0.8:
            risk_factors += 1
        
        # High short interest
        if analysis.stock_structure.short_interest > 30:
            risk_factors += 1
        
        # Low score
        if total_score < 30:
            risk_factors += 1
        
        if risk_factors >= 3:
            return "high"
        elif risk_factors >= 1:
            return "medium"
        else:
            return "low"
    
    def _determine_opportunity_type(self, analysis: StockAnalysis) -> str:
        """Determine the type of opportunity"""
        # Short squeeze setup
        if (analysis.stock_structure.short_interest > 20 and
            analysis.social_sentiment.sentiment_score > 0.3 and
            analysis.social_sentiment.mentions > 100):
            return "short_squeeze"
        
        # Momentum play
        if (analysis.social_sentiment.sentiment_score > 0.5 and
            analysis.technical_analysis.trend_direction == TrendDirection.BULLISH and
            analysis.technical_analysis.volume_spike):
            return "momentum"
        
        # Value play
        if (analysis.fundamental_data.pe_ratio and analysis.fundamental_data.pe_ratio < 20 and
            analysis.analyst_coverage.consensus_rating in [AnalystRating.BUY, AnalystRating.STRONG_BUY]):
            return "value"
        
        # Growth play
        if (analysis.fundamental_data.revenue_growth_yoy and 
            analysis.fundamental_data.revenue_growth_yoy > 20 and
            analysis.analyst_coverage.price_target_upside > 15):
            return "growth"
        
        # Contrarian play
        if (analysis.social_sentiment.sentiment_score < -0.3 and
            analysis.analyst_coverage.consensus_rating in [AnalystRating.BUY, AnalystRating.STRONG_BUY]):
            return "contrarian"
        
        return "general"
    
    def _calculate_confidence(self, analysis: StockAnalysis) -> float:
        """Calculate confidence level in the analysis"""
        confidence_factors = []
        
        # Data quality factors
        if analysis.social_sentiment.mentions > 50:
            confidence_factors.append(0.2)
        
        if analysis.analyst_coverage.num_analysts > 5:
            confidence_factors.append(0.2)
        
        if analysis.technical_analysis.pattern_detected:
            confidence_factors.append(analysis.technical_analysis.pattern_confidence * 0.2)
        
        if analysis.fundamental_data.market_cap > 1000000000:  # $1B+ market cap
            confidence_factors.append(0.2)
        
        if analysis.stock_structure.shares_outstanding > 0:
            confidence_factors.append(0.2)
        
        return min(sum(confidence_factors), 1.0)