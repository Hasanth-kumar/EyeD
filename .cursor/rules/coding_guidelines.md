# Coding Guidelines

## Overview
This document defines coding standards, style guidelines, and best practices for the EyeD project rebuild.

## Code Style

### Python Style Guide
Follow **PEP 8** with these specific rules:

- **Line length**: Maximum 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped and sorted (stdlib, third-party, local)
- **Blank lines**: 2 lines between top-level definitions, 1 line between methods

```python
# ✅ CORRECT
import os
from pathlib import Path
from typing import List, Optional, Dict

import numpy as np
import pandas as pd

from domain.entities.user import User
from domain.services.badge_calculator import BadgeCalculator


class AttendanceService:
    """Service for attendance operations."""
    
    def __init__(self, repository: AttendanceRepository):
        self.repository = repository
    
    def log_attendance(self, record: AttendanceRecord) -> bool:
        """Log attendance record."""
        return self.repository.save(record)
```

### Type Hints

**ALWAYS** use type hints for:
- Function parameters
- Return values
- Class attributes
- Variables (when type is not obvious)

```python
# ✅ CORRECT
def calculate_badges(
    attendance_data: List[AttendanceRecord],
    period_days: int = 30
) -> List[Badge]:
    """Calculate badges for attendance data."""
    pass

class User:
    def __init__(self, user_id: str, name: str):
        self.user_id: str = user_id
        self.name: str = name
```

**❌ WRONG:**
```python
# ❌ No type hints
def calculate_badges(attendance_data, period_days=30):
    pass
```

### Docstrings

**ALWAYS** include docstrings for:
- All public classes
- All public methods
- Complex private methods

**Format**: Google style

```python
# ✅ CORRECT
class BadgeCalculator:
    """Calculates badges based on attendance data.
    
    This service calculates various types of badges including
    attendance badges, streak badges, and timing badges.
    
    Attributes:
        badge_definitions: Dictionary of badge definitions
    """
    
    def calculate(
        self,
        attendance_data: List[AttendanceRecord],
        period_days: int = 30
    ) -> List[Badge]:
        """Calculate all badges for attendance data.
        
        Args:
            attendance_data: List of attendance records
            period_days: Number of days to consider (default: 30)
        
        Returns:
            List of earned badges
        
        Raises:
            ValueError: If attendance_data is empty
        """
        if not attendance_data:
            raise ValueError("attendance_data cannot be empty")
        # ...
```

## Code Organization

### File Structure

Each file should have this structure:

```python
"""
Module docstring explaining the file's purpose.
"""

# Standard library imports
import os
from pathlib import Path
from typing import List, Optional

# Third-party imports
import numpy as np
import pandas as pd

# Local imports
from domain.entities.user import User
from domain.services.badge_calculator import BadgeCalculator

# Constants
MAX_ATTENDANCE_ENTRIES = 5
CONFIDENCE_THRESHOLD = 0.6

# Classes and functions
class AttendanceService:
    """Service for attendance operations."""
    pass

def helper_function() -> None:
    """Helper function."""
    pass

# Module-level code (if any)
if __name__ == "__main__":
    pass
```

### Class Organization

Classes should be organized in this order:

1. Class docstring
2. Class constants
3. `__init__` method
4. Public methods
5. Private methods (prefixed with `_`)
6. Special methods (`__str__`, `__repr__`, etc.)

```python
# ✅ CORRECT
class BadgeCalculator:
    """Calculates badges based on attendance data."""
    
    # Class constants
    PERFECT_ATTENDANCE_THRESHOLD = 0.95
    
    def __init__(self, badge_definitions: Dict):
        """Initialize badge calculator."""
        self.badge_definitions = badge_definitions
    
    # Public methods
    def calculate(self, data: List[AttendanceRecord]) -> List[Badge]:
        """Calculate badges."""
        pass
    
    # Private methods
    def _calculate_attendance_badges(self, data: List) -> List[Badge]:
        """Calculate attendance-based badges."""
        pass
    
    # Special methods
    def __repr__(self) -> str:
        return f"BadgeCalculator(badges={len(self.badge_definitions)})"
```

## Error Handling

### Use Specific Exceptions

```python
# ✅ CORRECT
class UserNotFoundError(Exception):
    """Raised when user is not found."""
    pass

class LivenessVerificationFailedError(Exception):
    """Raised when liveness verification fails."""
    pass

def get_user(user_id: str) -> User:
    user = repository.find_by_id(user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
```

**❌ WRONG:**
```python
# ❌ Generic exceptions
def get_user(user_id: str) -> User:
    user = repository.find_by_id(user_id)
    if not user:
        raise Exception("User not found")  # Too generic
    return user
```

### Error Messages

- Be specific and actionable
- Include context (user_id, date, etc.)
- Use f-strings for formatting

```python
# ✅ CORRECT
raise UserNotFoundError(
    f"User with ID '{user_id}' not found in database"
)

raise LivenessVerificationFailedError(
    f"Liveness verification failed for user {user_id} at {datetime.now()}"
)
```

## Logging

### Use Structured Logging

```python
# ✅ CORRECT
import logging

logger = logging.getLogger(__name__)

class AttendanceService:
    def log_attendance(self, record: AttendanceRecord) -> bool:
        logger.info(
            "Logging attendance",
            extra={
                "user_id": record.user_id,
                "date": record.date,
                "confidence": record.confidence
            }
        )
        try:
            result = self.repository.save(record)
            logger.info(f"Attendance logged successfully for user {record.user_id}")
            return result
        except Exception as e:
            logger.error(
                f"Failed to log attendance for user {record.user_id}",
                exc_info=True
            )
            raise
```

**❌ WRONG:**
```python
# ❌ Print statements or vague logging
print(f"Logging attendance for {user_id}")  # Use logger
logger.info("Error")  # Too vague
```

## Testing

### Test Organization

Tests should mirror the source structure:

```
tests/
├── unit/
│   ├── core/
│   │   ├── test_face_detector.py
│   │   └── test_face_recognizer.py
│   ├── domain/
│   │   └── test_badge_calculator.py
│   └── use_cases/
│       └── test_mark_attendance.py
├── integration/
│   └── test_attendance_workflow.py
└── e2e/
    └── test_complete_attendance_flow.py
```

### Test Naming

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_is_being_tested>`

```python
# ✅ CORRECT
# tests/unit/domain/test_badge_calculator.py
import pytest
from domain.services.badge_calculator import BadgeCalculator

class TestBadgeCalculator:
    def test_calculate_perfect_attendance_badge(self):
        """Test that perfect attendance badge is calculated correctly."""
        calculator = BadgeCalculator(badge_definitions={...})
        data = [AttendanceRecord(...) for _ in range(30)]
        badges = calculator.calculate(data)
        assert any(b.name == "Perfect Attendance" for b in badges)
    
    def test_calculate_returns_empty_list_for_no_data(self):
        """Test that empty list is returned when no attendance data."""
        calculator = BadgeCalculator(badge_definitions={...})
        badges = calculator.calculate([])
        assert badges == []
```

## Code Review Checklist

Before submitting code, verify:

### Structure
- [ ] Follows Clean Architecture layers
- [ ] Single Responsibility Principle (one class = one purpose)
- [ ] Dependencies point inward only
- [ ] No circular dependencies

### Naming
- [ ] Descriptive names (no abbreviations)
- [ ] Follows naming conventions
- [ ] Type hints on all functions
- [ ] Docstrings on public methods

### Code Quality
- [ ] No code duplication
- [ ] Methods < 50 lines, classes < 300 lines
- [ ] Proper error handling with specific exceptions
- [ ] Logging instead of print statements

### Testing
- [ ] Unit tests for new code
- [ ] Tests are isolated and fast
- [ ] Test names describe what is being tested

## Anti-Patterns from Old Code

### 1. God Methods
**❌ OLD:**
```python
def process_attendance_request(self, face_image, device_info="", location=""):
    # 100+ lines doing everything
    # Recognition
    recognition_result = self.recognition_system.recognize_face(face_image)
    # Liveness
    liveness_result = self.liveness_system.detect_blink(face_image)
    # Logging
    attendance_entry = self.attendance_manager.log_attendance(...)
    # Persistence
    success = self.attendance_repository.add_attendance(attendance_entry)
    # Analytics
    self._update_analytics(attendance_entry)
    # Reporting
    self._generate_report(attendance_entry)
    # ... 50 more lines
```

**✅ NEW:**
```python
# Use case orchestrates focused services
class MarkAttendanceUseCase:
    def execute(self, image: np.ndarray) -> AttendanceRecord:
        user = self.recognizer.recognize(image)
        if not self.liveness_verifier.verify(image):
            raise LivenessVerificationFailedError()
        record = self.logger.log(user, image)
        self.repository.save(record)
        return record
```

### 2. Magic Numbers
**❌ OLD:**
```python
if confidence > 0.6:  # What is 0.6?
    if total_entries >= 20:  # What is 20?
        badges.append(...)
```

**✅ NEW:**
```python
CONFIDENCE_THRESHOLD = 0.6
PERFECT_ATTENDANCE_MIN_ENTRIES = 20

if confidence > CONFIDENCE_THRESHOLD:
    if total_entries >= PERFECT_ATTENDANCE_MIN_ENTRIES:
        badges.append(...)
```

### 3. Deep Nesting
**❌ OLD:**
```python
def calculate_badges(self, data):
    if data:
        if len(data) > 0:
            for entry in data:
                if entry.date:
                    if entry.confidence > 0.6:
                        if entry.liveness_verified:
                            # 5 levels deep!
                            badges.append(...)
```

**✅ NEW:**
```python
def calculate_badges(self, data: List[AttendanceRecord]) -> List[Badge]:
    if not data:
        return []
    
    valid_entries = [
        entry for entry in data
        if self._is_valid_entry(entry)
    ]
    
    return self._calculate_from_valid_entries(valid_entries)

def _is_valid_entry(self, entry: AttendanceRecord) -> bool:
    return (
        entry.date is not None
        and entry.confidence > CONFIDENCE_THRESHOLD
        and entry.liveness_verified
    )
```

### 4. Commented-Out Code
**❌ OLD:**
```python
def calculate_badges(self, data):
    # Old implementation
    # badges = []
    # for entry in data:
    #     if entry.confidence > 0.5:
    #         badges.append(...)
    
    # New implementation
    return self._new_calculate(data)
```

**✅ NEW:**
```python
# Remove commented code - use version control instead
def calculate_badges(self, data: List[AttendanceRecord]) -> List[Badge]:
    return self._calculate_badges(data)
```

## Future Agent Instructions

When writing code:

1. **Follow PEP 8**: Use 4 spaces, max 100 chars per line
2. **Always use type hints**: Every function needs parameter and return types
3. **Write docstrings**: All public classes and methods need docstrings
4. **Handle errors properly**: Use specific exceptions, not generic `Exception`
5. **Log instead of print**: Use logger for all output
6. **Keep methods small**: Max 50 lines per method
7. **Keep classes focused**: Max 300 lines per class
8. **Avoid magic numbers**: Use named constants
9. **Limit nesting**: Max 3 levels of indentation
10. **Remove dead code**: Don't comment out code, delete it













