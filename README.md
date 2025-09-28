# Guard Owl Chatbot

A lightweight security report chatbot that ingests reports, retrieves relevant information, and produces structured answers with citations.

## Features

- **Semantic Search**: Uses ChromaDB for vector-based similarity search
- **Structured Storage**: SQLite database for efficient filtering and retrieval
- **AI Summarization**: Groq API for generating concise, contextual answers
- **Flexible Filtering**: Support for site ID and date range filters
- **Modular Architecture**: Easy migration to different databases and services

## Quick Start

### 1. Setup Environment

```bash
# Clone/extract the project
cd guardowl-assignment

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your Groq API key
```

### 2. Run the API Server

```bash
python -m uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Use the CLI Interface

```bash
python cli.py
```

### 4. Test with API

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

4. **Service Layer** (`src/service.py`)
   - Orchestrates all components
   - Handles query processing pipeline
   - Manages data loading and filtering

### Data Flow

1. **Ingestion**: Reports loaded into both SQLite (structured) and ChromaDB (vectors)
2. **Query**: Vector search finds semantically similar reports
3. **Filter**: Additional filtering by site ID and date range
4. **Summarize**: Groq generates concise answer from relevant reports
5. **Response**: Structured JSON with answer and source citations

## Scaling Plan (1M+ Reports)

### Database Scaling
- **PostgreSQL Migration**: Replace SQLite with PostgreSQL for better concurrency
- **Partitioning**: Partition by date/site for faster queries
- **Read Replicas**: Separate read/write workloads
- **Connection Pooling**: Use pgbouncer for connection management

### Vector Database Scaling
- **Pinecone Migration**: Replace ChromaDB with managed Pinecone
- **Namespace Strategy**: Separate vectors by site/time period
- **Batch Processing**: Async ingestion for large datasets
- **Caching**: Redis cache for frequent queries

### Application Scaling
- **Microservices**: Split ingestion, search, and summarization
- **Message Queues**: Async processing with Redis/RabbitMQ
- **Load Balancing**: Multiple API instances behind load balancer
- **Caching**: Cache frequent query results

### Performance Optimizations
- **Indexing Strategy**: Composite indexes on (site_id, date)
- **Embedding Caching**: Cache embeddings for repeated content
- **Query Optimization**: Limit vector search results, optimize filters
- **Batch Operations**: Process multiple queries together

### Infrastructure
- **Containerization**: Docker containers for easy deployment
- **Orchestration**: Kubernetes for auto-scaling
- **Monitoring**: Prometheus/Grafana for metrics
- **Logging**: Centralized logging with ELK stack

## Migration Paths

### Database Migration (SQLite → PostgreSQL)
```python
# Replace in src/main.py
from src.database.postgresql_db import PostgreSQLDatabase
database = PostgreSQLDatabase(connection_string)
```

### Vector DB Migration (ChromaDB → Pinecone)
```python
# Replace in src/main.py
from src.vector_db.pinecone_db import PineconeVectorDatabase
vector_db = PineconeVectorDatabase(api_key, environment)
```

## Development

### Project Structure
```
src/
├── database/          # Database abstractions
├── vector_db/         # Vector database abstractions
├── llm/              # LLM abstractions
├── config.py         # Configuration management
├── models.py         # Data models
├── service.py        # Business logic
└── main.py          # FastAPI application
```

### Adding New Components
1. Create interface in appropriate package
2. Implement concrete class
3. Update dependency injection in main.py

### Testing
```bash
# Run the CLI for interactive testing
python cli.py

# Test API endpoints
curl -X GET "http://localhost:8000/health"
```

## Configuration

Environment variables (set in `.env`):
- `GROQ_API_KEY`: Groq API key (required)
- `SQLITE_DB_PATH`: SQLite database path (default: guard_owl.db)
- `CHROMA_PERSIST_DIRECTORY`: ChromaDB storage path (default: ./chroma_db)

## Dependencies

- **FastAPI**: Web framework for API
- **ChromaDB**: Vector database for semantic search
- **Groq**: Groq API for text generation
- **SQLite**: Structured data storage
- **Pydantic**: Data validation and serialization
- **Sentence Transformers**: Text embeddings (via ChromaDB)