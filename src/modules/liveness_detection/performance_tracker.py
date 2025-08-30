"""
Liveness Detection Performance Tracker

This module handles performance tracking for liveness detection,
following the Single-Responsibility Principle.
"""

from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Tracks performance metrics for liveness detection components"""
    
    def __init__(self):
        """Initialize performance tracker"""
        self.processing_times: List[float] = []
        self.test_counts: Dict[str, int] = {}
        self.start_time = time.time()
        
        logger.info("Performance tracker initialized")
    
    def start_timer(self) -> float:
        """Start timing a process"""
        return time.time()
    
    def end_timer(self, start_time: float) -> float:
        """End timing and return processing time in milliseconds"""
        processing_time = (time.time() - start_time) * 1000
        
        # Ensure minimum measurable time for testing (0.1ms)
        if processing_time < 0.1:
            processing_time = 0.1
            
        self.processing_times.append(processing_time)
        return processing_time
    
    def record_test(self, test_type: str, processing_time: float) -> None:
        """Record a test execution with its processing time"""
        if test_type not in self.test_counts:
            self.test_counts[test_type] = 0
        self.test_counts[test_type] += 1
        
        logger.debug(f"Recorded {test_type} test: {processing_time:.2f}ms")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        if not self.processing_times:
            return {
                'total_tests': 0,
                'average_processing_time': 0,
                'min_processing_time': 0,
                'max_processing_time': 0,
                'uptime_seconds': time.time() - self.start_time
            }
        
        return {
            'total_tests': len(self.processing_times),
            'average_processing_time': sum(self.processing_times) / len(self.processing_times),
            'min_processing_time': min(self.processing_times),
            'max_processing_time': max(self.processing_times),
            'uptime_seconds': time.time() - self.start_time,
            'test_counts': self.test_counts.copy()
        }
    
    def is_healthy(self) -> bool:
        """Check if performance is within acceptable limits"""
        if not self.processing_times:
            return True
        
        avg_time = sum(self.processing_times) / len(self.processing_times)
        # Consider healthy if average processing time is under 100ms
        return avg_time < 100.0
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics"""
        self.processing_times.clear()
        self.test_counts.clear()
        self.start_time = time.time()
        logger.info("Performance metrics reset")
    
    def get_recent_performance(self, num_samples: int = 10) -> List[float]:
        """Get recent processing times"""
        return self.processing_times[-num_samples:] if self.processing_times else []
