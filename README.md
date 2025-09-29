# Guard Owl Chatbot

A lightweight security report chatbot that ingests reports, retrieves relevant information, and produces structured answers with citations.

## Features

- **Semantic Search**: Uses ChromaDB for vector-based similarity search
- **Structured Storage**: SQLite database for efficient filtering and retrieval
- **AI Summarization**: Groq API for generating concise, contextual answers
- **Redis Caching**: Optional Redis cache for 100x faster repeated queries
- **Flexible Filtering**: Support for site ID and date range filters
- **Modular Architecture**: Easy migration to different databases and services
- **Advanced Prompting**: Engineered prompts with few-shot examples and anti-hallucination measures

## Quick Start

### 1. Setup Environment

```bash
# Clone/extract the project
cd guardowl-assignment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your Groq API key
```

### 2. Optional: Enable Redis Cache

```bash
# Install and start Redis (macOS)
brew install redis
brew services start redis

# Enable in .env
echo "REDIS_ENABLED=true" >> .env
```

### 3. Run the API Server

```bash
python3 -m uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Use the CLI Interface

```bash
python3 cli.py
```

### 5. Test with API

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What happened at Site S01 last night?",
    "siteId": "S01",
    "dateRange": {"start": "2025-08-29", "end": "2025-08-30"}
  }'
```

## API Endpoints

### POST /query
Query security reports with optional filters.

**Request Body:**
```json
{
  "query": "What happened at Site S01 last night?",
  "siteId": "S01",  // optional
  "dateRange": {    // optional
    "start": "2025-08-29",
    "end": "2025-08-30"
  }
}
```

**Date Range Behavior:**
- **Inclusive**: Both start and end dates include the entire day
- **Day-level**: `"2025-08-29"` includes all reports from 00:00:00 to 23:59:59
- **Hour-level**: Use ISO format `"2025-08-29T14:30:00"` for specific times

**Date Range Examples:**
```json
// Single day (inclusive)
{"start": "2025-08-29", "end": "2025-08-29"}

// Multiple days (both dates included)
{"start": "2025-08-29", "end": "2025-08-31"}

// Specific hours (exact time range)
{"start": "2025-08-29T20:00:00", "end": "2025-08-30T06:00:00"}

// Mixed: day start, hour end
{"start": "2025-08-29", "end": "2025-08-30T12:00:00"}
```

**Response:**
```json
{
  "answer": "Summary of relevant incidents...",
  "sources": ["r1000", "r1009", "r1021"]
}
```

### GET /health
Health check endpoint.

## Example Queries

- "What happened at Site S01 last night?"
- "Show me all incidents involving a red Toyota Camry"
- "Were there any geofence breaches this week?"
- "Any suspicious activity at the west gate?"
- "Were there any tailgating incidents?"
- "Show me incidents with a blue Honda Civic"

## Architecture

### Core Components

1. **Database Layer** (`src/database/`)
   - Abstract interface for easy migration
   - SQLite implementation with indexing
   - Ready for PostgreSQL/MongoDB migration

2. **Vector Database** (`src/vector_db/`)
   - Abstract interface for vector operations
   - ChromaDB implementation for semantic search
   - Ready for Pinecone migration

3. **LLM Layer** (`src/llm/`)
   - Abstract interface for text generation
   - Groq implementation for summarization
   - Easy to swap for other LLM providers

4. **Cache Layer** (`src/cache/`)
   - Abstract interface for caching operations
   - Redis implementation with error handling
   - Optional caching with graceful fallback

5. **Service Layer** (`src/service.py`)
   - Orchestrates all components
   - Handles query processing pipeline
   - Manages data loading and filtering

### Data Flow

1. **Cache Check**: Check Redis for cached results (if enabled)
2. **SQL Filtering**: Use indexed SQLite queries for site/date filters
3. **Vector Search**: Semantic search within filtered candidates
4. **LLM Summarization**: Generate structured summaries with citations
5. **Cache Storage**: Store results in Redis for future queries

### Performance Optimizations

- **SQL-First Filtering**: Use indexed database queries before vector search
- **Semantic Search**: ChromaDB vector similarity matching
- **Redis Caching**: 100x speedup for repeated queries (5ms vs 500ms)
- **Optimized Prompting**: Engineered prompts prevent hallucination and improve accuracy

## Scaling Considerations

### Current Architecture (52 Reports)
- **Database**: SQLite with composite indexes
- **Vector DB**: ChromaDB with local persistence
- **Cache**: Optional Redis for query results
- **Performance**: ~500ms first query, ~5ms cached queries

### Scaling to 1M+ Reports

#### Database Scaling
- **PostgreSQL Migration**: Replace SQLite for better concurrency
  ```python
  from src.database.postgresql_db import PostgreSQLDatabase
  database = PostgreSQLDatabase(connection_string)
  ```
- **Partitioning**: Partition by date/site for faster queries
- **Read Replicas**: Separate read/write workloads
- **Connection Pooling**: Use pgbouncer for connection management

#### Vector Database Scaling
- **Pinecone Migration**: Replace ChromaDB with managed Pinecone
  ```python
  from src.vector_db.pinecone_db import PineconeVectorDatabase
  vector_db = PineconeVectorDatabase(api_key, environment)
  ```
- **Namespace Strategy**: Separate vectors by site/time period
- **Batch Processing**: Async ingestion for large datasets
- **Embedding Caching**: Cache embeddings for repeated content

#### Application Scaling
- **Microservices**: Split ingestion, search, and summarization services
- **Message Queues**: Async processing with Redis/RabbitMQ
- **Load Balancing**: Multiple API instances behind load balancer
- **Multi-layer Caching**: 
  - L1: In-memory cache for hot queries
  - L2: Redis for distributed caching
  - L3: Database query result caching

#### Performance Optimizations
- **Indexing Strategy**: Composite indexes on (site_id, date, incident_type)
- **Query Optimization**: 
  - Limit vector search results based on filters
  - Use approximate nearest neighbor for speed
  - Implement query result pagination
- **Batch Operations**: Process multiple queries together
- **Smart Caching**: Cache at multiple levels with different TTLs

#### Infrastructure Scaling
- **Containerization**: Docker containers for easy deployment
- **Orchestration**: Kubernetes for auto-scaling
- **Monitoring**: Prometheus/Grafana for metrics and alerting
- **Logging**: Centralized logging with ELK stack
- **CDN**: Cache static responses at edge locations

#### Estimated Performance at Scale
- **1M Reports**: ~100-200ms query time (with optimizations)
- **10M Reports**: ~200-500ms query time (with partitioning)
- **Concurrent Users**: 1000+ with load balancing and caching
- **Cache Hit Ratio**: 80%+ for typical query patterns

## Configuration

Environment variables (set in `.env`):
- `GROQ_API_KEY`: Groq API key (required)
- `SQLITE_DB_PATH`: SQLite database path (default: guard_owl.db)
- `CHROMA_PERSIST_DIRECTORY`: ChromaDB storage path (default: ./chroma_db)
- `REDIS_ENABLED`: Enable Redis caching (default: false)
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)

## Dependencies

- **FastAPI**: Web framework for API
- **ChromaDB**: Vector database for semantic search
- **Groq**: Groq API for text generation
- **SQLite**: Structured data storage
- **Redis**: Optional caching layer
- **Pydantic**: Data validation and serialization
- **Sentence Transformers**: Text embeddings (via ChromaDB)

## Development

### Project Structure
```
src/
├── cache/            # Caching abstractions
├── database/         # Database abstractions
├── vector_db/        # Vector database abstractions
├── llm/             # LLM abstractions
├── prompts/         # Engineered prompt templates
├── config.py        # Configuration management
├── models.py        # Data models
├── service.py       # Business logic
└── main.py         # FastAPI application
```

### Adding New Components
1. Create interface in appropriate package
2. Implement concrete class
3. Update dependency injection in main.py

### Testing Cache Performance
```bash
# First request (cache miss)
time curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "red Toyota Camry"}'

# Second request (cache hit)
time curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "red Toyota Camry"}'
```

### Redis Management
```bash
# View cached queries
redis-cli KEYS "*"

# Clear cache
redis-cli FLUSHALL

# Check cache TTL
redis-cli TTL "query:abc123..."
```

## Migration Paths

The modular architecture supports easy migration:

### Database Migration
```python
# Replace in src/main.py
from src.database.postgresql_db import PostgreSQLDatabase
database = PostgreSQLDatabase(connection_string)
```

### Vector DB Migration
```python
# Replace in src/main.py
from src.vector_db.pinecone_db import PineconeVectorDatabase
vector_db = PineconeVectorDatabase(api_key, environment)
```

### Cache Migration
```python
# Replace in src/main.py
from src.cache.memcached_cache import MemcachedCache
cache = MemcachedCache(servers=['localhost:11211'])
```

## Production Deployment

### Docker Deployment
```bash
# Build and run
docker-compose up -d

# Scale API instances
docker-compose up -d --scale api=3
```

### Kubernetes Deployment
```yaml
# Deploy with auto-scaling
kubectl apply -f k8s/
kubectl autoscale deployment guard-owl-api --cpu-percent=70 --min=2 --max=10
```