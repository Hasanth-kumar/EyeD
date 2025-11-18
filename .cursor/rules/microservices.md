# Microservices & Modularity Rules

## Overview
This document defines rules for creating self-contained, independent, and reusable modules following microservice-style architecture principles.

## Core Principles

### 1. Self-Contained Modules
Each module should be:
- **Independent**: Can function without other modules
- **Reusable**: Can be used in different contexts
- **Testable**: Can be tested in isolation
- **Replaceable**: Can be swapped with alternative implementations

### 2. Clear Boundaries
Modules communicate through:
- **Well-defined interfaces** (Protocols/ABCs)
- **Data transfer objects** (DTOs/Entities)
- **No direct dependencies** on implementations

### 3. Single Responsibility
Each module has **one clear purpose**:
- ✅ `BadgeCalculator` - calculates badges only
- ✅ `FaceDetector` - detects faces only
- ✅ `AttendanceLogger` - logs attendance only
- ❌ `GamificationService` - does badges, leaderboards, achievements (TOO MUCH)

## Module Structure

### Standard Module Layout

```
<module_name>/
├── __init__.py              # Public API exports
├── <module_name>.py         # Main implementation
├── interfaces.py            # Protocol definitions (if needed)
├── entities.py              # Domain entities (if module-specific)
└── tests/
    └── test_<module_name>.py
```

### Example: Badge Module

```
domain/
└── services/
    └── badge/
        ├── __init__.py
        ├── badge_calculator.py
        ├── badge_definitions.py
        ├── badge_types.py
        └── tests/
            └── test_badge_calculator.py
```

## Module Communication

### Use Dependency Injection

**✅ CORRECT:**
```python
# domain/services/badge/badge_calculator.py
class BadgeCalculator:
    def __init__(
        self,
        attendance_repository: AttendanceRepository,  # Injected
        badge_definitions: Dict  # Injected
    ):
        self.attendance_repository = attendance_repository
        self.badge_definitions = badge_definitions
    
    def calculate(self, user_id: str) -> List[Badge]:
        attendance_data = self.attendance_repository.find_by_user_id(user_id)
        return self._calculate_from_data(attendance_data)
```

**❌ WRONG:**
```python
# ❌ Direct instantiation creates tight coupling
class BadgeCalculator:
    def __init__(self):
        self.attendance_repository = AttendanceRepository()  # Tight coupling!
        self.badge_definitions = self._load_definitions()  # Hidden dependency
```

### Use Interfaces (Protocols)

**✅ CORRECT:**
```python
# domain/services/badge/interfaces.py
from typing import Protocol

class AttendanceRepository(Protocol):
    """Protocol for attendance data access."""
    def find_by_user_id(self, user_id: str) -> List[AttendanceRecord]:
        """Find attendance records for user."""
        ...

# domain/services/badge/badge_calculator.py
class BadgeCalculator:
    def __init__(self, repository: AttendanceRepository):
        self.repository = repository  # Depends on interface, not implementation
```

### Use Data Transfer Objects

**✅ CORRECT:**
```python
# domain/entities/attendance_record.py
@dataclass
class AttendanceRecord:
    """Immutable attendance record."""
    user_id: str
    date: date
    time: time
    confidence: float
    liveness_verified: bool

# domain/services/badge/badge_calculator.py
class BadgeCalculator:
    def calculate(self, records: List[AttendanceRecord]) -> List[Badge]:
        # Works with data objects, not raw dictionaries
        pass
```

**❌ WRONG:**
```python
# ❌ Passing raw dictionaries creates coupling
def calculate(self, data: List[Dict]) -> List[Dict]:
    # What keys does the dict have? Unclear contract
    pass
```

## Service Boundaries

### Rule: One Service = One Domain Concern

**✅ CORRECT:**
```python
# domain/services/badge/badge_calculator.py
class BadgeCalculator:
    """ONLY calculates badges - nothing else."""
    def calculate(self, data: List[AttendanceRecord]) -> List[Badge]:
        pass

# domain/services/leaderboard/leaderboard_generator.py
class LeaderboardGenerator:
    """ONLY generates leaderboards - nothing else."""
    def generate(self, users: List[User], metric: str) -> Leaderboard:
        pass

# domain/services/achievement/achievement_tracker.py
class AchievementTracker:
    """ONLY tracks achievements - nothing else."""
    def track(self, user_id: str) -> List[Achievement]:
        pass
```

**❌ WRONG (from old code):**
```python
# ❌ One service doing everything
class GamificationService:
    """Does badges, leaderboards, achievements, timeline analysis."""
    def calculate_user_badges(self): pass
    def get_leaderboard(self): pass
    def get_achievements(self): pass
    def analyze_timeline(self): pass
    def get_user_stats(self): pass
    # 600+ lines - too many responsibilities
```

### Service Size Limits

- **Maximum service size**: 300 lines
- **Maximum methods per service**: 10 public methods
- **If exceeded**: Split into smaller services

## API Design

### RESTful Principles (if API layer exists)

```
GET    /api/users              # List users
GET    /api/users/{id}          # Get user
POST   /api/users               # Create user
PUT    /api/users/{id}          # Update user
DELETE /api/users/{id}          # Delete user

GET    /api/attendance          # List attendance
POST   /api/attendance          # Mark attendance
GET    /api/attendance/{id}     # Get attendance record
```

### Request/Response DTOs

**✅ CORRECT:**
```python
# api/dto/attendance_dto.py
@dataclass
class MarkAttendanceRequest:
    """Request DTO for marking attendance."""
    user_id: str
    image_data: str  # Base64 encoded
    device_info: Optional[str] = None
    location: Optional[str] = None

@dataclass
class AttendanceResponse:
    """Response DTO for attendance."""
    record_id: str
    user_id: str
    timestamp: datetime
    confidence: float
    liveness_verified: bool

# api/routes/attendance_routes.py
@router.post("/attendance")
def mark_attendance(
    request: MarkAttendanceRequest
) -> AttendanceResponse:
    use_case = MarkAttendanceUseCase(...)
    record = use_case.execute(request)
    return AttendanceResponse.from_record(record)
```

## Folder Structure by Feature

### Group by Domain, Not by Technical Type

**✅ CORRECT:**
```
eyed/
├── core/
│   ├── recognition/          # All recognition code together
│   │   ├── detector.py
│   │   ├── recognizer.py
│   │   └── embedding_extractor.py
│   ├── liveness/             # All liveness code together
│   │   ├── blink_detector.py
│   │   └── liveness_verifier.py
│   └── attendance/           # All attendance core logic
│       ├── logger.py
│       └── validator.py
├── domain/
│   ├── services/
│   │   ├── badge/            # Badge feature
│   │   │   ├── calculator.py
│   │   │   └── definitions.py
│   │   ├── leaderboard/      # Leaderboard feature
│   │   │   └── generator.py
│   │   └── analytics/        # Analytics feature
│   │       └── metrics_calculator.py
```

**❌ WRONG:**
```
# ❌ Grouping by technical type makes it hard to find related code
eyed/
├── services/                  # All services mixed together
│   ├── badge_service.py
│   ├── leaderboard_service.py
│   └── analytics_service.py
├── modules/                   # All modules mixed together
│   ├── recognition_module.py
│   └── liveness_module.py
```

## Module Dependencies

### Dependency Graph Rules

1. **No circular dependencies**: Module A → Module B, but not B → A
2. **Dependencies point inward**: Infrastructure → Domain → Application → Presentation
3. **Use interfaces**: Depend on abstractions, not implementations

### Dependency Injection Container

**✅ CORRECT:**
```python
# infrastructure/di/container.py
class Container:
    """Dependency injection container."""
    
    def __init__(self):
        self._services = {}
        self._setup()
    
    def _setup(self):
        # Register repositories
        self._services['attendance_repository'] = AttendanceRepository()
        
        # Register domain services
        self._services['badge_calculator'] = BadgeCalculator(
            repository=self._services['attendance_repository']
        )
        
        # Register use cases
        self._services['mark_attendance'] = MarkAttendanceUseCase(
            recognizer=self._services['face_recognizer'],
            liveness_verifier=self._services['liveness_verifier'],
            logger=self._services['attendance_logger'],
            repository=self._services['attendance_repository']
        )
    
    def get(self, service_name: str):
        return self._services.get(service_name)
```

**❌ WRONG (from old code):**
```python
# ❌ Complex factory with many dependencies
class ServiceFactory:
    def __init__(self):
        self._attendance_service = None
        self._user_service = None
        self._recognition_service = None
        # ... 10+ services
        # Hard to maintain, complex initialization
```

## Communication Patterns

### Synchronous Communication (Default)

For same-process modules, use direct method calls:

```python
# ✅ CORRECT
class MarkAttendanceUseCase:
    def execute(self, image: np.ndarray) -> AttendanceRecord:
        user = self.recognizer.recognize(image)  # Direct call
        verified = self.liveness_verifier.verify(image)  # Direct call
        return self.logger.log(user, image)  # Direct call
```

### Event-Driven Communication (If Needed)

For decoupled modules, use events:

```python
# domain/events/attendance_logged_event.py
@dataclass
class AttendanceLoggedEvent:
    """Event fired when attendance is logged."""
    record: AttendanceRecord
    timestamp: datetime

# domain/services/badge/badge_calculator.py
class BadgeCalculator:
    def on_attendance_logged(self, event: AttendanceLoggedEvent):
        """Handle attendance logged event."""
        badges = self.calculate(event.record.user_id)
        # Update user badges
```

## Anti-Patterns from Old Code

### 1. Tight Coupling
**❌ OLD:**
```python
class GamificationService:
    def __init__(self):
        # Direct instantiation - tight coupling
        self.attendance_repo = AttendanceRepository()
        self.face_db = FaceDatabase()
        # Hard to test, hard to replace
```

**✅ NEW:**
```python
class BadgeCalculator:
    def __init__(self, repository: AttendanceRepository):
        # Dependency injection - loose coupling
        self.repository = repository
        # Easy to test with mock, easy to replace
```

### 2. Shared State
**❌ OLD:**
```python
# Global state shared across modules
attendance_data = []  # Global variable

class AttendanceService:
    def log(self, record):
        attendance_data.append(record)  # Modifies global state

class AnalyticsService:
    def analyze(self):
        return analyze(attendance_data)  # Reads global state
```

**✅ NEW:**
```python
# State managed through repositories
class AttendanceRepository:
    def __init__(self):
        self._data: List[AttendanceRecord] = []
    
    def save(self, record: AttendanceRecord):
        self._data.append(record)
    
    def find_all(self) -> List[AttendanceRecord]:
        return self._data.copy()  # Return copy, don't expose internal state
```

### 3. God Services
**❌ OLD:**
```python
class AttendanceService:
    # 700+ lines doing everything
    def process_attendance_request(self): pass
    def get_attendance_report(self): pass
    def get_attendance_analytics(self): pass
    def export_attendance_data(self): pass
    def verify_attendance_eligibility(self): pass
    def get_user_performance_analytics(self): pass
    def get_trend_analytics(self): pass
    # ... 20+ methods
```

**✅ NEW:**
```python
# Split into focused services
class AttendanceLogger:
    """ONLY logs attendance."""
    def log(self, user: User, image: np.ndarray) -> AttendanceRecord:
        pass

class AttendanceReporter:
    """ONLY generates reports."""
    def generate_report(self, filters: ReportFilters) -> Report:
        pass

class AttendanceAnalytics:
    """ONLY calculates analytics."""
    def calculate_metrics(self, data: List[AttendanceRecord]) -> Metrics:
        pass
```

## Future Agent Instructions

When creating modules:

1. **Keep modules small**: Max 300 lines, max 10 public methods
2. **One responsibility**: Each module does one thing well
3. **Use dependency injection**: Never instantiate dependencies directly
4. **Define interfaces**: Use Protocols/ABCs for contracts
5. **Use DTOs**: Pass data objects, not raw dictionaries
6. **Group by feature**: Organize by domain, not technical type
7. **Avoid circular dependencies**: Dependencies should point in one direction
8. **No shared state**: Use repositories for data access
9. **Test in isolation**: Each module should be testable independently
10. **Document boundaries**: Clear contracts between modules











