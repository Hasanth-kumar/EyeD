"""
Face quality assessment module for EyeD AI Attendance System.

This module provides pure face quality assessment logic with no infrastructure dependencies.
It analyzes face images for resolution, brightness, contrast, and sharpness to determine
overall quality and suitability for recognition.
"""

from typing import List
import numpy as np
import cv2

from core.shared.constants import MIN_FACE_QUALITY_SCORE
from .value_objects import QualityResult


class QualityAssessor:
    """
    Pure face quality assessment logic.
    
    This class is responsible solely for assessing the quality of face images.
    It does not perform detection or recognition, only quality analysis.
    
    Attributes:
        min_quality_threshold: Minimum quality score required for suitability (default from constants).
        resolution_weight: Weight for resolution score in overall calculation (0.3).
        brightness_weight: Weight for brightness score in overall calculation (0.25).
        contrast_weight: Weight for contrast score in overall calculation (0.25).
        sharpness_weight: Weight for sharpness score in overall calculation (0.2).
    
    Examples:
        >>> import numpy as np
        >>> assessor = QualityAssessor()
        >>> face_image = np.array([[100, 120, ...], ...])  # Face image array
        >>> result = assessor.assess(face_image)
        >>> print(result.overall_score)
        0.85
        >>> print(result.is_suitable)
        True
    """
    
    def __init__(self, min_quality_threshold: float = None):
        """
        Initialize the quality assessor.
        
        Args:
            min_quality_threshold: Minimum quality score for suitability.
                                  If None, uses MIN_FACE_QUALITY_SCORE from constants.
        """
        self.min_quality_threshold = (
            min_quality_threshold if min_quality_threshold is not None 
            else MIN_FACE_QUALITY_SCORE
        )
        self.resolution_weight = 0.3
        self.brightness_weight = 0.25
        self.contrast_weight = 0.25
        self.sharpness_weight = 0.2
    
    def assess(self, face_image: np.ndarray) -> QualityResult:
        """
        Assess the quality of a single face image.
        
        Args:
            face_image: Face image to assess (cropped face, numpy array).
        
        Returns:
            QualityResult containing all quality metrics and suitability determination.
        
        Raises:
            ValueError: If face_image is None or empty.
        """
        if face_image is None or face_image.size == 0:
            return QualityResult(
                overall_score=0.0,
                resolution_score=0.0,
                brightness_score=0.0,
                contrast_score=0.0,
                sharpness_score=0.0,
                is_suitable=False,
                reason="Face image is None or empty"
            )
        
        # Convert to grayscale for analysis
        gray = self._to_grayscale(face_image)
        
        # Calculate individual quality scores
        resolution_score = self._calculate_resolution_score(gray)
        brightness_score = self._calculate_brightness_score(gray)
        contrast_score = self._calculate_contrast_score(gray)
        sharpness_score = self._calculate_sharpness_score(gray)
        
        # Calculate weighted overall score
        overall_score = (
            resolution_score * self.resolution_weight +
            brightness_score * self.brightness_weight +
            contrast_score * self.contrast_weight +
            sharpness_score * self.sharpness_weight
        )
        overall_score = max(0.0, min(1.0, overall_score))
        
        # Determine suitability
        is_suitable = overall_score >= self.min_quality_threshold
        reason = None
        if not is_suitable:
            reasons = []
            if resolution_score < 0.3:
                reasons.append("low resolution")
            if brightness_score < 0.3:
                reasons.append("poor brightness")
            if contrast_score < 0.3:
                reasons.append("low contrast")
            if sharpness_score < 0.3:
                reasons.append("blurry")
            reason = ", ".join(reasons) if reasons else "overall quality below threshold"
        
        return QualityResult(
            overall_score=overall_score,
            resolution_score=resolution_score,
            brightness_score=brightness_score,
            contrast_score=contrast_score,
            sharpness_score=sharpness_score,
            is_suitable=is_suitable,
            reason=reason
        )
    
    def assess_batch(self, face_images: List[np.ndarray]) -> List[QualityResult]:
        """
        Assess the quality of multiple face images.
        
        Args:
            face_images: List of face images to assess.
        
        Returns:
            List of QualityResult objects, one for each input image.
        """
        return [self.assess(face_image) for face_image in face_images]
    
    def _to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale if needed.
        
        Args:
            image: Input image (BGR, RGB, or grayscale).
        
        Returns:
            Grayscale image.
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _calculate_resolution_score(self, image: np.ndarray) -> float:
        """
        Calculate resolution quality score.
        
        Higher resolution (more pixels) generally means better quality.
        Score is normalized based on a reference resolution of 480x480.
        
        Args:
            image: Grayscale image.
        
        Returns:
            Resolution score between 0.0 and 1.0.
        """
        height, width = image.shape
        pixel_count = height * width
        reference_pixels = 480 * 480
        resolution_score = min(1.0, pixel_count / reference_pixels)
        return resolution_score
    
    def _calculate_brightness_score(self, image: np.ndarray) -> float:
        """
        Calculate brightness quality score.
        
        Optimal brightness is around 128 (middle of 0-255 range).
        Score decreases as brightness deviates from optimal.
        
        Args:
            image: Grayscale image.
        
        Returns:
            Brightness score between 0.0 and 1.0.
        """
        mean_brightness = np.mean(image)
        # Optimal brightness is 128 (middle of 0-255 range)
        optimal_brightness = 128.0
        deviation = abs(mean_brightness - optimal_brightness)
        # Score is 1.0 at optimal, decreases linearly to 0.0 at max deviation
        brightness_score = 1.0 - (deviation / optimal_brightness)
        return max(0.0, brightness_score)
    
    def _calculate_contrast_score(self, image: np.ndarray) -> float:
        """
        Calculate contrast quality score.
        
        Higher contrast (standard deviation) generally means better quality.
        Score is normalized based on a reference contrast of 50.
        
        Args:
            image: Grayscale image.
        
        Returns:
            Contrast score between 0.0 and 1.0.
        """
        contrast = np.std(image)
        reference_contrast = 50.0
        contrast_score = min(1.0, contrast / reference_contrast)
        return contrast_score
    
    def _calculate_sharpness_score(self, image: np.ndarray) -> float:
        """
        Calculate sharpness quality score using Laplacian variance.
        
        Higher Laplacian variance indicates sharper image.
        Score is normalized based on a reference variance of 500.
        
        Args:
            image: Grayscale image.
        
        Returns:
            Sharpness score between 0.0 and 1.0.
        """
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        reference_variance = 500.0
        sharpness_score = min(1.0, laplacian_var / reference_variance)
        return sharpness_score

