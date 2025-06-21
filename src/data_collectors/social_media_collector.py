import asyncio
import aiohttp
import praw
import tweepy
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from textblob import TextBlob
import re
from collections import Counter

from ..core.config import settings
from ..models.stock_data import SocialSentiment, TrendDirection
from ..utils.rate_limiter import RateLimiter


class RedditCollector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent
        )
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def get_stock_mentions(self, symbol: str, hours_back: int = 24) -> Dict:
        """Get Reddit mentions for a specific stock symbol"""
        mentions = []
        sentiment_scores = []
        keywords = []
        
        for subreddit_name in settings.reddit_subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for symbol mentions
                query = f"${symbol} OR {symbol}"
                for submission in subreddit.search(query, time_filter="day", limit=100):
                    if self._is_recent(submission.created_utc, hours_back):
                        text = f"{submission.title} {submission.selftext}"
                        mentions.append({
                            'text': text,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'created': datetime.fromtimestamp(submission.created_utc),
                            'subreddit': subreddit_name,
                            'url': submission.url
                        })
                        
                        # Extract sentiment
                        sentiment = TextBlob(text).sentiment.polarity
                        sentiment_scores.append(sentiment)
                        
                        # Extract keywords
                        keywords.extend(self._extract_keywords(text))
                
                await self.rate_limiter.wait()
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit_name}: {e}")
        
        return {
            'mentions': mentions,
            'sentiment_scores': sentiment_scores,
            'keywords': keywords,
            'mention_count': len(mentions)
        }
    
    def _is_recent(self, timestamp: float, hours_back: int) -> bool:
        """Check if timestamp is within the specified hours"""
        post_time = datetime.fromtimestamp(timestamp)
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        return post_time >= cutoff_time
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Remove stock symbols and common words
        text = re.sub(r'\$[A-Z]+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        words = text.lower().split()
        
        # Financial keywords to look for
        financial_keywords = [
            'moon', 'rocket', 'diamond', 'hands', 'hodl', 'squeeze', 'short',
            'calls', 'puts', 'bullish', 'bearish', 'buy', 'sell', 'yolo',
            'fomo', 'dd', 'catalyst', 'earnings', 'merger', 'acquisition'
        ]
        
        relevant_words = [word for word in words if word in financial_keywords]
        return relevant_words


class TwitterCollector:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=settings.twitter_bearer_token,
            consumer_key=settings.twitter_api_key,
            consumer_secret=settings.twitter_api_secret,
            access_token=settings.twitter_access_token,
            access_token_secret=settings.twitter_access_token_secret
        )
        self.rate_limiter = RateLimiter(requests_per_minute=300)  # Twitter API v2 limit
    
    async def get_stock_mentions(self, symbol: str, hours_back: int = 24) -> Dict:
        """Get Twitter mentions for a specific stock symbol"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            query = f"${symbol} OR #{symbol} -is:retweet lang:en"
            
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                start_time=start_time,
                end_time=end_time
            ).flatten(limit=1000)
            
            mentions = []
            sentiment_scores = []
            keywords = []
            
            for tweet in tweets:
                text = tweet.text
                mentions.append({
                    'text': text,
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'like_count': tweet.public_metrics['like_count'],
                    'created': tweet.created_at,
                    'author_id': tweet.author_id
                })
                
                # Extract sentiment
                sentiment = TextBlob(text).sentiment.polarity
                sentiment_scores.append(sentiment)
                
                # Extract keywords
                keywords.extend(self._extract_keywords(text))
                
                await self.rate_limiter.wait()
            
            return {
                'mentions': mentions,
                'sentiment_scores': sentiment_scores,
                'keywords': keywords,
                'mention_count': len(mentions)
            }
            
        except Exception as e:
            print(f"Error collecting Twitter data for {symbol}: {e}")
            return {'mentions': [], 'sentiment_scores': [], 'keywords': [], 'mention_count': 0}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from tweet text"""
        # Similar to Reddit keyword extraction
        text = re.sub(r'[\$#][A-Z]+', '', text)
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        words = text.lower().split()
        
        financial_keywords = [
            'bullish', 'bearish', 'moon', 'rocket', 'calls', 'puts',
            'squeeze', 'short', 'long', 'buy', 'sell', 'hold', 'target'
        ]
        
        return [word for word in words if word in financial_keywords]


class StockTwitsCollector:
    def __init__(self):
        self.base_url = "https://api.stocktwits.com/api/2"
        self.headers = {
            'Authorization': f'Bearer {settings.stocktwits_access_token}'
        } if settings.stocktwits_access_token else {}
        self.rate_limiter = RateLimiter(requests_per_minute=200)
    
    async def get_stock_mentions(self, symbol: str, hours_back: int = 24) -> Dict:
        """Get StockTwits mentions for a specific stock symbol"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/streams/symbol/{symbol}.json"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        messages = data.get('messages', [])
                        
                        mentions = []
                        sentiment_scores = []
                        bullish_count = 0
                        bearish_count = 0
                        
                        cutoff_time = datetime.now() - timedelta(hours=hours_back)
                        
                        for message in messages:
                            created_at = datetime.strptime(
                                message['created_at'], 
                                '%Y-%m-%dT%H:%M:%SZ'
                            )
                            
                            if created_at >= cutoff_time:
                                text = message['body']
                                sentiment_data = message.get('entities', {}).get('sentiment')
                                
                                mentions.append({
                                    'text': text,
                                    'created': created_at,
                                    'user_followers': message.get('user', {}).get('followers', 0),
                                    'sentiment': sentiment_data
                                })
                                
                                # StockTwits provides sentiment labels
                                if sentiment_data:
                                    if sentiment_data.get('basic') == 'Bullish':
                                        sentiment_scores.append(0.5)
                                        bullish_count += 1
                                    elif sentiment_data.get('basic') == 'Bearish':
                                        sentiment_scores.append(-0.5)
                                        bearish_count += 1
                                else:
                                    # Fallback to TextBlob
                                    sentiment = TextBlob(text).sentiment.polarity
                                    sentiment_scores.append(sentiment)
                        
                        await self.rate_limiter.wait()
                        
                        return {
                            'mentions': mentions,
                            'sentiment_scores': sentiment_scores,
                            'keywords': [],  # StockTwits doesn't need keyword extraction
                            'mention_count': len(mentions),
                            'bullish_count': bullish_count,
                            'bearish_count': bearish_count
                        }
                    
        except Exception as e:
            print(f"Error collecting StockTwits data for {symbol}: {e}")
            
        return {'mentions': [], 'sentiment_scores': [], 'keywords': [], 'mention_count': 0}


class SocialMediaCollector:
    def __init__(self):
        self.reddit = RedditCollector()
        self.twitter = TwitterCollector()
        self.stocktwits = StockTwitsCollector()
    
    async def collect_sentiment(self, symbol: str, hours_back: int = 24) -> SocialSentiment:
        """Collect social sentiment from all platforms"""
        try:
            # Collect from all platforms concurrently
            reddit_task = self.reddit.get_stock_mentions(symbol, hours_back)
            twitter_task = self.twitter.get_stock_mentions(symbol, hours_back)
            stocktwits_task = self.stocktwits.get_stock_mentions(symbol, hours_back)
            
            reddit_data, twitter_data, stocktwits_data = await asyncio.gather(
                reddit_task, twitter_task, stocktwits_task
            )
            
            # Aggregate data
            total_mentions = (
                reddit_data['mention_count'] + 
                twitter_data['mention_count'] + 
                stocktwits_data['mention_count']
            )
            
            all_sentiment_scores = (
                reddit_data['sentiment_scores'] + 
                twitter_data['sentiment_scores'] + 
                stocktwits_data['sentiment_scores']
            )
            
            avg_sentiment = sum(all_sentiment_scores) / len(all_sentiment_scores) if all_sentiment_scores else 0
            
            # Combine keywords
            all_keywords = reddit_data['keywords'] + twitter_data['keywords']
            top_keywords = [word for word, count in Counter(all_keywords).most_common(10)]
            
            # Determine trend direction
            if avg_sentiment > 0.2:
                trend = TrendDirection.BULLISH
            elif avg_sentiment < -0.2:
                trend = TrendDirection.BEARISH
            else:
                trend = TrendDirection.NEUTRAL
            
            # Count influencer mentions (users with high follower counts)
            influencer_mentions = self._count_influencer_mentions(
                reddit_data, twitter_data, stocktwits_data
            )
            
            return SocialSentiment(
                platform="aggregated",
                mentions=total_mentions,
                sentiment_score=avg_sentiment,
                volume_trend=trend,
                top_keywords=top_keywords,
                influencer_mentions=influencer_mentions,
                timestamp=datetime.now(),
                subreddit_scores=self._calculate_subreddit_scores(reddit_data)
            )
            
        except Exception as e:
            print(f"Error collecting social sentiment for {symbol}: {e}")
            return SocialSentiment(
                platform="aggregated",
                mentions=0,
                sentiment_score=0.0,
                volume_trend=TrendDirection.NEUTRAL,
                top_keywords=[],
                influencer_mentions=0,
                timestamp=datetime.now()
            )
    
    def _count_influencer_mentions(self, reddit_data, twitter_data, stocktwits_data) -> int:
        """Count mentions from influential users"""
        influencer_count = 0
        
        # Reddit: High karma posts
        for mention in reddit_data['mentions']:
            if mention.get('score', 0) > 100:
                influencer_count += 1
        
        # Twitter: High engagement tweets
        for mention in twitter_data['mentions']:
            if mention.get('like_count', 0) > 50 or mention.get('retweet_count', 0) > 25:
                influencer_count += 1
        
        # StockTwits: Users with many followers
        for mention in stocktwits_data['mentions']:
            if mention.get('user_followers', 0) > 1000:
                influencer_count += 1
        
        return influencer_count
    
    def _calculate_subreddit_scores(self, reddit_data) -> Dict[str, float]:
        """Calculate sentiment scores by subreddit"""
        subreddit_scores = {}
        
        for mention in reddit_data['mentions']:
            subreddit = mention.get('subreddit')
            if subreddit:
                if subreddit not in subreddit_scores:
                    subreddit_scores[subreddit] = []
                
                sentiment = TextBlob(mention['text']).sentiment.polarity
                subreddit_scores[subreddit].append(sentiment)
        
        # Average sentiment by subreddit
        for subreddit, sentiments in subreddit_scores.items():
            subreddit_scores[subreddit] = sum(sentiments) / len(sentiments) if sentiments else 0
        
        return subreddit_scores