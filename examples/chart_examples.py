#!/usr/bin/env python3
"""
Chart Examples - Demonstrating chart-img.com integration

This script shows how to use the ChartImageCollector to get various chart images
for stock analysis and display them.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_collectors.chart_image_collector import ChartImageCollector


async def demonstrate_chart_features():
    """Demonstrate various chart features"""
    
    print("🎯 Chart-img.com Integration Examples")
    print("=" * 50)
    
    # Initialize the chart collector
    chart_collector = ChartImageCollector()
    
    # Example symbols to analyze
    symbols = ["GME", "TSLA", "AMC", "NVDA"]
    
    for symbol in symbols:
        print(f"\n📊 Charts for {symbol}")
        print("-" * 30)
        
        # 1. Basic technical chart
        print("📈 Technical Analysis Chart:")
        technical_chart = await chart_collector.get_technical_chart(symbol)
        print(f"   {technical_chart}")
        
        # 2. Pattern analysis chart
        print("🔍 Pattern Analysis Chart:")
        pattern_chart = await chart_collector.get_pattern_analysis_chart(symbol)
        print(f"   {pattern_chart}")
        
        # 3. Short squeeze analysis chart
        print("🎯 Short Squeeze Analysis Chart:")
        squeeze_chart = await chart_collector.get_squeeze_analysis_chart(symbol)
        print(f"   {squeeze_chart}")
        
        # 4. Multiple timeframes
        print("⏰ Multiple Timeframes:")
        timeframe_charts = await chart_collector.get_multiple_timeframes(symbol)
        for timeframe, url in timeframe_charts.items():
            print(f"   {timeframe:12}: {url}")
        
        print()  # Add space between symbols


async def demonstrate_alert_charts():
    """Demonstrate alert-specific chart generation"""
    
    print("\n🚨 Alert-Specific Charts")
    print("=" * 30)
    
    chart_collector = ChartImageCollector()
    symbol = "GME"
    
    alert_types = [
        "short_squeeze",
        "momentum", 
        "breakout",
        "value",
        "divergence"
    ]
    
    for alert_type in alert_types:
        print(f"📊 {alert_type.upper()} Alert Chart:")
        alert_chart = await chart_collector.get_alert_chart(symbol, alert_type)
        print(f"   {alert_chart}")


async def demonstrate_comprehensive_package():
    """Demonstrate the comprehensive chart package"""
    
    print("\n📦 Comprehensive Chart Package")
    print("=" * 40)
    
    chart_collector = ChartImageCollector()
    symbol = "TSLA"
    
    print(f"🔄 Generating comprehensive chart package for {symbol}...")
    
    charts = await chart_collector.get_comprehensive_chart_package(symbol)
    
    print(f"\n✅ Generated {len(charts)} charts:")
    for chart_type, url in charts.items():
        print(f"   {chart_type:20}: {url}")


async def demonstrate_backup_options():
    """Demonstrate backup chart options"""
    
    print("\n🔄 Backup Chart Options")
    print("=" * 30)
    
    chart_collector = ChartImageCollector()
    symbol = "AAPL"
    
    print(f"📊 Primary Chart (chart-img.com):")
    primary_chart = await chart_collector.get_technical_chart(symbol)
    print(f"   {primary_chart}")
    
    print(f"🔄 TradingView Backup:")
    tradingview_backup = chart_collector.get_tradingview_backup_url(symbol)
    print(f"   {tradingview_backup}")
    
    print(f"📈 Yahoo Finance Backup:")
    yahoo_backup = chart_collector.get_yahoo_backup_url(symbol)
    print(f"   {yahoo_backup}")


async def demonstrate_chart_validation():
    """Demonstrate chart availability validation"""
    
    print("\n✅ Chart Availability Validation")
    print("=" * 40)
    
    chart_collector = ChartImageCollector()
    symbols = ["TSLA", "INVALID_SYMBOL"]
    
    for symbol in symbols:
        print(f"\n🔍 Validating charts for {symbol}:")
        
        validation = await chart_collector.validate_chart_availability(symbol)
        
        print(f"   Available: {validation['charts_available']}")
        print(f"   Chart URL: {validation.get('chart_url', 'N/A')}")
        print(f"   TradingView: {validation['backup_tradingview']}")
        print(f"   Yahoo: {validation['backup_yahoo']}")


def generate_html_display(symbol: str, charts: dict) -> str:
    """Generate HTML to display charts (example for dashboard)"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{symbol} - Technical Analysis Charts</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .chart-container {{ margin: 20px 0; }}
            .chart-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
            .chart-image {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
            .timeframe-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        </style>
    </head>
    <body>
        <h1>📊 {symbol} Technical Analysis</h1>
        
        <div class="chart-container">
            <div class="chart-title">📈 Daily Technical Analysis</div>
            <img src="{charts.get('technical_daily', '')}" alt="Daily Technical Chart" class="chart-image">
        </div>
        
        <div class="chart-container">
            <div class="chart-title">🔍 Pattern Analysis</div>
            <img src="{charts.get('pattern_analysis', '')}" alt="Pattern Analysis Chart" class="chart-image">
        </div>
        
        <div class="chart-container">
            <div class="chart-title">🎯 Short Squeeze Analysis</div>
            <img src="{charts.get('squeeze_analysis', '')}" alt="Squeeze Analysis Chart" class="chart-image">
        </div>
        
        <div class="chart-container">
            <div class="chart-title">⏰ Multiple Timeframes</div>
            <div class="timeframe-grid">
                <div>
                    <h3>1 Hour</h3>
                    <img src="{charts.get('intraday_1h', '')}" alt="1H Chart" class="chart-image">
                </div>
                <div>
                    <h3>Weekly</h3>
                    <img src="{charts.get('technical_weekly', '')}" alt="Weekly Chart" class="chart-image">
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">💬 Social Sentiment</div>
            <img src="{charts.get('social_sentiment', '')}" alt="Social Sentiment Chart" class="chart-image">
        </div>
    </body>
    </html>
    """
    
    return html


async def main():
    """Main function to run all examples"""
    
    try:
        # Run all demonstrations
        await demonstrate_chart_features()
        await demonstrate_alert_charts()
        await demonstrate_comprehensive_package()
        await demonstrate_backup_options()
        await demonstrate_chart_validation()
        
        # Generate HTML example
        print("\n📄 HTML Dashboard Example")
        print("=" * 30)
        
        chart_collector = ChartImageCollector()
        charts = await chart_collector.get_comprehensive_chart_package("GME")
        
        html_content = generate_html_display("GME", charts)
        
        # Save HTML file
        html_file = "gme_charts_example.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Generated HTML example: {html_file}")
        print(f"🌐 Open {html_file} in your browser to see the charts!")
        
        print(f"\n🎉 Chart integration examples completed!")
        print(f"📊 You can now see visual charts in your stock analysis!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())