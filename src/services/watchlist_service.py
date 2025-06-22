from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..database.watchlist_models import (
    WatchlistTicker, WatchlistAlert, WatchlistHistory, 
    AssetType, AlertType, Priority, WatchlistDatabase
)

class WatchlistService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # Ticker Management
    def add_ticker(self, 
                   symbol: str, 
                   asset_type: AssetType = AssetType.STOCK,
                   priority: Priority = Priority.MEDIUM,
                   reason_added: str = None,
                   entry_price_target: float = None,
                   exit_price_target: float = None,
                   stop_loss: float = None,
                   company_name: str = None,
                   sector: str = None,
                   exchange: str = None) -> WatchlistTicker:
        """Add a new ticker to the watchlist"""
        
        # Check if ticker already exists
        existing = self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.symbol == symbol.upper(), 
                 WatchlistTicker.is_active == True)
        ).first()
        
        if existing:
            raise ValueError(f"Ticker {symbol} is already in the active watchlist")
        
        new_ticker = WatchlistTicker(
            symbol=symbol.upper(),
            asset_type=asset_type,
            priority=priority,
            reason_added=reason_added,
            entry_price_target=entry_price_target,
            exit_price_target=exit_price_target,
            stop_loss=stop_loss,
            company_name=company_name,
            sector=sector,
            exchange=exchange,
            date_added=datetime.utcnow(),
            is_active=True
        )
        
        self.db.add(new_ticker)
        self.db.commit()
        self.db.refresh(new_ticker)
        
        return new_ticker
    
    def remove_ticker(self, symbol: str, soft_delete: bool = True) -> bool:
        """Remove a ticker from the watchlist"""
        ticker = self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.symbol == symbol.upper(), 
                 WatchlistTicker.is_active == True)
        ).first()
        
        if not ticker:
            return False
        
        if soft_delete:
            # Soft delete - just mark as inactive
            ticker.is_active = False
            # Also deactivate all alerts for this ticker
            alerts = self.db.query(WatchlistAlert).filter(
                WatchlistAlert.ticker_id == ticker.id
            ).all()
            for alert in alerts:
                alert.is_active = False
        else:
            # Hard delete
            self.db.delete(ticker)
        
        self.db.commit()
        return True
    
    def get_ticker(self, symbol: str) -> Optional[WatchlistTicker]:
        """Get a specific ticker from the watchlist"""
        return self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.symbol == symbol.upper(), 
                 WatchlistTicker.is_active == True)
        ).first()
    
    def get_all_tickers(self, 
                       asset_type: AssetType = None, 
                       priority: Priority = None,
                       active_only: bool = True) -> List[WatchlistTicker]:
        """Get all tickers from the watchlist with optional filters"""
        query = self.db.query(WatchlistTicker)
        
        if active_only:
            query = query.filter(WatchlistTicker.is_active == True)
        
        if asset_type:
            query = query.filter(WatchlistTicker.asset_type == asset_type)
            
        if priority:
            query = query.filter(WatchlistTicker.priority == priority)
        
        return query.order_by(
            WatchlistTicker.priority.desc(),
            WatchlistTicker.date_added.desc()
        ).all()
    
    def update_ticker_notes(self, symbol: str, notes: str, reason_added: str = None) -> bool:
        """Update ticker notes and reason"""
        ticker = self.get_ticker(symbol)
        if not ticker:
            return False
        
        ticker.notes = notes
        if reason_added:
            ticker.reason_added = reason_added
            
        self.db.commit()
        return True
    
    def update_ticker_targets(self, 
                             symbol: str, 
                             entry_price_target: float = None,
                             exit_price_target: float = None,
                             stop_loss: float = None) -> bool:
        """Update ticker price targets"""
        ticker = self.get_ticker(symbol)
        if not ticker:
            return False
        
        if entry_price_target is not None:
            ticker.entry_price_target = entry_price_target
        if exit_price_target is not None:
            ticker.exit_price_target = exit_price_target
        if stop_loss is not None:
            ticker.stop_loss = stop_loss
            
        self.db.commit()
        return True
    
    # Market Data Updates
    def update_ticker_market_data(self, 
                                 symbol: str,
                                 current_price: float,
                                 price_change_24h: float = None,
                                 price_change_percent_24h: float = None,
                                 volume_24h: float = None,
                                 market_cap: float = None,
                                 rsi_14: float = None,
                                 macd_signal: str = None) -> bool:
        """Update ticker with latest market data"""
        ticker = self.get_ticker(symbol)
        if not ticker:
            return False
        
        # Update price tracking
        if ticker.max_price_since_added is None or current_price > ticker.max_price_since_added:
            ticker.max_price_since_added = current_price
        if ticker.min_price_since_added is None or current_price < ticker.min_price_since_added:
            ticker.min_price_since_added = current_price
        
        # Update current market data
        ticker.current_price = current_price
        ticker.price_change_24h = price_change_24h
        ticker.price_change_percent_24h = price_change_percent_24h
        ticker.volume_24h = volume_24h
        ticker.market_cap = market_cap
        ticker.rsi_14 = rsi_14
        ticker.macd_signal = macd_signal
        ticker.date_last_checked = datetime.utcnow()
        
        self.db.commit()
        
        # Record historical data point
        self._record_historical_data(ticker)
        
        # Check alerts
        self._check_alerts_for_ticker(ticker)
        
        return True
    
    def _record_historical_data(self, ticker: WatchlistTicker):
        """Record a historical data point"""
        # Calculate distances to targets
        distance_to_entry = None
        distance_to_exit = None
        distance_to_stop = None
        
        if ticker.current_price and ticker.entry_price_target:
            distance_to_entry = ((ticker.current_price - ticker.entry_price_target) / ticker.entry_price_target) * 100
            
        if ticker.current_price and ticker.exit_price_target:
            distance_to_exit = ((ticker.exit_price_target - ticker.current_price) / ticker.current_price) * 100
            
        if ticker.current_price and ticker.stop_loss:
            distance_to_stop = ((ticker.current_price - ticker.stop_loss) / ticker.stop_loss) * 100
        
        history_entry = WatchlistHistory(
            ticker_id=ticker.id,
            symbol=ticker.symbol,
            price=ticker.current_price,
            volume=ticker.volume_24h,
            rsi_14=ticker.rsi_14,
            distance_to_entry=distance_to_entry,
            distance_to_exit=distance_to_exit,
            distance_to_stop=distance_to_stop
        )
        
        self.db.add(history_entry)
        self.db.commit()
    
    # Alert Management
    def add_alert(self, 
                  symbol: str, 
                  alert_type: AlertType, 
                  alert_value: float,
                  priority: Priority = Priority.MEDIUM,
                  message: str = None) -> WatchlistAlert:
        """Add an alert for a ticker"""
        ticker = self.get_ticker(symbol)
        if not ticker:
            raise ValueError(f"Ticker {symbol} not found in watchlist")
        
        alert = WatchlistAlert(
            ticker_id=ticker.id,
            symbol=symbol.upper(),
            alert_type=alert_type,
            alert_value=alert_value,
            priority=priority,
            message=message
        )
        
        self.db.add(alert)
        
        # Update ticker alert status
        ticker.has_active_alerts = True
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def remove_alert(self, alert_id: int) -> bool:
        """Remove an alert"""
        alert = self.db.query(WatchlistAlert).filter(WatchlistAlert.id == alert_id).first()
        if not alert:
            return False
        
        ticker_id = alert.ticker_id
        self.db.delete(alert)
        
        # Check if ticker still has active alerts
        remaining_alerts = self.db.query(WatchlistAlert).filter(
            and_(WatchlistAlert.ticker_id == ticker_id, 
                 WatchlistAlert.is_active == True)
        ).count()
        
        if remaining_alerts == 0:
            ticker = self.db.query(WatchlistTicker).filter(WatchlistTicker.id == ticker_id).first()
            if ticker:
                ticker.has_active_alerts = False
        
        self.db.commit()
        return True
    
    def get_alerts_for_ticker(self, symbol: str) -> List[WatchlistAlert]:
        """Get all alerts for a specific ticker"""
        return self.db.query(WatchlistAlert).filter(
            and_(WatchlistAlert.symbol == symbol.upper(),
                 WatchlistAlert.is_active == True)
        ).all()
    
    def _check_alerts_for_ticker(self, ticker: WatchlistTicker):
        """Check and trigger alerts for a ticker"""
        if not ticker.current_price:
            return
        
        alerts = self.get_alerts_for_ticker(ticker.symbol)
        
        for alert in alerts:
            triggered = False
            
            if alert.alert_type == AlertType.PRICE_ABOVE and ticker.current_price >= alert.alert_value:
                triggered = True
            elif alert.alert_type == AlertType.PRICE_BELOW and ticker.current_price <= alert.alert_value:
                triggered = True
            elif alert.alert_type == AlertType.RSI_OVERSOLD and ticker.rsi_14 and ticker.rsi_14 <= alert.alert_value:
                triggered = True
            elif alert.alert_type == AlertType.RSI_OVERBOUGHT and ticker.rsi_14 and ticker.rsi_14 >= alert.alert_value:
                triggered = True
            # Add more alert type checks as needed
            
            if triggered:
                alert.date_triggered = datetime.utcnow()
                alert.times_triggered += 1
                ticker.last_alert_triggered = datetime.utcnow()
                ticker.times_alerted += 1
                
                # For now, just mark as triggered. Later you can add notification logic
                print(f"🚨 ALERT TRIGGERED: {ticker.symbol} - {alert.alert_type.value} at {ticker.current_price}")
                
        self.db.commit()
    
    # Analytics and Reporting
    def get_watchlist_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the watchlist"""
        total_tickers = self.db.query(WatchlistTicker).filter(WatchlistTicker.is_active == True).count()
        
        high_priority = self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.is_active == True, 
                 WatchlistTicker.priority == Priority.HIGH)
        ).count()
        
        with_alerts = self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.is_active == True, 
                 WatchlistTicker.has_active_alerts == True)
        ).count()
        
        # Get tickers that hit entry targets (within 5%)
        near_entry_targets = self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.is_active == True,
                 WatchlistTicker.current_price.isnot(None),
                 WatchlistTicker.entry_price_target.isnot(None))
        ).all()
        
        near_entry_count = 0
        for ticker in near_entry_targets:
            if ticker.current_price and ticker.entry_price_target:
                diff_percent = abs((ticker.current_price - ticker.entry_price_target) / ticker.entry_price_target) * 100
                if diff_percent <= 5:  # Within 5%
                    near_entry_count += 1
        
        return {
            'total_tickers': total_tickers,
            'high_priority_tickers': high_priority,
            'tickers_with_alerts': with_alerts,
            'near_entry_targets': near_entry_count,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def get_top_movers(self, limit: int = 10) -> List[WatchlistTicker]:
        """Get the biggest movers in the watchlist"""
        return self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.is_active == True,
                 WatchlistTicker.price_change_percent_24h.isnot(None))
        ).order_by(
            desc(WatchlistTicker.price_change_percent_24h)
        ).limit(limit).all()
    
    def get_tickers_near_targets(self, threshold_percent: float = 5) -> List[Dict[str, Any]]:
        """Get tickers that are near their entry/exit targets"""
        tickers = self.db.query(WatchlistTicker).filter(
            and_(WatchlistTicker.is_active == True,
                 WatchlistTicker.current_price.isnot(None))
        ).all()
        
        near_targets = []
        
        for ticker in tickers:
            result = {'ticker': ticker.to_dict()}
            
            if ticker.entry_price_target:
                diff = abs((ticker.current_price - ticker.entry_price_target) / ticker.entry_price_target) * 100
                if diff <= threshold_percent:
                    result['near_entry'] = True
                    result['entry_distance_percent'] = diff
            
            if ticker.exit_price_target:
                diff = abs((ticker.current_price - ticker.exit_price_target) / ticker.exit_price_target) * 100
                if diff <= threshold_percent:
                    result['near_exit'] = True
                    result['exit_distance_percent'] = diff
            
            if 'near_entry' in result or 'near_exit' in result:
                near_targets.append(result)
        
        return near_targets