from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum


class TrendDirection(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class AnalystRating(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class SocialSentiment:
    platform: str
    mentions: int
    sentiment_score: float  # -1 to 1
    volume_trend: TrendDirection
    top_keywords: List[str]
    influencer_mentions: int
    timestamp: datetime
    subreddit_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class TechnicalAnalysis:
    price: float
    volume: int
    rsi: float
    macd_signal: str
    bollinger_position: float
    moving_averages: Dict[str, float]
    support_resistance: Dict[str, float]
    pattern_detected: Optional[str]
    pattern_confidence: float
    trend_direction: TrendDirection
    volume_spike: bool
    timestamp: datetime
    chart_images: Optional[Dict[str, str]] = field(default_factory=dict)


@dataclass
class FundamentalData:
    market_cap: float
    pe_ratio: Optional[float]
    ps_ratio: Optional[float]
    revenue_growth_yoy: Optional[float]
    profit_margin: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    roe: Optional[float]
    free_cash_flow: Optional[float]
    enterprise_value: Optional[float]
    book_value: Optional[float]
    timestamp: datetime


@dataclass
class AnalystCoverage:
    consensus_rating: AnalystRating
    num_analysts: int
    avg_price_target: float
    high_price_target: float
    low_price_target: float
    price_target_upside: float
    recent_upgrades: int
    recent_downgrades: int
    rating_changes_30d: List[Dict]
    analyst_firms: List[str]
    timestamp: datetime


@dataclass
class StockStructure:
    shares_outstanding: float
    float_shares: float
    short_interest: float
    short_ratio: float
    cost_to_borrow: Optional[float]
    utilization_rate: Optional[float]
    institutional_ownership: float
    insider_ownership: float
    days_to_cover: Optional[float]
    short_squeeze_score: float
    timestamp: datetime


@dataclass
class CompositeScore:
    total_score: float
    social_score: float
    technical_score: float
    fundamental_score: float
    analyst_score: float
    structure_score: float
    risk_level: str
    opportunity_type: str
    confidence_level: float
    timestamp: datetime


@dataclass
class StockAlert:
    symbol: str
    alert_type: str
    score: float
    trigger_reason: str
    priority: str
    social_catalyst: Optional[str]
    technical_catalyst: Optional[str]
    fundamental_catalyst: Optional[str]
    analyst_catalyst: Optional[str]
    structure_catalyst: Optional[str]
    timestamp: datetime
    chart_image_url: Optional[str] = None


@dataclass
class StockAnalysis:
    symbol: str
    company_name: str
    sector: str
    industry: str
    social_sentiment: SocialSentiment
    technical_analysis: TechnicalAnalysis
    fundamental_data: FundamentalData
    analyst_coverage: AnalystCoverage
    stock_structure: StockStructure
    composite_score: CompositeScore
    alerts: List[StockAlert] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_divergence_signals(self) -> Dict[str, str]:
        """Detect retail vs institutional sentiment divergence"""
        divergences = {}
        
        # High retail sentiment vs poor analyst rating
        if (self.social_sentiment.sentiment_score > 0.5 and 
            self.analyst_coverage.consensus_rating in [AnalystRating.SELL, AnalystRating.STRONG_SELL]):
            divergences["retail_vs_analyst"] = "retail_bullish_analyst_bearish"
            
        # Low retail sentiment vs strong analyst rating
        if (self.social_sentiment.sentiment_score < -0.3 and 
            self.analyst_coverage.consensus_rating in [AnalystRating.BUY, AnalystRating.STRONG_BUY]):
            divergences["retail_vs_analyst"] = "retail_bearish_analyst_bullish"
            
        # High short interest + positive retail sentiment = squeeze potential
        if (self.stock_structure.short_interest > 20 and 
            self.social_sentiment.sentiment_score > 0.3):
            divergences["squeeze_setup"] = "high_short_interest_positive_sentiment"
            
        return divergences
    
    def calculate_risk_reward(self) -> Dict[str, float]:
        """Calculate risk/reward metrics"""
        current_price = self.technical_analysis.price
        target_price = self.analyst_coverage.avg_price_target
        
        upside = (target_price - current_price) / current_price if target_price > 0 else 0
        
        # Risk factors
        risk_factors = []
        if self.fundamental_data.pe_ratio and self.fundamental_data.pe_ratio > 50:
            risk_factors.append("high_valuation")
        if self.stock_structure.short_interest > 30:
            risk_factors.append("high_short_interest")
        if self.social_sentiment.sentiment_score > 0.8:
            risk_factors.append("excessive_optimism")
            
        risk_score = len(risk_factors) / 3  # Normalize to 0-1
        
        return {
            "upside_potential": upside,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "risk_adjusted_return": upside * (1 - risk_score)
        }