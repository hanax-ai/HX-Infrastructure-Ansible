
# LiteLLM SQLAlchemy Integration - Python Backend Demo

This FastAPI application demonstrates the SQLAlchemy integration that replaces Prisma in the LiteLLM Gateway implementation.

## Features

- **SQLAlchemy Models**: Complete `requests` and `responses` tables with foreign key relationships
- **Performance Monitoring**: <5ms database logging overhead measurement
- **Connection Pooling**: Production-ready PostgreSQL connection management
- **API Compatibility**: Compatible with LiteLLM Gateway `/v1/chat/completions` endpoint
- **Real-time Metrics**: Database statistics and performance monitoring endpoints

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Database URL

```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### 3. Initialize Database

```bash
python db_models.py
```

### 4. Start Server

```bash
# Development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### Core Endpoints

- `POST /v1/chat/completions` - Chat completions with SQLAlchemy logging
- `GET /api/health` - Health check
- `GET /api/db-stats` - Database statistics

### Monitoring Endpoints

- `GET /api/requests?limit=10` - Recent requests from database
- `GET /api/responses?limit=10` - Recent responses with performance metrics

## Performance Metrics

The application measures and reports:

- **Database Logging Overhead**: Time spent writing to SQLAlchemy tables
- **Total Request Latency**: End-to-end request processing time
- **Connection Pool Efficiency**: Database connection reuse rates

Example response headers:
```
X-DB-Overhead: 2.34ms
X-Total-Latency: 156.78ms
X-Request-ID: req_1234567890
```

## Database Schema

### Requests Table
```sql
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    route VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    url TEXT NOT NULL,
    headers TEXT,
    body TEXT,
    model VARCHAR(100) NOT NULL,
    status_code INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Responses Table
```sql
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    request_id_fk INTEGER REFERENCES requests(id),
    response_body TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    latency_ms DECIMAL(10,2) NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost DECIMAL(10,6) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### Basic Test
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hello"}]}'
```

### Performance Test
```bash
# Check database stats
curl http://localhost:8000/api/db-stats

# View recent requests
curl http://localhost:8000/api/requests?limit=5

# View recent responses  
curl http://localhost:8000/api/responses?limit=5
```

## Production Deployment

For production deployment:

1. **Use Gunicorn**: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`
2. **Set Connection Pool**: Adjust `pool_size` and `max_overflow` in `db_models.py`
3. **Configure Monitoring**: Set up logging and metrics collection
4. **Security**: Use environment variables for database credentials

## Integration with LiteLLM Gateway

This backend can be integrated with LiteLLM Gateway by:

1. **Replacing Prisma**: Use these SQLAlchemy models instead of Prisma schema
2. **Database Logging**: Implement the same logging calls in LiteLLM Gateway
3. **Performance Monitoring**: Use the same overhead measurement techniques
4. **Connection Management**: Apply the same connection pooling configuration

The models and patterns demonstrated here provide a drop-in replacement for Prisma with improved performance and PostgreSQL optimization.
