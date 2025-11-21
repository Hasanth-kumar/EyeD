<div align="center">

# 👁️ EyeD

### AI-Powered Attendance Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Intelligent face recognition system with liveness detection, real-time analytics, and gamification features.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation)

---

</div>

## ✨ Features

### 🔐 **Face Recognition**
- Advanced face detection and recognition using DeepFace
- High-accuracy user identification with confidence scoring
- Support for multiple face recognition models

### 🎭 **Liveness Detection**
- Anti-spoofing protection with blink detection via MediaPipe
- Prevents photo/video-based attacks
- Real-time facial landmark tracking

### 📊 **Attendance Tracking**
- Automated attendance logging with timestamps
- Confidence-based validation system
- Historical attendance records

### 📈 **Analytics Dashboard**
- Real-time metrics and performance tracking
- Trend analysis and visualizations
- Export capabilities for reports

### 🏆 **Gamification**
- Badge system for achievements
- Leaderboards and rankings
- Performance-based rewards

### 🚀 **Modern Stack**
- FastAPI backend with comprehensive REST API
- Next.js frontend with modern UI/UX
- TypeScript for type safety

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core language |
| **FastAPI** | High-performance web framework |
| **OpenCV** | Computer vision operations |
| **DeepFace** | Face recognition engine |
| **MediaPipe** | Liveness detection & facial landmarks |
| **Pandas** | Data manipulation |
| **NumPy** | Numerical computations |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React framework with SSR |
| **TypeScript** | Type-safe development |
| **Tailwind CSS** | Utility-first styling |
| **React Query** | Data fetching & caching |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 18+ and npm
- Git

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd EyeD
```

### Step 2: Set Up Backend

Create and activate a virtual environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Frontend

Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Quick Start

### Start the API Server

```bash
python start_api.py
```

The API server will start at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

### Start the Frontend

Open a new terminal and run:
```bash
cd frontend
npm run dev
```

The frontend will be available at:
- **Web App**: `http://localhost:3000`

---

## 📁 Project Structure

```
EyeD/
├── 📂 api/                    # FastAPI routes and middleware
│   ├── routes/               # API endpoint definitions
│   └── middleware/          # CORS, error handling, logging
│
├── 📂 core/                  # Core domain logic
│   ├── recognition/         # Face recognition engine
│   ├── liveness/            # Liveness detection
│   └── attendance/          # Attendance validation
│
├── 📂 domain/                # Domain entities and services
│   ├── entities/            # Business entities
│   └── services/            # Domain services
│
├── 📂 use_cases/             # Application use cases
│   ├── mark_attendance.py
│   ├── register_user.py
│   └── ...
│
├── 📂 repositories/          # Data access layer
│   ├── user_repository.py
│   ├── attendance_repository.py
│   └── face_repository.py
│
├── 📂 infrastructure/        # External concerns
│   ├── storage/             # File storage
│   ├── camera/              # Camera interface
│   └── config/              # Configuration
│
├── 📂 frontend/              # Next.js frontend application
│   ├── app/                 # Next.js app directory
│   ├── src/                 # Source files
│   └── public/              # Static assets
│
├── 📂 tests/                 # Unit and integration tests
│
├── 📂 data/                  # Data storage
│   ├── faces/               # Face images and embeddings
│   └── attendance.csv       # Attendance records
│
├── start_api.py             # API server entry point
└── requirements.txt         # Python dependencies
```

---

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/attendance` | `POST` | Mark attendance with face recognition |
| `/api/attendance` | `GET` | Retrieve attendance records |
| `/api/users` | `GET` | Get all registered users |
| `/api/users` | `POST` | Register a new user |
| `/api/users/{user_id}` | `GET` | Get user details |
| `/api/analytics` | `GET` | Get analytics and metrics |
| `/api/leaderboard` | `GET` | Get leaderboard rankings |

### Documentation
- **Swagger UI**: Visit `http://localhost:8000/docs` for interactive API documentation
- **ReDoc**: Visit `http://localhost:8000/redoc` for alternative documentation

---

## 🎯 Usage Examples

### Register a New User
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "full_name": "John Doe",
    "email": "john@example.com"
  }'
```

### Mark Attendance
```bash
curl -X POST "http://localhost:8000/api/attendance" \
  -F "image=@face_photo.jpg"
```

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

---

## 📝 License

This project is licensed under the **MIT License**.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">

**Made with ❤️ using AI and Computer Vision**

[⬆ Back to Top](#-eyed)

</div>
