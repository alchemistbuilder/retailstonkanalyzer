from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from ..database.watchlist_models import (
    AssetType, AlertType, Priority, get_database_session
)
from ..services.watchlist_service import WatchlistService
from ..services.simple_market_data import SimpleMarketDataService

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

# Pydantic Models for API
class AddTickerRequest(BaseModel):
    symbol: str = Field(..., description="Stock/Crypto symbol (e.g., AAPL, ETH)")
    asset_type: AssetType = Field(default=AssetType.STOCK, description="Type of asset")
    priority: Priority = Field(default=Priority.MEDIUM, description="Watchlist priority")
    reason_added: Optional[str] = Field(None, description="Why this ticker was added")
    entry_price_target: Optional[float] = Field(None, description="Target entry price")
    exit_price_target: Optional[float] = Field(None, description="Target exit price")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    company_name: Optional[str] = Field(None, description="Company name")
    sector: Optional[str] = Field(None, description="Sector")
    exchange: Optional[str] = Field(None, description="Exchange")

class UpdateTickerNotesRequest(BaseModel):
    notes: str
    reason_added: Optional[str] = None

class UpdateTickerTargetsRequest(BaseModel):
    entry_price_target: Optional[float] = None
    exit_price_target: Optional[float] = None
    stop_loss: Optional[float] = None

class AddAlertRequest(BaseModel):
    symbol: str
    alert_type: AlertType
    alert_value: float
    priority: Priority = Priority.MEDIUM
    message: Optional[str] = None

class UpdateMarketDataRequest(BaseModel):
    symbol: str
    current_price: float
    price_change_24h: Optional[float] = None
    price_change_percent_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    rsi_14: Optional[float] = None
    macd_signal: Optional[str] = None

# Dependency to get watchlist service
def get_watchlist_service(db: Session = Depends(get_database_session)) -> WatchlistService:
    return WatchlistService(db)

# Ticker Management Endpoints
@router.post("/tickers", summary="Add ticker to watchlist")
async def add_ticker(
    request: AddTickerRequest,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Add a new ticker to the watchlist"""
    try:
        ticker = service.add_ticker(
            symbol=request.symbol,
            asset_type=request.asset_type,
            priority=request.priority,
            reason_added=request.reason_added,
            entry_price_target=request.entry_price_target,
            exit_price_target=request.exit_price_target,
            stop_loss=request.stop_loss,
            company_name=request.company_name,
            sector=request.sector,
            exchange=request.exchange
        )
        return {
            "success": True,
            "message": f"Added {request.symbol} to watchlist",
            "ticker": ticker.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding ticker: {str(e)}")

@router.get("/tickers", summary="Get all watchlist tickers")
async def get_tickers(
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset type"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    active_only: bool = Query(True, description="Show only active tickers"),
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Get all tickers from the watchlist"""
    try:
        tickers = service.get_all_tickers(
            asset_type=asset_type,
            priority=priority,
            active_only=active_only
        )
        return {
            "success": True,
            "count": len(tickers),
            "tickers": [ticker.to_dict() for ticker in tickers]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tickers: {str(e)}")

@router.get("/tickers/{symbol}", summary="Get specific ticker")
async def get_ticker(
    symbol: str,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Get a specific ticker from the watchlist"""
    try:
        ticker = service.get_ticker(symbol)
        if not ticker:
            raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found in watchlist")
        
        return {
            "success": True,
            "ticker": ticker.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ticker: {str(e)}")

@router.delete("/tickers/{symbol}", summary="Remove ticker from watchlist")
async def remove_ticker(
    symbol: str,
    soft_delete: bool = Query(True, description="Soft delete (deactivate) vs hard delete"),
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Remove a ticker from the watchlist"""
    try:
        success = service.remove_ticker(symbol, soft_delete=soft_delete)
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found in watchlist")
        
        return {
            "success": True,
            "message": f"Removed {symbol} from watchlist"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing ticker: {str(e)}")

@router.put("/tickers/{symbol}/notes", summary="Update ticker notes")
async def update_ticker_notes(
    symbol: str,
    request: UpdateTickerNotesRequest,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Update notes and reason for a ticker"""
    try:
        success = service.update_ticker_notes(
            symbol=symbol,
            notes=request.notes,
            reason_added=request.reason_added
        )
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found in watchlist")
        
        return {
            "success": True,
            "message": f"Updated notes for {symbol}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notes: {str(e)}")

@router.put("/tickers/{symbol}/targets", summary="Update ticker price targets")
async def update_ticker_targets(
    symbol: str,
    request: UpdateTickerTargetsRequest,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Update price targets for a ticker"""
    try:
        success = service.update_ticker_targets(
            symbol=symbol,
            entry_price_target=request.entry_price_target,
            exit_price_target=request.exit_price_target,
            stop_loss=request.stop_loss
        )
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found in watchlist")
        
        return {
            "success": True,
            "message": f"Updated targets for {symbol}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating targets: {str(e)}")

@router.put("/tickers/{symbol}/market-data", summary="Update ticker market data")
async def update_ticker_market_data(
    symbol: str,
    request: UpdateMarketDataRequest,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Update market data for a ticker (used by data collection services)"""
    try:
        success = service.update_ticker_market_data(
            symbol=symbol,
            current_price=request.current_price,
            price_change_24h=request.price_change_24h,
            price_change_percent_24h=request.price_change_percent_24h,
            volume_24h=request.volume_24h,
            market_cap=request.market_cap,
            rsi_14=request.rsi_14,
            macd_signal=request.macd_signal
        )
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found in watchlist")
        
        return {
            "success": True,
            "message": f"Updated market data for {symbol}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating market data: {str(e)}")

# Alert Management Endpoints
@router.post("/alerts", summary="Add alert for ticker")
async def add_alert(
    request: AddAlertRequest,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Add an alert for a ticker"""
    try:
        alert = service.add_alert(
            symbol=request.symbol,
            alert_type=request.alert_type,
            alert_value=request.alert_value,
            priority=request.priority,
            message=request.message
        )
        return {
            "success": True,
            "message": f"Added alert for {request.symbol}",
            "alert": alert.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding alert: {str(e)}")

@router.get("/alerts/{symbol}", summary="Get alerts for ticker")
async def get_ticker_alerts(
    symbol: str,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Get all alerts for a specific ticker"""
    try:
        alerts = service.get_alerts_for_ticker(symbol)
        return {
            "success": True,
            "symbol": symbol,
            "count": len(alerts),
            "alerts": [alert.to_dict() for alert in alerts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.delete("/alerts/{alert_id}", summary="Remove alert")
async def remove_alert(
    alert_id: int,
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Remove an alert"""
    try:
        success = service.remove_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        return {
            "success": True,
            "message": f"Removed alert {alert_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing alert: {str(e)}")

# Analytics Endpoints
@router.get("/summary", summary="Get watchlist summary")
async def get_watchlist_summary(
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Get summary statistics for the watchlist"""
    try:
        summary = service.get_watchlist_summary()
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")

@router.get("/movers", summary="Get top movers in watchlist")
async def get_top_movers(
    limit: int = Query(10, description="Number of top movers to return"),
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Get the biggest movers in the watchlist"""
    try:
        movers = service.get_top_movers(limit=limit)
        return {
            "success": True,
            "count": len(movers),
            "movers": [ticker.to_dict() for ticker in movers]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching movers: {str(e)}")

@router.get("/near-targets", summary="Get tickers near price targets")
async def get_tickers_near_targets(
    threshold_percent: float = Query(5.0, description="Threshold percentage for 'near' targets"),
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Get tickers that are near their entry/exit targets"""
    try:
        near_targets = service.get_tickers_near_targets(threshold_percent=threshold_percent)
        return {
            "success": True,
            "count": len(near_targets),
            "threshold_percent": threshold_percent,
            "tickers": near_targets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching near targets: {str(e)}")

# Bulk Operations
@router.post("/bulk/update-market-data", summary="Bulk update market data")
async def bulk_update_market_data(
    updates: List[UpdateMarketDataRequest],
    service: WatchlistService = Depends(get_watchlist_service)
):
    """Bulk update market data for multiple tickers"""
    try:
        results = []
        for update in updates:
            try:
                success = service.update_ticker_market_data(
                    symbol=update.symbol,
                    current_price=update.current_price,
                    price_change_24h=update.price_change_24h,
                    price_change_percent_24h=update.price_change_percent_24h,
                    volume_24h=update.volume_24h,
                    market_cap=update.market_cap,
                    rsi_14=update.rsi_14,
                    macd_signal=update.macd_signal
                )
                results.append({
                    "symbol": update.symbol,
                    "success": success,
                    "error": None
                })
            except Exception as e:
                results.append({
                    "symbol": update.symbol,
                    "success": False,
                    "error": str(e)
                })
        
        successful_updates = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "total_requested": len(updates),
            "successful_updates": successful_updates,
            "failed_updates": len(updates) - successful_updates,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in bulk update: {str(e)}")

# Market Data Update Endpoints
@router.post("/refresh", summary="Manual refresh of all market data")
async def refresh_market_data(background_tasks: BackgroundTasks):
    """Manually refresh market data for all watchlist tickers"""
    try:
        # Start refresh in background
        market_data_service = SimpleMarketDataService()
        background_tasks.add_task(market_data_service.update_all_watchlist_data)
        
        return {
            "success": True,
            "message": "Market data refresh started in background",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting refresh: {str(e)}")

@router.post("/refresh/{symbol}", summary="Refresh market data for specific ticker")
async def refresh_ticker_data(symbol: str, background_tasks: BackgroundTasks):
    """Manually refresh market data for a specific ticker"""
    try:
        market_data_service = SimpleMarketDataService()
        background_tasks.add_task(market_data_service.update_single_ticker, symbol.upper())
        
        return {
            "success": True,
            "message": f"Market data refresh started for {symbol}",
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing {symbol}: {str(e)}")

@router.get("/scheduler/status", summary="Get market data scheduler status")
async def get_scheduler_status():
    """Get the status of the market data updates"""
    return {
        "success": True,
        "scheduler": {
            "running": True,
            "update_interval_minutes": 10,
            "message": "Use manual refresh for now"
        }
    }

@router.post("/scheduler/start", summary="Start automatic market data updates")
async def start_scheduler(background_tasks: BackgroundTasks):
    """Start automatic market data updates (simplified)"""
    return {
        "success": True,
        "message": "Use manual refresh button for now. Auto-updates will be enhanced in next version.",
        "update_interval_minutes": 10
    }

@router.post("/scheduler/stop", summary="Stop automatic market data updates")
async def stop_scheduler():
    """Stop automatic market data updates"""
    return {
        "success": True,
        "message": "Manual refresh mode active"
    }

# Health Check
@router.get("/health", summary="Watchlist API health check")
async def health_check():
    """Health check for the watchlist API"""
    return {
        "status": "healthy",
        "service": "watchlist_api",
        "timestamp": datetime.utcnow().isoformat()
    }