from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from datetime import datetime

from ..core.stock_analyzer import StockAnalyzer, WatchlistAnalyzer
from ..models.stock_data import StockAnalysis
from ..core.config import settings

app = FastAPI(
    title="Retail Meme Stock Analyzer",
    description="API for analyzing retail meme stocks using social sentiment, technical analysis, fundamentals, analyst coverage, and stock structure",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
stock_analyzer = StockAnalyzer()
watchlist_analyzer = WatchlistAnalyzer()

# Global storage for latest analysis results (in production, use Redis/database)
latest_analyses: Dict[str, StockAnalysis] = {}
last_scan_time: Optional[datetime] = None


class AnalyzeRequest(BaseModel):
    symbols: List[str]
    company_names: Optional[List[str]] = None


class ScanResponse(BaseModel):
    status: str
    message: str
    symbols_analyzed: int
    timestamp: datetime


class StockSummary(BaseModel):
    symbol: str
    company_name: str
    total_score: float
    social_score: float
    technical_score: float
    fundamental_score: float
    analyst_score: float
    structure_score: float
    risk_level: str
    opportunity_type: str
    alerts_count: int
    last_updated: datetime


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Retail Meme Stock Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze",
            "scan": "/scan",
            "stock": "/stock/{symbol}",
            "watchlist": "/watchlist",
            "top_opportunities": "/top-opportunities",
            "alerts": "/alerts"
        },
        "status": "running"
    }


@app.post("/analyze", response_model=Dict[str, Optional[dict]])
async def analyze_stocks(request: AnalyzeRequest):
    """Analyze specific stocks"""
    try:
        print(f"Analyzing stocks: {request.symbols}")
        
        results = await stock_analyzer.analyze_multiple_stocks(request.symbols)
        
        # Convert StockAnalysis objects to dictionaries for JSON response
        response = {}
        for symbol, analysis in results.items():
            if analysis:
                response[symbol] = {
                    "symbol": analysis.symbol,
                    "company_name": analysis.company_name,
                    "composite_score": {
                        "total_score": analysis.composite_score.total_score,
                        "social_score": analysis.composite_score.social_score,
                        "technical_score": analysis.composite_score.technical_score,
                        "fundamental_score": analysis.composite_score.fundamental_score,
                        "analyst_score": analysis.composite_score.analyst_score,
                        "structure_score": analysis.composite_score.structure_score,
                        "risk_level": analysis.composite_score.risk_level,
                        "opportunity_type": analysis.composite_score.opportunity_type,
                        "confidence_level": analysis.composite_score.confidence_level
                    },
                    "alerts": [
                        {
                            "type": alert.alert_type,
                            "priority": alert.priority,
                            "reason": alert.trigger_reason,
                            "score": alert.score
                        } for alert in analysis.alerts
                    ],
                    "last_updated": analysis.last_updated.isoformat()
                }
                
                # Store in global cache
                latest_analyses[symbol] = analysis
            else:
                response[symbol] = None
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing stocks: {str(e)}")


@app.post("/scan", response_model=ScanResponse)
async def scan_watchlist(background_tasks: BackgroundTasks):
    """Scan the default watchlist in the background"""
    try:
        # Start background scan
        background_tasks.add_task(perform_watchlist_scan)
        
        return ScanResponse(
            status="started",
            message="Watchlist scan started in background",
            symbols_analyzed=len(settings.default_watchlist),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scan: {str(e)}")


async def perform_watchlist_scan():
    """Perform the actual watchlist scan"""
    global latest_analyses, last_scan_time
    
    try:
        print("Starting watchlist scan...")
        results = await watchlist_analyzer.analyze_watchlist()
        
        # Update global storage
        latest_analyses.update(results)
        last_scan_time = datetime.now()
        
        print(f"Watchlist scan completed. Analyzed {len(results)} stocks.")
        
    except Exception as e:
        print(f"Error in watchlist scan: {e}")


@app.get("/stock/{symbol}")
async def get_stock_analysis(symbol: str):
    """Get detailed analysis for a specific stock"""
    symbol = symbol.upper()
    
    if symbol not in latest_analyses:
        # If not in cache, analyze on demand
        analysis = await stock_analyzer.analyze_stock(symbol)
        if analysis:
            latest_analyses[symbol] = analysis
        else:
            raise HTTPException(status_code=404, detail=f"Could not analyze stock {symbol}")
    
    analysis = latest_analyses[symbol]
    
    return {
        "symbol": analysis.symbol,
        "company_name": analysis.company_name,
        "sector": analysis.sector,
        "industry": analysis.industry,
        "social_sentiment": {
            "platform": analysis.social_sentiment.platform,
            "mentions": analysis.social_sentiment.mentions,
            "sentiment_score": analysis.social_sentiment.sentiment_score,
            "volume_trend": analysis.social_sentiment.volume_trend.value,
            "top_keywords": analysis.social_sentiment.top_keywords,
            "influencer_mentions": analysis.social_sentiment.influencer_mentions
        },
        "technical_analysis": {
            "price": analysis.technical_analysis.price,
            "volume": analysis.technical_analysis.volume,
            "rsi": analysis.technical_analysis.rsi,
            "macd_signal": analysis.technical_analysis.macd_signal,
            "bollinger_position": analysis.technical_analysis.bollinger_position,
            "pattern_detected": analysis.technical_analysis.pattern_detected,
            "pattern_confidence": analysis.technical_analysis.pattern_confidence,
            "trend_direction": analysis.technical_analysis.trend_direction.value,
            "volume_spike": analysis.technical_analysis.volume_spike,
            "chart_images": analysis.technical_analysis.chart_images
        },
        "fundamental_data": {
            "market_cap": analysis.fundamental_data.market_cap,
            "pe_ratio": analysis.fundamental_data.pe_ratio,
            "ps_ratio": analysis.fundamental_data.ps_ratio,
            "revenue_growth_yoy": analysis.fundamental_data.revenue_growth_yoy,
            "profit_margin": analysis.fundamental_data.profit_margin,
            "debt_to_equity": analysis.fundamental_data.debt_to_equity,
            "current_ratio": analysis.fundamental_data.current_ratio,
            "roe": analysis.fundamental_data.roe
        },
        "analyst_coverage": {
            "consensus_rating": analysis.analyst_coverage.consensus_rating.value,
            "num_analysts": analysis.analyst_coverage.num_analysts,
            "avg_price_target": analysis.analyst_coverage.avg_price_target,
            "price_target_upside": analysis.analyst_coverage.price_target_upside,
            "recent_upgrades": analysis.analyst_coverage.recent_upgrades,
            "recent_downgrades": analysis.analyst_coverage.recent_downgrades
        },
        "stock_structure": {
            "shares_outstanding": analysis.stock_structure.shares_outstanding,
            "float_shares": analysis.stock_structure.float_shares,
            "short_interest": analysis.stock_structure.short_interest,
            "cost_to_borrow": analysis.stock_structure.cost_to_borrow,
            "utilization_rate": analysis.stock_structure.utilization_rate,
            "institutional_ownership": analysis.stock_structure.institutional_ownership,
            "short_squeeze_score": analysis.stock_structure.short_squeeze_score
        },
        "composite_score": {
            "total_score": analysis.composite_score.total_score,
            "social_score": analysis.composite_score.social_score,
            "technical_score": analysis.composite_score.technical_score,
            "fundamental_score": analysis.composite_score.fundamental_score,
            "analyst_score": analysis.composite_score.analyst_score,
            "structure_score": analysis.composite_score.structure_score,
            "risk_level": analysis.composite_score.risk_level,
            "opportunity_type": analysis.composite_score.opportunity_type,
            "confidence_level": analysis.composite_score.confidence_level
        },
        "alerts": [
            {
                "type": alert.alert_type,
                "priority": alert.priority,
                "reason": alert.trigger_reason,
                "score": alert.score,
                "timestamp": alert.timestamp.isoformat(),
                "chart_image_url": alert.chart_image_url
            } for alert in analysis.alerts
        ],
        "last_updated": analysis.last_updated.isoformat()
    }


@app.get("/watchlist", response_model=List[StockSummary])
async def get_watchlist_summary():
    """Get summary of all stocks in watchlist"""
    summaries = []
    
    for symbol, analysis in latest_analyses.items():
        if analysis and analysis.composite_score:
            summary = StockSummary(
                symbol=analysis.symbol,
                company_name=analysis.company_name,
                total_score=analysis.composite_score.total_score,
                social_score=analysis.composite_score.social_score,
                technical_score=analysis.composite_score.technical_score,
                fundamental_score=analysis.composite_score.fundamental_score,
                analyst_score=analysis.composite_score.analyst_score,
                structure_score=analysis.composite_score.structure_score,
                risk_level=analysis.composite_score.risk_level,
                opportunity_type=analysis.composite_score.opportunity_type,
                alerts_count=len(analysis.alerts),
                last_updated=analysis.last_updated
            )
            summaries.append(summary)
    
    # Sort by total score
    summaries.sort(key=lambda x: x.total_score, reverse=True)
    
    return summaries


@app.get("/top-opportunities")
async def get_top_opportunities(limit: int = 10, min_score: float = 70.0):
    """Get top opportunities from analyzed stocks"""
    opportunities = []
    
    for symbol, analysis in latest_analyses.items():
        if (analysis and analysis.composite_score and 
            analysis.composite_score.total_score >= min_score):
            opportunities.append(analysis)
    
    # Sort by score
    opportunities.sort(key=lambda x: x.composite_score.total_score, reverse=True)
    opportunities = opportunities[:limit]
    
    return [
        {
            "symbol": analysis.symbol,
            "company_name": analysis.company_name,
            "total_score": analysis.composite_score.total_score,
            "opportunity_type": analysis.composite_score.opportunity_type,
            "risk_level": analysis.composite_score.risk_level,
            "key_catalysts": [alert.trigger_reason for alert in analysis.alerts[:3]],
            "price": analysis.technical_analysis.price,
            "price_target_upside": analysis.analyst_coverage.price_target_upside,
            "short_interest": analysis.stock_structure.short_interest,
            "social_mentions": analysis.social_sentiment.mentions,
            "last_updated": analysis.last_updated.isoformat()
        } for analysis in opportunities
    ]


@app.get("/alerts")
async def get_alerts(priority: Optional[str] = None):
    """Get all alerts, optionally filtered by priority"""
    all_alerts = []
    
    for symbol, analysis in latest_analyses.items():
        if analysis and analysis.alerts:
            for alert in analysis.alerts:
                if priority is None or alert.priority == priority:
                    all_alerts.append({
                        "symbol": alert.symbol,
                        "type": alert.alert_type,
                        "priority": alert.priority,
                        "reason": alert.trigger_reason,
                        "score": alert.score,
                        "timestamp": alert.timestamp.isoformat()
                    })
    
    # Sort by score and timestamp
    all_alerts.sort(key=lambda x: (x["score"], x["timestamp"]), reverse=True)
    
    return all_alerts


@app.get("/status")
async def get_status():
    """Get API status and last scan information"""
    return {
        "status": "running",
        "stocks_in_cache": len(latest_analyses),
        "last_scan_time": last_scan_time.isoformat() if last_scan_time else None,
        "watchlist_size": len(settings.default_watchlist),
        "api_keys_configured": {
            "alpha_vantage": bool(settings.alpha_vantage_api_key),
            "polygon": bool(settings.polygon_api_key),
            "fmp": bool(settings.fmp_api_key),
            "ortex": bool(settings.ortex_api_key),
            "reddit": bool(settings.reddit_client_id),
            "twitter": bool(settings.twitter_bearer_token),
            "chart_img": bool(getattr(settings, 'chart_img_api_key', None))
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)