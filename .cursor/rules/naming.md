# Naming Conventions

## Overview
Consistent naming is critical for maintainability. This document defines naming rules for all components, files, and folders.

## General Rules

### 1. Use Descriptive Names
- ✅ `FaceDetector` not `FD` or `Detector`
- ✅ `calculate_attendance_badges` not `calc_badges` or `badges`
- ✅ `attendance_repository.py` not `att_repo.py` or `repo.py`

### 2. Follow Python Conventions
- **Classes**: `PascalCase` (e.g., `FaceRecognizer`, `AttendanceLogger`)
- **Functions/Methods**: `snake_case` (e.g., `detect_faces`, `calculate_badges`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ATTENDANCE_ENTRIES`, `CONFIDENCE_THRESHOLD`)
- **Private**: Prefix with `_` (e.g., `_calculate_internal_metric`)
- **Files/Modules**: `snake_case` (e.g., `face_detector.py`, `attendance_repository.py`)

## Layer-Specific Naming

### Domain Layer (`domain/`, `core/`)

#### Entities
- **File**: `snake_case` with entity name
- **Class**: `PascalCase` entity name
- **Example**: `domain/entities/user.py` → `class User:`

```python
# ✅ CORRECT
# domain/entities/user.py
class User:
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name

# domain/entities/attendance_record.py
class AttendanceRecord:
    pass
```

#### Domain Services
- **File**: `snake_case` with service purpose
- **Class**: `PascalCase` with `Service` or purpose suffix
- **Example**: `domain/services/badge_calculator.py` → `class BadgeCalculator:`

```python
# ✅ CORRECT
# domain/services/badge_calculator.py
class BadgeCalculator:
    def calculate(self, attendance_data: List[AttendanceRecord]) -> List[Badge]:
        pass

# domain/services/leaderboard_generator.py
class LeaderboardGenerator:
    def generate(self, users: List[User]) -> Leaderboard:
        pass
```

#### Core Domain Logic
- **File**: `snake_case` describing the operation
- **Class**: `PascalCase` describing the component
- **Example**: `core/recognition/detector.py` → `class FaceDetector:`

```python
# ✅ CORRECT
# core/recognition/detector.py
class FaceDetector:
    def detect(self, image: np.ndarray) -> List[Face]:
        pass

# core/recognition/recognizer.py
class FaceRecognizer:
    def recognize(self, embedding: np.ndarray) -> Optional[User]:
        pass
```

### Application Layer (`use_cases/`)

#### Use Cases
- **File**: `snake_case` with action verb
- **Class**: `PascalCase` with `UseCase` suffix
- **Example**: `use_cases/register_user.py` → `class RegisterUserUseCase:`

```python
# ✅ CORRECT
# use_cases/register_user.py
class RegisterUserUseCase:
    def execute(self, user_data: UserData) -> User:
        pass

# use_cases/mark_attendance.py
class MarkAttendanceUseCase:
    def execute(self, image: np.ndarray) -> AttendanceRecord:
        pass
```

**❌ WRONG (from old code):**
```python
# ❌ Service doing use case work
class AttendanceService:
    def process_attendance_request(self, face_image):  # Should be in use case
        pass
```

### Infrastructure Layer (`repositories/`, `infrastructure/`)

#### Repositories
- **File**: `snake_case` with `_repository` suffix
- **Class**: `PascalCase` with `Repository` suffix
- **Example**: `repositories/attendance_repository.py` → `class AttendanceRepository:`

```python
# ✅ CORRECT
# repositories/attendance_repository.py
class AttendanceRepository:
    def save(self, record: AttendanceRecord) -> bool:
        pass
    
    def find_by_user_id(self, user_id: str) -> List[AttendanceRecord]:
        pass
```

#### Infrastructure Services
- **File**: `snake_case` describing the infrastructure concern
- **Class**: `PascalCase` describing the component
- **Example**: `infrastructure/storage/file_storage.py` → `class FileStorage:`

```python
# ✅ CORRECT
# infrastructure/storage/file_storage.py
class FileStorage:
    def save(self, path: str, data: bytes) -> bool:
        pass

# infrastructure/camera/camera_manager.py
class CameraManager:
    def capture_frame(self) -> np.ndarray:
        pass
```

### Presentation Layer (`ui/`, `api/`)

#### UI Components
- **File**: `snake_case` describing the component
- **Function**: `snake_case` with action verb (e.g., `show_`, `render_`, `display_`)
- **Example**: `ui/dashboard/components/overview.py` → `def show_overview():`

```python
# ✅ CORRECT
# ui/dashboard/components/overview.py
def show_overview():
    """Display dashboard overview"""
    pass

# ui/dashboard/components/attendance_table.py
def render_attendance_table(data: List[AttendanceRecord]):
    """Render attendance table component"""
    pass
```

#### API Routes
- **File**: `snake_case` with `_routes` or `_api` suffix
- **Function**: `snake_case` with HTTP method prefix (e.g., `get_`, `post_`, `put_`, `delete_`)
- **Example**: `api/attendance_routes.py` → `def get_attendance():`

```python
# ✅ CORRECT
# api/attendance_routes.py
@router.get("/attendance")
def get_attendance(user_id: str) -> List[AttendanceRecord]:
    pass

@router.post("/attendance")
def create_attendance(data: AttendanceData) -> AttendanceRecord:
    pass
```

## Method Naming

### Use Action Verbs
- **Actions**: `register`, `calculate`, `generate`, `validate`, `detect`
- **Queries**: `get`, `find`, `fetch`, `retrieve`
- **Checks**: `is_`, `has_`, `can_`, `should_`

```python
# ✅ CORRECT
def register_user(user_data: UserData) -> User:
    pass

def calculate_badges(attendance_data: List[AttendanceRecord]) -> List[Badge]:
    pass

def is_eligible_for_attendance(user_id: str, date: date) -> bool:
    pass

def has_attendance_today(user_id: str) -> bool:
    pass
```

**❌ WRONG (from old code):**
```python
# ❌ Vague method names
def process(self):  # Process what?
    pass

def handle(self, data):  # Handle how?
    pass

def do_stuff(self):  # What stuff?
    pass
```

### Boolean Methods
- Prefix with `is_`, `has_`, `can_`, `should_`

```python
# ✅ CORRECT
def is_valid(user: User) -> bool:
    pass

def has_attendance_today(user_id: str) -> bool:
    pass

def can_register(user_data: UserData) -> bool:
    pass
```

### Private Methods
- Prefix with `_` (single underscore)

```python
# ✅ CORRECT
class BadgeCalculator:
    def calculate(self, data: List[AttendanceRecord]) -> List[Badge]:
        return self._calculate_attendance_badges(data) + \
               self._calculate_streak_badges(data)
    
    def _calculate_attendance_badges(self, data: List[AttendanceRecord]) -> List[Badge]:
        # Internal implementation
        pass
```

## Variable Naming

### Use Descriptive Names
```python
# ✅ CORRECT
user_attendance_records = repository.find_by_user_id(user_id)
total_badge_count = len(badges)
is_liveness_verified = liveness_verifier.verify(image)

# ❌ WRONG
recs = repo.find(user_id)  # Too short, unclear
cnt = len(b)  # Abbreviations
flag = verify(img)  # Vague name
```

### Collections
- Use plural nouns: `users`, `records`, `badges`
- Use descriptive prefixes: `user_`, `attendance_`, `face_`

```python
# ✅ CORRECT
users = [User(...), User(...)]
attendance_records = repository.find_all()
face_embeddings = extractor.extract(image)

# ❌ WRONG
user_list = [...]  # Redundant suffix
data = [...]  # Too generic
items = [...]  # Too vague
```

## File and Folder Naming

### Files
- **Python files**: `snake_case.py`
- **Test files**: `test_<name>.py` or `<name>_test.py`
- **Config files**: `config.py`, `settings.py`

```python
# ✅ CORRECT
face_detector.py
attendance_repository.py
test_face_detector.py
test_attendance_repository.py

# ❌ WRONG
FaceDetector.py  # Wrong case
att_repo.py  # Abbreviations
test.py  # Too generic
```

### Folders
- **Directories**: `snake_case`
- **Feature folders**: Group by domain/feature

```
# ✅ CORRECT
core/
├── recognition/
├── liveness/
└── attendance/

domain/
├── entities/
└── services/

use_cases/
├── register_user.py
└── mark_attendance.py

# ❌ WRONG
Core/  # Wrong case
Recognition/  # Wrong case
useCases/  # Wrong case
```

## Constants

### Use UPPER_SNAKE_CASE
```python
# ✅ CORRECT
MAX_ATTENDANCE_ENTRIES_PER_DAY = 5
CONFIDENCE_THRESHOLD = 0.6
LIVENESS_VERIFICATION_REQUIRED = True
DEFAULT_CAMERA_ID = 0

# ❌ WRONG
maxEntries = 5  # Wrong case
threshold = 0.6  # Not a constant
```

## Type Hints

### Always Use Type Hints
```python
# ✅ CORRECT
def calculate_badges(
    attendance_data: List[AttendanceRecord],
    period_days: int = 30
) -> List[Badge]:
    pass

# ❌ WRONG
def calculate_badges(attendance_data, period_days=30):  # No type hints
    pass
```

## Anti-Patterns from Old Code

### 1. Generic Names
**❌ OLD:**
```python
class Service:
    def process(self, data):
        pass

def handle(data):
    pass
```

**✅ NEW:**
```python
class AttendanceService:
    def log_attendance(self, record: AttendanceRecord) -> bool:
        pass

def register_user(user_data: UserData) -> User:
    pass
```

### 2. Abbreviations
**❌ OLD:**
```python
def calc_badges(att_data):
    pass

att_repo = AttendanceRepository()
```

**✅ NEW:**
```python
def calculate_badges(attendance_data: List[AttendanceRecord]) -> List[Badge]:
    pass

attendance_repository = AttendanceRepository()
```

### 3. Hungarian Notation
**❌ OLD:**
```python
str_user_id = "123"
list_records = []
dict_data = {}
```

**✅ NEW:**
```python
user_id = "123"
records = []
data = {}
```

### 4. Redundant Suffixes
**❌ OLD:**
```python
class AttendanceServiceClass:
    pass

def get_user_list():
    pass
```

**✅ NEW:**
```python
class AttendanceService:
    pass

def get_users() -> List[User]:
    pass
```

## Future Agent Instructions

When naming code:

1. **Use descriptive names**: Names should explain purpose without comments
2. **Follow Python conventions**: `PascalCase` for classes, `snake_case` for functions
3. **Use action verbs**: Methods should clearly indicate what they do
4. **Avoid abbreviations**: Use full words unless universally understood
5. **Prefix booleans**: Use `is_`, `has_`, `can_`, `should_` for boolean methods
6. **Group by domain**: Organize files by feature, not technical type
7. **Use type hints**: Always include type hints for parameters and return values
8. **Avoid redundancy**: Don't use `UserClass`, `get_user_list()` - use `User`, `get_users()`











