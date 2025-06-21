# 🚀 API Keys Setup Guide

This guide will help you obtain all the necessary API keys to run the Retail Meme Stock Analyzer.

## 📋 Quick Setup Checklist

### ✅ Essential APIs (Free - Start Here)
- [ ] Alpha Vantage - Financial data
- [ ] Financial Modeling Prep - Company financials 
- [ ] Reddit - Social sentiment
- [ ] Twitter - Social sentiment

### 🌟 Enhanced APIs (Free with limits)
- [ ] Polygon.io - Real-time data
- [ ] Finnhub - Additional financial data

### 💎 Premium APIs (Optional but powerful)
- [ ] ORTEX - Short interest data
- [ ] Benzinga - Analyst ratings

---

## 🔑 Free APIs Setup

### 1. Alpha Vantage (Essential)
**Purpose**: Stock prices, technical indicators
**Limit**: 5 calls/minute, 500 calls/day

1. Go to [alphavantage.co](https://www.alphavantage.co/support/#api-key)
2. Click "Get your free API key today"
3. Fill out the form (name, email, phone)
4. Check your email for the API key
5. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

### 2. Financial Modeling Prep (Essential)
**Purpose**: Company fundamentals, analyst data  
**Limit**: 250 calls/day

1. Go to [financialmodelingprep.com](https://financialmodelingprep.com/developer/docs)
2. Click "Sign Up" (top right)
3. Verify your email
4. Go to Dashboard → API Keys
5. Copy your API key
6. Add to `.env`: `FMP_API_KEY=your_key_here`

### 3. Reddit API (Essential for social sentiment)
**Purpose**: Social media sentiment from Reddit
**Limit**: 60 calls/minute

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Log in to your Reddit account
3. Scroll down and click "Create App" or "Create Another App"
4. Fill out the form:
   - **Name**: "Retail Stock Analyzer"
   - **App type**: Select "script"
   - **Description**: "Stock sentiment analysis"
   - **About URL**: Leave blank
   - **Redirect URI**: `http://localhost:8080`
5. Click "Create app"
6. Note the values:
   - **Client ID**: The string under your app name
   - **Client Secret**: The "secret" value
7. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   ```

### 4. Twitter API (Essential for social sentiment)
**Purpose**: Social media sentiment from Twitter/X
**Limit**: 300 calls/15min window

1. Go to [developer.twitter.com](https://developer.twitter.com/)
2. Click "Sign up" and log in with your Twitter account
3. Apply for a developer account:
   - Select "Hobbyist" → "Making a bot"
   - Fill out the application form
   - Wait for approval (usually instant to 24 hours)
4. Once approved, create a new app:
   - Go to Developer Portal → Projects & Apps
   - Click "Create App"
   - Name: "Retail Stock Analyzer"
5. Generate keys:
   - Go to your app → Keys and Tokens
   - Generate Bearer Token, API Key, API Secret, Access Token, Access Token Secret
6. Add to `.env`:
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
   ```

---

## 🌟 Enhanced Free APIs

### 5. Polygon.io (Recommended)
**Purpose**: Real-time stock data, better technical analysis
**Limit**: 5 calls/minute

1. Go to [polygon.io](https://polygon.io/)
2. Click "Get Free API Key"
3. Sign up with email
4. Verify email and log in
5. Go to Dashboard → API Keys
6. Copy your API key
7. Add to `.env`: `POLYGON_API_KEY=your_key_here`

### 6. Finnhub (Recommended)
**Purpose**: Additional financial data, company profiles
**Limit**: 60 calls/minute

1. Go to [finnhub.io](https://finnhub.io/register)
2. Sign up for free account
3. Verify email
4. Go to Dashboard → API Keys
5. Copy your API key
6. Add to `.env`: `FINNHUB_API_KEY=your_key_here`

### 7. StockTwits (Optional)
**Purpose**: Specialized financial social sentiment
**Limit**: 200 calls/hour

1. Go to [stocktwits.com](https://stocktwits.com/)
2. Create account and log in
3. Go to [stocktwits.com/developers](https://stocktwits.com/developers)
4. Create a new application
5. Get your access token
6. Add to `.env`: `STOCKTWITS_ACCESS_TOKEN=your_token_here`

---

## 💎 Premium APIs (Optional but Powerful)

### 8. ORTEX (Premium - Most Valuable)
**Purpose**: Real-time short interest data, utilization rates
**Cost**: Starts at ~$99/month

ORTEX provides the most accurate short interest data. This is highly valuable for meme stock analysis.

1. Go to [public.ortex.com](https://public.ortex.com)
2. Contact sales for API access
3. They offer different tiers - API access requires Pro subscription
4. Once you have access, you'll get an API key
5. Add to `.env`: `ORTEX_API_KEY=your_key_here`

**Alternative**: The system will work without ORTEX but with limited short interest data.

### 9. Benzinga API (Premium)
**Purpose**: High-quality analyst ratings, news, price targets
**Cost**: Custom pricing

1. Go to [benzinga.com/apis](https://www.benzinga.com/apis/)
2. Request a quote for API access
3. They offer a free tier for basic news
4. For analyst ratings, you need a paid plan
5. Add to `.env`: `BENZINGA_API_KEY=your_key_here`

---

## 💡 Cost-Effective Strategy

### Phase 1: Start Free (Total Cost: $0)
Get these essential APIs first:
- ✅ Alpha Vantage (free)
- ✅ Financial Modeling Prep (free)  
- ✅ Reddit API (free)
- ✅ Twitter API (free)

This gives you ~80% functionality.

### Phase 2: Add Enhanced Free APIs (Total Cost: $0)
- ✅ Polygon.io (free tier)
- ✅ Finnhub (free tier)

This gets you to ~90% functionality.

### Phase 3: Premium Upgrade (Optional)
- 💎 ORTEX (~$99/month) - Most valuable upgrade
- 💎 Benzinga (custom pricing)

This gets you to 100% functionality with professional-grade data.

---

## 🔧 Testing Your Setup

1. Copy your `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Add your API keys to `.env`

3. Test configuration:
   ```bash
   python main.py --config
   ```

4. Test with a single stock:
   ```bash
   python main.py --symbol TSLA
   ```

---

## 🚨 Common Issues & Solutions

### Reddit API Issues
- **Error**: "Invalid credentials"
- **Solution**: Make sure you're using the client ID (not the name) and client secret

### Twitter API Issues  
- **Error**: "Rate limit exceeded"
- **Solution**: The free tier has strict limits. Wait 15 minutes or upgrade.

### API Key Not Working
- **Error**: "Invalid API key"
- **Solution**: 
  - Check for extra spaces in your `.env` file
  - Make sure the key is active (some require email verification)
  - Check if you need to whitelist your IP

### SSL Certificate Errors
- **Error**: SSL verification errors
- **Solution**: This is usually a network/firewall issue. Try from a different network.

---

## 📊 Expected Costs Summary

| Service | Free Tier | Paid Tier | Recommended |
|---------|-----------|-----------|-------------|
| Alpha Vantage | 5 calls/min | $50+/month | Free OK |
| Financial Modeling Prep | 250 calls/day | $15+/month | Free OK |
| Reddit | 60 calls/min | N/A | Free |
| Twitter | 300 calls/15min | $100+/month | Free OK |
| Polygon | 5 calls/min | $99+/month | Free OK |
| Finnhub | 60 calls/min | $60+/month | Free OK |
| **ORTEX** | **None** | **$99+/month** | **Worth it** |
| Benzinga | Limited | Custom | Optional |

**Total to start**: $0  
**For professional use**: ~$99/month (just ORTEX)

---

## 🎯 Ready to Go!

Once you have at least the 4 essential APIs configured, you're ready to start analyzing meme stocks! 

Run this to verify everything works:
```bash
python main.py --symbol GME
```

If you see analysis results, you're all set! 🚀