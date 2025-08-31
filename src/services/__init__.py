"""
Service Layer for EyeD AI Attendance System

This module provides service initialization and dependency injection
for the dashboard components.
"""

from typing import Optional
import logging

from .attendance_service import AttendanceService
from .user_service import UserService
from .recognition_service import RecognitionService
from .analytics_service import AnalyticsService
from .gamification_service import GamificationService
from ..repositories.attendance_repository import AttendanceRepository
from ..repositories.user_repository import UserRepository
from ..repositories.face_repository import FaceRepository
from ..modules.attendance import AttendanceManager
from ..modules.recognition import FaceRecognition
from ..modules.liveness import LivenessDetection
from ..modules.face_db import FaceDatabase

logger = logging.getLogger(__name__)


class ServiceFactory:
    """Factory for creating and managing service instances"""
    
    def __init__(self):
        self._attendance_service: Optional[AttendanceService] = None
        self._user_service: Optional['UserService'] = None
        self._recognition_service: Optional['RecognitionService'] = None
        self._analytics_service: Optional['AnalyticsService'] = None
        self._gamification_service: Optional['GamificationService'] = None
        self._attendance_repository: Optional[AttendanceRepository] = None
        self._user_repository: Optional[UserRepository] = None
        self._face_repository: Optional[FaceRepository] = None
        self._attendance_manager: Optional[AttendanceManager] = None
        self._recognition_system: Optional[FaceRecognition] = None
        self._liveness_system: Optional[LivenessDetection] = None
        self._face_database: Optional[FaceDatabase] = None
        
    def get_attendance_service(self) -> AttendanceService:
        """Get or create attendance service instance"""
        if self._attendance_service is None:
            self._attendance_service = AttendanceService(
                attendance_repository=self.get_attendance_repository(),
                attendance_manager=self.get_attendance_manager(),
                recognition_system=self.get_recognition_system(),
                liveness_system=self.get_liveness_system()
            )
            logger.info("Attendance service created")
        
        return self._attendance_service
    
    def get_attendance_repository(self) -> AttendanceRepository:
        """Get or create attendance repository instance"""
        if self._attendance_repository is None:
            self._attendance_repository = AttendanceRepository()
            logger.info("Attendance repository created")
        
        return self._attendance_repository
    
    def get_user_repository(self) -> UserRepository:
        """Get or create user repository instance"""
        if self._user_repository is None:
            self._user_repository = UserRepository()
            logger.info("User repository created")
        
        return self._user_repository
    
    def get_face_repository(self) -> FaceRepository:
        """Get or create face repository instance"""
        if self._face_repository is None:
            try:
                self._face_repository = FaceRepository()
                logger.info("Face repository created successfully")
            except Exception as e:
                logger.error(f"Failed to create face repository: {e}")
                raise
        else:
            logger.debug("Face repository already exists")
        
        return self._face_repository
    
    def get_attendance_manager(self) -> AttendanceManager:
        """Get or create attendance manager instance"""
        if self._attendance_manager is None:
            self._attendance_manager = AttendanceManager()
            logger.info("Attendance manager created")
        
        return self._attendance_manager
    
    def get_recognition_system(self) -> FaceRecognition:
        """Get or create face recognition system instance"""
        if self._recognition_system is None:
            self._recognition_system = FaceRecognition()
            logger.info("Face recognition system created")
        
        return self._recognition_system
    
    def get_liveness_system(self) -> LivenessDetection:
        """Get or create liveness detection system instance"""
        if self._liveness_system is None:
            self._liveness_system = LivenessDetection()
            logger.info("Liveness detection system created")
        
        return self._liveness_system
    
    def get_face_database(self) -> FaceDatabase:
        """Get or create face database instance"""
        if self._face_database is None:
            try:
                face_repo = self.get_face_repository()
                logger.info(f"Face repository obtained: {type(face_repo)}")
                
                self._face_database = FaceDatabase(
                    face_repository=face_repo
                )
                logger.info("Face database created successfully")
            except Exception as e:
                logger.error(f"Failed to create face database: {e}")
                raise
        else:
            logger.debug("Face database already exists")
        
        return self._face_database
    
    def get_user_service(self) -> 'UserService':
        """Get or create user service instance"""
        if self._user_service is None:
            self._user_service = UserService(
                face_database=self.get_face_database(),
                recognition_system=self.get_recognition_system(),
                attendance_repository=self.get_attendance_repository()
            )
            logger.info("User service created")
        
        return self._user_service
    
    def get_recognition_service(self) -> 'RecognitionService':
        """Get or create recognition service instance"""
        if self._recognition_service is None:
            self._recognition_service = RecognitionService(
                recognition_system=self.get_recognition_system(),
                liveness_system=self.get_liveness_system(),
                face_database=self.get_face_database()
            )
            logger.info("Recognition service created")
        
        return self._recognition_service
    
    def get_analytics_service(self) -> 'AnalyticsService':
        """Get or create analytics service instance"""
        if self._analytics_service is None:
            self._analytics_service = AnalyticsService(
                attendance_repository=self.get_attendance_repository(),
                face_database=self.get_face_database()
            )
            logger.info("Analytics service created")
        
        return self._analytics_service
    
    def get_gamification_service(self) -> 'GamificationService':
        """Get or create gamification service instance"""
        if self._gamification_service is None:
            self._gamification_service = GamificationService(
                attendance_repository=self.get_attendance_repository(),
                face_database=self.get_face_database()
            )
            logger.info("Gamification service created")
        
        return self._gamification_service
    
    def reset_services(self):
        """Reset all service instances (useful for testing)"""
        self._attendance_service = None
        self._user_service = None
        self._recognition_service = None
        self._analytics_service = None
        self._gamification_service = None
        self._attendance_repository = None
        self._user_repository = None
        self._face_repository = None
        self._attendance_manager = None
        self._recognition_system = None
        self._liveness_system = None
        self._face_database = None
        logger.info("All services reset")
    
    def get_all_services(self):
        """Get all service instances for testing or bulk operations"""
        return {
            'attendance_service': self.get_attendance_service(),
            'user_service': self.get_user_service(),
            'recognition_service': self.get_recognition_service(),
            'analytics_service': self.get_analytics_service(),
            'gamification_service': self.get_gamification_service()
        }
    
    def get_all_repositories(self):
        """Get all repository instances for testing or bulk operations"""
        return {
            'attendance_repository': self.get_attendance_repository(),
            'user_repository': self.get_user_repository(),
            'face_repository': self.get_face_repository()
        }
    
    def validate_dependencies(self):
        """Validate that all services can be created successfully"""
        try:
            validation_results = {}
            
            # Test service creation
            validation_results['attendance_service'] = self.get_attendance_service() is not None
            validation_results['user_service'] = self.get_user_service() is not None
            validation_results['recognition_service'] = self.get_recognition_service() is not None
            validation_results['analytics_service'] = self.get_analytics_service() is not None
            validation_results['gamification_service'] = self.get_gamification_service() is not None
            
            # Test repository creation
            validation_results['attendance_repository'] = self.get_attendance_repository() is not None
            validation_results['user_repository'] = self.get_user_repository() is not None
            validation_results['face_repository'] = self.get_face_repository() is not None
            
            logger.info("Service factory dependency validation completed")
            return validation_results
            
        except Exception as e:
            logger.error(f"Service factory dependency validation failed: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Clean up all service and repository instances"""
        try:
            self._attendance_service = None
            self._user_service = None
            self._recognition_service = None
            self._analytics_service = None
            self._gamification_service = None
            self._attendance_repository = None
            self._user_repository = None
            self._face_repository = None
            self._attendance_manager = None
            self._recognition_system = None
            self._liveness_system = None
            self._face_database = None
            
            logger.info("Service factory cleanup completed")
            
        except Exception as e:
            logger.error(f"Service factory cleanup failed: {e}")


# Global service factory instance
service_factory = ServiceFactory()


def get_attendance_service() -> AttendanceService:
    """Get attendance service instance"""
    return service_factory.get_attendance_service()


def get_attendance_repository() -> AttendanceRepository:
    """Get attendance repository instance"""
    return service_factory.get_attendance_repository()


def get_attendance_manager() -> AttendanceManager:
    """Get attendance manager instance"""
    return service_factory.get_attendance_manager()


def get_recognition_system() -> FaceRecognition:
    """Get face recognition system instance"""
    return service_factory.get_recognition_system()


def get_liveness_system() -> LivenessDetection:
    """Get liveness detection system instance"""
    return service_factory.get_liveness_system()


def get_face_database() -> FaceDatabase:
    """Get face database instance"""
    return service_factory.get_face_database()


def get_user_service() -> 'UserService':
    """Get user service instance"""
    return service_factory.get_user_service()


def get_recognition_service() -> 'RecognitionService':
    """Get recognition service instance"""
    return service_factory.get_recognition_service()


def get_analytics_service() -> 'AnalyticsService':
    """Get analytics service instance"""
    return service_factory.get_analytics_service()


def get_gamification_service() -> 'GamificationService':
    """Get gamification service instance"""
    return service_factory.get_gamification_service()


def get_user_repository() -> UserRepository:
    """Get user repository instance"""
    return service_factory.get_user_repository()


def get_face_repository() -> FaceRepository:
    """Get face repository instance"""
    return service_factory.get_face_repository()
