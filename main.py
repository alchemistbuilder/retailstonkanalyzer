#!/usr/bin/env python3
"""
Retail Meme Stock Analyzer - Main Entry Point

This is the main entry point for the Retail Meme Stock Analyzer.
It provides a command-line interface to run the analysis and start the API server.
"""

import asyncio
import argparse
import sys
from datetime import datetime
from typing import List

from src.core.stock_analyzer import StockAnalyzer, WatchlistAnalyzer
from src.core.config import settings


async def analyze_single_stock(symbol: str):
    """Analyze a single stock and print results"""
    analyzer = StockAnalyzer()
    
    print(f"\n🔍 Analyzing {symbol}...")
    print("=" * 50)
    
    analysis = await analyzer.analyze_stock(symbol)
    
    if not analysis:
        print(f"❌ Failed to analyze {symbol}")
        return
    
    # Print analysis results
    print(f"📊 {analysis.symbol} - {analysis.company_name}")
    print(f"🎯 Composite Score: {analysis.composite_score.total_score:.1f}/100")
    print(f"🏷️  Opportunity Type: {analysis.composite_score.opportunity_type}")
    print(f"⚠️  Risk Level: {analysis.composite_score.risk_level}")
    print(f"🔒 Confidence: {analysis.composite_score.confidence_level:.2f}")
    
    print(f"\n📈 Component Scores:")
    print(f"  📱 Social Sentiment: {analysis.composite_score.social_score:.1f}")
    print(f"  📊 Technical Analysis: {analysis.composite_score.technical_score:.1f}")
    print(f"  💰 Fundamental Analysis: {analysis.composite_score.fundamental_score:.1f}")
    print(f"  👥 Analyst Coverage: {analysis.composite_score.analyst_score:.1f}")
    print(f"  🏗️  Stock Structure: {analysis.composite_score.structure_score:.1f}")
    
    print(f"\n💬 Social Sentiment:")
    print(f"  Mentions: {analysis.social_sentiment.mentions}")
    print(f"  Sentiment Score: {analysis.social_sentiment.sentiment_score:.3f}")
    print(f"  Trend: {analysis.social_sentiment.volume_trend.value}")
    print(f"  Top Keywords: {', '.join(analysis.social_sentiment.top_keywords[:5])}")
    
    print(f"\n📊 Technical Analysis:")
    print(f"  Price: ${analysis.technical_analysis.price:.2f}")
    print(f"  RSI: {analysis.technical_analysis.rsi:.1f}")
    print(f"  Trend: {analysis.technical_analysis.trend_direction.value}")
    if analysis.technical_analysis.pattern_detected:
        print(f"  Pattern: {analysis.technical_analysis.pattern_detected} ({analysis.technical_analysis.pattern_confidence:.2f})")
    
    # Display chart images if available
    if analysis.technical_analysis.chart_images:
        print(f"\n📈 Chart Images:")
        for chart_type, url in analysis.technical_analysis.chart_images.items():
            print(f"  {chart_type}: {url}")
    else:
        print(f"\n📈 Chart: https://chart-img.com/chart/{symbol}")
    
    print(f"\n💰 Fundamentals:")
    print(f"  Market Cap: ${analysis.fundamental_data.market_cap:,.0f}" if analysis.fundamental_data.market_cap else "  Market Cap: N/A")
    print(f"  P/E Ratio: {analysis.fundamental_data.pe_ratio:.1f}" if analysis.fundamental_data.pe_ratio else "  P/E Ratio: N/A")
    print(f"  Revenue Growth: {analysis.fundamental_data.revenue_growth_yoy:.1f}%" if analysis.fundamental_data.revenue_growth_yoy else "  Revenue Growth: N/A")
    
    print(f"\n👥 Analyst Coverage:")
    print(f"  Consensus: {analysis.analyst_coverage.consensus_rating.value}")
    print(f"  Analysts: {analysis.analyst_coverage.num_analysts}")
    print(f"  Price Target: ${analysis.analyst_coverage.avg_price_target:.2f}" if analysis.analyst_coverage.avg_price_target else "  Price Target: N/A")
    print(f"  Upside: {analysis.analyst_coverage.price_target_upside:.1f}%" if analysis.analyst_coverage.price_target_upside else "  Upside: N/A")
    
    print(f"\n🏗️  Stock Structure:")
    print(f"  Short Interest: {analysis.stock_structure.short_interest:.1f}%")
    print(f"  Float: {analysis.stock_structure.float_shares:,.0f}" if analysis.stock_structure.float_shares else "  Float: N/A")
    print(f"  Squeeze Score: {analysis.stock_structure.short_squeeze_score:.1f}/100")
    
    if analysis.alerts:
        print(f"\n🚨 Alerts ({len(analysis.alerts)}):")
        for alert in analysis.alerts[:5]:  # Show top 5 alerts
            print(f"  {alert.priority.upper()}: {alert.trigger_reason}")
            if alert.chart_image_url:
                print(f"    📊 Chart: {alert.chart_image_url}")
    
    print(f"\n⏰ Last Updated: {analysis.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")


async def analyze_watchlist():
    """Analyze the entire watchlist"""
    analyzer = WatchlistAnalyzer()
    
    print("\n🔍 Analyzing Watchlist...")
    print("=" * 50)
    print(f"📋 Stocks to analyze: {', '.join(settings.default_watchlist)}")
    print()
    
    results = await analyzer.analyze_watchlist()
    
    # Print summary
    successful = len([r for r in results.values() if r is not None])
    print(f"\n✅ Successfully analyzed {successful}/{len(settings.default_watchlist)} stocks")
    
    # Get top opportunities
    opportunities = analyzer.get_top_opportunities(results, min_score=60.0, limit=10)
    
    if opportunities:
        print(f"\n🏆 Top Opportunities (Score ≥ 60):")
        print("-" * 70)
        for i, analysis in enumerate(opportunities, 1):
            score = analysis.composite_score.total_score
            risk = analysis.composite_score.risk_level
            opp_type = analysis.composite_score.opportunity_type
            
            print(f"{i:2d}. {analysis.symbol:6s} - {score:5.1f} - {risk:6s} - {opp_type}")
    
    # Get alerts summary
    alerts_summary = analyzer.get_alerts_summary(results)
    
    total_alerts = sum(len(alerts) for alerts in alerts_summary.values())
    if total_alerts > 0:
        print(f"\n🚨 Alerts Summary ({total_alerts} total):")
        for priority in ["high", "medium", "low"]:
            count = len(alerts_summary[priority])
            if count > 0:
                print(f"  {priority.upper()}: {count}")
                for alert in alerts_summary[priority][:3]:  # Show top 3 per priority
                    print(f"    • {alert.symbol}: {alert.trigger_reason}")


def start_api_server():
    """Start the FastAPI server"""
    import uvicorn
    from src.api.main import app
    
    print("🚀 Starting Retail Meme Stock Analyzer API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


async def generate_chart_examples(symbol: str):
    """Generate chart examples for a symbol"""
    from src.data_collectors.chart_image_collector import ChartImageCollector
    
    print(f"📊 Generating Chart Examples for {symbol}")
    print("=" * 50)
    
    chart_collector = ChartImageCollector()
    
    try:
        # Generate comprehensive chart package
        print("🔄 Generating comprehensive chart package...")
        charts = await chart_collector.get_comprehensive_chart_package(symbol)
        
        print(f"\n✅ Generated {len(charts)} chart types:")
        for chart_type, url in charts.items():
            print(f"  📈 {chart_type:20}: {url}")
        
        # Generate alert-specific charts
        print(f"\n🚨 Alert-Specific Charts:")
        alert_types = ["short_squeeze", "momentum", "breakout", "value"]
        for alert_type in alert_types:
            alert_chart = await chart_collector.get_alert_chart(symbol, alert_type)
            print(f"  🎯 {alert_type:15}: {alert_chart}")
        
        # Show backup options
        print(f"\n🔄 Backup Chart Options:")
        print(f"  📊 TradingView: {chart_collector.get_tradingview_backup_url(symbol)}")
        print(f"  📈 Yahoo Finance: {chart_collector.get_yahoo_backup_url(symbol)}")
        
        print(f"\n🎉 Chart examples generated! You can now see visual analysis!")
        
    except Exception as e:
        print(f"❌ Error generating charts: {e}")


def check_configuration():
    """Check if API keys are configured"""
    print("🔧 Configuration Check:")
    print("=" * 30)
    
    api_keys = {
        "Alpha Vantage": settings.alpha_vantage_api_key,
        "Polygon": settings.polygon_api_key,
        "Financial Modeling Prep": settings.fmp_api_key,
        "ORTEX": settings.ortex_api_key,
        "Reddit": settings.reddit_client_id,
        "Twitter": settings.twitter_bearer_token,
        "StockTwits": settings.stocktwits_access_token,
        "Benzinga": settings.benzinga_api_key,
        "Chart-img.com": getattr(settings, 'chart_img_api_key', None)
    }
    
    configured = 0
    for name, key in api_keys.items():
        status = "✅ Configured" if key else "❌ Missing"
        print(f"  {name:25s}: {status}")
        if key:
            configured += 1
    
    print(f"\n📊 {configured}/{len(api_keys)} API keys configured")
    
    if configured == 0:
        print("\n⚠️  WARNING: No API keys configured!")
        print("   Please copy .env.example to .env and add your API keys.")
        print("   The system will use default/mock data without API keys.")
    elif configured < len(api_keys):
        print("\n💡 Some API keys are missing. The system will work with reduced functionality.")
    else:
        print("\n🎉 All API keys configured! Full functionality available.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Retail Meme Stock Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --symbol GME              # Analyze GameStop
  python main.py --symbols GME AMC TSLA    # Analyze multiple stocks
  python main.py --watchlist               # Analyze entire watchlist
  python main.py --server                  # Start API server
  python main.py --config                  # Check configuration
  python main.py --charts TSLA             # Generate chart examples
        """
    )
    
    parser.add_argument("--symbol", type=str, help="Analyze a single stock symbol")
    parser.add_argument("--symbols", nargs="+", help="Analyze multiple stock symbols")
    parser.add_argument("--watchlist", action="store_true", help="Analyze the entire watchlist")
    parser.add_argument("--server", action="store_true", help="Start the API server")
    parser.add_argument("--config", action="store_true", help="Check configuration")
    parser.add_argument("--charts", type=str, help="Generate chart examples for a symbol")
    
    args = parser.parse_args()
    
    # Print header
    print("🎯 Retail Meme Stock Analyzer")
    print("=" * 50)
    
    if args.config:
        check_configuration()
    elif args.server:
        start_api_server()
    elif args.symbol:
        asyncio.run(analyze_single_stock(args.symbol.upper()))
    elif args.symbols:
        symbols = [s.upper() for s in args.symbols]
        for symbol in symbols:
            asyncio.run(analyze_single_stock(symbol))
    elif args.watchlist:
        asyncio.run(analyze_watchlist())
    elif args.charts:
        asyncio.run(generate_chart_examples(args.charts.upper()))
    else:
        # No arguments provided, show help and run config check
        parser.print_help()
        print()
        check_configuration()


if __name__ == "__main__":
    main()