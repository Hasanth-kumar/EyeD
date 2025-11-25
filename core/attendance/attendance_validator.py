"""
Attendance Validator - Operational validation during attendance logging.

This module provides pure operational validation for attendance records
without any business rules or infrastructure dependencies.
"""

from typing import Optional, Dict, Any
import numpy as np

from core.attendance.value_objects import ValidationResult
from core.shared.constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    MIN_FACE_QUALITY_SCORE
)


class AttendanceValidator:
    """
    Pure operational validation for attendance records during logging.
    
    This class validates data integrity, types, and value ranges ONLY.
    It does not handle business rules (that's in domain/services) or
    persistence (that's in infrastructure).
    
    Examples:
        >>> validator = AttendanceValidator()
        >>> result = validator.validate_confidence(0.85, 0.6)
        >>> result.is_valid
        True
        >>> 
        >>> record_data = {'record_id': 'rec_001', 'user_id': 'user_001', ...}
        >>> result = validator.validate_record(record_data)
        >>> result.is_valid
        True
    """
    
    def __init__(self):
        """Initialize the attendance validator."""
        pass
    
    def validate_record(self, record_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate an attendance record's structure and data integrity.
        
        This method validates:
        - Required fields are present and non-empty
        - Data types are correct
        - Value ranges are within acceptable bounds
        - Record structure is valid
        
        Args:
            record_data: Dictionary containing attendance record data.
        
        Returns:
            ValidationResult indicating whether the record is valid.
        """
        # Validate record_id
        if 'record_id' not in record_data or not record_data['record_id'] or not isinstance(record_data['record_id'], str):
            return ValidationResult.failure(
                "Record ID is required and must be a non-empty string",
                error_code="INVALID_RECORD_ID"
            )
        
        # Validate user_id
        if 'user_id' not in record_data or not record_data['user_id'] or not isinstance(record_data['user_id'], str):
            return ValidationResult.failure(
                "User ID is required and must be a non-empty string",
                error_code="INVALID_USER_ID"
            )
        
        # Validate user_name
        if 'user_name' not in record_data or not record_data['user_name'] or not isinstance(record_data['user_name'], str):
            return ValidationResult.failure(
                "User name is required and must be a non-empty string",
                error_code="INVALID_USER_NAME"
            )
        
        # Validate date
        if 'date' not in record_data or not record_data['date']:
            return ValidationResult.failure(
                "Date is required",
                error_code="INVALID_DATE"
            )
        
        # Validate time
        if 'time' not in record_data or not record_data['time']:
            return ValidationResult.failure(
                "Time is required",
                error_code="INVALID_TIME"
            )
        
        # Validate confidence
        if 'confidence' not in record_data:
            return ValidationResult.failure(
                "Confidence is required",
                error_code="MISSING_CONFIDENCE"
            )
        confidence_result = self.validate_confidence(
            record_data['confidence'],
            DEFAULT_CONFIDENCE_THRESHOLD
        )
        if not confidence_result.is_valid:
            return confidence_result
        
        # Validate liveness
        if 'liveness_verified' not in record_data or not isinstance(record_data['liveness_verified'], bool):
            return ValidationResult.failure(
                "Liveness verified must be a boolean value",
                error_code="INVALID_LIVENESS_TYPE"
            )
        
        # Validate face quality score
        if 'face_quality_score' not in record_data:
            return ValidationResult.failure(
                "Face quality score is required",
                error_code="MISSING_QUALITY_SCORE"
            )
        quality_result = self.validate_quality(
            record_data['face_quality_score'],
            MIN_FACE_QUALITY_SCORE
        )
        if not quality_result.is_valid:
            return quality_result
        
        # Validate processing time
        if 'processing_time_ms' not in record_data:
            return ValidationResult.failure(
                "Processing time is required",
                error_code="MISSING_PROCESSING_TIME"
            )
        if not isinstance(record_data['processing_time_ms'], (int, float)):
            return ValidationResult.failure(
                "Processing time must be a number",
                error_code="INVALID_PROCESSING_TIME_TYPE"
            )
        if record_data['processing_time_ms'] < 0:
            return ValidationResult.failure(
                "Processing time must be non-negative",
                error_code="INVALID_PROCESSING_TIME_RANGE"
            )
        
        # Validate verification_stage
        if 'verification_stage' not in record_data or not record_data['verification_stage'] or not isinstance(record_data['verification_stage'], str):
            return ValidationResult.failure(
                "Verification stage is required and must be a non-empty string",
                error_code="INVALID_VERIFICATION_STAGE"
            )
        
        # Validate session_id
        if 'session_id' not in record_data or not record_data['session_id'] or not isinstance(record_data['session_id'], str):
            return ValidationResult.failure(
                "Session ID is required and must be a non-empty string",
                error_code="INVALID_SESSION_ID"
            )
        
        # Validate device_info
        if 'device_info' not in record_data or not isinstance(record_data['device_info'], str):
            return ValidationResult.failure(
                "Device info must be a string",
                error_code="INVALID_DEVICE_INFO_TYPE"
            )
        
        # Validate location
        if 'location' not in record_data or not isinstance(record_data['location'], str):
            return ValidationResult.failure(
                "Location must be a string",
                error_code="INVALID_LOCATION_TYPE"
            )
        
        # Validate status (if provided, otherwise it's optional and will be set by domain layer)
        if 'status' in record_data and record_data['status'] is not None:
            if not isinstance(record_data['status'], str):
                return ValidationResult.failure(
                    "Status must be a string",
                    error_code="INVALID_STATUS_TYPE"
                )
            if record_data['status'].lower() not in ['present', 'absent']:
                return ValidationResult.failure(
                    f"Status must be 'Present' or 'Absent', got '{record_data['status']}'",
                    error_code="INVALID_STATUS_VALUE"
                )
        
        return ValidationResult.success("Attendance record is valid")
    
    def validate_image(self, face_image: np.ndarray) -> ValidationResult:
        """
        Validate a face image array.
        
        This method validates:
        - Image is a numpy array
        - Image has valid dimensions (not empty)
        - Image has valid shape (at least 2D)
        - Image data type is numeric
        
        Args:
            face_image: The face image array to validate.
        
        Returns:
            ValidationResult indicating whether the image is valid.
        """
        # Validate that it's a numpy array
        if not isinstance(face_image, np.ndarray):
            return ValidationResult.failure(
                "Face image must be a numpy array",
                error_code="INVALID_IMAGE_TYPE"
            )
        
        # Validate that array is not empty
        if face_image.size == 0:
            return ValidationResult.failure(
                "Face image array cannot be empty",
                error_code="EMPTY_IMAGE"
            )
        
        # Validate that array has at least 2 dimensions
        if face_image.ndim < 2:
            return ValidationResult.failure(
                f"Face image must have at least 2 dimensions, got {face_image.ndim}",
                error_code="INVALID_IMAGE_DIMENSIONS"
            )
        
        # Validate that array has valid shape (all dimensions > 0)
        if any(dim <= 0 for dim in face_image.shape):
            return ValidationResult.failure(
                f"Face image dimensions must be positive, got shape {face_image.shape}",
                error_code="INVALID_IMAGE_SHAPE"
            )
        
        # Validate that data type is numeric
        if not np.issubdtype(face_image.dtype, np.number):
            return ValidationResult.failure(
                f"Face image must have numeric data type, got {face_image.dtype}",
                error_code="INVALID_IMAGE_DTYPE"
            )
        
        return ValidationResult.success("Face image is valid")
    
    def validate_confidence(
        self,
        confidence: float,
        threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    ) -> ValidationResult:
        """
        Validate a confidence score.
        
        This method validates:
        - Confidence is a number
        - Confidence is within valid range [0.0, 1.0]
        - Confidence meets the threshold requirement
        
        Args:
            confidence: The confidence score to validate (0.0 to 1.0).
            threshold: The minimum confidence threshold required.
                      Defaults to DEFAULT_CONFIDENCE_THRESHOLD.
        
        Returns:
            ValidationResult indicating whether the confidence is valid.
        """
        # Validate that confidence is a number (including numpy types)
        # Convert numpy types to Python float for validation
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            return ValidationResult.failure(
                "Confidence must be a number",
                error_code="INVALID_CONFIDENCE_TYPE"
            )
        
        # Validate that confidence is within valid range
        if confidence < 0.0 or confidence > 1.0:
            return ValidationResult.failure(
                f"Confidence must be between 0.0 and 1.0, got {confidence}",
                error_code="INVALID_CONFIDENCE_RANGE"
            )
        
        # Validate that threshold is valid (including numpy types)
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return ValidationResult.failure(
                "Threshold must be a number",
                error_code="INVALID_THRESHOLD_TYPE"
            )
        
        if threshold < 0.0 or threshold > 1.0:
            return ValidationResult.failure(
                f"Threshold must be between 0.0 and 1.0, got {threshold}",
                error_code="INVALID_THRESHOLD_RANGE"
            )
        
        # Validate that confidence meets threshold
        if confidence < threshold:
            return ValidationResult.failure(
                f"Confidence {confidence:.3f} is below threshold {threshold:.3f}",
                error_code="CONFIDENCE_BELOW_THRESHOLD"
            )
        
        return ValidationResult.success(
            f"Confidence {confidence:.3f} meets threshold {threshold:.3f}"
        )
    
    def validate_liveness(
        self,
        liveness_verified: bool,
        required: bool = True
    ) -> ValidationResult:
        """
        Validate liveness verification status.
        
        This method validates:
        - Liveness verified is a boolean
        - If required, liveness must be verified
        
        Args:
            liveness_verified: Whether liveness verification passed.
            required: Whether liveness verification is required.
                    Defaults to True.
        
        Returns:
            ValidationResult indicating whether liveness is valid.
        """
        # Validate that liveness_verified is a boolean
        if not isinstance(liveness_verified, bool):
            return ValidationResult.failure(
                "Liveness verified must be a boolean value",
                error_code="INVALID_LIVENESS_TYPE"
            )
        
        # Validate that required is a boolean
        if not isinstance(required, bool):
            return ValidationResult.failure(
                "Required parameter must be a boolean value",
                error_code="INVALID_REQUIRED_TYPE"
            )
        
        # If liveness is required but not verified, fail
        if required and not liveness_verified:
            return ValidationResult.failure(
                "Liveness verification is required but was not verified",
                error_code="LIVENESS_NOT_VERIFIED"
            )
        
        if liveness_verified:
            return ValidationResult.success("Liveness verification passed")
        else:
            return ValidationResult.success(
                "Liveness verification not required or not verified"
            )
    
    def validate_quality(
        self,
        quality_score: float,
        threshold: float = MIN_FACE_QUALITY_SCORE
    ) -> ValidationResult:
        """
        Validate a face quality score.
        
        This method validates:
        - Quality score is a number
        - Quality score is within valid range [0.0, 1.0]
        - Quality score meets the threshold requirement
        
        Args:
            quality_score: The quality score to validate (0.0 to 1.0).
            threshold: The minimum quality threshold required.
                      Defaults to MIN_FACE_QUALITY_SCORE.
        
        Returns:
            ValidationResult indicating whether the quality is valid.
        """
        # Validate that quality_score is a number (including numpy types)
        try:
            quality_score = float(quality_score)
        except (TypeError, ValueError):
            return ValidationResult.failure(
                "Quality score must be a number",
                error_code="INVALID_QUALITY_TYPE"
            )
        
        # Validate that quality_score is within valid range
        if quality_score < 0.0 or quality_score > 1.0:
            return ValidationResult.failure(
                f"Quality score must be between 0.0 and 1.0, got {quality_score}",
                error_code="INVALID_QUALITY_RANGE"
            )
        
        # Validate that threshold is valid (including numpy types)
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return ValidationResult.failure(
                "Threshold must be a number",
                error_code="INVALID_THRESHOLD_TYPE"
            )
        
        if threshold < 0.0 or threshold > 1.0:
            return ValidationResult.failure(
                f"Threshold must be between 0.0 and 1.0, got {threshold}",
                error_code="INVALID_THRESHOLD_RANGE"
            )
        
        # Validate that quality_score meets threshold
        if quality_score < threshold:
            return ValidationResult.failure(
                f"Quality score {quality_score:.3f} is below threshold {threshold:.3f}",
                error_code="QUALITY_BELOW_THRESHOLD"
            )
        
        return ValidationResult.success(
            f"Quality score {quality_score:.3f} meets threshold {threshold:.3f}"
        )

