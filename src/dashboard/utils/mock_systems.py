"""
Mock Systems for Dashboard Testing and Demonstration
Provides mock implementations of core systems for testing without real backend dependencies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class MockFaceDatabase:
    """Mock face database for demonstration purposes"""
    
    def __init__(self):
        self.users_db = {
            'U001': {'name': 'Alice Johnson', 'embeddings': [np.random.rand(4096) for _ in range(3)]},
            'U002': {'name': 'Bob Smith', 'embeddings': [np.random.rand(4096) for _ in range(3)]},
            'U003': {'name': 'Carol Davis', 'embeddings': [np.random.rand(4096) for _ in range(3)]},
            'U004': {'name': 'David Wilson', 'embeddings': [np.random.rand(4096) for _ in range(3)]},
            'U005': {'name': 'Eva Brown', 'embeddings': [np.random.rand(4096) for _ in range(3)]}
        }
    
    def get_all_users(self):
        """Get all registered users"""
        return [data['name'] for data in self.users_db.values()]
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        if user_id in self.users_db:
            return self.users_db[user_id]['name']
        return None
    
    def get_user_embeddings(self, user_id):
        """Get embeddings for a specific user"""
        if user_id in self.users_db:
            return self.users_db[user_id]['embeddings']
        return []
    
    def get_user_count(self):
        """Get total user count"""
        return len(self.users_db)
    
    def add_user(self, name, user_id, embeddings):
        """Add a new user"""
        self.users_db[user_id] = {'name': name, 'embeddings': embeddings}
    
    def remove_user(self, user_id):
        """Remove a user"""
        if user_id in self.users_db:
            del self.users_db[user_id]
            return True
        return False
    
    def get_user_data(self, user_id):
        """Get complete user data by ID"""
        if user_id in self.users_db:
            return self.users_db[user_id]
        return None
    
    def update_user(self, user_id, updates):
        """Update user information"""
        if user_id in self.users_db:
            self.users_db[user_id].update(updates)
            return True
        return False
    
    def search_users(self, query):
        """Search users by name or ID"""
        results = []
        query_lower = query.lower()
        
        for user_id, data in self.users_db.items():
            if (query_lower in user_id.lower() or 
                query_lower in data['name'].lower()):
                results.append((user_id, data))
        
        return results
    
    def get_user_statistics(self):
        """Get user database statistics"""
        return {
            'total_users': len(self.users_db),
            'users_with_embeddings': len([u for u in self.users_db.values() if u.get('embeddings')]),
            'last_updated': datetime.now().isoformat()
        }

class MockAttendanceManager:
    """Mock attendance manager for demonstration purposes"""
    
    def __init__(self):
        self.attendance_data = []
        self.session_counter = 0
        self.generate_sample_data()
    
    def generate_sample_data(self):
        """Generate sample attendance data"""
        users = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown']
        user_ids = ['U001', 'U002', 'U003', 'U004', 'U005']
        
        # Generate data for the last 8 days
        base_date = datetime.now() - timedelta(days=8)
        
        for day in range(8):
            current_date = base_date + timedelta(days=day)
            
            for i, (name, user_id) in enumerate(zip(users, user_ids)):
                # Generate random attendance times
                hour = random.randint(8, 10)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                time = current_date.replace(hour=hour, minute=minute, second=second)
                
                # Determine status based on time
                if hour == 8:
                    status = 'Present'
                elif hour == 9:
                    status = 'Present' if random.random() > 0.3 else 'Late'
                else:
                    status = 'Late'
                
                # Generate quality metrics
                confidence = round(random.uniform(0.7, 0.95), 3)
                face_quality = round(random.uniform(0.6, 0.9), 3)
                processing_time = round(random.uniform(50, 200), 1)
                liveness_verified = random.random() > 0.1  # 90% success rate
                
                # Create session ID
                session_id = f"S{day:03d}_{user_id}"
                
                attendance_entry = {
                    'Name': name,
                    'ID': user_id,
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Time': time.strftime('%H:%M:%S'),
                    'Status': status,
                    'Confidence': confidence,
                    'Liveness_Verified': liveness_verified,
                    'Face_Quality_Score': face_quality,
                    'Processing_Time_MS': processing_time,
                    'Verification_Stage': 'Completed',
                    'Session_ID': session_id,
                    'Device_Info': 'Demo System',
                    'Location': 'Demo Office'
                }
                
                self.attendance_data.append(attendance_entry)
    
    def get_attendance_data(self, start_date=None, end_date=None, user_name=None):
        """Get attendance data with optional filtering"""
        df = pd.DataFrame(self.attendance_data)
        
        if start_date:
            df = df[df['Date'] >= start_date]
        if end_date:
            df = df[df['Date'] <= end_date]
        if user_name:
            df = df[df['Name'] == user_name]
        
        return df
    
    def get_attendance_summary(self):
        """Get attendance summary statistics"""
        df = pd.DataFrame(self.attendance_data)
        
        total_entries = len(df)
        present_count = len(df[df['Status'] == 'Present'])
        late_count = len(df[df['Status'] == 'Late'])
        absent_count = len(df[df['Status'] == 'Absent'])
        
        return {
            'total_entries': total_entries,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'present_percentage': round((present_count / total_entries) * 100, 1) if total_entries > 0 else 0,
            'late_percentage': round((late_count / total_entries) * 100, 1) if total_entries > 0 else 0,
            'absent_percentage': round((absent_count / total_entries) * 100, 1) if total_entries > 0 else 0
        }
    
    def get_user_performance(self, user_name):
        """Get performance metrics for a specific user"""
        df = pd.DataFrame(self.attendance_data)
        user_data = df[df['Name'] == user_name]
        
        if len(user_data) == 0:
            return None
        
        total_attendance = len(user_data)
        present_count = len(user_data[user_data['Status'] == 'Present'])
        late_count = len(user_data[user_data['Status'] == 'Late'])
        absent_count = len(user_data[user_data['Status'] == 'Absent'])
        
        avg_confidence = user_data['Confidence'].mean()
        avg_quality = user_data['Face_Quality_Score'].mean()
        avg_processing_time = user_data['Processing_Time_MS'].mean()
        
        return {
            'user_name': user_name,
            'total_attendance': total_attendance,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'present_percentage': round((present_count / total_attendance) * 100, 1),
            'late_percentage': round((late_count / total_attendance) * 100, 1),
            'absent_percentage': round((absent_count / total_attendance) * 100, 1),
            'avg_confidence': round(avg_confidence, 3),
            'avg_quality': round(avg_quality, 3),
            'avg_processing_time': round(avg_processing_time, 1)
        }
    
    def get_daily_trends(self, days=7):
        """Get daily attendance trends"""
        df = pd.DataFrame(self.attendance_data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Get last N days
        end_date = df['Date'].max()
        start_date = end_date - timedelta(days=days-1)
        
        daily_data = df[df['Date'] >= start_date].groupby('Date').agg({
            'Status': 'count',
            'Confidence': 'mean',
            'Face_Quality_Score': 'mean',
            'Processing_Time_MS': 'mean'
        }).reset_index()
        
        daily_data.columns = ['Date', 'Attendance_Count', 'Avg_Confidence', 'Avg_Quality', 'Avg_Processing_Time']
        
        return daily_data
    
    def get_quality_metrics(self):
        """Get overall quality metrics"""
        df = pd.DataFrame(self.attendance_data)
        
        return {
            'avg_confidence': round(df['Confidence'].mean(), 3),
            'avg_quality': round(df['Face_Quality_Score'].mean(), 3),
            'avg_processing_time': round(df['Processing_Time_MS'].mean(), 1),
            'liveness_success_rate': round((df['Liveness_Verified'].sum() / len(df)) * 100, 1),
            'high_confidence_rate': round((len(df[df['Confidence'] >= 0.8]) / len(df)) * 100, 1),
            'high_quality_rate': round((len(df[df['Face_Quality_Score'] >= 0.7]) / len(df)) * 100, 1)
        }
    
    def export_data(self, format='csv', filename=None):
        """Export attendance data"""
        df = pd.DataFrame(self.attendance_data)
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'attendance_export_{timestamp}.{format}'
        
        if format.lower() == 'csv':
            df.to_csv(filename, index=False)
        elif format.lower() == 'json':
            df.to_json(filename, orient='records', indent=2)
        elif format.lower() == 'excel':
            df.to_excel(filename, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return filename
    
    def reset_data(self):
        """Reset to sample data"""
        self.attendance_data = []
        self.generate_sample_data()
    
    def add_attendance_entry(self, entry):
        """Add a new attendance entry"""
        self.attendance_data.append(entry)
    
    def get_session_count(self):
        """Get total session count"""
        df = pd.DataFrame(self.attendance_data)
        return df['Session_ID'].nunique()
    
    def get_today_attendance_count(self):
        """Get today's attendance count"""
        today = datetime.now().strftime('%Y-%m-%d')
        df = pd.DataFrame(self.attendance_data)
        today_data = df[df['Date'] == today]
        return len(today_data)
