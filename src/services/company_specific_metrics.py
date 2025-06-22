"""
Company-specific key driver metrics based on industry and business model
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class CompanySpecificMetrics:
    """Extract and analyze company-specific key driver metrics"""
    
    # Define key metrics by sector/company
    SECTOR_METRICS = {
        'Financial Services': {
            'key_drivers': ['Assets Under Management (AUM)', 'Net Interest Margin', 'Trading Revenue %', 'Active Users', 'ARPU'],
            'description': 'Focus on user growth, trading volumes, and revenue per user'
        },
        'Healthcare': {
            'key_drivers': ['Revenue per Member', 'Member Growth', 'Medical Loss Ratio', 'Administrative Costs %'],
            'description': 'Health insurance metrics focused on member growth and cost efficiency'
        },
        'Consumer Discretionary': {
            'key_drivers': ['Same-Store Sales Growth', 'Digital Sales %', 'Customer Acquisition Cost', 'Market Share'],
            'description': 'Retail and consumer spending patterns'
        },
        'Communication Services': {
            'key_drivers': ['Subscriber Growth', 'ARPU', 'Churn Rate', 'Content Costs %'],
            'description': 'Media and entertainment subscriber metrics'
        },
        'Technology': {
            'key_drivers': ['Revenue Growth', 'R&D Investment %', 'Market Share', 'Product Innovation'],
            'description': 'Technology and innovation metrics'
        },
        'Cryptocurrency': {
            'key_drivers': ['Network Activity', 'Market Cap Rank', 'Transaction Volume', 'Adoption Rate'],
            'description': 'Blockchain and cryptocurrency adoption metrics'
        }
    }
    
    # Company-specific metrics
    COMPANY_METRICS = {
        'HOOD': {
            'key_drivers': [
                'Monthly Active Users (MAU)',
                'Assets Under Management (AUM)', 
                'Trading Revenue as % of Total Revenue',
                'Cryptocurrency Revenue Growth',
                'Average Revenue Per User (ARPU)',
                'Net Deposits Flow'
            ],
            'description': 'Robinhood: Focus on user growth, trading activity, and crypto adoption'
        },
        'OSCR': {
            'key_drivers': [
                'Member Enrollment Growth',
                'Revenue per Member per Month (PMPM)',
                'Medical Loss Ratio (MLR)',
                'Technology Platform Efficiency',
                'Market Expansion (Geographic)',
                'Administrative Cost Ratio'
            ],
            'description': 'Oscar Health: Insurance metrics focused on member growth and cost management'
        },
        'TSLA': {
            'key_drivers': [
                'Vehicle Deliveries Growth',
                'Energy Storage Deployments', 
                'Supercharger Network Expansion',
                'Automotive Gross Margin',
                'Full Self-Driving (FSD) Adoption',
                'Energy Business Revenue Growth'
            ],
            'description': 'Tesla: EV deliveries, energy business, and autonomous driving progress'
        },
        'GME': {
            'key_drivers': [
                'Digital Sales Growth',
                'NFT Marketplace Activity',
                'Same-Store Sales Growth',
                'Inventory Turnover',
                'E-commerce Transformation',
                'Collectibles Market Share'
            ],
            'description': 'GameStop: Digital transformation and e-commerce growth'
        },
        'AMC': {
            'key_drivers': [
                'Box Office Recovery vs Pre-COVID',
                'Average Ticket Price',
                'Concession Revenue per Patron',
                'Theater Utilization Rate',
                'Premium Format Revenue (IMAX/Dolby)',
                'Debt Reduction Progress'
            ],
            'description': 'AMC: Movie theater recovery and premium experience monetization'
        },
        'NFLX': {
            'key_drivers': [
                'Global Subscriber Growth',
                'Revenue per Member (ARM)',
                'Content Spend as % of Revenue',
                'Churn Rate by Region',
                'Ad-Tier Subscriber Growth',
                'International Market Penetration'
            ],
            'description': 'Netflix: Subscriber growth and content monetization'
        }
    }
    
    def get_key_drivers(self, symbol: str, sector: str = None, industry: str = None) -> Dict[str, Any]:
        """Get company-specific key driver metrics"""
        
        # Check for company-specific metrics first
        if symbol.upper() in self.COMPANY_METRICS:
            return self.COMPANY_METRICS[symbol.upper()]
        
        # Fall back to sector-based metrics
        if sector and sector in self.SECTOR_METRICS:
            return self.SECTOR_METRICS[sector]
        
        # Default generic metrics
        return {
            'key_drivers': [
                'Revenue Growth Rate',
                'Profit Margin Trend', 
                'Market Share',
                'Customer Growth',
                'Operating Efficiency',
                'Return on Investment'
            ],
            'description': 'General business performance metrics'
        }
    
    def analyze_key_drivers(self, symbol: str, fundamental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company performance against key drivers"""
        
        sector = fundamental_data.get('sector', 'Unknown')
        industry = fundamental_data.get('industry', 'Unknown')
        
        # Get relevant key drivers
        key_drivers_info = self.get_key_drivers(symbol, sector, industry)
        
        # Calculate relevant metrics based on available data
        analysis = {
            'key_drivers': key_drivers_info['key_drivers'],
            'description': key_drivers_info['description'],
            'metrics_analysis': {}
        }
        
        # Revenue growth analysis
        quarterly_revenue = fundamental_data.get('latest_quarterly_revenue')
        annual_revenue = fundamental_data.get('annual_revenue')
        revenue_growth = fundamental_data.get('quarterly_revenue_growth')
        
        if revenue_growth is not None:
            analysis['metrics_analysis']['Revenue Growth'] = {
                'value': f"{revenue_growth:.1f}%",
                'status': 'positive' if revenue_growth > 0 else 'negative',
                'description': 'Quarter-over-quarter revenue growth'
            }
        
        # Profitability analysis
        quarterly_income = fundamental_data.get('latest_quarterly_net_income')
        if quarterly_income and quarterly_revenue:
            profit_margin = (quarterly_income / quarterly_revenue) * 100
            analysis['metrics_analysis']['Profit Margin'] = {
                'value': f"{profit_margin:.1f}%",
                'status': 'positive' if profit_margin > 0 else 'negative',
                'description': 'Net profit margin (latest quarter)'
            }
        
        # Valuation metrics
        ev_to_sales = fundamental_data.get('ev_to_sales')
        if ev_to_sales:
            analysis['metrics_analysis']['EV/Sales Multiple'] = {
                'value': f"{ev_to_sales:.1f}x",
                'status': 'neutral',
                'description': 'Enterprise value to sales ratio'
            }
        
        # Company-specific analysis
        if symbol.upper() == 'HOOD':
            # For Robinhood, emphasize fintech metrics
            analysis['company_specific_insights'] = [
                "Monitor MAU growth as key driver of trading revenue",
                "Cryptocurrency trading becoming significant revenue stream", 
                "ARPU expansion through premium features and margin lending",
                "Regulatory environment impacts on payment for order flow"
            ]
        elif symbol.upper() == 'OSCR':
            # For Oscar Health, emphasize insurance metrics
            analysis['company_specific_insights'] = [
                "Member growth is primary driver of revenue expansion",
                "MLR management critical for profitability",
                "Technology platform differentiation vs traditional insurers",
                "Geographic expansion opportunities in underserved markets"
            ]
        elif symbol.upper() == 'TSLA':
            # For Tesla, emphasize EV and energy metrics
            analysis['company_specific_insights'] = [
                "Vehicle delivery growth drives automotive revenue",
                "Energy storage business becoming material revenue contributor",
                "FSD software represents high-margin recurring revenue opportunity",
                "Manufacturing efficiency improvements expanding margins"
            ]
        
        return analysis

# Global instance
company_metrics_analyzer = CompanySpecificMetrics()