# FanPulse API

REST API for the FanPulse platform - AI-powered FIFA World Cup match understanding.

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the Server

```bash
# From project root
python src/api/main.py

# Or with uvicorn directly
uvicorn src.api.main:app --reload --port 8000
```

### 3. Access API

- **API Root:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### General Endpoints

#### GET `/`
Root endpoint with API information.

**Response:**
```json
{
  "name": "FanPulse API",
  "version": "1.0.0",
  "agents": {
    "var_lens": {...},
    "tactical_pulse": {...}
  }
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "FanPulse API",
  "version": "1.0.0"
}
```

### VAR-Lens Endpoints

#### POST `/var-lens/explain`
Explain a VAR decision or rule.

**Request:**
```json
{
  "question": "Why was that goal disallowed for offside?",
  "language": "en",
  "include_sources": true
}
```

**Response:**
```json
{
  "question": "Why was that goal disallowed for offside?",
  "answer": "A goal is disallowed for offside when...",
  "sources": [
    {
      "content": "According to Law 11...",
      "file": "Laws of the Game 2026_27.md",
      "relevance_score": 0.95
    }
  ],
  "language": "en"
}
```

#### GET `/var-lens/health`
VAR-Lens agent health check.

**Response:**
```json
{
  "status": "healthy",
  "agent": "VAR-Lens",
  "vector_store_loaded": true,
  "llm_available": true
}
```

#### GET `/var-lens/stats`
Get VAR-Lens agent statistics.

**Response:**
```json
{
  "agent": "VAR-Lens",
  "status": "operational",
  "docs_path": "data/processed_documents",
  "num_vectors": 450,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

#### GET `/var-lens/sample-questions`
Get sample questions for testing.

**Response:**
```json
{
  "questions": [
    "What is VAR?",
    "When can VAR be used?",
    ...
  ],
  "count": 8
}
```

#### POST `/var-lens/rebuild-index`
Rebuild the vector store (maintenance endpoint).

**Response:**
```json
{
  "status": "success",
  "message": "Vector store rebuilt successfully",
  "stats": {...}
}
```

## Usage Examples

### Python

```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/var-lens/explain",
    json={
        "question": "What is VAR?",
        "language": "en",
        "include_sources": True
    }
)

result = response.json()
print(result["answer"])
```

### cURL

```bash
# Ask a question
curl -X POST "http://localhost:8000/var-lens/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is VAR?",
    "language": "en",
    "include_sources": true
  }'

# Health check
curl "http://localhost:8000/var-lens/health"
```

### JavaScript/Fetch

```javascript
// Ask a question
const response = await fetch('http://localhost:8000/var-lens/explain', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What is VAR?',
    language: 'en',
    include_sources: true
  })
});

const result = await response.json();
console.log(result.answer);
```

## Error Handling

### 400 Bad Request
Invalid request parameters.

```json
{
  "detail": "Validation error: question must be at least 5 characters"
}
```

### 503 Service Unavailable
Agent not initialized or vector store not loaded.

```json
{
  "detail": "VAR-Lens agent not initialized. Please contact administrator."
}
```

### 500 Internal Server Error
Unexpected error during processing.

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred. Please try again later."
}
```

## Configuration

### Environment Variables

```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-key-here

# Or for IBM Granite
IBM_CLOUD_API_KEY=your-ibm-key
IBM_WATSONX_PROJECT_ID=your-project-id

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### CORS Configuration

By default, CORS is enabled for all origins. In production, update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn src.api.main:app --reload --port 8000

# With custom host
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test with sample questions
python -c "
import requests
questions = [
    'What is VAR?',
    'When can VAR be used?',
    'What are the reviewable incidents?'
]
for q in questions:
    r = requests.post('http://localhost:8000/var-lens/explain', 
                      json={'question': q})
    print(f'Q: {q}')
    print(f'A: {r.json()[\"answer\"][:100]}...\n')
"
```

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Use a production ASGI server:**
   ```bash
   pip install gunicorn
   gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Add authentication:**
   - API keys
   - OAuth2
   - JWT tokens

3. **Rate limiting:**
   - Use middleware like `slowapi`

4. **Monitoring:**
   - Add logging
   - Use APM tools (New Relic, DataDog)

5. **Caching:**
   - Cache frequent queries
   - Use Redis for session storage

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   API Routes                          │  │
│  │                                                        │  │
│  │  /var-lens/*        /tactical-pulse/*                │  │
│  │       ↓                     ↓                         │  │
│  │  VAR-Lens Agent    Tactical Pulse Agent              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              RAG Engine / Data Pipeline               │  │
│  │                                                        │  │
│  │  • Vector Store (FAISS)                              │  │
│  │  • LLM (IBM Granite / OpenAI)                        │  │
│  │  • Document Processing                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Issue: "Module not found"
**Solution:** Make sure you're running from project root:
```bash
cd /path/to/FanPulse
python src/api/main.py
```

### Issue: "Vector store not loaded"
**Solution:** Build vector store first:
```bash
python scripts/build_var_lens_vectorstore.py
```

### Issue: "LLM not available"
**Solution:** Set API key and initialize LLM:
```bash
export OPENAI_API_KEY="sk-your-key"
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Last Updated:** 2026-06-10  
**Version:** 1.0.0  
**Status:** Production Ready 🚀