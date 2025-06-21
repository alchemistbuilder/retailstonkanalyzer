#!/usr/bin/env python3
"""
System Testing Script

This script helps you test the Retail Meme Stock Analyzer system
without needing all API keys configured.
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.core.config import settings
from src.data_collectors.chart_image_collector import ChartImageCollector


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'-'*40}")
    print(f"📊 {title}")
    print(f"{'-'*40}")


def check_api_configuration():
    """Check which API keys are configured"""
    print_header("API Configuration Check")
    
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
        print("\n⚠️  No API keys configured - testing with mock data")
    elif configured < 4:
        print("\n💡 Some key APIs missing - limited functionality")
    else:
        print("\n🎉 Good configuration for testing!")
    
    return configured


async def test_chart_integration():
    """Test chart image generation"""
    print_header("Chart Integration Test")
    
    chart_collector = ChartImageCollector()
    symbol = "TSLA"
    
    try:
        print(f"🔄 Testing chart generation for {symbol}...")
        
        # Test basic chart
        print_section("Basic Chart")
        basic_chart = await chart_collector.get_technical_chart(symbol)
        print(f"✅ Technical Chart: {basic_chart}")
        
        # Test multiple timeframes
        print_section("Multiple Timeframes")
        timeframes = await chart_collector.get_multiple_timeframes(symbol)
        for timeframe, url in timeframes.items():
            print(f"  📈 {timeframe:15}: {url}")
        
        # Test alert charts
        print_section("Alert-Specific Charts")
        alert_types = ["short_squeeze", "momentum", "breakout"]
        for alert_type in alert_types:
            alert_chart = await chart_collector.get_alert_chart(symbol, alert_type)
            print(f"  🎯 {alert_type:15}: {alert_chart}")
        
        # Test comprehensive package
        print_section("Comprehensive Package")
        comprehensive = await chart_collector.get_comprehensive_chart_package(symbol)
        print(f"✅ Generated {len(comprehensive)} chart types")
        
        print(f"\n🎉 Chart integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Chart integration test failed: {e}")
        return False


async def test_single_stock_analysis():
    """Test analyzing a single stock"""
    print_header("Single Stock Analysis Test")
    
    try:
        from src.core.stock_analyzer import StockAnalyzer
        
        analyzer = StockAnalyzer()
        symbol = "TSLA"
        
        print(f"🔄 Analyzing {symbol}...")
        print("⏰ This may take 30-60 seconds with API calls...")
        
        start_time = time.time()
        analysis = await analyzer.analyze_stock(symbol)
        end_time = time.time()
        
        if analysis:
            print(f"✅ Analysis completed in {end_time - start_time:.1f} seconds")
            print(f"📊 Composite Score: {analysis.composite_score.total_score:.1f}/100")
            print(f"🎯 Opportunity Type: {analysis.composite_score.opportunity_type}")
            print(f"⚠️  Risk Level: {analysis.composite_score.risk_level}")
            print(f"🚨 Alerts: {len(analysis.alerts)}")
            
            # Check if charts are included
            if analysis.technical_analysis.chart_images:
                print(f"📈 Chart Images: {len(analysis.technical_analysis.chart_images)}")
                for chart_type in analysis.technical_analysis.chart_images.keys():
                    print(f"    📊 {chart_type}")
            
            print(f"\n🎉 Single stock analysis test passed!")
            return True
        else:
            print(f"❌ Analysis returned None")
            return False
            
    except Exception as e:
        print(f"❌ Single stock analysis test failed: {e}")
        return False


async def test_api_server():
    """Test if API server is working"""
    print_header("API Server Test")
    
    try:
        import aiohttp
        
        # Test if server is running
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://localhost:8000/status', timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ API server is running!")
                        print(f"📊 Stocks in cache: {data.get('stocks_in_cache', 0)}")
                        print(f"📋 Watchlist size: {data.get('watchlist_size', 0)}")
                        
                        # Show API key status
                        api_keys = data.get('api_keys_configured', {})
                        print(f"\n🔑 API Keys Status:")
                        for key, status in api_keys.items():
                            status_icon = "✅" if status else "❌"
                            print(f"    {status_icon} {key}")
                        
                        return True
                    else:
                        print(f"❌ API server returned status {response.status}")
                        return False
                        
            except asyncio.TimeoutError:
                print("❌ API server is not responding (timeout)")
                print("💡 Start it with: python main.py --server")
                return False
                
    except ImportError:
        print("❌ aiohttp not installed for testing")
        return False
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        print("💡 Start the server with: python main.py --server")
        return False


def test_dashboard_file():
    """Test if dashboard file exists and is accessible"""
    print_header("Dashboard File Test")
    
    dashboard_path = "src/dashboard/simple_dashboard.html"
    
    if os.path.exists(dashboard_path):
        print(f"✅ Dashboard file exists: {dashboard_path}")
        
        # Get file size
        file_size = os.path.getsize(dashboard_path)
        print(f"📄 File size: {file_size:,} bytes")
        
        # Show how to access it
        abs_path = os.path.abspath(dashboard_path)
        print(f"\n🌐 To open dashboard:")
        print(f"   1. Start API server: python main.py --server")
        print(f"   2. Open in browser: file://{abs_path}")
        print(f"   3. Or drag the file to your browser")
        
        return True
    else:
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return False


async def run_comprehensive_test():
    """Run all tests"""
    print_header("Comprehensive System Test")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Configuration
    print_section("Test 1: Configuration")
    config_score = check_api_configuration()
    results.append(("Configuration", config_score > 0))
    
    # Test 2: Chart Integration
    print_section("Test 2: Chart Integration")
    chart_result = await test_chart_integration()
    results.append(("Chart Integration", chart_result))
    
    # Test 3: Dashboard File
    print_section("Test 3: Dashboard File")
    dashboard_result = test_dashboard_file()
    results.append(("Dashboard File", dashboard_result))
    
    # Test 4: API Server
    print_section("Test 4: API Server")
    api_result = await test_api_server()
    results.append(("API Server", api_result))
    
    # Test 5: Stock Analysis (only if we have some APIs)
    if config_score > 0:
        print_section("Test 5: Stock Analysis")
        analysis_result = await test_single_stock_analysis()
        results.append(("Stock Analysis", analysis_result))
    else:
        print_section("Test 5: Stock Analysis")
        print("⏭️  Skipped - no API keys configured")
        results.append(("Stock Analysis", None))
    
    # Summary
    print_header("Test Results Summary")
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name:20s}: PASSED")
        elif result is False:
            print(f"❌ {test_name:20s}: FAILED")
        else:
            print(f"⏭️  {test_name:20s}: SKIPPED")
    
    print(f"\n📊 Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print(f"🎉 All available tests passed!")
    else:
        print(f"⚠️  Some tests failed - check configuration")
    
    # Next steps
    print_header("Next Steps")
    
    if not api_result:
        print("1. 🚀 Start API server: python main.py --server")
    
    if config_score == 0:
        print("2. 🔑 Add API keys to .env file (see SETUP_GUIDE.md)")
    
    if dashboard_result:
        print("3. 🌐 Open dashboard in browser")
    
    if passed >= 3:
        print("4. 🎯 Try analyzing: python main.py --symbol GME")
    
    print("5. 📚 See README.md for full setup instructions")


def quick_demo():
    """Show a quick demo of what the system can do"""
    print_header("Quick Demo")
    
    print("🎯 Retail Meme Stock Analyzer Demo")
    print("\n📊 This system analyzes stocks using 5 factors:")
    print("   1. 📱 Social Sentiment (Reddit, Twitter, StockTwits)")
    print("   2. 📊 Technical Analysis (RSI, MACD, patterns)")
    print("   3. 💰 Fundamental Analysis (P/E, growth, margins)")
    print("   4. 👥 Analyst Coverage (ratings, price targets)")
    print("   5. 🏗️  Stock Structure (short interest, float)")
    
    print("\n📈 Chart Integration:")
    print("   • Technical analysis charts")
    print("   • Pattern recognition charts")
    print("   • Short squeeze analysis charts")
    print("   • Alert-specific visualizations")
    
    print("\n🚀 How to use:")
    print("   • CLI: python main.py --symbol GME")
    print("   • API: python main.py --server")
    print("   • Web: Open dashboard.html in browser")
    
    print("\n🔍 Example output:")
    print("   GME - GameStop Corp.")
    print("   🎯 Composite Score: 78.5/100")
    print("   🏷️  Opportunity Type: short_squeeze")
    print("   ⚠️  Risk Level: high")
    print("   📈 Chart: https://chart-img.com/chart/GME")


async def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        quick_demo()
    else:
        await run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())