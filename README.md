# Deep Search App

A parallel search application that uses Azure OpenAI and multiple free search modules to conduct comprehensive searches across different sources.

## 🚀 Features

- **Parallel Search**: Simultaneous searches across Google, DuckDuckGo, and Wikipedia
- **AI Synthesis**: Azure OpenAI-powered result analysis and synthesis
- **Real-time Streaming**: Watch results arrive in real-time from different sources
- **Modern Web Interface**: Responsive Next.js frontend with Tailwind CSS
- **Free Deployment**: Deploy on Vercel + Railway/Render free tiers
- **No API Keys Required**: Uses free search libraries (except optional Reddit)

## 🏗️ Architecture

- **Frontend**: Next.js (TypeScript) + Tailwind CSS → Deployed on Vercel
- **Backend**: FastAPI (Python) → Deployed on Railway/Render
- **AI**: Azure OpenAI (o3-mini model)
- **Search Sources**: 
  - Google Search (googlesearch-python)
  - DuckDuckGo Search (duckduckgo-search)
  - Wikipedia Search (wikipedia)
  - Reddit Search (PRAW - optional)

## 📁 Project Structure

```
/backend              # FastAPI Python backend
  ├── main.py         # FastAPI application
  ├── models.py       # Pydantic data models
  ├── search_modules.py # Search engine implementations
  ├── azure_openai_client.py # Azure OpenAI integration
  ├── requirements.txt # Python dependencies
  ├── Dockerfile      # Container configuration
  └── start.sh        # Local startup script

/frontend             # Next.js frontend
  ├── app/            # Next.js 14 app directory
  ├── components/     # React components
  ├── package.json    # Node.js dependencies
  └── tailwind.config.js # Tailwind configuration

/docs                 # Documentation
  ├── DEPLOYMENT.md   # Deployment guide
  └── API.md          # API documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Azure OpenAI API credentials

### 1. Clone and Setup
```bash
git clone <repository-url>
cd deep-search
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment
Update `backend/.env` with your Azure OpenAI credentials:
```bash
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=o3-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 3. Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 4. Start Frontend
```bash
cd frontend
npm run dev
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🌐 Usage

1. **Enter Search Query**: Type your search terms in the search box
2. **Select Sources**: Choose which search engines to query
3. **Choose Mode**: 
   - Regular: Get all results at once with AI synthesis
   - Streaming: Watch results arrive in real-time
4. **View Results**: 
   - Overview tab shows summary statistics
   - AI Synthesis tab shows AI-generated analysis
   - Individual source tabs show detailed results

## 🔧 API Endpoints

### Search
- `POST /search` - Perform parallel search with AI synthesis
- `GET /search/stream/{query}` - Stream search results in real-time
- `POST /analyze` - Get AI insights without full synthesis

### Utility
- `GET /health` - Health check
- `GET /sources` - List available search sources

## 📊 Features in Detail

### Parallel Search Execution
The application uses Python's `asyncio` to execute searches across multiple sources simultaneously, significantly reducing total search time.

### AI-Powered Synthesis
Azure OpenAI analyzes results from all sources to provide:
- Comprehensive summaries
- Key insights and patterns
- Conflicting information identification
- Source reliability assessment

### Real-time Streaming
WebSocket-like streaming allows users to see results as they arrive from each source, providing immediate feedback and improved user experience.

### Responsive Design
The frontend adapts to different screen sizes and provides an intuitive interface for monitoring parallel search progress.

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

### Quick Deploy
1. **Backend**: Deploy to Railway/Render
2. **Frontend**: Deploy to Vercel
3. **Set Environment Variables**
4. **Update API URL in frontend**

## 🔧 Configuration

### Search Sources
Add new search sources by:
1. Creating a new `SearchModule` class in `search_modules.py`
2. Adding the source to `SearchSource` enum in `models.py`
3. Registering in `ParallelSearchManager.setup_modules()`

### AI Models
Change the Azure OpenAI model by updating:
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=your_model_name
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🔗 Links

- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Deployment](https://vercel.com/docs)
- [Railway Deployment](https://docs.railway.app/)

## 🐛 Troubleshooting

### Common Issues
1. **Search Failures**: Check internet connection and search library versions
2. **AI Synthesis Errors**: Verify Azure OpenAI credentials and quotas
3. **CORS Issues**: Update CORS settings in `main.py` for production
4. **Rate Limiting**: Implement delays between requests if needed

### Support
- Check the [GitHub Issues](issues) for known problems
- Review [API Documentation](http://localhost:8000/docs) when backend is running
- Consult [Deployment Guide](DEPLOYMENT.md) for hosting issues
