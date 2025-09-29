from typing import Optional
from fastapi import FastAPI, HTTPException
from .config import settings
from .database.sqlite_db import SQLiteDatabase
from .vector_db.chroma_db import ChromaVectorDatabase
from .llm.groq_llm import GroqLLM
from .cache.redis_cache import RedisCache
from .service import GuardOwlService
from .models import QueryRequest, QueryResponse

app = FastAPI(title="Guard Owl Chatbot", version="1.0.0")

# Initialize components
database = SQLiteDatabase(settings.sqlite_db_path)
vector_db = ChromaVectorDatabase(settings.chroma_persist_directory)

# Initialize LLM only if API key is provided
if not settings.groq_api_key:
    raise ValueError("GROQ_API_KEY is required. Please set it in your .env file.")

llm = GroqLLM(settings.groq_api_key)

# Initialize cache if enabled
cache = None
if getattr(settings, 'redis_enabled', False):
    try:
        redis_host = getattr(settings, 'redis_host', 'localhost')
        redis_port = getattr(settings, 'redis_port', 6379)
        cache = RedisCache(redis_host, redis_port)
    except Exception as e:
        print(f"Warning: Redis connection failed: {e}. Running without cache.")

service = GuardOwlService(database, vector_db, llm, cache)

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    try:
        service.load_reports("guard_owl_mock_reports.json")
    except FileNotFoundError:
        print("Warning: guard_owl_mock_reports.json not found. Please ensure the file exists.")

@app.post("/query", response_model=QueryResponse)
async def query_reports(request: QueryRequest):
    """Query security reports"""
    try:
        return service.query(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)