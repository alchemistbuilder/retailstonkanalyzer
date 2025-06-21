from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from ..models.stock_data import (
    StockAnalysis, SocialSentiment, AnalystCoverage, StockStructure,
    TechnicalAnalysis, AnalystRating, TrendDirection
)


class DivergenceType(Enum):
    RETAIL_BULLISH_INST_BEARISH = "retail_bullish_institutional_bearish"
    RETAIL_BEARISH_INST_BULLISH = "retail_bearish_institutional_bullish"
    SQUEEZE_SETUP = "short_squeeze_setup"
    MOMENTUM_DIVERGENCE = "momentum_divergence"
    VALUE_TRAP = "value_trap"
    HIDDEN_GEM = "hidden_gem"
    HYPE_BUBBLE = "hype_bubble"
    OVERSOLD_REVERSAL = "oversold_reversal"


@dataclass
class DivergenceSignal:
    symbol: str
    divergence_type: DivergenceType
    strength: float  # 0-1 scale
    confidence: float  # 0-1 scale
    description: str
    catalyst: Optional[str]
    timeframe: str  # "short", "medium", "long"
    risk_level: str  # "low", "medium", "high"
    expected_move: Optional[float]  # Expected price move percentage
    timestamp: datetime
    supporting_factors: List[str]
    warning_factors: List[str]


class RetailVsInstitutionalAnalyzer:
    def __init__(self):
        pass
    
    def detect_sentiment_divergence(self, 
                                  social: SocialSentiment, 
                                  analyst: AnalystCoverage) -> List[DivergenceSignal]:
        """Detect divergence between retail and institutional sentiment"""
        signals = []
        
        # Retail bullish, institutions bearish
        if (social.sentiment_score > 0.4 and 
            analyst.consensus_rating in [AnalystRating.SELL, AnalystRating.STRONG_SELL]):
            
            strength = min(social.sentiment_score + (5 - int(analyst.consensus_rating.value)) / 5, 1.0)
            
            signals.append(DivergenceSignal(
                symbol="",  # Will be filled by caller
                divergence_type=DivergenceType.RETAIL_BULLISH_INST_BEARISH,
                strength=strength,
                confidence=0.7 if analyst.num_analysts > 5 else 0.5,
                description=f"High retail optimism (sentiment: {social.sentiment_score:.2f}) vs analyst pessimism",
                catalyst="Retail FOMO vs institutional concerns",
                timeframe="short",
                risk_level="high",
                expected_move=-10.0,  # Expected downward correction
                timestamp=datetime.now(),
                supporting_factors=[
                    f"Retail sentiment: {social.sentiment_score:.2f}",
                    f"Analyst rating: {analyst.consensus_rating.value}",
                    f"Social mentions: {social.mentions}"
                ],
                warning_factors=[
                    "Potential bubble formation",
                    "Institutional selling pressure",
                    "Overvaluation risk"
                ]
            ))
        
        # Retail bearish, institutions bullish
        elif (social.sentiment_score < -0.3 and 
              analyst.consensus_rating in [AnalystRating.BUY, AnalystRating.STRONG_BUY]):
            
            strength = min(abs(social.sentiment_score) + int(analyst.consensus_rating.value) / 5, 1.0)
            
            signals.append(DivergenceSignal(
                symbol="",
                divergence_type=DivergenceType.RETAIL_BEARISH_INST_BULLISH,
                strength=strength,
                confidence=0.8 if analyst.num_analysts > 8 else 0.6,
                description=f"Retail pessimism (sentiment: {social.sentiment_score:.2f}) vs analyst optimism",
                catalyst="Institutional accumulation opportunity",
                timeframe="medium",
                risk_level="medium",
                expected_move=analyst.price_target_upside * 0.7,  # Conservative estimate
                timestamp=datetime.now(),
                supporting_factors=[
                    f"Strong analyst consensus: {analyst.consensus_rating.value}",
                    f"Price target upside: {analyst.price_target_upside:.1f}%",
                    f"Low retail interest: {social.mentions} mentions"
                ],
                warning_factors=[
                    "Need catalysts for retail adoption",
                    "May take time to materialize"
                ]
            ))
        
        return signals


class ShortSqueezeDetector:
    def __init__(self):
        self.min_short_interest = 15.0
        self.min_utilization = 80.0
        self.min_mentions = 100
    
    def detect_squeeze_setup(self, 
                           social: SocialSentiment,
                           structure: StockStructure,
                           technical: TechnicalAnalysis) -> List[DivergenceSignal]:
        """Detect potential short squeeze setups"""
        signals = []
        
        # Basic squeeze criteria
        high_short_interest = structure.short_interest > self.min_short_interest
        high_utilization = (structure.utilization_rate or 0) > self.min_utilization
        retail_interest = social.mentions > self.min_mentions
        positive_sentiment = social.sentiment_score > 0.2
        
        if high_short_interest and retail_interest and positive_sentiment:
            # Calculate squeeze strength
            strength = self._calculate_squeeze_strength(social, structure, technical)
            
            # Determine timeframe and risk
            timeframe = "short" if social.volume_trend == TrendDirection.BULLISH else "medium"
            risk_level = "high" if structure.short_interest > 30 else "medium"
            
            # Expected move based on short interest and sentiment
            expected_move = min(structure.short_interest * 2, 100.0)  # Cap at 100%
            
            supporting_factors = [
                f"Short interest: {structure.short_interest:.1f}%",
                f"Social mentions: {social.mentions}",
                f"Sentiment: {social.sentiment_score:.2f}"
            ]
            
            if high_utilization:
                supporting_factors.append(f"Utilization: {structure.utilization_rate:.1f}%")
            
            if structure.cost_to_borrow and structure.cost_to_borrow > 10:
                supporting_factors.append(f"Cost to borrow: {structure.cost_to_borrow:.1f}%")
            
            if technical.volume_spike:
                supporting_factors.append("Volume spike detected")
            
            warning_factors = [
                "High volatility expected",
                "Risk of rapid reversal",
                "Timing is crucial"
            ]
            
            if structure.float_shares / structure.shares_outstanding > 0.8:
                warning_factors.append("Large float may limit squeeze")
            
            signals.append(DivergenceSignal(
                symbol="",
                divergence_type=DivergenceType.SQUEEZE_SETUP,
                strength=strength,
                confidence=0.6 + (0.3 if high_utilization else 0) + (0.1 if technical.volume_spike else 0),
                description=f"Short squeeze setup: {structure.short_interest:.1f}% SI, {social.mentions} mentions",
                catalyst="Retail buying pressure vs short covering",
                timeframe=timeframe,
                risk_level=risk_level,
                expected_move=expected_move,
                timestamp=datetime.now(),
                supporting_factors=supporting_factors,
                warning_factors=warning_factors
            ))
        
        return signals
    
    def _calculate_squeeze_strength(self, 
                                  social: SocialSentiment,
                                  structure: StockStructure,
                                  technical: TechnicalAnalysis) -> float:
        """Calculate squeeze strength score (0-1)"""
        score = 0.0
        
        # Short interest component (0-0.4)
        score += min(structure.short_interest / 50, 0.4)
        
        # Social sentiment component (0-0.3)
        score += max(0, social.sentiment_score) * 0.3
        
        # Volume component (0-0.2)
        if social.mentions > 500:
            score += 0.2
        elif social.mentions > 200:
            score += 0.15
        elif social.mentions > 100:
            score += 0.1
        
        # Technical component (0-0.1)
        if technical.volume_spike:
            score += 0.1
        
        return min(score, 1.0)


class MomentumDivergenceDetector:
    def __init__(self):
        pass
    
    def detect_momentum_divergence(self,
                                 social: SocialSentiment,
                                 technical: TechnicalAnalysis,
                                 analyst: AnalystCoverage) -> List[DivergenceSignal]:
        """Detect momentum vs fundamental divergences"""
        signals = []
        
        # Strong social momentum but weak technicals
        if (social.sentiment_score > 0.6 and 
            social.volume_trend == TrendDirection.BULLISH and
            technical.trend_direction != TrendDirection.BULLISH):
            
            signals.append(DivergenceSignal(
                symbol="",
                divergence_type=DivergenceType.MOMENTUM_DIVERGENCE,
                strength=0.7,
                confidence=0.6,
                description="Strong social momentum not confirmed by technical analysis",
                catalyst="Social media hype",
                timeframe="short",
                risk_level="high",
                expected_move=None,
                timestamp=datetime.now(),
                supporting_factors=[
                    f"Social sentiment: {social.sentiment_score:.2f}",
                    f"Social trend: {social.volume_trend.value}",
                    f"Mentions: {social.mentions}"
                ],
                warning_factors=[
                    "Technical indicators not supportive",
                    "Momentum may be artificial",
                    "Risk of rapid reversal"
                ]
            ))
        
        return signals


class ValueTrapDetector:
    def __init__(self):
        pass
    
    def detect_value_trap(self,
                         fundamental,
                         analyst: AnalystCoverage,
                         technical: TechnicalAnalysis) -> List[DivergenceSignal]:
        """Detect potential value traps"""
        signals = []
        
        # Low valuation but declining business
        appears_cheap = (fundamental.pe_ratio and fundamental.pe_ratio < 15) or \
                       (fundamental.ps_ratio and fundamental.ps_ratio < 2)
        
        declining_business = (fundamental.revenue_growth_yoy and fundamental.revenue_growth_yoy < -10) or \
                           (fundamental.profit_margin and fundamental.profit_margin < 0)
        
        analyst_concerns = analyst.recent_downgrades > analyst.recent_upgrades
        
        if appears_cheap and (declining_business or analyst_concerns):
            signals.append(DivergenceSignal(
                symbol="",
                divergence_type=DivergenceType.VALUE_TRAP,
                strength=0.6,
                confidence=0.7,
                description="Appears cheap but fundamental issues present",
                catalyst="Business deterioration",
                timeframe="long",
                risk_level="medium",
                expected_move=-15.0,
                timestamp=datetime.now(),
                supporting_factors=[
                    f"P/E ratio: {fundamental.pe_ratio}" if fundamental.pe_ratio else "Low P/S ratio",
                    f"Recent downgrades: {analyst.recent_downgrades}"
                ],
                warning_factors=[
                    "Declining fundamentals",
                    "Analyst skepticism",
                    "Value may be deserved"
                ]
            ))
        
        return signals


class HiddenGemDetector:
    def __init__(self):
        pass
    
    def detect_hidden_gem(self,
                         social: SocialSentiment,
                         fundamental,
                         analyst: AnalystCoverage) -> List[DivergenceSignal]:
        """Detect hidden gems (good fundamentals, low attention)"""
        signals = []
        
        # Good fundamentals but low social attention
        good_fundamentals = (
            (fundamental.revenue_growth_yoy and fundamental.revenue_growth_yoy > 15) and
            (fundamental.profit_margin and fundamental.profit_margin > 10) and
            (fundamental.roe and fundamental.roe > 15)
        )
        
        strong_analyst_support = (
            analyst.consensus_rating in [AnalystRating.BUY, AnalystRating.STRONG_BUY] and
            analyst.price_target_upside > 20
        )
        
        low_retail_attention = social.mentions < 50 and abs(social.sentiment_score) < 0.3
        
        if good_fundamentals and strong_analyst_support and low_retail_attention:
            signals.append(DivergenceSignal(
                symbol="",
                divergence_type=DivergenceType.HIDDEN_GEM,
                strength=0.8,
                confidence=0.8,
                description="Strong fundamentals and analyst support with low retail attention",
                catalyst="Institutional accumulation",
                timeframe="long",
                risk_level="low",
                expected_move=analyst.price_target_upside * 0.8,
                timestamp=datetime.now(),
                supporting_factors=[
                    f"Revenue growth: {fundamental.revenue_growth_yoy:.1f}%",
                    f"ROE: {fundamental.roe:.1f}%",
                    f"Price target upside: {analyst.price_target_upside:.1f}%",
                    f"Analyst rating: {analyst.consensus_rating.value}"
                ],
                warning_factors=[
                    "May take time for market recognition",
                    "Requires patience"
                ]
            ))
        
        return signals


class DivergenceDetector:
    def __init__(self):
        self.retail_vs_institutional = RetailVsInstitutionalAnalyzer()
        self.squeeze_detector = ShortSqueezeDetector()
        self.momentum_detector = MomentumDivergenceDetector()
        self.value_trap_detector = ValueTrapDetector()
        self.hidden_gem_detector = HiddenGemDetector()
    
    def detect_all_divergences(self, analysis: StockAnalysis) -> List[DivergenceSignal]:
        """Detect all types of divergences for a stock"""
        all_signals = []
        
        try:
            # Retail vs institutional sentiment
            sentiment_signals = self.retail_vs_institutional.detect_sentiment_divergence(
                analysis.social_sentiment, analysis.analyst_coverage
            )
            all_signals.extend(sentiment_signals)
            
            # Short squeeze setups
            squeeze_signals = self.squeeze_detector.detect_squeeze_setup(
                analysis.social_sentiment, analysis.stock_structure, analysis.technical_analysis
            )
            all_signals.extend(squeeze_signals)
            
            # Momentum divergences
            momentum_signals = self.momentum_detector.detect_momentum_divergence(
                analysis.social_sentiment, analysis.technical_analysis, analysis.analyst_coverage
            )
            all_signals.extend(momentum_signals)
            
            # Value traps
            value_trap_signals = self.value_trap_detector.detect_value_trap(
                analysis.fundamental_data, analysis.analyst_coverage, analysis.technical_analysis
            )
            all_signals.extend(value_trap_signals)
            
            # Hidden gems
            hidden_gem_signals = self.hidden_gem_detector.detect_hidden_gem(
                analysis.social_sentiment, analysis.fundamental_data, analysis.analyst_coverage
            )
            all_signals.extend(hidden_gem_signals)
            
            # Set symbol for all signals
            for signal in all_signals:
                signal.symbol = analysis.symbol
            
        except Exception as e:
            print(f"Error detecting divergences for {analysis.symbol}: {e}")
        
        return all_signals
    
    def rank_signals_by_importance(self, signals: List[DivergenceSignal]) -> List[DivergenceSignal]:
        """Rank divergence signals by importance"""
        def signal_importance(signal: DivergenceSignal) -> float:
            # Base score from strength and confidence
            base_score = (signal.strength + signal.confidence) / 2
            
            # Type multipliers
            type_multipliers = {
                DivergenceType.SQUEEZE_SETUP: 1.5,
                DivergenceType.HIDDEN_GEM: 1.3,
                DivergenceType.RETAIL_BEARISH_INST_BULLISH: 1.2,
                DivergenceType.MOMENTUM_DIVERGENCE: 1.0,
                DivergenceType.RETAIL_BULLISH_INST_BEARISH: 0.8,
                DivergenceType.VALUE_TRAP: 0.7,
                DivergenceType.HYPE_BUBBLE: 0.6,
            }
            
            multiplier = type_multipliers.get(signal.divergence_type, 1.0)
            
            # Risk adjustment (lower risk = higher score)
            risk_adjustments = {"low": 1.2, "medium": 1.0, "high": 0.8}
            risk_adj = risk_adjustments.get(signal.risk_level, 1.0)
            
            return base_score * multiplier * risk_adj
        
        return sorted(signals, key=signal_importance, reverse=True)