# Architecture Rules

## Overview
This document defines the high-level architecture for the EyeD project rebuild. All code must follow Clean Architecture principles with strict layer separation and SOLID compliance.

## Core Principles

### 1. Clean Architecture Layers

The project follows a strict layered architecture with clear boundaries:

```
┌─────────────────────────────────────────────────────────┐
│  Presentation Layer (Frontend)                          │
│  - Next.js App Router (React)                          │
│  - WebRTC + Canvas for camera capture                    │
│  - REST API client for backend communication           │
│  - UI components (shadcn/ui)                           │
│  - Input validation only (Zod schemas)                │
│  - NO business logic                                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Application Layer (Use Cases)                           │
│  - RegisterUserUseCase                                   │
│  - MarkAttendanceUseCase                                 │
│  - GenerateReportUseCase                                 │
│  - CalculateBadgesUseCase                                │
│  - ExportAttendanceDataUseCase                          │
│  - GenerateLeaderboardUseCase                           │
│  - GetAnalyticsUseCase                                  │
│  - GetUserInfoUseCase                                   │
│  - GetUserPerformanceUseCase                            │
│  - UpdateUserInfoUseCase                                │
│  - Orchestrates services, no business logic             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Domain Layer (Business Logic)                           │
│  - Core business rules                                  │
│  - Domain entities (User, AttendanceRecord, etc.)       │
│  - Domain services (BadgeCalculator, etc.)              │
│  - Pure logic, no dependencies on infrastructure         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Infrastructure Layer (External Concerns)               │
│  - Repositories (data access)                           │
│  - File storage                                          │
│  - Camera handling                                       │
│  - External APIs                                         │
└─────────────────────────────────────────────────────────┘
```

### 2. Dependency Rule

**CRITICAL**: Dependencies must point inward only.

- ✅ **Presentation** → Application → Domain
- ✅ **Application** → Domain
- ✅ **Infrastructure** → Domain
- ❌ **Domain** → Infrastructure (NEVER)
- ❌ **Domain** → Application (NEVER)
- ❌ **Domain** → Presentation (NEVER)

### 3. Layer Responsibilities

#### Presentation Layer (`frontend/`)
- **ONLY**: User interface, input/output formatting, display logic
- **NO**: Business logic, data access, calculations
- **Technologies**: Next.js (App Router), WebRTC, Canvas API, REST API client
- **Example**: React components that call REST API endpoints (which call use cases)

#### Application Layer (`use_cases/`)
- **ONLY**: Orchestrates domain services to fulfill use cases
- **NO**: Business rules, data access, UI logic
- **Example**: `MarkAttendanceUseCase` coordinates recognition, liveness, and logging

#### Domain Layer (`domain/`, `core/`)
- **ONLY**: Business logic, domain rules, entities
- **NO**: Infrastructure concerns (files, databases, APIs)
- **Example**: `BadgeCalculator` calculates badges based on attendance data

#### Infrastructure Layer (`infrastructure/`, `repositories/`)
- **ONLY**: Data persistence, external services, file I/O
- **NO**: Business logic, domain rules
- **Components**:
  - `repositories/`: UserRepository, AttendanceRepository, FaceRepository
  - `infrastructure/storage/`: FileStorage, CSVHandler, ExportFormatter
  - `infrastructure/camera/`: CameraManager
  - `infrastructure/config/`: Settings
  - `infrastructure/utils/`: ImageConverter
- **Example**: `AttendanceRepository` saves/loads attendance records using `CSVHandler`

## Project Structure

```
eyed/
├── core/                          # Core domain logic (SRP-compliant)
│   ├── recognition/              # Face recognition domain
│   │   ├── __init__.py           # Package exports
│   │   ├── detector.py           # Face detection ONLY
│   │   ├── recognizer.py         # Face recognition ONLY
│   │   ├── embedding_extractor.py # Embedding extraction ONLY
│   │   ├── quality_assessor.py   # Quality assessment ONLY
│   │   ├── strategies.py         # Detection strategies (MediaPipe, OpenCV)
│   │   └── value_objects.py      # Recognition value objects
│   ├── liveness/                 # Liveness detection domain
│   │   ├── __init__.py           # Package exports
│   │   ├── blink_detector.py     # Blink detection ONLY
│   │   ├── landmark_extractor.py # Landmark extraction ONLY
│   │   └── value_objects.py      # Liveness value objects
│   ├── attendance/               # Attendance domain
│   │   ├── __init__.py           # Package exports
│   │   ├── attendance_logger.py  # Logging attendance ONLY
│   │   ├── attendance_validator.py # Validation ONLY
│   │   └── value_objects.py      # Attendance value objects
│   └── shared/                   # Shared core components
│       ├── __init__.py           # Package exports
│       └── constants.py          # Core constants
│
├── domain/                       # Domain models (pure data)
│   ├── entities/                # Domain entities
│   │   ├── __init__.py           # Package exports
│   │   ├── user.py              # User entity
│   │   ├── attendance_record.py  # Attendance record entity
│   │   ├── attendance_session.py # Attendance session entity
│   │   ├── badge.py             # Badge entity
│   │   └── face_embedding.py    # Face embedding entity
│   ├── services/                # Domain services (business logic)
│   │   ├── __init__.py           # Package exports
│   │   ├── analytics/           # Analytics domain services
│   │   │   ├── __init__.py       # Package exports
│   │   │   ├── metrics_calculator.py # Metrics calculation logic
│   │   │   ├── timeline_analyzer.py   # Timeline analysis logic
│   │   │   └── value_objects.py       # Analytics value objects
│   │   ├── attendance/          # Attendance domain services
│   │   │   ├── __init__.py       # Package exports
│   │   │   └── attendance_service.py  # Attendance business logic
│   │   ├── gamification/        # Gamification domain services
│   │   │   ├── __init__.py       # Package exports
│   │   │   ├── badge_calculator.py    # Badge calculation logic
│   │   │   ├── badge_definitions.py   # Badge definitions
│   │   │   ├── leaderboard_generator.py # Leaderboard logic
│   │   │   ├── streak_calculator.py   # Streak calculation logic
│   │   │   └── value_objects.py       # Gamification value objects
│   │   ├── liveness/            # Liveness domain services
│   │   │   ├── __init__.py       # Package exports
│   │   │   ├── liveness_service.py    # Liveness business logic
│   │   │   └── liveness_verifier.py   # Liveness verification logic
│   │   ├── recognition/         # Recognition domain services
│   │   │   ├── __init__.py       # Package exports
│   │   │   ├── face_recognition_service.py # Face recognition business logic
│   │   │   └── user_registration_service.py # User registration business logic
│   │   ├── report_generation/   # Report generation domain services
│   │   │   ├── __init__.py       # Package exports
│   │   │   ├── daily_report_generator.py    # Daily report generation
│   │   │   ├── monthly_report_generator.py  # Monthly report generation
│   │   │   ├── overview_report_generator.py # Overview report generation
│   │   │   ├── report_generator.py          # Base report generator
│   │   │   ├── report_generator_factory.py  # Report generator factory
│   │   │   ├── user_report_generator.py     # User report generation
│   │   │   └── weekly_report_generator.py    # Weekly report generation
│   │   └── protocols.py         # Domain service protocols (interfaces)
│   └── shared/                  # Shared domain components
│       ├── __init__.py           # Package exports
│       ├── constants.py         # Domain constants
│       ├── enums.py             # Domain enums
│       ├── exceptions.py        # Domain exceptions
│       └── attendance_value_objects.py # Attendance validation value objects
│
├── use_cases/                    # Application use cases (SRP: one use case per file)
│   ├── __init__.py               # Package exports
│   ├── register_user.py          # Register user use case
│   ├── recognize_face.py         # Recognize face use case
│   ├── mark_attendance.py        # Mark attendance use case
│   ├── generate_report.py        # Generate report use case
│   ├── calculate_badges.py       # Calculate badges use case
│   ├── export_attendance_data.py # Export attendance data use case
│   ├── generate_leaderboard.py   # Generate leaderboard use case
│   ├── get_all_users.py          # Get all users use case
│   ├── get_analytics.py          # Get analytics use case
│   ├── get_attendance_records.py # Get attendance records use case
│   ├── get_user_info.py          # Get user info use case
│   ├── get_user_performance.py   # Get user performance use case
│   └── update_user_info.py      # Update user info use case
│
├── repositories/                 # Data access (SRP: persistence only)
│   ├── __init__.py               # Package exports
│   ├── attendance_repository.py  # CRUD for attendance
│   ├── user_repository.py        # CRUD for users
│   └── face_repository.py        # CRUD for faces
│
├── infrastructure/               # External concerns
│   ├── __init__.py               # Package exports
│   ├── storage/                  # File/database storage
│   │   ├── __init__.py           # Package exports
│   │   ├── file_storage.py       # File operations
│   │   ├── csv_handler.py        # CSV operations
│   │   └── export_formatter.py   # Export formatting
│   ├── camera/                   # Camera handling
│   │   ├── __init__.py           # Package exports
│   │   └── camera_manager.py     # Camera operations
│   ├── config/                   # Configuration
│   │   ├── __init__.py           # Package exports
│   │   └── settings.py           # App configuration
│   └── utils/                    # Infrastructure utilities
│       ├── __init__.py           # Package exports
│       └── image_converter.py    # Image conversion utilities
│
├── api/                          # REST API Layer (FastAPI)
│   ├── __init__.py               # Package exports
│   ├── main.py                   # FastAPI application entry point
│   ├── dependencies.py           # Dependency injection setup
│   ├── README.md                 # API documentation
│   ├── middleware/               # API middleware
│   │   ├── __init__.py           # Package exports
│   │   ├── cors.py               # CORS configuration
│   │   ├── error_handler.py      # Global error handling
│   │   └── logging.py            # Request logging
│   └── routes/                   # API route handlers
│       ├── __init__.py           # Package exports
│       ├── attendance.py         # Attendance endpoints
│       ├── users.py              # User endpoints
│       ├── analytics.py          # Analytics endpoints
│       └── leaderboard.py        # Leaderboard endpoints
│
├── data/                         # Data storage directory
│   ├── attendance.csv            # Attendance records CSV
│   ├── faces/                    # Face images and embeddings
│   │   ├── embeddings_cache.pkl # Cached face embeddings
│   │   ├── faces.json           # Face metadata
│   │   ├── backups/             # Backup face images
│   │   └── *.jpg                # Face image files
│   └── exports/                 # Generated export files
│       ├── monthly_summary.csv
│       ├── weekly_trends.csv
│       └── user_performance_summary.csv
│
├── logs/                         # Application logs
│   └── eyed_YYYYMMDD.log        # Daily log files
│
├── tests/                        # Test files
│   └── unit/                     # Unit tests
│       ├── core/                 # Core domain tests
│       │   └── liveness/         # Liveness core tests
│       └── domain/               # Domain tests
│           └── services/         # Domain service tests
│               └── liveness/     # Liveness service tests
│
└── frontend/                     # Next.js Frontend (Presentation Layer)
    ├── app/                      # Next.js App Router
    │   ├── layout.tsx            # Root layout
    │   ├── page.tsx              # Home page
    │   ├── providers.tsx         # React Query and other providers
    │   └── dashboard/            # Dashboard routes
    │       ├── layout.tsx        # Dashboard layout
    │       ├── page.tsx          # Dashboard overview
    │       ├── attendance/       # Mark attendance page
    │       │   └── page.tsx
    │       ├── register/         # User registration page
    │       │   └── page.tsx
    │       ├── analytics/        # Analytics page
    │       │   └── page.tsx
    │       ├── leaderboard/      # Leaderboard page
    │       │   └── page.tsx
    │       ├── users/            # Users management page
    │       │   └── page.tsx
    │       └── reports/          # Reports page
    │           └── page.tsx
    ├── src/                      # Source code directory
    │   ├── components/           # React components
    │   │   ├── ui/               # shadcn/ui components
    │   │   │   ├── button.tsx
    │   │   │   ├── card.tsx
    │   │   │   ├── input.tsx
    │   │   │   └── ...           # All shadcn/ui components
    │   │   ├── camera/           # Camera components
    │   │   │   ├── CameraCapture.tsx # WebRTC camera capture
    │   │   │   ├── FrameCollector.tsx # Frame collection logic
    │   │   │   ├── CanvasRenderer.tsx # Canvas rendering
    │   │   │   └── LivenessVerifier.tsx # Liveness verification UI
    │   │   ├── layout/           # Layout components
    │   │   │   ├── Sidebar.tsx
    │   │   │   ├── Header.tsx
    │   │   │   └── MainLayout.tsx
    │   │   └── NavLink.tsx       # Navigation link component
    │   ├── lib/                  # Utility libraries
    │   │   ├── api/              # API client
    │   │   │   ├── client.ts     # REST API client
    │   │   │   └── endpoints.ts  # API endpoint definitions
    │   │   ├── hooks/            # Custom React hooks
    │   │   │   ├── useCamera.ts # Camera WebRTC hook
    │   │   │   ├── useMediaPipe.ts # MediaPipe integration hook
    │   │   │   ├── useFrameCollection.ts # Frame collection hook
    │   │   │   └── useApi.ts     # API call hook
    │   │   ├── store/            # State management (Zustand)
    │   │   │   ├── attendanceStore.ts
    │   │   │   ├── userStore.ts
    │   │   │   └── uiStore.ts
    │   │   ├── schemas/          # Zod validation schemas
    │   │   │   ├── attendance.ts
    │   │   │   ├── user.ts
    │   │   │   └── api.ts
    │   │   └── utils/            # Utility functions
    │   │       ├── blinkDetection.ts # Blink detection utilities
    │   │       ├── formatters.ts
    │   │       ├── validators.ts
    │   │       └── utils.ts      # General utilities
    │   ├── types/                # TypeScript types
    │   │   ├── attendance.ts
    │   │   ├── user.ts
    │   │   └── api.ts
    │   ├── hooks/                # Additional React hooks
    │   │   ├── use-mobile.tsx    # Mobile detection hook
    │   │   └── use-toast.ts     # Toast notification hook
    │   └── index.css             # Global styles
    ├── public/                   # Static assets
    │   ├── favicon.ico
    │   ├── placeholder.svg
    │   └── robots.txt
    ├── package.json
    ├── package-lock.json
    ├── bun.lockb
    ├── tsconfig.json
    ├── tsconfig.tsbuildinfo
    ├── next.config.js
    ├── tailwind.config.ts
    ├── postcss.config.js
    ├── components.json
    ├── eslint.config.js
    ├── next-env.d.ts
    └── README.md
├── requirements.txt              # Python dependencies
├── start_api.py                 # API startup script
├── ARCHIVE_SUMMARY.md           # Archive documentation
└── README.md                    # Project documentation
```

## Single Responsibility Principle (SRP)

### Rule: One Class = One Responsibility

**✅ CORRECT:**
```python
# core/recognition/detector.py
class FaceDetector:
    """ONLY detects faces in images"""
    def detect(self, image: np.ndarray) -> List[Face]:
        pass

# core/recognition/recognizer.py  
class FaceRecognizer:
    """ONLY recognizes faces from embeddings"""
    def recognize(self, embedding: np.ndarray) -> Optional[User]:
        pass
```

**❌ WRONG (from old code):**
```python
# ❌ BAD: Multiple responsibilities
class GamificationService:
    """Does badges, leaderboards, achievements, timeline analysis"""
    def calculate_user_badges(self): pass
    def get_leaderboard(self): pass
    def get_achievements(self): pass
    def analyze_timeline(self): pass
    # 600+ lines doing too many things
```

**✅ CORRECT (new approach):**
```python
# domain/services/badge_calculator.py
class BadgeCalculator:
    """ONLY calculates badges"""
    def calculate(self, attendance_data: List[AttendanceRecord]) -> List[Badge]:
        pass

# domain/services/leaderboard_generator.py
class LeaderboardGenerator:
    """ONLY generates leaderboards"""
    def generate(self, users: List[User], metric: str) -> Leaderboard:
        pass
```

## Service Size Limits

- **Maximum class size**: 300 lines
- **Maximum method size**: 50 lines
- **Maximum file size**: 500 lines
- **If exceeded**: Split into smaller, focused classes

## Anti-Patterns to Avoid

### 1. God Classes
**❌ OLD CODE:**
```python
class AttendanceService:
    # 700+ lines
    # Handles recognition, liveness, logging, reporting, analytics, export
```

**✅ NEW CODE:**
```python
# Use case orchestrates focused services
class MarkAttendanceUseCase:
    def __init__(self, recognizer, liveness_verifier, logger):
        self.recognizer = recognizer
        self.liveness_verifier = liveness_verifier
        self.logger = logger
    
    def execute(self, image):
        user = self.recognizer.recognize(image)
        if not self.liveness_verifier.verify(image):
            raise LivenessFailedError()
        return self.logger.log(user)
```

### 2. Mixed Concerns
**❌ OLD CODE:**
```python
class AttendanceService:
    def export_attendance_data(self, format: str):
        # Business logic
        data = self.get_attendance_data()
        # Data formatting (should be in repository/formatter)
        if format == "csv":
            return df.to_csv(index=False)
        elif format == "json":
            return df.to_json()
```

**✅ NEW CODE:**
```python
# Repository handles data formatting
class AttendanceRepository:
    def export_csv(self, data: List[AttendanceRecord]) -> str:
        return self.csv_formatter.format(data)
    
    def export_json(self, data: List[AttendanceRecord]) -> str:
        return self.json_formatter.format(data)

# Use case orchestrates
class ExportAttendanceUseCase:
    def execute(self, format: str):
        data = self.repository.get_all()
        return self.repository.export(format, data)
```

### 3. Backward Compatibility Bloat
**❌ OLD CODE:**
```python
class AttendanceService:
    def get_attendance_report(self): pass
    def get_attendance_report_by_type(self): pass  # Backward compat
    def get_attendance_analytics(self): pass
    def get_attendance_analytics_by_type(self): pass  # Backward compat
    def _get_overview_report(self): pass  # Internal helper
    def _get_recent_activity_report(self): pass  # Internal helper
```

**✅ NEW CODE:**
```python
# One clear method, no backward compat methods
class GenerateReportUseCase:
    def execute(self, report_type: ReportType, filters: ReportFilters):
        generator = self.report_factory.create(report_type)
        return generator.generate(filters)
```

## Dependency Injection

### Rule: Always inject dependencies through constructor

**✅ CORRECT:**
```python
class MarkAttendanceUseCase:
    def __init__(
        self,
        recognizer: FaceRecognizer,
        liveness_verifier: LivenessVerifier,
        attendance_logger: AttendanceLogger,
        repository: AttendanceRepository
    ):
        self.recognizer = recognizer
        self.liveness_verifier = liveness_verifier
        self.attendance_logger = attendance_logger
        self.repository = repository
```

**❌ WRONG:**
```python
class MarkAttendanceUseCase:
    def __init__(self):
        # ❌ Direct instantiation - hard to test, tight coupling
        self.recognizer = FaceRecognizer()
        self.repository = AttendanceRepository()
```

## Interface Segregation

### Rule: Interfaces should be small and focused

**✅ CORRECT:**
```python
class FaceDetector(Protocol):
    def detect(self, image: np.ndarray) -> List[Face]:
        """Detect faces in image"""
        pass

class FaceRecognizer(Protocol):
    def recognize(self, embedding: np.ndarray) -> Optional[User]:
        """Recognize face from embedding"""
        pass
```

**❌ WRONG:**
```python
# ❌ Large interface with multiple concerns
class RecognitionInterface(Protocol):
    def detect_faces(self): pass
    def recognize_face(self): pass
    def extract_embeddings(self): pass
    def assess_quality(self): pass
    def compare_faces(self): pass
    def load_known_faces(self): pass
    # Too many responsibilities
```

## Module Organization

### Rule: Group by feature/domain, not by technical layer

**✅ CORRECT:**
```
core/
├── recognition/        # All recognition-related code
│   ├── detector.py
│   ├── recognizer.py
│   └── embedding_extractor.py
└── liveness/          # All liveness-related code
    ├── blink_detector.py
    ├── liveness_verifier.py
    ├── motion_analyzer.py
    └── spoofing_detector.py
```

**❌ WRONG:**
```
# ❌ Grouping by technical type makes it hard to find related code
services/
├── recognition_service.py
├── liveness_service.py
├── attendance_service.py
modules/
├── recognition_module.py
├── liveness_module.py
```

## Testing Architecture

- **Unit tests**: Test each class in isolation with mocks
- **Integration tests**: Test use cases with real repositories
- **E2E tests**: Test complete workflows through UI/API

Tests should mirror the architecture:
```
tests/
├── unit/
│   ├── core/
│   ├── domain/
│   └── use_cases/
├── integration/
│   └── use_cases/
└── e2e/
    └── workflows/
```

## Presentation Layer: Next.js Architecture

### Foundational Technologies (Required)

#### Next.js App Router
- **Purpose**: React framework for building the frontend
- **Version**: Latest stable (14+)
- **Features Used**:
  - App Router for routing
  - Server Components (where applicable)
  - Client Components for interactivity
  - Route groups for organization

#### WebRTC + Canvas API
- **Purpose**: Camera capture and frame extraction
- **Implementation**:
  - `navigator.mediaDevices.getUserMedia()` for camera access
  - Canvas API for frame capture and processing
  - No business logic - only capture and format for API

#### REST API Client
- **Purpose**: Communication with backend API
- **Implementation**:
  - Fetch API or axios for HTTP requests
  - Type-safe API client with TypeScript
  - Error handling and retry logic
  - Request/response interceptors

### Optional Technologies

#### Zustand (State Management)
- **Purpose**: Client-side state management
- **Usage**: UI state only (filters, selections, form state)
- **NOT for**: Business logic or business state

#### shadcn/ui (Component Library)
- **Purpose**: Pre-built, accessible UI components
- **Usage**: Buttons, forms, cards, tables, etc.
- **Customization**: Fully customizable via Tailwind CSS

#### Zod (Validation)
- **Purpose**: Schema validation for forms and API responses
- **Usage**: Input validation only (client-side)
- **NOT for**: Business rule validation (that's in domain layer)

#### Framer Motion (Animations)
- **Purpose**: Smooth animations and transitions
- **Usage**: UI animations only

#### WebSockets (Real-time Updates)
- **Purpose**: Real-time notifications and updates
- **Usage**: Optional for live attendance updates
- **Implementation**: Socket.io or native WebSocket API

### Frontend Architecture Rules

#### 1. No Business Logic in Frontend

**✅ CORRECT:**
```typescript
// frontend/components/attendance/MarkAttendanceForm.tsx
'use client'

import { useApi } from '@/lib/hooks/useApi'
import { markAttendanceSchema } from '@/lib/schemas/attendance'

export function MarkAttendanceForm() {
  const { mutate, isLoading } = useApi()
  
  const handleSubmit = async (data: FormData) => {
    // Validate input only (Zod schema)
    const validated = markAttendanceSchema.parse(data)
    
    // Call API - business logic is in backend
    await mutate('/api/attendance/mark', {
      method: 'POST',
      body: JSON.stringify(validated)
    })
  }
  
  return <form onSubmit={handleSubmit}>...</form>
}
```

**❌ WRONG:**
```typescript
// ❌ Business logic in frontend
export function MarkAttendanceForm() {
  const handleSubmit = async (data: FormData) => {
    // ❌ Business rule in frontend!
    if (data.blinkCount < 3) {
      throw new Error('Need 3 blinks')
    }
    
    // ❌ Calculating attendance status in frontend!
    const status = calculateAttendanceStatus(data)
    
    // ❌ Business logic should be in backend
  }
}
```

#### 2. API Client Pattern

**✅ CORRECT:**
```typescript
// frontend/lib/api/client.ts
export class ApiClient {
  private baseUrl: string
  
  async markAttendance(request: MarkAttendanceRequest): Promise<MarkAttendanceResponse> {
    const response = await fetch(`${this.baseUrl}/api/attendance/mark`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    
    if (!response.ok) {
      throw new ApiError(response.status, await response.text())
    }
    
    return response.json()
  }
}
```

#### 3. Camera Capture Pattern

**✅ CORRECT:**
```typescript
// frontend/lib/hooks/useCamera.ts
export function useCamera() {
  const [stream, setStream] = useState<MediaStream | null>(null)
  
  const startCamera = async () => {
    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720 }
    })
    setStream(mediaStream)
  }
  
  const captureFrame = (videoElement: HTMLVideoElement): Blob => {
    const canvas = document.createElement('canvas')
    canvas.width = videoElement.videoWidth
    canvas.height = videoElement.videoHeight
    const ctx = canvas.getContext('2d')!
    ctx.drawImage(videoElement, 0, 0)
    
    // Return frame as Blob - no processing, just capture
    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob!), 'image/jpeg')
    })
  }
  
  return { stream, startCamera, captureFrame }
}
```

#### 4. State Management Boundaries

**✅ CORRECT:**
```typescript
// frontend/lib/store/attendanceStore.ts
import { create } from 'zustand'

interface AttendanceStore {
  // UI state only
  selectedDate: Date | null
  filters: AttendanceFilters
  isLoading: boolean
  
  // Actions (UI only)
  setSelectedDate: (date: Date | null) => void
  setFilters: (filters: AttendanceFilters) => void
}

export const useAttendanceStore = create<AttendanceStore>((set) => ({
  selectedDate: null,
  filters: {},
  isLoading: false,
  setSelectedDate: (date) => set({ selectedDate: date }),
  setFilters: (filters) => set({ filters })
}))
```

**❌ WRONG:**
```typescript
// ❌ Business state in frontend store
interface AttendanceStore {
  // ❌ Business logic state
  attendanceRecords: AttendanceRecord[]  // Should come from API
  calculateBadges: () => Badge[]  // ❌ Business logic!
  validateAttendance: () => boolean  // ❌ Business rule!
}
```

### API Layer Responsibilities

The REST API layer (`api/`) acts as a thin adapter between frontend and use cases:

**✅ CORRECT:**
```python
# api/routes/attendance.py
from fastapi import APIRouter, Depends
from use_cases.mark_attendance import MarkAttendanceUseCase, MarkAttendanceRequest

router = APIRouter()

@router.post("/mark")
async def mark_attendance(
    request: MarkAttendanceRequestDTO,
    use_case: MarkAttendanceUseCase = Depends(get_mark_attendance_use_case)
):
    """Mark attendance endpoint.
    
    This endpoint:
    1. Validates request (DTO validation)
    2. Converts DTO to use case request
    3. Calls use case
    4. Converts use case response to DTO
    5. Returns HTTP response
    
    NO business logic here - all in use case.
    """
    # Convert DTO to use case request
    use_case_request = MarkAttendanceRequest(
        frames_sequence=request.frames,
        landmarks_sequence=request.landmarks,
        device_info=request.device_info,
        location=request.location
    )
    
    # Call use case (business logic is here)
    response = use_case.execute(use_case_request)
    
    # Convert to DTO
    return MarkAttendanceResponseDTO(
        success=response.success,
        attendance_record=response.attendance_record,
        error=response.error
    )
```

### Migration Notes

#### From Streamlit to Next.js

1. **Create API Layer**
   - Add `api/` directory with FastAPI
   - Create route handlers that call use cases
   - Add CORS middleware for frontend access
   - Add error handling middleware

3. **Build Next.js Frontend**
   - Initialize Next.js project in `frontend/`
   - Set up App Router structure
   - Create API client
   - Build components following patterns above

4. **Camera Migration**
   - Replace Streamlit `st.camera_input` with WebRTC
   - Use Canvas API for frame capture
   - Implement frame collection logic in React hooks
   - Send frames to API via REST

5. **State Management Migration**
   - Replace Streamlit session state with Zustand
   - Keep only UI state in frontend
   - Fetch business data from API

6. **Validation Migration**
   - Replace Streamlit form validation with Zod schemas
   - Keep client-side validation for UX
   - Backend still validates (single source of truth)

### Boundaries Enforcement

#### Frontend → API Boundary

- **Frontend sends**: HTTP requests with DTOs
- **Frontend receives**: HTTP responses with DTOs
- **Frontend does NOT**: Call use cases directly, access repositories, execute business logic

#### API → Use Cases Boundary

- **API calls**: Use cases only
- **API does NOT**: Execute business logic, access domain services directly, access repositories

#### Use Cases → Domain Boundary

- **Use cases call**: Domain services
- **Use cases do NOT**: Access infrastructure directly (except through repositories)

### Testing Frontend

- **Unit tests**: Test components in isolation with mock data
- **Integration tests**: Test API client with mock server
- **E2E tests**: Test complete flows (camera → API → use case)
- **NO business logic tests in frontend**: Test UI behavior only

## Future Agent Instructions

When generating or refactoring code:

1. **Check layer boundaries**: Ensure dependencies point inward only
2. **Verify SRP**: Each class should have one clear responsibility
3. **Limit size**: Split classes exceeding 300 lines
4. **Use dependency injection**: Never instantiate dependencies directly
5. **Create focused interfaces**: Small, single-purpose interfaces
6. **Group by domain**: Organize by feature, not technical type
7. **Remove backward compat**: Don't add methods for old code compatibility
8. **Extract use cases**: Business workflows belong in use cases, not services
9. **Frontend rules**: NO business logic in frontend, only UI and API calls
10. **API rules**: API is thin adapter, delegates to use cases immediately


