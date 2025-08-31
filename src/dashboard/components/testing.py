"""
Testing Component
Handles image quality testing and face detection validation
"""

import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image
import io
from pathlib import Path
import time

def show_testing():
    """Show testing suite interface"""
    st.markdown("**Test image quality, face detection, and system performance**")
    
    # Testing tabs
    tab1, tab2, tab3 = st.tabs([
        "📸 Image Quality Testing", 
        "👁️ Face Detection Testing", 
        "⚡ Performance Testing"
    ])
    
    with tab1:
        show_image_quality_testing()
    
    with tab2:
        show_face_detection_testing()
    
    with tab3:
        show_performance_testing()

def show_image_quality_testing():
    """Show image quality testing interface"""
    st.subheader("Image Quality Testing")
    
    # Test image upload
    test_image = st.file_uploader(
        "Upload test image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image to test quality metrics"
    )
    
    if test_image is not None:
        # Load and display image
        image = Image.open(test_image)
        st.image(image, caption="Test Image", use_container_width=True)
        
        # Run quality assessment
        quality_results = run_comprehensive_quality_test(image)
        
        # Display results
        st.subheader("📊 Quality Assessment Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Overall score
            overall_score = quality_results['overall_score']
            st.metric("Overall Quality Score", f"{overall_score:.2f}/1.0")
            
            # Score breakdown
            st.write("**Score Breakdown:**")
            st.write(f"📏 Resolution: {quality_results['resolution_score']:.2f}")
            st.write(f"💡 Brightness: {quality_results['brightness_score']:.2f}")
            st.write(f"🎨 Contrast: {quality_results['contrast_score']:.2f}")
            st.write(f"🔍 Sharpness: {quality_results['sharpness_score']:.2f}")
        
        with col2:
            # Quality indicators
            if overall_score >= 0.8:
                st.success("✅ Excellent Quality")
            elif overall_score >= 0.6:
                st.info("ℹ️ Good Quality")
            elif overall_score >= 0.4:
                st.warning("⚠️ Acceptable Quality")
            else:
                st.error("❌ Poor Quality")
            
            # Recommendations
            st.write("**Recommendations:**")
            recommendations = get_quality_recommendations(quality_results)
            for rec in recommendations:
                st.write(f"💡 {rec}")
        
        # Quality charts
        st.subheader("📈 Quality Metrics Visualization")
        
        # Create quality metrics chart
        metrics_df = pd.DataFrame({
            'Metric': ['Resolution', 'Brightness', 'Contrast', 'Sharpness'],
            'Score': [
                quality_results['resolution_score'],
                quality_results['brightness_score'],
                quality_results['contrast_score'],
                quality_results['sharpness_score']
            ]
        })
        
        import plotly.express as px
        fig = px.bar(
            metrics_df, 
            x='Metric', 
            y='Score',
            title="Quality Metrics Breakdown",
            color='Score',
            color_continuous_scale='viridis'
        )
        fig.update_layout(yaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)

def show_face_detection_testing():
    """Show face detection testing interface"""
    st.subheader("Face Detection Testing")
    
    # Test image upload for face detection
    face_test_image = st.file_uploader(
        "Upload image for face detection test",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image to test face detection capabilities"
    )
    
    if face_test_image is not None:
        # Load image
        image = Image.open(face_test_image)
        st.image(image, caption="Face Detection Test Image", use_container_width=True)
        
        # Run face detection test
        detection_results = run_face_detection_test(image)
        
        # Display results
        st.subheader("👁️ Face Detection Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Detection status
            if detection_results['faces_detected'] > 0:
                st.success(f"✅ {detection_results['faces_detected']} face(s) detected")
            else:
                st.error("❌ No faces detected")
            
            # Detection confidence
            if detection_results['faces_detected'] > 0:
                st.metric("Detection Confidence", f"{detection_results['avg_confidence']:.2f}")
            
            # Processing time
            st.metric("Processing Time", f"{detection_results['processing_time']:.2f} ms")
        
        with col2:
            # Face details
            if detection_results['faces_detected'] > 0:
                st.write("**Face Details:**")
                for i, face in enumerate(detection_results['face_details']):
                    st.write(f"👤 Face {i+1}: {face['bbox']} (Conf: {face['confidence']:.2f})")
        
        # Face detection visualization
        if detection_results['faces_detected'] > 0:
            st.subheader("🎯 Face Detection Visualization")
            
            # Create annotated image
            annotated_image = create_annotated_image(image, detection_results['face_details'])
            st.image(annotated_image, caption="Annotated Image with Face Detection", use_container_width=True)

def show_performance_testing():
    """Show performance testing interface"""
    st.subheader("Performance Testing")
    
    # Performance test options
    col1, col2 = st.columns(2)
    
    with col1:
        test_type = st.selectbox(
            "Test Type",
            ["Image Quality Assessment", "Face Detection", "Full Pipeline", "Custom Test"]
        )
        
        iterations = st.slider("Number of Iterations", 1, 100, 10)
    
    with col2:
        if st.button("🚀 Run Performance Test", key="testing_performance_test_btn"):
            with st.spinner("Running performance test..."):
                performance_results = run_performance_test(test_type, iterations)
                
                # Display results
                st.subheader("📊 Performance Test Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Time", f"{performance_results['total_time']:.2f} s")
                
                with col2:
                    st.metric("Avg Time/Iteration", f"{performance_results['avg_time']:.2f} ms")
                
                with col3:
                    st.metric("Throughput", f"{performance_results['throughput']:.1f} ops/s")
                
                # Performance chart
                if 'timings' in performance_results:
                    st.subheader("📈 Performance Timeline")
                    
                    timings_df = pd.DataFrame({
                        'Iteration': range(1, len(performance_results['timings']) + 1),
                        'Time (ms)': performance_results['timings']
                    })
                    
                    import plotly.express as px
                    fig = px.line(
                        timings_df, 
                        x='Iteration', 
                        y='Time (ms)',
                        title="Performance Over Iterations",
                        markers=True
                    )
                    fig.update_layout(
                        xaxis_title="Iteration",
                        yaxis_title="Processing Time (ms)"
                    )
                    st.plotly_chart(fig, use_container_width=True)

def run_comprehensive_quality_test(image):
    """Run comprehensive image quality assessment"""
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Calculate quality metrics
        height, width = gray.shape
        
        # Resolution score (0-0.3)
        resolution_score = min(1.0, (height * width) / (480 * 480)) * 0.3
        
        # Brightness score (0-0.3)
        mean_brightness = np.mean(gray)
        if 30 <= mean_brightness <= 250:
            brightness_score = 0.3
        else:
            brightness_score = 0.3 * (1 - abs(mean_brightness - 140) / 140)
        brightness_score = max(0, brightness_score)
        
        # Contrast score (0-0.2)
        contrast = np.std(gray)
        contrast_score = min(0.2, contrast / 50 * 0.2)
        
        # Sharpness score (0-0.2)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(0.2, laplacian_var / 500 * 0.2)
        
        # Overall score
        overall_score = resolution_score + brightness_score + contrast_score + sharpness_score
        
        return {
            'overall_score': overall_score,
            'resolution_score': resolution_score / 0.3,  # Normalize to 0-1
            'brightness_score': brightness_score / 0.3,  # Normalize to 0-1
            'contrast_score': contrast_score / 0.2,      # Normalize to 0-1
            'sharpness_score': sharpness_score / 0.2     # Normalize to 0-1
        }
        
    except Exception as e:
        st.error(f"Error in quality test: {e}")
        return {
            'overall_score': 0.0,
            'resolution_score': 0.0,
            'brightness_score': 0.0,
            'contrast_score': 0.0,
            'sharpness_score': 0.0
        }

def get_quality_recommendations(quality_results):
    """Get quality improvement recommendations"""
    recommendations = []
    
    if quality_results['resolution_score'] < 0.7:
        recommendations.append("Increase image resolution (minimum 480x480 recommended)")
    
    if quality_results['brightness_score'] < 0.7:
        recommendations.append("Improve lighting conditions for better brightness")
    
    if quality_results['contrast_score'] < 0.7:
        recommendations.append("Ensure good contrast between face and background")
    
    if quality_results['sharpness_score'] < 0.7:
        recommendations.append("Use a stable camera or tripod for sharper images")
    
    if not recommendations:
        recommendations.append("Image quality is excellent! No improvements needed.")
    
    return recommendations

def run_face_detection_test(image):
    """Run face detection test"""
    try:
        start_time = time.time()
        
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Process results
        face_details = []
        for (x, y, w, h) in faces:
            face_details.append({
                'bbox': f"({x}, {y}, {w}, {h})",
                'confidence': 0.8  # Mock confidence for cascade classifier
            })
        
        return {
            'faces_detected': len(faces),
            'face_details': face_details,
            'avg_confidence': np.mean([f['confidence'] for f in face_details]) if face_details else 0.0,
            'processing_time': processing_time
        }
        
    except Exception as e:
        st.error(f"Error in face detection test: {e}")
        return {
            'faces_detected': 0,
            'face_details': [],
            'avg_confidence': 0.0,
            'processing_time': 0.0
        }

def create_annotated_image(image, face_details):
    """Create annotated image with face detection boxes"""
    try:
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        
        # Draw bounding boxes
        for face in face_details:
            # Parse bbox string "(x, y, w, h)"
            bbox_str = face['bbox'].strip('()').split(',')
            x, y, w, h = map(int, bbox_str)
            
            # Draw rectangle
            cv2.rectangle(img_cv, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add confidence label
            label = f"Conf: {face['confidence']:.2f}"
            cv2.putText(img_cv, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Convert back to PIL
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)
        
    except Exception as e:
        st.error(f"Error creating annotated image: {e}")
        return image

def run_performance_test(test_type, iterations):
    """Run performance test"""
    try:
        start_time = time.time()
        timings = []
        
        # Create test image
        test_image = Image.new('RGB', (640, 480), color='white')
        
        for i in range(iterations):
            iter_start = time.time()
            
            if test_type == "Image Quality Assessment":
                run_comprehensive_quality_test(test_image)
            elif test_type == "Face Detection":
                run_face_detection_test(test_image)
            elif test_type == "Full Pipeline":
                run_comprehensive_quality_test(test_image)
                run_face_detection_test(test_image)
            else:
                # Custom test
                time.sleep(0.001)  # Simulate processing
            
            iter_time = (time.time() - iter_start) * 1000  # Convert to ms
            timings.append(iter_time)
        
        total_time = time.time() - start_time
        avg_time = np.mean(timings)
        throughput = iterations / total_time
        
        return {
            'total_time': total_time,
            'avg_time': avg_time,
            'throughput': throughput,
            'timings': timings
        }
        
    except Exception as e:
        st.error(f"Error in performance test: {e}")
        return {
            'total_time': 0.0,
            'avg_time': 0.0,
            'throughput': 0.0,
            'timings': []
        }

