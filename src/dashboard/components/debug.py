"""
Debug Component
Handles performance metrics, debug logging, and system diagnostics
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import json
from pathlib import Path

def show_debug():
    """Show debug tools and performance monitoring"""
    st.markdown("**System diagnostics, performance metrics, and debug logging**")
    
    # Debug tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Performance Metrics", 
        "📝 Debug Logs", 
        "🔧 System Diagnostics"
    ])
    
    with tab1:
        show_performance_metrics()
    
    with tab2:
        show_debug_logs()
    
    with tab3:
        show_system_diagnostics()

def show_performance_metrics():
    """Show performance metrics and monitoring"""
    st.subheader("Performance Metrics")
    
    # Initialize performance tracking
    if 'performance_metrics' not in st.session_state:
        st.session_state.performance_metrics = []
    
    # Performance overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_operations = len(st.session_state.performance_metrics)
        st.metric("Total Operations", total_operations)
    
    with col2:
        if st.session_state.performance_metrics:
            avg_time = sum(m['processing_time'] for m in st.session_state.performance_metrics) / len(st.session_state.performance_metrics)
            st.metric("Avg Processing Time", f"{avg_time:.2f} ms")
        else:
            st.metric("Avg Processing Time", "N/A")
    
    with col3:
        if st.session_state.performance_metrics:
            max_time = max(m['processing_time'] for m in st.session_state.performance_metrics)
            st.metric("Max Processing Time", f"{max_time:.2f} ms")
        else:
            st.metric("Max Processing Time", "N/A")
    
    with col4:
        if st.session_state.performance_metrics:
            min_time = min(m['processing_time'] for m in st.session_state.performance_metrics)
            st.metric("Min Processing Time", f"{min_time:.2f} ms")
        else:
            st.metric("Min Processing Time", "N/A")
    
    # Performance controls
    st.subheader("Performance Testing")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        test_operation = st.selectbox(
            "Test Operation",
            ["Image Quality Assessment", "Face Detection", "Data Loading", "Chart Generation"]
        )
    
    with col2:
        test_iterations = st.slider("Iterations", 1, 50, 5)
    
    with col3:
        if st.button("🚀 Run Performance Test", key="debug_performance_test_btn"):
            run_performance_benchmark(test_operation, test_iterations)
    
    # Performance charts
    if st.session_state.performance_metrics:
        st.subheader("📈 Performance Trends")
        
        # Convert to dataframe
        df_perf = pd.DataFrame(st.session_state.performance_metrics)
        df_perf['timestamp'] = pd.to_datetime(df_perf['timestamp'])
        
        # Time series chart
        col1, col2 = st.columns(2)
        
        with col1:
            import plotly.express as px
            fig_time = px.line(
                df_perf, 
                x='timestamp', 
                y='processing_time',
                title="Processing Time Over Time",
                markers=True
            )
            fig_time.update_layout(
                xaxis_title="Time",
                yaxis_title="Processing Time (ms)"
            )
            st.plotly_chart(fig_time, use_container_width=True)
        
        with col2:
            # Histogram of processing times
            fig_hist = px.histogram(
                df_perf,
                x='processing_time',
                nbins=20,
                title="Processing Time Distribution",
                color_discrete_sequence=['lightblue']
            )
            fig_hist.update_layout(
                xaxis_title="Processing Time (ms)",
                yaxis_title="Frequency"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Performance by operation type
        if 'operation_type' in df_perf.columns:
            st.subheader("Performance by Operation Type")
            
            op_performance = df_perf.groupby('operation_type')['processing_time'].agg(['mean', 'count', 'std']).reset_index()
            op_performance.columns = ['Operation', 'Avg Time (ms)', 'Count', 'Std Dev']
            
            st.dataframe(op_performance, use_container_width=True)
            
            # Bar chart
            fig_op = px.bar(
                op_performance,
                x='Operation',
                y='Avg Time (ms)',
                title="Average Processing Time by Operation",
                color='Avg Time (ms)',
                color_continuous_scale='viridis'
            )
            fig_op.update_xaxes(tickangle=45)
            st.plotly_chart(fig_op, use_container_width=True)
    
    # Performance actions
    st.subheader("Performance Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Metrics", key="debug_clear_metrics_btn"):
            st.session_state.performance_metrics = []
            st.rerun()
    
    with col2:
        if st.button("📤 Export Metrics", key="debug_export_metrics_btn"):
            export_performance_metrics()
    
    with col3:
        if st.button("🔄 Refresh", key="debug_refresh_btn"):
            st.rerun()

def show_debug_logs():
    """Show debug logging interface"""
    st.subheader("Debug Logs")
    
    # Initialize debug logs
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    
    # Log level filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_level_filter = st.selectbox(
            "Log Level",
            ["All", "INFO", "WARNING", "ERROR", "DEBUG"]
        )
    
    with col2:
        if st.button("📝 Add Test Log", key="debug_add_log_btn"):
            add_test_log_entry()
    
    with col3:
        if st.button("🗑️ Clear Logs", key="debug_clear_logs_btn"):
            st.session_state.debug_logs = []
            st.rerun()
    
    # Add manual log entry
    st.subheader("Add Manual Log Entry")
    
    with st.form("manual_log"):
        col1, col2 = st.columns(2)
        
        with col1:
            manual_level = st.selectbox("Log Level", ["INFO", "WARNING", "ERROR", "DEBUG"])
            manual_message = st.text_area("Log Message", placeholder="Enter log message...")
        
        with col2:
            manual_source = st.text_input("Source", placeholder="Component/module name")
            manual_timestamp = st.text_input("Timestamp", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if st.form_submit_button("Add Log Entry"):
            if manual_message:
                add_log_entry(manual_level, manual_message, manual_source, manual_timestamp)
                st.success("Log entry added!")
                st.rerun()
            else:
                st.error("Please enter a log message")
    
    # Display logs
    st.subheader("Log Entries")
    
    # Filter logs
    filtered_logs = st.session_state.debug_logs
    if log_level_filter != "All":
        filtered_logs = [log for log in st.session_state.debug_logs if log['level'] == log_level_filter]
    
    if filtered_logs:
        # Convert to dataframe for better display
        logs_df = pd.DataFrame(filtered_logs)
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        
        # Sort by timestamp (newest first)
        logs_df = logs_df.sort_values('timestamp', ascending=False)
        
        # Display logs
        for _, log in logs_df.iterrows():
            # Color code by level
            if log['level'] == 'ERROR':
                st.error(f"**{log['timestamp'].strftime('%H:%M:%S')} [{log['level']}] {log['source']}**: {log['message']}")
            elif log['level'] == 'WARNING':
                st.warning(f"**{log['timestamp'].strftime('%H:%M:%S')} [{log['level']}] {log['source']}**: {log['message']}")
            elif log['level'] == 'DEBUG':
                st.info(f"**{log['timestamp'].strftime('%H:%M:%S')} [{log['level']}] {log['source']}**: {log['message']}")
            else:
                st.write(f"**{log['timestamp'].strftime('%H:%M:%S')} [{log['level']}] {log['source']}**: {log['message']}")
        
        # Log statistics
        st.subheader("Log Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_logs = len(filtered_logs)
            st.metric("Total Logs", total_logs)
        
        with col2:
            error_count = len([log for log in filtered_logs if log['level'] == 'ERROR'])
            st.metric("Errors", error_count)
        
        with col3:
            warning_count = len([log for log in filtered_logs if log['level'] == 'WARNING'])
            st.metric("Warnings", warning_count)
        
        # Export logs
        if st.button("📤 Export Logs", key="debug_export_logs_btn"):
            export_debug_logs(filtered_logs)
    
    else:
        st.info("No log entries available. Add some logs to see them here.")

def show_system_diagnostics():
    """Show system diagnostics and health checks"""
    st.subheader("System Diagnostics")
    
    # System health check
    st.subheader("🏥 System Health Check")
    
    health_results = run_system_health_check()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall health
        overall_health = health_results['overall_health']
        if overall_health == 'Healthy':
            st.success(f"✅ Overall System Health: {overall_health}")
        elif overall_health == 'Warning':
            st.warning(f"⚠️ Overall System Health: {overall_health}")
        else:
            st.error(f"❌ Overall System Health: {overall_health}")
        
        # Component health
        st.write("**Component Health:**")
        for component, status in health_results['components'].items():
            if status['status'] == 'Healthy':
                st.write(f"✅ {component}: {status['status']}")
            elif status['status'] == 'Warning':
                st.write(f"⚠️ {component}: {status['status']}")
            else:
                st.write(f"❌ {component}: {status['status']}")
    
    with col2:
        # System metrics
        st.write("**System Metrics:**")
        st.metric("Memory Usage", health_results['memory_usage'])
        st.metric("Disk Space", health_results['disk_space'])
        st.metric("CPU Load", health_results['cpu_load'])
        st.metric("Active Sessions", health_results['active_sessions'])
    
    # Detailed diagnostics
    st.subheader("🔍 Detailed Diagnostics")
    
    # File system check
    st.write("**File System Check:**")
    file_check = check_file_system()
    
    for file_path, status in file_check.items():
        if status['exists']:
            st.success(f"✅ {file_path}: {status['size']}")
        else:
            st.error(f"❌ {file_path}: Missing")
    
    # Database connectivity
    st.write("**Database Connectivity:**")
    db_check = check_database_connectivity()
    
    for db_name, status in db_check.items():
        if status['connected']:
            st.success(f"✅ {db_name}: Connected")
        else:
            st.error(f"❌ {db_name}: Connection Failed - {status['error']}")
    
    # Performance recommendations
    st.subheader("💡 Performance Recommendations")
    
    recommendations = generate_performance_recommendations(health_results)
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

def run_performance_benchmark(operation_type, iterations):
    """Run performance benchmark for specified operation"""
    try:
        for i in range(iterations):
            start_time = time.time()
            
            # Simulate operation
            if operation_type == "Image Quality Assessment":
                time.sleep(0.05)  # Simulate processing
            elif operation_type == "Face Detection":
                time.sleep(0.1)   # Simulate processing
            elif operation_type == "Data Loading":
                time.sleep(0.02)  # Simulate processing
            elif operation_type == "Chart Generation":
                time.sleep(0.03)  # Simulate processing
            
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Add to performance metrics
            metric = {
                'timestamp': datetime.now(),
                'operation_type': operation_type,
                'processing_time': processing_time,
                'iteration': i + 1
            }
            
            st.session_state.performance_metrics.append(metric)
        
        st.success(f"Performance benchmark completed! {iterations} iterations of {operation_type}")
        
    except Exception as e:
        st.error(f"Performance benchmark failed: {e}")

def add_test_log_entry():
    """Add a test log entry"""
    test_messages = [
        "System initialization completed successfully",
        "User authentication successful",
        "Face detection processing started",
        "Database connection established",
        "Image quality assessment completed",
        "Attendance log updated",
        "Performance metrics recorded",
        "Debug mode activated"
    ]
    
    import random
    message = random.choice(test_messages)
    level = random.choice(["INFO", "WARNING", "ERROR", "DEBUG"])
    source = random.choice(["Dashboard", "FaceRecognition", "Database", "Analytics", "Testing"])
    
    add_log_entry(level, message, source, datetime.now())

def add_log_entry(level, message, source, timestamp):
    """Add a log entry to the debug logs"""
    log_entry = {
        'timestamp': timestamp,
        'level': level,
        'message': message,
        'source': source
    }
    
    st.session_state.debug_logs.append(log_entry)

def export_performance_metrics():
    """Export performance metrics to CSV"""
    if st.session_state.performance_metrics:
        df = pd.DataFrame(st.session_state.performance_metrics)
        csv = df.to_csv(index=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_metrics_{timestamp}.csv"
        
        st.download_button(
            label="📥 Download Performance Metrics",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )
        
        st.success(f"Performance metrics exported! {len(df)} entries included.")
    else:
        st.warning("No performance metrics to export.")

def export_debug_logs(logs):
    """Export debug logs to CSV"""
    if logs:
        df = pd.DataFrame(logs)
        csv = df.to_csv(index=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_logs_{timestamp}.csv"
        
        st.download_button(
            label="📥 Download Debug Logs",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )
        
        st.success(f"Debug logs exported! {len(logs)} entries included.")
    else:
        st.warning("No logs to export.")

def run_system_health_check():
    """Run comprehensive system health check"""
    try:
        # Mock health check results
        health_results = {
            'overall_health': 'Healthy',
            'components': {
                'Face Database': {'status': 'Healthy', 'details': 'All systems operational'},
                'Attendance System': {'status': 'Healthy', 'details': 'Processing normally'},
                'Analytics Engine': {'status': 'Healthy', 'details': 'Charts generating correctly'},
                'Image Processing': {'status': 'Healthy', 'details': 'Quality assessment working'}
            },
            'memory_usage': '45%',
            'disk_space': '2.1 GB free',
            'cpu_load': 'Low',
            'active_sessions': '3'
        }
        
        return health_results
        
    except Exception as e:
        return {
            'overall_health': 'Error',
            'components': {},
            'memory_usage': 'Unknown',
            'disk_space': 'Unknown',
            'cpu_load': 'Unknown',
            'active_sessions': 'Unknown'
        }

def check_file_system():
    """Check file system health"""
    try:
        file_check = {}
        
        # Check important files
        important_files = [
            "data/attendance.csv",
            "data/faces/faces.json",
            "src/dashboard/app.py"
        ]
        
        for file_path in important_files:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.1f} MB"
                file_check[file_path] = {'exists': True, 'size': size_str}
            else:
                file_check[file_path] = {'exists': False, 'size': 'N/A'}
        
        return file_check
        
    except Exception as e:
        return {"Error": {'exists': False, 'size': str(e)}}

def check_database_connectivity():
    """Check database connectivity"""
    try:
        # Mock database check
        db_check = {
            'Attendance CSV': {'connected': True, 'error': None},
            'Faces JSON': {'connected': True, 'error': None},
            'Embeddings Cache': {'connected': True, 'error': None}
        }
        
        return db_check
        
    except Exception as e:
        return {"Database": {'connected': False, 'error': str(e)}}

def generate_performance_recommendations(health_results):
    """Generate performance recommendations based on health check"""
    recommendations = []
    
    # Mock recommendations based on health status
    if health_results['overall_health'] == 'Healthy':
        recommendations.append("System is performing well. Continue monitoring for optimal performance.")
        recommendations.append("Consider enabling additional logging for better debugging capabilities.")
    elif health_results['overall_health'] == 'Warning':
        recommendations.append("Monitor system resources more closely.")
        recommendations.append("Consider optimizing image processing algorithms.")
    else:
        recommendations.append("Immediate attention required. Check error logs for details.")
        recommendations.append("Verify all required files and dependencies are present.")
    
    # General recommendations
    recommendations.append("Regular performance monitoring helps identify bottlenecks early.")
    recommendations.append("Keep debug logs enabled for troubleshooting.")
    recommendations.append("Monitor disk space usage to prevent storage issues.")
    
    return recommendations

