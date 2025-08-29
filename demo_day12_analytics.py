#!/usr/bin/env python3
"""
Day 12: Analytics View with Advanced Visualizations - Demo Script
Demonstrates enhanced analytics features including:
- Advanced attendance percentage charts
- Enhanced late arrival analysis  
- Weekly/monthly summaries
- Performance insights and recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def generate_demo_data():
    """Generate comprehensive demo data for Day 12 analytics"""
    print("🎯 Generating Demo Data for Day 12 Analytics...")
    
    # Create sample attendance data
    users = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown']
    user_ids = ['U001', 'U002', 'U003', 'U004', 'U005']
    
    attendance_data = []
    
    # Generate data for the last 30 days
    base_date = datetime.now() - timedelta(days=30)
    
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        
        for i, (name, user_id) in enumerate(zip(users, user_ids)):
            # Generate realistic attendance patterns
            if current_date.weekday() < 5:  # Weekdays only
                # Generate random attendance times
                if random.random() > 0.1:  # 90% attendance rate
                    hour = random.randint(8, 10)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    time = current_date.replace(hour=hour, minute=minute, second=second)
                    
                    # Determine status based on time
                    if hour == 8:
                        status = 'Present'
                    elif hour == 9:
                        status = 'Present' if random.random() > 0.4 else 'Late'
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
                    
                    attendance_data.append(attendance_entry)
    
    # Create DataFrame
    df = pd.DataFrame(attendance_data)
    
    # Save to CSV
    df.to_csv('data/attendance_demo_day12.csv', index=False)
    
    print(f"✅ Generated {len(df)} attendance records for {len(users)} users over 30 days")
    print(f"📁 Saved to: data/attendance_demo_day12.csv")
    
    return df

def demonstrate_enhanced_analytics(df):
    """Demonstrate Day 12 enhanced analytics features"""
    print("\n" + "="*80)
    print("🚀 DAY 12: ENHANCED ANALYTICS DEMONSTRATION")
    print("="*80)
    
    # 1. Enhanced Attendance Overview
    print("\n📊 1. ENHANCED ATTENDANCE OVERVIEW")
    print("-" * 50)
    
    # Key metrics
    total_entries = len(df)
    present_count = len(df[df['Status'] == 'Present'])
    late_count = len(df[df['Status'] == 'Late'])
    absent_count = len(df[df['Status'] == 'Absent'])
    
    print(f"📈 Key Metrics:")
    print(f"   • Total Entries: {total_entries}")
    print(f"   • Present: {present_count} ({present_count/total_entries*100:.1f}%)")
    print(f"   • Late: {late_count} ({late_count/total_entries*100:.1f}%)")
    print(f"   • Absent: {absent_count} ({absent_count/total_entries*100:.1f}%)")
    
    # 2. Enhanced Time Analysis
    print("\n⏰ 2. ENHANCED TIME ANALYSIS")
    print("-" * 50)
    
    # Late arrival analysis
    late_data = df[df['Status'] == 'Late'].copy()
    late_data['Hour'] = pd.to_datetime(late_data['Time']).dt.hour
    
    print(f"🚨 Late Arrival Analysis:")
    print(f"   • Total Late Arrivals: {len(late_data)}")
    
    if len(late_data) > 0:
        late_hourly = late_data.groupby('Hour').size().reset_index(name='Count')
        print(f"   • Late Arrivals by Hour:")
        for _, row in late_hourly.iterrows():
            print(f"     - {row['Hour']:02d}:00: {row['Count']} arrivals")
    
    # 3. Enhanced User Performance
    print("\n👥 3. ENHANCED USER PERFORMANCE")
    print("-" * 50)
    
    user_summary = df.groupby('Name').agg({
        'Status': 'count',
        'Confidence': 'mean',
        'Face_Quality_Score': 'mean',
        'Processing_Time_MS': 'mean'
    }).reset_index()
    
    user_summary.columns = ['Name', 'Total_Attendance', 'Avg_Confidence', 'Avg_Quality', 'Avg_Processing_Time']
    
    print(f"👤 User Performance Summary:")
    for _, user in user_summary.iterrows():
        print(f"   • {user['Name']}:")
        print(f"     - Attendance: {user['Total_Attendance']}")
        print(f"     - Avg Confidence: {user['Avg_Confidence']:.3f}")
        print(f"     - Avg Quality: {user['Avg_Quality']:.3f}")
        print(f"     - Avg Processing Time: {user['Avg_Processing_Time']:.1f} ms")
    
    # 4. Enhanced Quality Metrics
    print("\n🔍 4. ENHANCED QUALITY METRICS")
    print("-" * 50)
    
    quality_metrics = {
        'avg_confidence': df['Confidence'].mean(),
        'avg_quality': df['Face_Quality_Score'].mean(),
        'avg_processing_time': df['Processing_Time_MS'].mean(),
        'liveness_success_rate': (df['Liveness_Verified'].sum() / len(df)) * 100,
        'high_confidence_rate': (len(df[df['Confidence'] >= 0.8]) / len(df)) * 100,
        'high_quality_rate': (len(df[df['Face_Quality_Score'] >= 0.7]) / len(df)) * 100
    }
    
    print(f"📊 Quality Metrics:")
    print(f"   • Average Confidence: {quality_metrics['avg_confidence']:.3f}")
    print(f"   • Average Face Quality: {quality_metrics['avg_quality']:.3f}")
    print(f"   • Average Processing Time: {quality_metrics['avg_processing_time']:.1f} ms")
    print(f"   • Liveness Success Rate: {quality_metrics['liveness_success_rate']:.1f}%")
    print(f"   • High Confidence Rate: {quality_metrics['high_confidence_rate']:.1f}%")
    print(f"   • High Quality Rate: {quality_metrics['high_quality_rate']:.1f}%")
    
    # 5. Performance Insights
    print("\n🚀 5. PERFORMANCE INSIGHTS")
    print("-" * 50)
    
    # Session analysis
    total_sessions = df['Session_ID'].nunique()
    print(f"📅 Session Analysis:")
    print(f"   • Total Sessions: {total_sessions}")
    
    # Performance recommendations
    print(f"💡 Performance Recommendations:")
    
    if quality_metrics['avg_processing_time'] > 200:
        print(f"   ⚠️  Average processing time is high ({quality_metrics['avg_processing_time']:.1f} ms)")
        print(f"      Consider optimizing face detection algorithms")
    elif quality_metrics['avg_processing_time'] > 150:
        print(f"   ℹ️  Processing time is moderate ({quality_metrics['avg_processing_time']:.1f} ms)")
        print(f"      Some optimization may be beneficial")
    else:
        print(f"   ✅ Processing time is optimal ({quality_metrics['avg_processing_time']:.1f} ms)")
        print(f"      System is performing well")
    
    if quality_metrics['avg_quality'] < 0.6:
        print(f"   ⚠️  Average face quality is low ({quality_metrics['avg_quality']:.3f})")
        print(f"      Consider improving lighting conditions or camera quality")
    elif quality_metrics['avg_quality'] < 0.7:
        print(f"   ℹ️  Face quality is acceptable but could be improved ({quality_metrics['avg_quality']:.3f})")
    else:
        print(f"   ✅ Face quality is excellent ({quality_metrics['avg_quality']:.3f})")
        print(f"      System is capturing high-quality images")
    
    if quality_metrics['avg_confidence'] < 0.7:
        print(f"   ⚠️  Average confidence is low ({quality_metrics['avg_confidence']:.3f})")
        print(f"      Consider retraining or improving recognition models")
    elif quality_metrics['avg_confidence'] < 0.8:
        print(f"   ℹ️  Confidence is acceptable but could be improved ({quality_metrics['avg_confidence']:.3f})")
    else:
        print(f"   ✅ Confidence is high ({quality_metrics['avg_confidence']:.3f})")
        print(f"      Recognition system is performing well")
    
    # 6. Weekly/Monthly Summary - Day 12 Requirement
    print("\n📅 6. WEEKLY/MONTHLY SUMMARY (Day 12 Requirement)")
    print("-" * 50)
    
    # Add date columns
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week_Number'] = df['Date'].dt.isocalendar().week
    df['Month'] = df['Date'].dt.month_name()
    df['Year'] = df['Date'].dt.year
    
    # Weekly trends
    weekly_data = df.groupby(['Week_Number', 'Status']).size().reset_index(name='Count')
    weekly_pivot = weekly_data.pivot(index='Week_Number', columns='Status', values='Count').fillna(0)
    
    if 'Total' not in weekly_pivot.columns:
        weekly_pivot['Total'] = weekly_pivot.sum(axis=1)
    
    if 'Present' in weekly_pivot.columns:
        weekly_pivot['Present_Pct'] = (weekly_pivot['Present'] / weekly_pivot['Total'] * 100).round(1)
    
    if 'Late' in weekly_pivot.columns:
        weekly_pivot['Late_Pct'] = (weekly_pivot['Late'] / weekly_pivot['Total'] * 100).round(1)
    
    print(f"📊 Weekly Trends:")
    for week in weekly_pivot.index:
        print(f"   • Week {week}:")
        if 'Present' in weekly_pivot.columns:
            print(f"     - Present: {weekly_pivot.loc[week, 'Present']} ({weekly_pivot.loc[week, 'Present_Pct']:.1f}%)")
        if 'Late' in weekly_pivot.columns:
            print(f"     - Late: {weekly_pivot.loc[week, 'Late']} ({weekly_pivot.loc[week, 'Late_Pct']:.1f}%)")
        print(f"     - Total: {weekly_pivot.loc[week, 'Total']}")
    
    # Monthly summary
    monthly_summary = df.groupby(['Year', 'Month']).agg({
        'Status': 'count'
    }).reset_index()
    
    monthly_summary.columns = ['Year', 'Month', 'Total_Attendance']
    
    print(f"📅 Monthly Summary:")
    for _, month in monthly_summary.iterrows():
        print(f"   • {month['Month']} {month['Year']}: {month['Total_Attendance']} entries")
    
    # 7. Data Export Capabilities
    print("\n📤 7. DATA EXPORT CAPABILITIES")
    print("-" * 50)
    
    # Create export directory
    export_dir = 'data/exports'
    os.makedirs(export_dir, exist_ok=True)
    
    # Export user summary
    user_export = user_summary.copy()
    user_export['Present_Percentage'] = (user_export['Total_Attendance'] / user_export['Total_Attendance'] * 100).round(1)
    
    export_file = os.path.join(export_dir, 'user_performance_summary.csv')
    user_export.to_csv(export_file, index=False)
    print(f"✅ Exported user performance summary to: {export_file}")
    
    # Export weekly trends
    weekly_export = weekly_pivot.reset_index()
    export_file = os.path.join(export_dir, 'weekly_trends.csv')
    weekly_export.to_csv(export_file, index=False)
    print(f"✅ Exported weekly trends to: {export_file}")
    
    # Export monthly summary
    export_file = os.path.join(export_dir, 'monthly_summary.csv')
    monthly_summary.to_csv(export_file, index=False)
    print(f"✅ Exported monthly summary to: {export_file}")

def run_dashboard_demo():
    """Instructions for running the Streamlit dashboard"""
    print("\n" + "="*80)
    print("🎯 STREAMLIT DASHBOARD DEMO INSTRUCTIONS")
    print("="*80)
    
    print("""
🚀 To see the enhanced Day 12 analytics in action:

1. Launch the Streamlit dashboard:
   streamlit run src/dashboard/app.py

2. Navigate to the "Analytics & Insights" tab

3. Explore the enhanced features:
   📊 Attendance Overview - Advanced percentage charts
   ⏰ Time Analysis - Enhanced late arrival analysis
   👥 User Performance - User performance insights
   🔍 Quality Metrics - Advanced quality analysis
   🚀 Performance Insights - System performance & recommendations

4. Key Day 12 Enhancements:
   • Attendance percentage charts with trends
   • Enhanced late arrival analysis by hour and user
   • Weekly trends with percentage breakdowns
   • Monthly performance summaries
   • Performance insights and recommendations
   • Advanced quality metrics correlation
   • Data export capabilities

5. Interactive Features:
   • Hover over charts for detailed information
   • Filter data by date ranges
   • Export data in multiple formats
   • Performance recommendations based on metrics

🎉 The enhanced analytics provide comprehensive insights into:
   • Attendance patterns and trends
   • User performance and behavior
   • System quality and performance
   • Late arrival patterns and causes
   • Quality vs. confidence correlations
   • Performance optimization recommendations
""")

def main():
    """Main demo function"""
    print("🎯 EyeD - Day 12 Analytics Enhancement Demo")
    print("=" * 60)
    
    # Check if demo data exists, create if not
    demo_file = 'data/attendance_demo_day12.csv'
    if os.path.exists(demo_file):
        print(f"📁 Using existing demo data: {demo_file}")
        df = pd.read_csv(demo_file)
    else:
        print("📁 Creating new demo data...")
        df = generate_demo_data()
    
    # Demonstrate enhanced analytics
    demonstrate_enhanced_analytics(df)
    
    # Show dashboard demo instructions
    run_dashboard_demo()
    
    print("\n" + "="*80)
    print("✅ Day 12 Analytics Demo Complete!")
    print("="*80)
    print("🎯 Next Steps:")
    print("   1. Run the Streamlit dashboard to see interactive charts")
    print("   2. Explore the enhanced analytics features")
    print("   3. Test data export and filtering capabilities")
    print("   4. Review performance recommendations")
    print("\n🚀 Ready for Day 13: User Registration Page!")

if __name__ == '__main__':
    main()
