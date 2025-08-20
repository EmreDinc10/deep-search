# Deployment Guide

This guide covers deploying the Deep Search application to free hosting platforms.

## Architecture

- **Frontend**: Next.js → Vercel (Free tier)
- **Backend**: FastAPI → Railway/Render (Free tier)

## Prerequisites

1. Azure OpenAI API credentials
2. GitHub account
3. Vercel account
4. Railway or Render account

## Backend Deployment (Railway)

### Option 1: Railway (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the backend service

3. **Set Environment Variables**:
   ```
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=o3-mini
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   ```

4. **Custom Start Command** (if needed):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Get your backend URL**: `https://your-app.up.railway.app`

### Option 2: Render

1. **Deploy to Render**:
   - Go to [render.com](https://render.com)
   - Create new "Web Service"
   - Connect your GitHub repository
   - Select the `backend` folder as root directory

2. **Configuration**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.11

3. **Environment Variables**: Same as Railway

## Frontend Deployment (Vercel)

1. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub
   - Click "New Project"
   - Import your repository
   - Set root directory to `frontend`

2. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
   ```

3. **Build Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: frontend
   - **Build Command**: npm run build
   - **Output Directory**: .next

## Alternative Free Hosting Options

### Backend Alternatives:
1. **Heroku** (Free tier discontinued, but still available with paid plans)
2. **PythonAnywhere** (Free tier with limitations)
3. **Deta Space** (Free tier)
4. **Fly.io** (Free tier with limitations)

### Frontend Alternatives:
1. **Netlify** (Free tier)
2. **GitHub Pages** (Static only, requires adaptation)
3. **Surge.sh** (Free for static sites)

## Environment Variables Reference

### Backend (.env)
```bash
# Required
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=o3-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Optional
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name

# Server
PORT=8000
HOST=0.0.0.0
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

## Post-Deployment Steps

1. **Test the API**: Visit `https://your-backend-url/docs` for API documentation
2. **Test the Frontend**: Visit your Vercel URL
3. **Update CORS**: If needed, update CORS settings in `main.py`
4. **Monitor Usage**: Keep track of API usage and hosting limits

## Troubleshooting

### Common Issues:

1. **CORS Errors**: 
   - Update `allow_origins` in `main.py`
   - Ensure frontend URL is included

2. **Environment Variables Not Loading**:
   - Check variable names match exactly
   - Restart the deployment after adding variables

3. **Build Failures**:
   - Check Python/Node versions
   - Verify all dependencies are listed

4. **API Rate Limits**:
   - Implement request throttling
   - Add caching for search results

### Free Tier Limitations:

- **Railway**: 500 hours/month, sleeps after 5 minutes of inactivity
- **Render**: 750 hours/month, sleeps after 15 minutes of inactivity
- **Vercel**: 100GB bandwidth/month, 100 executions/day for serverless functions

## Scaling Considerations

When ready to scale beyond free tiers:

1. **Upgrade hosting plans**
2. **Add Redis for caching**
3. **Implement rate limiting**
4. **Add database for search history**
5. **Use CDN for static assets**
