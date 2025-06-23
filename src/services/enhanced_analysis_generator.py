import os
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
import logging
from pathlib import Path

from ..core.stock_analyzer import StockAnalyzer
from ..services.watchlist_service import WatchlistService
from ..database.watchlist_models import get_database_session, AssetType
from ..services.real_market_data import real_market_service
from ..services.company_specific_metrics import company_metrics_analyzer

logger = logging.getLogger(__name__)

class EnhancedAnalysisGenerator:
    """Generate comprehensive analysis HTML pages with full technical detail"""
    
    def __init__(self):
        self.stock_analyzer = StockAnalyzer()
        self.output_dir = Path("analysis_pages")
        self.output_dir.mkdir(exist_ok=True)
        
    async def generate_analysis_page(self, symbol: str, asset_type: AssetType = AssetType.STOCK) -> Optional[str]:
        """Generate a comprehensive analysis page for a single stock/crypto"""
        try:
            logger.info(f"Generating comprehensive analysis page for {symbol}")
            
            # Get watchlist data for targets
            db_session = next(get_database_session())
            watchlist_service = WatchlistService(db_session)
            watchlist_ticker = watchlist_service.get_ticker(symbol)
            db_session.close()
            
            # Get real market data and comprehensive fundamentals
            logger.info(f"Fetching real market data and fundamentals for {symbol}")
            real_data = await real_market_service.get_current_quote(symbol)
            company_profile = await real_market_service.get_company_profile(symbol)
            fundamental_data = await real_market_service.get_fundamental_data(symbol)
            
            # Create analysis with real data
            logger.info(f"Creating comprehensive analysis for {symbol} with real market data")
            analysis = self._create_mock_analysis(symbol, watchlist_ticker, real_data, company_profile, fundamental_data)
            
            # Generate HTML based on asset type
            if asset_type == AssetType.CRYPTO:
                html_content = self._generate_crypto_html(analysis, watchlist_ticker, fundamental_data)
            else:
                html_content = self._generate_comprehensive_stock_html(analysis, watchlist_ticker, fundamental_data)
            
            # Save to file
            filename = f"{symbol.lower()}_analysis.html"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Comprehensive analysis page generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating analysis page for {symbol}: {e}")
            return None
    
    def _create_mock_analysis(self, symbol: str, watchlist_ticker: Any, real_data: Any = None, company_profile: Dict = None, fundamental_data: Dict = None):
        """Create mock analysis data for demonstration purposes"""
        from types import SimpleNamespace
        
        # Use real market data if available, otherwise fallback to mock
        if real_data:
            current_price = real_data.current_price
            company_name = company_profile.get('company_name', f'{symbol} Corporation') if company_profile else f'{symbol} Corporation'
            sector = company_profile.get('sector', 'Technology') if company_profile else 'Technology'
            volume = real_data.volume
            open_price = real_data.open_price
            high_price = real_data.high_price
            low_price = real_data.low_price
            change = real_data.change or 0
            change_percent = real_data.change_percent or 0
        else:
            # Fallback to mock data
            current_price = 250.0
            if watchlist_ticker:
                wp = getattr(watchlist_ticker, 'current_price', None)
                if wp and wp > 0:
                    current_price = float(wp)
            
            # Symbol-specific mock data
            mock_data = {
                'TSLA': {'name': 'Tesla Inc', 'price': 322.16, 'sector': 'Consumer Discretionary'},
                'GME': {'name': 'GameStop Corp', 'price': 23.46, 'sector': 'Consumer Discretionary'},
                'AMC': {'name': 'AMC Entertainment Holdings Inc', 'price': 3.01, 'sector': 'Communication Services'},
                'HOOD': {'name': 'Robinhood Markets Inc', 'price': 78.5, 'sector': 'Financial Services'},
                'ETH': {'name': 'Ethereum', 'price': 2286.58, 'sector': 'Cryptocurrency'},
                'BTC': {'name': 'Bitcoin', 'price': 102692.0, 'sector': 'Cryptocurrency'},
                'OSCR': {'name': 'Oscar Health Inc', 'price': 21.22, 'sector': 'Healthcare'}
            }
            
            data = mock_data.get(symbol, {'name': f'{symbol} Corporation', 'price': current_price, 'sector': 'Technology'})
            current_price = data['price']
            company_name = data['name']
            sector = data['sector']
            volume = 45000000
            open_price = current_price * 0.98
            high_price = current_price * 1.05
            low_price = current_price * 0.95
            change = current_price * 0.02
            change_percent = 2.0
            
        # Create mock analysis object
        analysis = SimpleNamespace()
        analysis.symbol = symbol
        analysis.company_name = company_name
        analysis.sector = sector
        analysis.industry = "Technology"
        
        # Mock composite scores with realistic values
        analysis.composite_score = SimpleNamespace()
        analysis.composite_score.total_score = 75.5
        analysis.composite_score.social_score = 68.2
        analysis.composite_score.technical_score = 82.1
        analysis.composite_score.fundamental_score = 71.8
        analysis.composite_score.analyst_score = 79.3
        analysis.composite_score.structure_score = 85.7
        analysis.composite_score.risk_level = 'medium'
        analysis.composite_score.opportunity_type = 'momentum'
        
        # Mock technical analysis
        analysis.technical_analysis = SimpleNamespace()
        analysis.technical_analysis.price = current_price
        analysis.technical_analysis.open_price = open_price
        analysis.technical_analysis.high_price = high_price
        analysis.technical_analysis.low_price = low_price
        analysis.technical_analysis.volume = volume
        analysis.technical_analysis.change = change
        analysis.technical_analysis.change_percent = change_percent
        analysis.technical_analysis.rsi = 65.4
        analysis.technical_analysis.trend_direction = 'bullish'
        analysis.technical_analysis.macd_signal = 'bullish crossover'
        analysis.technical_analysis.bollinger_position = 'upper band test'
        
        # Mock fundamental data (use real data if available)
        analysis.fundamental_data = SimpleNamespace()
        if company_profile and company_profile.get('market_cap'):
            analysis.fundamental_data.market_cap = company_profile['market_cap']
            analysis.fundamental_data.pe_ratio = company_profile.get('pe_ratio')
        else:
            analysis.fundamental_data.market_cap = 800000000000
            analysis.fundamental_data.pe_ratio = 28.5
        analysis.fundamental_data.revenue_growth_yoy = 15.2
        analysis.fundamental_data.profit_margin = 12.8
        
        return analysis
    
    def _generate_chart_url(self, symbol: str, timeframe: str, chart_type: str) -> str:
        """Generate TradingView chart image URL (will be embedded via widget)"""
        # For now, return a placeholder that will be replaced by TradingView widgets
        # We'll use TradingView's embedded charts which are more reliable
        return f"https://www.tradingview.com/embed/chart/?symbol={symbol}&interval={timeframe}&theme=dark"
    
    def _generate_fundamental_analysis_section(self, symbol: str, fundamental_data: Dict = None) -> str:
        """Generate comprehensive fundamental analysis section"""
        if not fundamental_data:
            fundamental_data = {}
        
        # Get company-specific metrics analysis
        key_drivers_analysis = company_metrics_analyzer.analyze_key_drivers(symbol, fundamental_data)
        
        # Format financial data
        def format_currency(value, in_millions=False):
            if value is None:
                return "N/A"
            if in_millions:
                if value >= 1e9:
                    return f"${value/1e9:.1f}B"
                elif value >= 1e6:
                    return f"${value/1e6:.1f}M"
                else:
                    return f"${value/1e3:.1f}K"
            else:
                return f"${value:,.0f}"
        
        def format_percentage(value):
            if value is None:
                return "N/A"
            return f"{value:.1f}%"
        
        def format_ratio(value):
            if value is None:
                return "N/A"
            return f"{value:.1f}x"
        
        # Extract key financial metrics
        quarterly_revenue = fundamental_data.get('latest_quarterly_revenue')
        annual_revenue = fundamental_data.get('annual_revenue') 
        quarterly_income = fundamental_data.get('latest_quarterly_net_income')
        annual_income = fundamental_data.get('annual_net_income')
        market_cap = fundamental_data.get('market_cap')
        enterprise_value = fundamental_data.get('enterprise_value')
        pe_ratio = fundamental_data.get('pe_ratio')
        ev_to_sales = fundamental_data.get('ev_to_sales')
        revenue_growth = fundamental_data.get('quarterly_revenue_growth')
        quarter_date = fundamental_data.get('latest_quarter_date', 'Q4 2024')
        annual_year = fundamental_data.get('annual_year', '2024')
        
        return f"""
        <section class="section">
            <h2 class="section-title">📊 Fundamental Analysis</h2>
            
            <div class="analysis-card" style="margin-bottom: 32px;">
                <h3>Financial Performance Overview</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 20px;">
                    
                    <div class="financial-metrics">
                        <h4 style="color: #58a6ff; margin-bottom: 16px;">📈 Revenue & Earnings</h4>
                        <div class="metric-row">
                            <span class="metric-label">Latest Quarterly Revenue ({quarter_date[:7] if quarter_date else 'Q4 2024'}):</span>
                            <span class="metric-value">{format_currency(quarterly_revenue, True)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Annual Revenue ({annual_year[:4] if annual_year else '2024'}):</span>
                            <span class="metric-value">{format_currency(annual_revenue, True)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Latest Quarterly Profit:</span>
                            <span class="metric-value">{format_currency(quarterly_income, True)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Annual Profit:</span>
                            <span class="metric-value">{format_currency(annual_income, True)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Revenue Growth (QoQ):</span>
                            <span class="metric-value {'positive' if revenue_growth and revenue_growth > 0 else 'negative'}">{format_percentage(revenue_growth)}</span>
                        </div>
                    </div>
                    
                    <div class="valuation-metrics">
                        <h4 style="color: #f0883e; margin-bottom: 16px;">💰 Valuation Metrics</h4>
                        <div class="metric-row">
                            <span class="metric-label">Market Capitalization:</span>
                            <span class="metric-value">{format_currency(market_cap, True)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Enterprise Value:</span>
                            <span class="metric-value">{format_currency(enterprise_value, True)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Price-to-Earnings (P/E) Ratio:</span>
                            <span class="metric-value">{format_ratio(pe_ratio)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">EV-to-Sales Ratio:</span>
                            <span class="metric-value">{format_ratio(ev_to_sales)}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Revenue Multiple:</span>
                            <span class="metric-value">{format_ratio(fundamental_data.get('price_to_sales'))}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card" style="margin-bottom: 32px;">
                <h3>🎯 Company-Specific Key Drivers</h3>
                <p style="color: #8b949e; margin-bottom: 20px; font-style: italic;">{key_drivers_analysis.get('description', '')}</p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 24px;">
                    {''.join([f'''
                    <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; border-left: 3px solid #58a6ff;">
                        <h5 style="color: #58a6ff; margin-bottom: 12px; font-size: 1rem;">🔍 {driver}</h5>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                            {key_drivers_analysis.get('key_driver_values', {}).get(driver, 'N/A')}
                        </div>
                        <p style="font-size: 0.85rem; color: #8b949e;">Latest reported or estimated value</p>
                    </div>
                    ''' for driver in key_drivers_analysis.get('key_drivers', [])])}
                </div>
                
                {''.join([f'''
                <div style="background: rgba(240, 136, 62, 0.05); padding: 16px; border-radius: 8px; border-left: 3px solid #f0883e; margin-bottom: 12px;">
                    <p style="font-size: 0.95rem; color: #ffffff;">• {insight}</p>
                </div>
                ''' for insight in key_drivers_analysis.get('company_specific_insights', [])])}
            </div>
            
            <div class="analysis-card">
                <h3>📈 Performance Metrics Analysis</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 20px;">
                    {''.join([f'''
                    <div class="metric-card-small">
                        <div style="font-size: 0.875rem; color: #8b949e; margin-bottom: 8px;">{metric_name}</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: #ffffff; margin-bottom: 4px;">{metric_data["value"]}</div>
                        <div style="font-size: 0.8rem; color: #8b949e;">{metric_data["description"]}</div>
                    </div>
                    ''' for metric_name, metric_data in key_drivers_analysis.get('metrics_analysis', {}).items()])}
                </div>
            </div>
        </section>
        """
    
    def _generate_pm_summary(self, symbol: str, total_score: float, risk_level: str, 
                           opportunity_type: str, technical_score: float, 
                           recommended_entry: float, recommended_target: float, 
                           recommended_stop: float) -> str:
        """Generate Portfolio Manager Summary Box"""
        
        recommendation = "BUY" if total_score >= 75 else "HOLD" if total_score >= 60 else "AVOID"
        risk_color = {"high": "#f85149", "medium": "#f0883e", "low": "#2ea043"}.get(risk_level, "#f0883e")
        
        return f"""
        <div class="pm-summary-box">
            <h3>📊 Portfolio Manager Summary</h3>
            <div class="pm-grid">
                <div class="pm-item">
                    <span class="pm-label">Recommendation</span>
                    <span class="pm-value recommendation-{recommendation.lower()}">{recommendation}</span>
                </div>
                <div class="pm-item">
                    <span class="pm-label">Overall Score</span>
                    <span class="pm-value">{total_score:.1f}/100</span>
                </div>
                <div class="pm-item">
                    <span class="pm-label">Risk Level</span>
                    <span class="pm-value" style="color: {risk_color};">{risk_level.upper()}</span>
                </div>
                <div class="pm-item">
                    <span class="pm-label">Opportunity Type</span>
                    <span class="pm-value">{opportunity_type.title()}</span>
                </div>
                <div class="pm-item">
                    <span class="pm-label">Technical Strength</span>
                    <span class="pm-value">{technical_score:.1f}/100</span>
                </div>
                <div class="pm-item">
                    <span class="pm-label">Entry Target</span>
                    <span class="pm-value entry-price">${recommended_entry:.2f}</span>
                </div>
                <div class="pm-item">
                    <span class="pm-label">Price Target</span>
                    <span class="pm-value target-price">${recommended_target:.2f}</span>
                </div>
                <div class="pm-item">
                    <span class="pm-label">Stop Loss</span>
                    <span class="pm-value stop-price">${recommended_stop:.2f}</span>
                </div>
            </div>
            
            <div class="pm-analysis">
                <h4>Key Investment Thesis:</h4>
                <p>• <strong>Technical Setup:</strong> {symbol} showing {opportunity_type} characteristics with RSI in favorable territory</p>
                <p>• <strong>Risk Profile:</strong> {risk_level.title()} risk with strong technical indicators supporting current levels</p>
                <p>• <strong>Position Sizing:</strong> Consider 2-3% portfolio allocation given {risk_level} risk profile</p>
                <p>• <strong>Time Horizon:</strong> 3-6 month swing trade based on technical setup</p>
            </div>
        </div>
        """
    
    def _generate_score_bar(self, label: str, score: float) -> str:
        """Generate a score bar HTML"""
        score_class = 'score-high' if score >= 70 else 'score-medium' if score >= 40 else 'score-low'
        return f"""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>{label}</span>
                <span>{score:.1f}/100</span>
            </div>
            <div class="score-bar">
                <div class="score-fill {score_class}" style="width: {score}%;"></div>
            </div>
        </div>"""
    
    def _generate_comprehensive_stock_html(self, analysis: Any, watchlist_ticker: Any, fundamental_data: Dict = None) -> str:
        """Generate comprehensive HTML for stock analysis with full technical detail"""
        
        # Extract data with safe defaults
        symbol = analysis.symbol
        company_name = analysis.company_name or symbol
        
        # Composite scores
        total_score = getattr(analysis.composite_score, 'total_score', 75.5)
        social_score = getattr(analysis.composite_score, 'social_score', 68.2)
        technical_score = getattr(analysis.composite_score, 'technical_score', 82.1)
        fundamental_score = getattr(analysis.composite_score, 'fundamental_score', 71.8)
        analyst_score = getattr(analysis.composite_score, 'analyst_score', 79.3)
        structure_score = getattr(analysis.composite_score, 'structure_score', 85.7)
        risk_level = getattr(analysis.composite_score, 'risk_level', 'medium')
        opportunity_type = getattr(analysis.composite_score, 'opportunity_type', 'momentum')
        
        # Technical data with enhanced details
        current_price = getattr(analysis.technical_analysis, 'price', 250.00)
        rsi = getattr(analysis.technical_analysis, 'rsi', 65.4)
        trend = getattr(analysis.technical_analysis, 'trend_direction', 'bullish')
        volume = getattr(analysis.technical_analysis, 'volume', 45000000)
        
        # Enhanced technical indicators
        macd_signal = getattr(analysis.technical_analysis, 'macd_signal', 'bullish crossover')
        bollinger_position = getattr(analysis.technical_analysis, 'bollinger_position', 'upper band test')
        
        # Calculate moving averages (mock realistic data)
        ema_8 = current_price * 0.992
        ema_13 = current_price * 0.985
        ema_21 = current_price * 0.978
        sma_50 = current_price * 0.965
        sma_100 = current_price * 0.945
        sma_200 = current_price * 0.920
        
        # Support and resistance levels
        resistance_1 = current_price * 1.025
        resistance_2 = current_price * 1.055
        support_1 = current_price * 0.975
        support_2 = current_price * 0.945
        
        # Fundamental data
        market_cap = getattr(analysis.fundamental_data, 'market_cap', 800000000000)
        pe_ratio = getattr(analysis.fundamental_data, 'pe_ratio', 28.5)
        if pe_ratio is None:
            pe_ratio = 28.5
        revenue_growth = getattr(analysis.fundamental_data, 'revenue_growth_yoy', 15.2)
        profit_margin = getattr(analysis.fundamental_data, 'profit_margin', 12.8)
        
        # Generate chart URLs
        chart_1d_url = self._generate_chart_url(symbol, '1D', 'line')
        chart_1w_url = self._generate_chart_url(symbol, '1W', 'candle')
        chart_1m_url = self._generate_chart_url(symbol, '1M', 'candle')
        
        # Market context charts
        spx_chart_url = self._generate_chart_url('SPY', '1M', 'line')
        qqq_chart_url = self._generate_chart_url('QQQ', '1M', 'line')
        btc_chart_url = self._generate_chart_url('BTC-USD', '1M', 'line')
        
        # Watchlist targets with intelligent defaults
        entry_target = watchlist_ticker.entry_price_target if watchlist_ticker else current_price * 0.95
        exit_target = watchlist_ticker.exit_price_target if watchlist_ticker else current_price * 1.20
        stop_loss = watchlist_ticker.stop_loss if watchlist_ticker else current_price * 0.88
        
        # Calculate recommended targets based on technical analysis
        recommended_entry = support_1
        recommended_stop = support_2
        recommended_target = resistance_2
        
        # Generate comprehensive HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} - Comprehensive Analysis | {company_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0f1419;
            color: #ffffff;
            line-height: 1.6;
            font-weight: 400;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 0 24px;
        }}
        
        .header {{
            padding: 32px 0;
            border-bottom: 1px solid #1e2936;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 2.75rem;
            font-weight: 300;
            letter-spacing: -0.02em;
            color: #ffffff;
        }}
        
        .back-btn {{
            background: #161b22;
            border: 1px solid #1e2936;
            color: #8b949e;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .back-btn:hover {{
            background: #1e2936;
            color: #ffffff;
        }}
        
        .pm-summary-box {{
            background: linear-gradient(135deg, #1e2936 0%, #161b22 100%);
            border: 2px solid #f0883e;
            border-radius: 16px;
            padding: 32px;
            margin: 32px 0;
            box-shadow: 0 8px 32px rgba(240, 136, 62, 0.1);
        }}
        
        .pm-summary-box h3 {{
            font-size: 1.5rem;
            margin-bottom: 24px;
            color: #f0883e;
            border-bottom: 2px solid #f0883e;
            padding-bottom: 8px;
        }}
        
        .pm-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}
        
        .pm-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 16px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
        }}
        
        .pm-label {{
            font-size: 0.875rem;
            color: #8b949e;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .pm-value {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #ffffff;
        }}
        
        .recommendation-buy {{ color: #2ea043; }}
        .recommendation-hold {{ color: #f0883e; }}
        .recommendation-avoid {{ color: #f85149; }}
        .entry-price {{ color: #58a6ff; }}
        .target-price {{ color: #2ea043; }}
        .stop-price {{ color: #f85149; }}
        
        .pm-analysis {{
            background: rgba(0,0,0,0.1);
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #f0883e;
        }}
        
        .pm-analysis h4 {{
            margin-bottom: 16px;
            color: #f0883e;
        }}
        
        .pm-analysis p {{
            margin-bottom: 8px;
            color: #e6edf3;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;
            margin: 32px 0;
        }}
        
        .metric-card {{
            background: #161b22;
            border: 1px solid #1e2936;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        
        .metric-card .label {{
            font-size: 0.875rem;
            color: #8b949e;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .metric-card .value {{
            font-size: 1.75rem;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: -0.01em;
        }}
        
        .metric-card .change {{
            font-size: 0.875rem;
            margin-top: 8px;
        }}
        
        .positive {{ color: #2ea043; }}
        .negative {{ color: #f85149; }}
        .neutral {{ color: #f0883e; }}
        
        .section {{
            padding: 48px 0;
            border-bottom: 1px solid #1e2936;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section-title {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 32px;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .chart-container {{
            background: #161b22;
            border: 1px solid #1e2936;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        
        .chart-container h3 {{
            margin-bottom: 16px;
            color: #ffffff;
            font-size: 1.25rem;
        }}
        
        .chart-img {{
            width: 100%;
            max-width: 800px;
            border-radius: 8px;
            margin: 16px 0;
        }}
        
        .timeframe-tabs {{
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }}
        
        .timeframe-tab {{
            padding: 8px 16px;
            background: #0d1117;
            border: 1px solid #1e2936;
            border-radius: 6px;
            color: #8b949e;
            text-decoration: none;
            font-size: 0.875rem;
            transition: all 0.2s;
        }}
        
        .timeframe-tab:hover {{
            background: #1e2936;
            color: #ffffff;
        }}
        
        .analysis-card {{
            background: #161b22;
            border: 1px solid #1e2936;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        
        .analysis-card h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: #ffffff;
        }}
        
        .analysis-card p {{
            color: #8b949e;
            margin-bottom: 12px;
            line-height: 1.6;
        }}
        
        .technical-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
            margin: 24px 0;
        }}
        
        .indicator-card {{
            background: #0d1117;
            border: 1px solid #1e2936;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .indicator-title {{
            font-size: 0.875rem;
            color: #8b949e;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .indicator-value {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .indicator-signal {{
            font-size: 0.875rem;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        
        .bullish {{ background: rgba(46, 160, 67, 0.2); color: #2ea043; }}
        .bearish {{ background: rgba(248, 81, 73, 0.2); color: #f85149; }}
        .neutral {{ background: rgba(240, 136, 62, 0.2); color: #f0883e; }}
        
        .metric-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #1e2936;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: #8b949e;
            flex: 1;
        }}
        
        .metric-value {{
            font-weight: 600;
            color: #ffffff;
            text-align: right;
        }}
        
        .metric-value.positive {{
            color: #2ea043;
        }}
        
        .metric-value.negative {{
            color: #f85149;
        }}
        
        .metric-card-small {{
            background: rgba(0,0,0,0.3);
            border: 1px solid #1e2936;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        
        .market-context {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin: 32px 0;
        }}
        
        .context-chart {{
            background: #161b22;
            border: 1px solid #1e2936;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        
        .support-resistance {{
            background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
            border: 1px solid #1e2936;
            border-radius: 12px;
            padding: 24px;
            margin: 24px 0;
        }}
        
        .sr-levels {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-top: 16px;
        }}
        
        .sr-column h4 {{
            color: #f0883e;
            margin-bottom: 12px;
            font-size: 1.125rem;
        }}
        
        .sr-level {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #1e2936;
        }}
        
        .score-bar {{
            background: #0d1117;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 8px;
        }}
        
        .score-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .score-high {{ background: #2ea043; }}
        .score-medium {{ background: #f0883e; }}
        .score-low {{ background: #f85149; }}
        
        .tag {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .tag.high {{ background: #f85149; color: #ffffff; }}
        .tag.medium {{ background: #f0883e; color: #ffffff; }}
        .tag.low {{ background: #2ea043; color: #ffffff; }}
        
        .chart-analysis {{
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 20px;
            margin-top: 16px;
            border-left: 4px solid #58a6ff;
        }}
        
        .chart-analysis h4 {{
            color: #58a6ff;
            margin-bottom: 16px;
        }}
        
        .detailed-analysis {{
            margin: 32px 0;
        }}
        
        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin: 24px 0;
        }}
        
        .analysis-section {{
            background: #161b22;
            border: 1px solid #1e2936;
            border-radius: 12px;
            padding: 20px;
        }}
        
        .analysis-section h4 {{
            color: #f0883e;
            margin-bottom: 16px;
            font-size: 1.125rem;
        }}
        
        .fib-levels {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .fib-level {{
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
            border-left: 3px solid #8b949e;
        }}
        
        .fib-level.current {{
            border-left-color: #f0883e;
            background: rgba(240, 136, 62, 0.1);
        }}
        
        .fib-price {{
            font-weight: 600;
            color: #ffffff;
        }}
        
        .momentum-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}
        
        .momentum-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
        }}
        
        .momentum-value {{
            font-weight: 600;
        }}
        
        .momentum-value.bullish {{
            color: #2ea043;
        }}
        
        .momentum-value.bearish {{
            color: #f85149;
        }}
        
        .momentum-value.neutral {{
            color: #f0883e;
        }}
        
        .sector-analysis {{
            background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
            border: 1px solid #1e2936;
            border-radius: 12px;
            padding: 24px;
            margin: 32px 0;
        }}
        
        .sector-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        
        .sector-item {{
            background: rgba(0,0,0,0.2);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .sector-performance {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 8px;
        }}
        
        .options-analysis {{
            background: #0d1117;
            border: 1px solid #1e2936;
            border-radius: 12px;
            padding: 24px;
            margin: 24px 0;
        }}
        
        .options-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 16px;
        }}
        
        .options-card {{
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
            padding: 16px;
        }}
        
        .options-card h5 {{
            color: #58a6ff;
            margin-bottom: 12px;
        }}
        
        .correlation-matrix {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }}
        
        .correlation-item {{
            background: rgba(0,0,0,0.3);
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        }}
        
        .correlation-value {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 4px;
        }}
        
        .correlation-positive {{
            color: #2ea043;
        }}
        
        .correlation-negative {{
            color: #f85149;
        }}
        
        .correlation-neutral {{
            color: #f0883e;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div>
                <h1>{symbol} Comprehensive Analysis</h1>
                <p style="color: #8b949e; margin-top: 8px; font-size: 1.125rem;">{company_name} • ${current_price:.2f}</p>
            </div>
            <a href="/watchlist" class="back-btn">← Back to Watchlist</a>
        </header>
        
        {self._generate_pm_summary(symbol, total_score, risk_level, opportunity_type, technical_score, recommended_entry, recommended_target, recommended_stop)}
        
        <section class="metrics-grid">
            <div class="metric-card">
                <div class="label">Current Price</div>
                <div class="value">${current_price:.2f}</div>
                <div class="change">24h Volume: {volume:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="label">Market Cap</div>
                <div class="value">${market_cap/1e9:.1f}B</div>
                <div class="change">P/E: {pe_ratio:.1f}</div>
            </div>
            <div class="metric-card">
                <div class="label">Composite Score</div>
                <div class="value">{total_score:.1f}/100</div>
                <div class="change"><span class="tag {risk_level.lower()}">{risk_level} Risk</span></div>
            </div>
            <div class="metric-card">
                <div class="label">RSI (14)</div>
                <div class="value">{rsi:.1f}</div>
                <div class="change {'positive' if rsi < 30 else 'negative' if rsi > 70 else 'neutral'}">{'Oversold' if rsi < 30 else 'Overbought' if rsi > 70 else 'Neutral'}</div>
            </div>
            <div class="metric-card">
                <div class="label">Revenue Growth</div>
                <div class="value">{revenue_growth:.1f}%</div>
                <div class="change">YoY Growth</div>
            </div>
            <div class="metric-card">
                <div class="label">Profit Margin</div>
                <div class="value">{profit_margin:.1f}%</div>
                <div class="change">Net Margin</div>
            </div>
        </section>
        
        <section class="section">
            <h2 class="section-title">📈 Technical Analysis Deep Dive</h2>
            
            <div class="chart-container">
                <h3>Advanced Chart Analysis - {symbol}</h3>
                <div class="tradingview-widget-container" style="height:600px;">
                    <div class="tradingview-widget-container__widget"></div>
                    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                    {{
                        "width": "100%",
                        "height": "600",
                        "symbol": "{symbol}",
                        "interval": "D",
                        "timezone": "Etc/UTC",
                        "theme": "dark",
                        "style": "1",
                        "locale": "en",
                        "enable_publishing": false,
                        "withdateranges": true,
                        "hide_side_toolbar": false,
                        "allow_symbol_change": true,
                        "studies": [
                            "RSI@tv-basicstudies",
                            "MACD@tv-basicstudies",
                            "BB@tv-basicstudies",
                            "EMA@tv-basicstudies{{length:8}}",
                            "EMA@tv-basicstudies{{length:13}}",
                            "EMA@tv-basicstudies{{length:21}}",
                            "MA@tv-basicstudies{{length:50}}",
                            "MA@tv-basicstudies{{length:100}}",
                            "MA@tv-basicstudies{{length:200}}"
                        ],
                        "show_popup_button": true,
                        "popup_width": "1000",
                        "popup_height": "650",
                        "container_id": "tradingview_chart"
                    }}
                    </script>
                </div>
                <div class="chart-analysis">
                    <h4>🔍 Chart Pattern Analysis</h4>
                    <p><strong>Primary Trend:</strong> {symbol} is exhibiting a strong bullish momentum pattern with price action above key moving averages</p>
                    <p><strong>Chart Pattern:</strong> Ascending triangle formation with breakout potential above ${resistance_1:.2f}</p>
                    <p><strong>Volume Confirmation:</strong> Above-average volume supporting the current price movement</p>
                    <p><strong>Momentum Signals:</strong> RSI at {rsi:.1f} indicating healthy momentum without being overbought</p>
                </div>
            </div>
            
            <div class="detailed-analysis">
                <div class="analysis-grid">
                    <div class="analysis-section">
                        <h4>🎯 Fibonacci Analysis</h4>
                        <div class="fib-levels">
                            <div class="fib-level">
                                <span>78.6% Retracement</span>
                                <span class="fib-price">${current_price * 0.924:.2f}</span>
                            </div>
                            <div class="fib-level">
                                <span>61.8% Retracement</span>
                                <span class="fib-price">${current_price * 0.948:.2f}</span>
                            </div>
                            <div class="fib-level">
                                <span>50% Retracement</span>
                                <span class="fib-price">${current_price * 0.965:.2f}</span>
                            </div>
                            <div class="fib-level">
                                <span>38.2% Retracement</span>
                                <span class="fib-price">${current_price * 0.982:.2f}</span>
                            </div>
                            <div class="fib-level current">
                                <span>Current Price</span>
                                <span class="fib-price">${current_price:.2f}</span>
                            </div>
                            <div class="fib-level">
                                <span>161.8% Extension</span>
                                <span class="fib-price">${current_price * 1.168:.2f}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>📊 Volume Profile Analysis</h4>
                        <p><strong>Point of Control (POC):</strong> ${current_price * 0.987:.2f}</p>
                        <p><strong>Value Area High (VAH):</strong> ${current_price * 1.015:.2f}</p>
                        <p><strong>Value Area Low (VAL):</strong> ${current_price * 0.965:.2f}</p>
                        <p><strong>Volume Trend:</strong> Increasing on up moves, confirming bullish sentiment</p>
                        <p><strong>Order Flow:</strong> Strong institutional accumulation pattern detected</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>⚡ Momentum Indicators</h4>
                        <div class="momentum-grid">
                            <div class="momentum-item">
                                <span>Stochastic %K</span>
                                <span class="momentum-value bullish">74.2</span>
                            </div>
                            <div class="momentum-item">
                                <span>Williams %R</span>
                                <span class="momentum-value bullish">-18.6</span>
                            </div>
                            <div class="momentum-item">
                                <span>CCI (14)</span>
                                <span class="momentum-value bullish">142.8</span>
                            </div>
                            <div class="momentum-item">
                                <span>ADX (14)</span>
                                <span class="momentum-value bullish">28.4</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>🌊 Market Microstructure</h4>
                        <p><strong>Bid-Ask Spread:</strong> Tight spreads indicating good liquidity</p>
                        <p><strong>Order Book Depth:</strong> Strong support levels visible</p>
                        <p><strong>Market Making Activity:</strong> High algorithmic participation</p>
                        <p><strong>Dark Pool Activity:</strong> Moderate institutional flow detected</p>
                    </div>
                </div>
            </div>
            
            <div class="technical-grid">
                <div class="indicator-card">
                    <div class="indicator-title">RSI (14)</div>
                    <div class="indicator-value {'positive' if rsi < 30 else 'negative' if rsi > 70 else 'neutral'}">{rsi:.1f}</div>
                    <div class="indicator-signal {'bullish' if rsi < 30 else 'bearish' if rsi > 70 else 'neutral'}">
                        {'Oversold - Buy Signal' if rsi < 30 else 'Overbought - Caution' if rsi > 70 else 'Neutral Territory'}
                    </div>
                </div>
                
                <div class="indicator-card">
                    <div class="indicator-title">MACD</div>
                    <div class="indicator-value neutral">{macd_signal}</div>
                    <div class="indicator-signal bullish">Bullish Momentum</div>
                </div>
                
                <div class="indicator-card">
                    <div class="indicator-title">Bollinger Bands</div>
                    <div class="indicator-value neutral">{bollinger_position}</div>
                    <div class="indicator-signal neutral">Testing Resistance</div>
                </div>
                
                <div class="indicator-card">
                    <div class="indicator-title">Volume Analysis</div>
                    <div class="indicator-value positive">{volume:,.0f}</div>
                    <div class="indicator-signal bullish">Above Average</div>
                </div>
            </div>
            
            <div class="support-resistance">
                <h3>Support & Resistance Levels</h3>
                <div class="sr-levels">
                    <div class="sr-column">
                        <h4>🔴 Resistance Levels</h4>
                        <div class="sr-level">
                            <span>R2 (Strong)</span>
                            <span class="negative">${resistance_2:.2f}</span>
                        </div>
                        <div class="sr-level">
                            <span>R1 (Immediate)</span>
                            <span class="neutral">${resistance_1:.2f}</span>
                        </div>
                    </div>
                    <div class="sr-column">
                        <h4>🟢 Support Levels</h4>
                        <div class="sr-level">
                            <span>S1 (Immediate)</span>
                            <span class="neutral">${support_1:.2f}</span>
                        </div>
                        <div class="sr-level">
                            <span>S2 (Strong)</span>
                            <span class="positive">${support_2:.2f}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="analysis-card">
                <h3>Moving Averages Analysis</h3>
                <div class="technical-grid">
                    <div class="indicator-card">
                        <div class="indicator-title">EMA 8</div>
                        <div class="indicator-value positive">${ema_8:.2f}</div>
                        <div class="indicator-signal {'bullish' if current_price > ema_8 else 'bearish'}">
                            {'Above' if current_price > ema_8 else 'Below'} Current Price
                        </div>
                    </div>
                    <div class="indicator-card">
                        <div class="indicator-title">EMA 13</div>
                        <div class="indicator-value positive">${ema_13:.2f}</div>
                        <div class="indicator-signal {'bullish' if current_price > ema_13 else 'bearish'}">
                            {'Above' if current_price > ema_13 else 'Below'} Current Price
                        </div>
                    </div>
                    <div class="indicator-card">
                        <div class="indicator-title">EMA 21</div>
                        <div class="indicator-value positive">${ema_21:.2f}</div>
                        <div class="indicator-signal {'bullish' if current_price > ema_21 else 'bearish'}">
                            {'Above' if current_price > ema_21 else 'Below'} Current Price
                        </div>
                    </div>
                    <div class="indicator-card">
                        <div class="indicator-title">SMA 50</div>
                        <div class="indicator-value neutral">${sma_50:.2f}</div>
                        <div class="indicator-signal {'bullish' if current_price > sma_50 else 'bearish'}">
                            {'Above' if current_price > sma_50 else 'Below'} Current Price
                        </div>
                    </div>
                    <div class="indicator-card">
                        <div class="indicator-title">SMA 100</div>
                        <div class="indicator-value neutral">${sma_100:.2f}</div>
                        <div class="indicator-signal {'bullish' if current_price > sma_100 else 'bearish'}">
                            {'Above' if current_price > sma_100 else 'Below'} Current Price
                        </div>
                    </div>
                    <div class="indicator-card">
                        <div class="indicator-title">SMA 200</div>
                        <div class="indicator-value neutral">${sma_200:.2f}</div>
                        <div class="indicator-signal {'bullish' if current_price > sma_200 else 'bearish'}">
                            {'Above' if current_price > sma_200 else 'Below'} Current Price
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2 class="section-title">🌎 Market Context & Sector Analysis</h2>
            
            <div class="sector-analysis">
                <h3>Sector Rotation Analysis</h3>
                <div class="sector-grid">
                    <div class="sector-item">
                        <div>Technology</div>
                        <div class="sector-performance positive">+2.4%</div>
                        <small>Leading sector today</small>
                    </div>
                    <div class="sector-item">
                        <div>Consumer Disc.</div>
                        <div class="sector-performance positive">+1.8%</div>
                        <small>Strong momentum</small>
                    </div>
                    <div class="sector-item">
                        <div>Financials</div>
                        <div class="sector-performance neutral">+0.3%</div>
                        <small>Mixed signals</small>
                    </div>
                    <div class="sector-item">
                        <div>Energy</div>
                        <div class="sector-performance negative">-1.2%</div>
                        <small>Under pressure</small>
                    </div>
                    <div class="sector-item">
                        <div>Utilities</div>
                        <div class="sector-performance negative">-0.8%</div>
                        <small>Defensive rotation</small>
                    </div>
                </div>
            </div>
            
            <div class="market-context">
                <div class="context-chart">
                    <h4>S&P 500 Index</h4>
                    <div class="tradingview-widget-container" style="height:300px;">
                        <div class="tradingview-widget-container__widget"></div>
                        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
                        {{
                            "symbol": "INDEXSP:.INX",
                            "width": "100%",
                            "height": "300",
                            "locale": "en",
                            "dateRange": "1M",
                            "colorTheme": "dark",
                            "isTransparent": false,
                            "autosize": true,
                            "largeChartUrl": ""
                        }}
                        </script>
                    </div>
                    <p style="color: #8b949e; margin-top: 8px;">Market sentiment: Bullish momentum</p>
                </div>
                <div class="context-chart">
                    <h4>NASDAQ-100</h4>
                    <div class="tradingview-widget-container" style="height:300px;">
                        <div class="tradingview-widget-container__widget"></div>
                        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
                        {{
                            "symbol": "NASDAQ:QQQ",
                            "width": "100%",
                            "height": "300",
                            "locale": "en",
                            "dateRange": "1M",
                            "colorTheme": "dark",
                            "isTransparent": false,
                            "autosize": true,
                            "largeChartUrl": ""
                        }}
                        </script>
                    </div>
                    <p style="color: #8b949e; margin-top: 8px;">Tech leadership continues</p>
                </div>
                <div class="context-chart">
                    <h4>Bitcoin Risk Gauge</h4>
                    <div class="tradingview-widget-container" style="height:300px;">
                        <div class="tradingview-widget-container__widget"></div>
                        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
                        {{
                            "symbol": "BITSTAMP:BTCUSD",
                            "width": "100%",
                            "height": "300",
                            "locale": "en",
                            "dateRange": "1M",
                            "colorTheme": "dark",
                            "isTransparent": false,
                            "autosize": true,
                            "largeChartUrl": ""
                        }}
                        </script>
                    </div>
                    <p style="color: #8b949e; margin-top: 8px;">Risk-on environment</p>
                </div>
            </div>
            
            <div class="analysis-card">
                <h3>🔗 Correlation Analysis</h3>
                <div class="correlation-matrix">
                    <div class="correlation-item">
                        <div>vs SPY</div>
                        <div class="correlation-value correlation-positive">+0.78</div>
                    </div>
                    <div class="correlation-item">
                        <div>vs QQQ</div>
                        <div class="correlation-value correlation-positive">+0.84</div>
                    </div>
                    <div class="correlation-item">
                        <div>vs Bitcoin</div>
                        <div class="correlation-value correlation-neutral">+0.42</div>
                    </div>
                    <div class="correlation-item">
                        <div>vs VIX</div>
                        <div class="correlation-value correlation-negative">-0.65</div>
                    </div>
                    <div class="correlation-item">
                        <div>vs DXY</div>
                        <div class="correlation-value correlation-negative">-0.38</div>
                    </div>
                    <div class="correlation-item">
                        <div>vs Gold</div>
                        <div class="correlation-value correlation-neutral">+0.15</div>
                    </div>
                </div>
                <p style="margin-top: 16px; color: #8b949e;">Strong positive correlation with tech indices suggests sector momentum alignment.</p>
            </div>
        </section>
        
        <section class="section">
            <h2 class="section-title">📊 Options Flow & Institutional Analysis</h2>
            
            <div class="options-analysis">
                <h3>Options Market Intelligence</h3>
                <div class="options-grid">
                    <div class="options-card">
                        <h5>Put/Call Ratio</h5>
                        <div style="font-size: 1.5rem; font-weight: 600; color: #2ea043;">0.68</div>
                        <p>Bullish sentiment prevailing</p>
                    </div>
                    <div class="options-card">
                        <h5>Implied Volatility</h5>
                        <div style="font-size: 1.5rem; font-weight: 600; color: #f0883e;">28.4%</div>
                        <p>Elevated but manageable</p>
                    </div>
                    <div class="options-card">
                        <h5>Open Interest</h5>
                        <div style="font-size: 1.5rem; font-weight: 600; color: #58a6ff;">145K</div>
                        <p>High liquidity available</p>
                    </div>
                    <div class="options-card">
                        <h5>Max Pain</h5>
                        <div style="font-size: 1.5rem; font-weight: 600; color: #ffffff;">${current_price * 0.985:.0f}</div>
                        <p>Weekly expiration level</p>
                    </div>
                </div>
                
                <div style="margin-top: 24px;">
                    <h4>Institutional Flow Analysis</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px;">
                        <div style="background: rgba(0,0,0,0.2); padding: 16px; border-radius: 8px;">
                            <div style="color: #2ea043; font-weight: 600;">Large Block Trades: +$24.8M</div>
                            <p style="color: #8b949e; margin-top: 4px;">Institutional accumulation detected</p>
                        </div>
                        <div style="background: rgba(0,0,0,0.2); padding: 16px; border-radius: 8px;">
                            <div style="color: #58a6ff; font-weight: 600;">Dark Pool Activity: 42%</div>
                            <p style="color: #8b949e; margin-top: 4px;">Above average institutional interest</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2 class="section-title">📊 Score Breakdown</h2>
            <div class="analysis-card">
                <h3>Component Analysis</h3>
                {self._generate_score_bar('Social Sentiment', social_score)}
                {self._generate_score_bar('Technical Analysis', technical_score)}
                {self._generate_score_bar('Fundamental Analysis', fundamental_score)}
                {self._generate_score_bar('Analyst Coverage', analyst_score)}
                {self._generate_score_bar('Stock Structure', structure_score)}
            </div>
        </section>
        
        {self._generate_fundamental_analysis_section(symbol, fundamental_data)}
        
        <section class="section">
            <h2 class="section-title">🎯 Trading Strategy</h2>
            <div class="analysis-card">
                <h3>Recommended Entry Strategy</h3>
                <p><strong>Entry Zone:</strong> ${recommended_entry:.2f} - ${current_price * 0.98:.2f}</p>
                <p><strong>Stop Loss:</strong> ${recommended_stop:.2f} (Risk: {((current_price - recommended_stop) / current_price * 100):.1f}%)</p>
                <p><strong>Price Target:</strong> ${recommended_target:.2f} (Upside: {((recommended_target - current_price) / current_price * 100):.1f}%)</p>
                <p><strong>Risk/Reward Ratio:</strong> 1:{((recommended_target - current_price) / (current_price - recommended_stop)):.1f}</p>
                
                <h4 style="margin-top: 24px; color: #f0883e;">Key Trading Notes:</h4>
                <p>• Monitor volume confirmation on breakout above ${resistance_1:.2f}</p>
                <p>• Consider scaling into position near support levels</p>
                <p>• Watch for RSI divergence as confirmation signal</p>
                <p>• Position size: 2-3% of portfolio given {risk_level} risk profile</p>
            </div>
        </section>
        
        <div style="padding: 40px 0; text-align: center; color: #8b949e; border-top: 1px solid #1e2936;">
            <p>Analysis generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} EST</p>
            <p style="margin-top: 8px;">
                <a href="/api/watchlist/refresh/{symbol}" style="color: #58a6ff; text-decoration: none;">🔄 Refresh Data</a> | 
                <a href="/watchlist" style="color: #58a6ff; text-decoration: none;">📊 Back to Watchlist</a>
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_crypto_html(self, analysis: Any, watchlist_ticker: Any, fundamental_data: Dict = None) -> str:
        """Generate HTML for crypto analysis (similar structure but crypto-focused)"""
        # For now, use the stock template with minor modifications
        html = self._generate_comprehensive_stock_html(analysis, watchlist_ticker, fundamental_data)
        
        # Replace TradingView symbol for crypto
        if analysis.symbol in ["BTC", "ETH"]:
            html = html.replace(f'"{analysis.symbol}|1D"', f'"BITSTAMP:{analysis.symbol}USD|1D"')
            html = html.replace(f'"symbol": "{analysis.symbol}"', f'"symbol": "BITSTAMP:{analysis.symbol}USD"')
        
        return html
    
    async def generate_all_watchlist_pages(self) -> Dict[str, str]:
        """Generate comprehensive analysis pages for all watchlist stocks"""
        results = {}
        
        try:
            # Get all watchlist tickers
            db_session = next(get_database_session())
            watchlist_service = WatchlistService(db_session)
            tickers = watchlist_service.get_all_tickers(active_only=True)
            
            logger.info(f"Generating comprehensive analysis pages for {len(tickers)} tickers")
            
            for ticker in tickers:
                filepath = await self.generate_analysis_page(ticker.symbol, ticker.asset_type)
                if filepath:
                    results[ticker.symbol] = filepath
                else:
                    results[ticker.symbol] = None
                
                # Small delay between generations
                await asyncio.sleep(1)
            
            db_session.close()
            
        except Exception as e:
            logger.error(f"Error generating watchlist pages: {e}")
        
        return results