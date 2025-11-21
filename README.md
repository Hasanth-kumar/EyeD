# EyeD - AI Attendance System

AI-powered attendance management system using face recognition, liveness detection, and real-time analytics.

## Features

- **Face Recognition**: Register and recognize users using DeepFace
- **Liveness Detection**: Anti-spoofing with blink detection via MediaPipe
- **Attendance Tracking**: Automated attendance logging with confidence scoring
- **Analytics Dashboard**: Real-time metrics, trends, and performance tracking
- **Gamification**: Badge system, leaderboards, and achievement tracking
- **REST API**: FastAPI backend with comprehensive endpoints
- **Web Dashboard**: Next.js frontend with modern UI

## Tech Stack

**Backend:**
- Python 3.8+
- FastAPI
- OpenCV, DeepFace, MediaPipe
- Pandas, NumPy

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- React Query

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd EyeD
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Running the Project

### Start the API Server

```bash
python start_api.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
EyeD/
├── api/              # FastAPI routes and middleware
├── core/             # Core domain logic (recognition, liveness, attendance)
├── domain/           # Domain entities and services
├── use_cases/        # Application use cases
├── repositories/     # Data access layer
├── infrastructure/   # External concerns (storage, camera, config)
├── frontend/         # Next.js frontend application
└── tests/            # Unit tests
```

## API Endpoints

- `/api/attendance` - Attendance operations
- `/api/users` - User management
- `/api/analytics` - Analytics and reporting
- `/api/leaderboard` - Gamification and leaderboards

## License

MIT License
