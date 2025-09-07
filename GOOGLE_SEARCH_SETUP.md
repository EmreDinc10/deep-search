# Google Search Setup Guide

This application supports multiple methods for Google search integration. Here are the available options:

## Option 1: Google Custom Search API (Recommended)

This is the official and most reliable method:

### Setup Steps:

1. **Get Google API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Custom Search API
   - Create credentials (API Key)

2. **Create Custom Search Engine:**
   - Go to [Custom Search Engine](https://cse.google.com/cse/create/new)
   - Add `*` as the site to search (for searching the entire web)
   - Get your Search Engine ID (CSE ID)

3. **Configure Environment Variables:**
   ```bash
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_CSE_ID=your_custom_search_engine_id_here
   ```

### Free Tier Limits:
- 100 search queries per day for free
- $5 per 1000 additional queries

## Option 2: SerpAPI (Alternative)

Professional Google search API service:

### Setup Steps:

1. **Sign up for SerpAPI:**
   - Go to [SerpAPI](https://serpapi.com/)
   - Sign up for an account
   - Get your API key from dashboard

2. **Configure Environment Variable:**
   ```bash
   SERPAPI_KEY=your_serpapi_key_here
   ```

### Free Tier Limits:
- 100 searches per month for free
- Paid plans available for higher usage

## Option 3: Web Scraping Fallback

The application includes intelligent web scraping as a fallback:

- **No setup required**
- Uses rotating user agents and multiple Google domains
- May be rate-limited or blocked
- Works as backup when API methods fail

## Option 4: googlesearch-python Library

Simple Python library for Google search:

- **No setup required**
- Already included in requirements
- May be unreliable in production
- Used as final fallback

## How It Works

The application tries these methods in order:

1. **Google Custom Search API** (if credentials provided)
2. **SerpAPI** (if credentials provided)  
3. **Web scraping** (with rotating user agents)
4. **googlesearch-python library** (last resort)

## Deployment Configuration

### For Render Deployment:

1. Go to your Render dashboard
2. Select your service
3. Go to Environment tab
4. Add the environment variables:
   - `GOOGLE_API_KEY` (if using Google Custom Search)
   - `GOOGLE_CSE_ID` (if using Google Custom Search)
   - `SERPAPI_KEY` (if using SerpAPI)

### Testing Without API Keys:

The application will still work with DuckDuckGo and Wikipedia search even without Google API credentials. The web scraping fallback may provide some Google results depending on server location and rate limiting.

## Recommended Setup:

For production use, we recommend:
1. **SerpAPI** for reliable, high-quality Google results
2. **Google Custom Search API** for cost-effective solution with moderate usage
3. Keep fallback methods enabled for redundancy

Both API services provide much more reliable results than web scraping and are less likely to be blocked.
