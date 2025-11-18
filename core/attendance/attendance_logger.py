"""
Attendance Logger - Pure attendance record creation logic.

This module provides the core logic for creating attendance records
without any persistence, validation, or infrastructure dependencies.
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np


class AttendanceLogger:
    """
    Pure attendance record creation logic.
    
    This class is responsible for creating attendance records ONLY.
    It does not handle persistence, validation, or any infrastructure concerns.
    
        Examples:
        >>> logger = AttendanceLogger()
        >>> record_data = logger.create_record(
        ...     user_id="user_001",
        ...     user_name="John Doe",
        ...     face_image=np.array([...]),
        ...     confidence=0.85,
        ...     liveness_verified=True,
        ...     face_quality_score=0.9,
        ...     device_info="Webcam",
        ...     location="Office"
        ... )
        >>> isinstance(record_data, dict)
        True
    """
    
    def __init__(self):
        """Initialize the attendance logger."""
        pass
    
    def create_record(
        self,
        user_id: str,
        user_name: str,
        face_image: np.ndarray,
        confidence: float,
        liveness_verified: bool,
        face_quality_score: float,
        device_info: str,
        location: str,
        verification_stage: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create an attendance record from provided data.
        
        Args:
            user_id: ID of the user for this attendance record.
            user_name: Name of the user for this attendance record.
            face_image: Face image array (used for processing time calculation).
            confidence: Confidence score for face recognition (0.0 to 1.0).
            liveness_verified: Whether liveness verification passed.
            face_quality_score: Quality score of the face image (0.0 to 1.0).
            device_info: Information about the device used.
            location: Location where attendance was recorded.
            verification_stage: Optional stage of verification process.
                             Defaults to "completed" if liveness_verified is True,
                             otherwise "pending".
            session_id: Optional session ID. If not provided, a new one is generated.
            start_time: Optional start time for processing time calculation.
                       If not provided, processing time is set to 0.0.
        
        Returns:
            A dictionary containing attendance record data. The domain layer
            should convert this to an AttendanceRecord entity.
        """
        # Calculate processing time if start_time is provided
        if start_time is not None:
            processing_time_ms = (time.time() - start_time) * 1000
        else:
            processing_time_ms = 0.0
        
        # Generate record ID
        record_id = self.generate_record_id()
        
        # Get current date and time
        current_datetime = datetime.now()
        record_date = current_datetime.date()
        record_time = current_datetime.time()
        
        # Determine verification stage if not provided
        if verification_stage is None:
            if liveness_verified:
                verification_stage = "completed"
            else:
                verification_stage = "pending"
        
        # Generate session ID if not provided
        if session_id is None:
            session_id = self._generate_session_id()
        
        # Return dictionary with attendance record data
        return {
            'record_id': record_id,
            'user_id': user_id,
            'user_name': user_name,
            'date': record_date,
            'time': record_time,
            'confidence': confidence,
            'liveness_verified': liveness_verified,
            'face_quality_score': face_quality_score,
            'processing_time_ms': processing_time_ms,
            'verification_stage': verification_stage,
            'session_id': session_id,
            'device_info': device_info,
            'location': location,
            'status': None  # Status will be determined by domain layer
        }
    
    def create_record_from_data(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an attendance record from a dictionary of data.
        
        This method is useful when you have attendance data in dictionary format
        and want to convert it to a standardized dictionary format.
        
        Args:
            record_data: Dictionary containing attendance record data.
                        Required keys:
                        - user_id: str
                        - user_name: str
                        - confidence: float
                        - liveness_verified: bool
                        - face_quality_score: float
                        - device_info: str
                        - location: str
                        Optional keys:
                        - face_image: np.ndarray (for processing time calculation)
                        - verification_stage: str
                        - session_id: str
                        - start_time: float
                        - record_id: str (if not provided, will be generated)
                        - date: date or str (if not provided, uses current date)
                        - time: time or str (if not provided, uses current time)
                        - processing_time_ms: float (if not provided, calculated or 0.0)
        
        Returns:
            A dictionary containing attendance record data. The domain layer
            should convert this to an AttendanceRecord entity.
        
        Raises:
            KeyError: If required keys are missing from record_data.
            ValueError: If data types are invalid.
        """
        # Extract required fields
        user_id = record_data['user_id']
        user_name = record_data['user_name']
        confidence = float(record_data['confidence'])
        liveness_verified = bool(record_data['liveness_verified'])
        face_quality_score = float(record_data['face_quality_score'])
        device_info = str(record_data.get('device_info', ''))
        location = str(record_data.get('location', ''))
        
        # Extract optional fields
        verification_stage = record_data.get('verification_stage')
        session_id = record_data.get('session_id')
        start_time = record_data.get('start_time')
        face_image = record_data.get('face_image')
        
        # Handle date
        if 'date' in record_data:
            record_date = record_data['date']
            if isinstance(record_date, str):
                record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
            elif isinstance(record_date, datetime):
                record_date = record_date.date()
        else:
            record_date = datetime.now().date()
        
        # Handle time
        if 'time' in record_data:
            record_time = record_data['time']
            if isinstance(record_time, str):
                record_time = datetime.strptime(record_time, '%H:%M:%S').time()
            elif isinstance(record_time, datetime):
                record_time = record_time.time()
        else:
            record_time = datetime.now().time()
        
        # Handle processing time
        if 'processing_time_ms' in record_data:
            processing_time_ms = float(record_data['processing_time_ms'])
        elif start_time is not None:
            processing_time_ms = (time.time() - start_time) * 1000
        else:
            processing_time_ms = 0.0
        
        # Generate record ID if not provided
        record_id = record_data.get('record_id', self.generate_record_id())
        
        # Return dictionary with attendance record data
        return {
            'record_id': record_id,
            'user_id': user_id,
            'user_name': user_name,
            'date': record_date,
            'time': record_time,
            'confidence': confidence,
            'liveness_verified': liveness_verified,
            'face_quality_score': face_quality_score,
            'processing_time_ms': processing_time_ms,
            'verification_stage': verification_stage or ("completed" if liveness_verified else "pending"),
            'session_id': session_id or self._generate_session_id(),
            'device_info': device_info,
            'location': location,
            'status': None  # Status will be determined by domain layer
        }
    
    def generate_record_id(self) -> str:
        """
        Generate a unique record ID using UUID.
        
        Returns:
            A unique record ID string in the format "rec_{uuid}".
        """
        unique_id = str(uuid.uuid4())
        return f"rec_{unique_id}"
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        This is a helper method for generating session IDs when not provided.
        Uses timestamp and UUID for uniqueness.
        
        Returns:
            A unique session ID string in the format "session_{timestamp}_{uuid}".
        """
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
        return f"session_{timestamp}_{unique_id}"

