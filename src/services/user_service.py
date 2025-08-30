"""
User Service for EyeD AI Attendance System

This module handles user management operations with clear separation of concerns.
Following SRP: Each method has a single, focused responsibility.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import uuid

from ..repositories.attendance_repository import AttendanceRepository
from ..interfaces.face_database_interface import FaceDatabaseInterface
from ..interfaces.recognition_interface import RecognitionInterface

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for user management operations.
    
    Responsibilities:
    - User registration and management
    - User information retrieval and updates
    - User performance metrics calculation
    - User attendance data enhancement
    """
    
    def __init__(self, 
                 face_database: FaceDatabaseInterface,
                 recognition_system: RecognitionInterface,
                 attendance_repository: AttendanceRepository):
        """Initialize user service with dependencies"""
        self.face_database = face_database
        self.recognition_system = recognition_system
        self.attendance_repository = attendance_repository
        
        logger.info("User service initialized successfully")
    
    # ============================================================================
    # USER REGISTRATION AND MANAGEMENT METHODS
    # ============================================================================
    
    def register_user(self, user_id: str, user_name: str, face_image, 
                     additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a new user with face recognition"""
        try:
            # Step 1: Validate user ID uniqueness
            if self.face_database.user_exists(user_id):
                return {
                    'success': False,
                    'error': f'User ID {user_id} already exists',
                    'stage': 'validation'
                }
            
            # Step 2: Assess face image quality
            quality_result = self.recognition_system.assess_face_quality(face_image)
            if not quality_result.is_suitable:
                return {
                    'success': False,
                    'error': f'Face image quality insufficient: {quality_result.reason}',
                    'stage': 'quality_assessment',
                    'quality_score': quality_result.score
                }
            
            # Step 3: Generate face embeddings
            embedding_result = self.recognition_system.generate_embeddings(face_image)
            if not embedding_result.success:
                return {
                    'success': False,
                    'error': f'Failed to generate face embeddings: {embedding_result.error}',
                    'stage': 'embedding_generation'
                }
            
            # Step 4: Store user in database
            user_data = {
                'user_id': user_id,
                'user_name': user_name,
                'registration_date': datetime.now(),
                'face_embeddings': embedding_result.embeddings,
                'face_quality_score': quality_result.score,
                'additional_info': additional_info or {}
            }
            
            storage_result = self.face_database.store_user_face(user_data)
            if not storage_result.success:
                return {
                    'success': False,
                    'error': f'Failed to store user data: {storage_result.error}',
                    'stage': 'storage'
                }
            
            logger.info(f"User {user_id} registered successfully")
            return {
                'success': True,
                'user_id': user_id,
                'user_name': user_name,
                'registration_date': user_data['registration_date'],
                'face_quality_score': quality_result.score,
                'message': 'User registration completed successfully'
            }
            
        except Exception as e:
            logger.error(f"User registration failed for {user_id}: {e}")
            return {
                'success': False,
                'error': f'User registration failed: {str(e)}',
                'stage': 'unknown'
            }
    
    def update_user_info(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            # Validate user exists
            if not self.face_database.user_exists(user_id):
                return {
                    'success': False,
                    'error': f'User {user_id} not found'
                }
            
            # Update user information
            update_result = self.face_database.update_user_info(user_id, updates)
            if not update_result.success:
                return {
                    'success': False,
                    'error': f'Failed to update user: {update_result.error}'
                }
            
            logger.info(f"User {user_id} information updated successfully")
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User information updated successfully',
                'updated_fields': list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"User update failed for {user_id}: {e}")
            return {
                'success': False,
                'error': f'User update failed: {str(e)}'
            }
    
    def deactivate_user(self, user_id: str, reason: str = "") -> Dict[str, Any]:
        """Deactivate a user account"""
        try:
            # Validate user exists
            if not self.face_database.user_exists(user_id):
                return {
                    'success': False,
                    'error': f'User {user_id} not found'
                }
            
            # Deactivate user
            deactivation_result = self.face_database.deactivate_user(user_id, reason)
            if not deactivation_result.success:
                return {
                    'success': False,
                    'error': f'Failed to deactivate user: {deactivation_result.error}'
                }
            
            logger.info(f"User {user_id} deactivated successfully")
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User deactivated successfully',
                'deactivation_reason': reason
            }
            
        except Exception as e:
            logger.error(f"User deactivation failed for {user_id}: {e}")
            return {
                'success': False,
                'error': f'User deactivation failed: {str(e)}'
            }
    
    # ============================================================================
    # USER INFORMATION RETRIEVAL METHODS
    # ============================================================================
    
    def get_user_info(self, user_id: str, include_performance: bool = False) -> Dict[str, Any]:
        """Get user information with optional performance metrics"""
        try:
            # Get basic user info
            user_info = self.face_database.get_user_info(user_id)
            if not user_info.success:
                return {
                    'success': False,
                    'error': f'Failed to get user info: {user_info.error}'
                }
            
            result = {
                'success': True,
                'user_info': user_info.data
            }
            
            # Add performance metrics if requested
            if include_performance:
                performance_metrics = self._calculate_user_performance(user_id)
                result['performance_metrics'] = performance_metrics
            
            return result
            
        except Exception as e:
            logger.error(f"User info retrieval failed for {user_id}: {e}")
            return {
                'success': False,
                'error': f'User info retrieval failed: {str(e)}'
            }
    
    def get_all_users(self, include_inactive: bool = False, 
                     include_attendance: bool = False) -> Dict[str, Any]:
        """Get list of all registered users"""
        try:
            users = self.face_database.get_all_users(include_inactive=include_inactive)
            if not users.success:
                return {
                    'success': False,
                    'error': f'Failed to get users: {users.error}'
                }
            
            # Enhance with attendance data if requested
            if include_attendance:
                enhanced_users = []
                for user in users.data:
                    attendance_summary = self.attendance_repository.get_user_attendance_summary(user['user_id'])
                    user['attendance_summary'] = attendance_summary
                    enhanced_users.append(user)
                users.data = enhanced_users
            
            logger.info(f"Retrieved {len(users.data)} users")
            return {
                'success': True,
                'users': users.data,
                'total_count': len(users.data)
            }
            
        except Exception as e:
            logger.error(f"User list retrieval failed: {e}")
            return {
                'success': False,
                'error': f'User list retrieval failed: {str(e)}'
            }
    
    def search_users(self, query: str, search_fields: List[str] = None) -> Dict[str, Any]:
        """Search users by various criteria"""
        try:
            if not search_fields:
                search_fields = ['user_id', 'user_name']
            
            # Get all users and filter
            users_result = self.get_all_users()
            if not users_result['success']:
                return users_result
            
            # Filter users based on search query
            matching_users = []
            query_lower = query.lower()
            
            for user in users_result['users']:
                for field in search_fields:
                    if field in user and query_lower in str(user[field]).lower():
                        matching_users.append(user)
                        break
            
            return {
                'success': True,
                'users': matching_users,
                'total_count': len(matching_users),
                'search_query': query,
                'search_fields': search_fields
            }
            
        except Exception as e:
            logger.error(f"User search failed: {e}")
            return {
                'success': False,
                'error': f'User search failed: {str(e)}'
            }
    
    # ============================================================================
    # PRIVATE HELPER METHODS - PERFORMANCE CALCULATION
    # ============================================================================
    
    def _calculate_user_performance(self, user_id: str) -> Dict[str, Any]:
        """Calculate user performance metrics"""
        try:
            # Get attendance history
            attendance_history = self.attendance_repository.get_attendance_history(user_id=user_id)
            
            if not attendance_history:
                return {
                    'total_attendance': 0,
                    'attendance_rate': 0.0,
                    'average_confidence': 0.0,
                    'best_streak': 0,
                    'current_streak': 0
                }
            
            # Calculate metrics
            total_attendance = len(attendance_history)
            attendance_rate = self._calculate_attendance_rate(user_id, total_attendance)
            average_confidence = sum(entry.confidence for entry in attendance_history) / total_attendance
            streak_info = self._calculate_attendance_streaks(attendance_history)
            
            return {
                'total_attendance': total_attendance,
                'attendance_rate': attendance_rate,
                'average_confidence': round(average_confidence, 3),
                'best_streak': streak_info['best_streak'],
                'current_streak': streak_info['current_streak']
            }
            
        except Exception as e:
            logger.error(f"Performance calculation failed for user {user_id}: {e}")
            return {
                'total_attendance': 0,
                'attendance_rate': 0.0,
                'average_confidence': 0.0,
                'best_streak': 0,
                'current_streak': 0
            }
    
    def _calculate_attendance_rate(self, user_id: str, total_attendance: int) -> float:
        """Calculate user attendance rate"""
        # This would need business logic to determine expected attendance days
        # For now, return a simple calculation
        return min(1.0, total_attendance / 30.0)  # Assuming 30 days as baseline
    
    def _calculate_attendance_streaks(self, attendance_history: List) -> Dict[str, int]:
        """Calculate attendance streaks"""
        # This would need business logic to calculate consecutive days
        # For now, return placeholder values
        return {
            'best_streak': 5,  # Placeholder
            'current_streak': 2  # Placeholder
        }
