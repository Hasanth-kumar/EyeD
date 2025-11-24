# EyeD API

FastAPI REST API layer for the EyeD AI Attendance System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you're in the project root directory.

## Running the API Server

### Development Mode

```bash
python -m api.main
```

Or using uvicorn directly:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### Attendance
- `POST /api/attendance/mark` - Mark attendance with face recognition and liveness detection

### Health Check
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API info

## Architecture

This API layer follows Clean Architecture principles:
- **Thin adapter layer**: Converts HTTP requests/responses to/from use cases
- **No business logic**: All business logic is in use cases and domain services
- **Dependency injection**: Use cases are injected via FastAPI dependencies
- **Error handling**: Domain exceptions are converted to appropriate HTTP responses

## CORS

CORS is configured to allow requests from:
- `http://localhost:3000` (Next.js dev server)
- `http://localhost:3001` (Alternative Next.js port)

To add more origins, edit `api/middleware/cors.py`.









