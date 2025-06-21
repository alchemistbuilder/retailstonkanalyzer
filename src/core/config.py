from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Keys
    alpha_vantage_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None
    fmp_api_key: Optional[str] = None
    ortex_api_key: Optional[str] = None
    benzinga_api_key: Optional[str] = None
    
    # Social Media APIs
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "retail_meme_analyzer_v1.0"
    
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    
    stocktwits_access_token: Optional[str] = None
    
    # Chart APIs
    chart_img_api_key: Optional[str] = None
    chart_img_base_url: str = "https://chart-img.com/chart"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/meme_stocks_db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Application settings
    debug: bool = True
    log_level: str = "INFO"
    max_stocks_to_track: int = 100
    scan_interval_minutes: int = 15
    alert_threshold_score: float = 75.0
    
    # Rate limiting
    requests_per_minute: int = 60
    burst_limit: int = 10
    
    # Notification settings
    discord_webhook_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    email_smtp_server: str = "smtp.gmail.com"
    email_port: int = 587
    email_user: Optional[str] = None
    email_password: Optional[str] = None
    
    # Watchlist configuration
    default_watchlist: list = [
        "GME", "AMC", "BBBY", "TSLA", "NVDA", "PLTR", "COIN", "HOOD", 
        "RBLX", "SOFI", "WISH", "CLOV", "BB", "NOK", "SNDL", "PROG",
        "ASTS", "RDDT", "TRUMP", "DJT"
    ]
    
    # Reddit subreddits to monitor
    reddit_subreddits: list = [
        "wallstreetbets", "stocks", "investing", "SecurityAnalysis",
        "ValueInvesting", "pennystocks", "RobinHood", "StockMarket"
    ]
    
    # Scoring weights (must sum to 1.0)
    social_sentiment_weight: float = 0.25
    technical_analysis_weight: float = 0.25
    fundamental_analysis_weight: float = 0.20
    analyst_coverage_weight: float = 0.15
    stock_structure_weight: float = 0.15
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()