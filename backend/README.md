# Factify Backend API

FastAPI backend for the Factify fact-checking browser extension.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Server
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## 📋 API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Health Check
```http
GET /health
```

#### Fact Check Text
```http
POST /fact-check
Content-Type: application/json

{
  "text": "Text to fact-check",
  "url": "optional source URL",
  "context": "optional additional context"
}
```

#### Get Trusted Sources
```http
GET /sources
```

## 🔑 Required API Keys

### OpenAI (Primary AI Service)
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env`: `OPENAI_API_KEY=your_key_here`

### Google Fact Check Tools (Optional)
1. Go to https://console.developers.google.com/
2. Enable the Fact Check Tools API
3. Create credentials
4. Add to `.env`: `GOOGLE_FACT_CHECK_API_KEY=your_key_here`

## 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI app and main endpoints
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── services/
│   ├── ai_service.py      # AI analysis (OpenAI, etc.)
│   └── fact_check_service.py  # Fact-checking databases
└── run.py                 # Server startup script
```

## 🔧 Configuration

Edit `.env` file:

```env
# Required
OPENAI_API_KEY=your_openai_key

# Optional
GOOGLE_FACT_CHECK_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=chrome-extension://your-extension-id

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Production (Docker)
```bash
docker build -t factify-backend .
docker run -p 8000:8000 factify-backend
```

### Cloud Deployment
- **Heroku**: Use `Procfile`
- **Railway**: Connect GitHub repo
- **Vercel**: Use serverless functions
- **AWS/GCP**: Use container services

## 🔒 Security Features

- CORS configuration for browser extensions
- Rate limiting (60 requests/minute default)
- Input validation and sanitization
- API key protection
- Error handling without data leakage

## 📊 Response Format

```json
{
  "status": "verified|questionable|false|mixed",
  "verdict": "Human-readable verdict",
  "summary": "Brief summary of findings",
  "analysis": "Detailed analysis text",
  "confidence_score": 0.85,
  "sources": [
    {
      "title": "Source Name",
      "url": "https://example.com",
      "credibility_score": 0.95
    }
  ],
  "education": "Tips for verifying similar claims",
  "timestamp": "2024-01-01T12:00:00Z",
  "processing_time": 1.23
}
```

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test fact-check endpoint
curl -X POST http://localhost:8000/fact-check \
  -H "Content-Type: application/json" \
  -d '{"text": "The Earth is flat"}'
```

## 🔄 Integration with Extension

Update your extension's `content.js` to call the backend:

```javascript
async function callFactifyAPI(text) {
  const response = await fetch('http://localhost:8000/fact-check', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: text })
  });
  
  return await response.json();
}
```

## 📈 Monitoring

- Check logs for API usage
- Monitor response times
- Track fact-check accuracy
- Review error rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details