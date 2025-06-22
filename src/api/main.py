from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from datetime import datetime
from pathlib import Path

from ..core.stock_analyzer import StockAnalyzer, WatchlistAnalyzer
from ..models.stock_data import StockAnalysis
from ..core.config import settings
from .watchlist_api import router as watchlist_router
from ..services.enhanced_analysis_generator import EnhancedAnalysisGenerator

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

# Include routers
app.include_router(watchlist_router)

# Mount static files for analysis pages
analysis_dir = Path("analysis_pages")
analysis_dir.mkdir(exist_ok=True)
app.mount("/analysis", StaticFiles(directory=str(analysis_dir), html=True), name="analysis")

# Initialize analyzers
stock_analyzer = StockAnalyzer()
watchlist_analyzer = WatchlistAnalyzer()
analysis_generator = EnhancedAnalysisGenerator()

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


# Moved to /api/stock/{symbol} for JSON data


@app.get("/api/watchlist-summary", response_model=List[StockSummary])
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


# Watchlist Dashboard Route (HTML)
@app.get("/watchlist", response_class=HTMLResponse)
async def get_watchlist_dashboard():
    """Serve the watchlist dashboard"""
    try:
        with open("watchlist_dashboard.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Watchlist dashboard not found")


# Generate Analysis Page Route
@app.post("/generate-analysis/{symbol}")
async def generate_analysis_page(symbol: str, background_tasks: BackgroundTasks):
    """Generate an analysis page for a specific symbol"""
    try:
        # Generate in background
        background_tasks.add_task(analysis_generator.generate_analysis_page, symbol.upper())
        
        return {
            "success": True,
            "message": f"Analysis page generation started for {symbol}",
            "symbol": symbol.upper()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")


# Generate All Watchlist Analyses
@app.post("/generate-all-analyses")
async def generate_all_analyses(background_tasks: BackgroundTasks):
    """Generate analysis pages for all watchlist stocks"""
    try:
        background_tasks.add_task(analysis_generator.generate_all_watchlist_pages)
        
        return {
            "success": True,
            "message": "Analysis generation started for all watchlist stocks"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analyses: {str(e)}")


# Serve analysis page directly
@app.get("/stock/{symbol}", response_class=HTMLResponse)
async def get_analysis_page(symbol: str):
    """Serve the analysis page for a specific stock"""
    try:
        analysis_file = f"analysis_pages/{symbol.lower()}_analysis.html"
        with open(analysis_file, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Analysis page for {symbol} not found. Try generating it first.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)