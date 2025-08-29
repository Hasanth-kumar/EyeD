# 👁️ EyeD - AI Attendance System with Liveness Detection

A modern, AI-powered attendance system that uses facial recognition and MediaPipe-based liveness detection to ensure authentic user verification.

## 🚀 Features

- **Facial Recognition**: Deep learning-based face identification using DeepFace VGG-Face
- **Multi-stage Detection**: OpenCV + MediaPipe fallback for robust face detection
- **Real-time Processing**: Live webcam feed with instant recognition and confidence scoring
- **Attendance Logging**: Automated CSV-based attendance tracking with confidence metrics
- **Modern Dashboard**: Streamlit-powered web interface with analytics and monitoring
- **User Registration**: Simple selfie-based user onboarding with quality validation
- **Enhanced Security**: Liveness detection and multi-parameter verification

## 🛠️ Technology Stack

- **AI/ML**: DeepFace, MediaPipe, TensorFlow
- **Computer Vision**: OpenCV
- **Web Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Language**: Python 3.11+

## 📁 Project Structure

```
EyeD/
├── src/                   # Source code
│   ├── main.py           # Entry point
│   ├── dashboard/        # Streamlit app
│   ├── modules/          # Core AI modules
│   ├── utils/            # Helper functions
│   └── tests/            # Unit tests
├── data/                 # User data + attendance logs
│   ├── faces/            # Registered selfies
│   └── attendance.csv    # Attendance records
├── demos/                # Demo videos/screenshots
├── docs/                 # Documentation
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Webcam access
- Windows 10/11 (tested)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd EyeD
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test installation**
   ```bash
   python test_dependencies.py
   ```

### Usage

1. **Start webcam mode** (face recognition)
   ```bash
   python main.py --mode webcam
   ```

2. **Launch dashboard**
   ```bash
   python main.py --mode dashboard
   ```

3. **User registration**
   ```bash
   python main.py --mode register
   ```

4. **Live video recognition** (Day 5)
   ```bash
   python main.py --mode webcam
   ```

## 📅 Implementation Timeline

### Phase 1: Core Setup & Face Registration (Days 1-4) ✅ **COMPLETED**
- ✅ **Day 1**: Project Setup - **COMPLETED**
- ✅ **Day 2**: Face Registration (Selfie Capture) - **COMPLETED**
- ✅ **Day 3**: Embedding Database - **COMPLETED**
- ✅ **Day 4**: Face Recognition (Basic) - **COMPLETED**

### Phase 2: Recognition + Liveness (Days 5-7) 🔄 **IN PROGRESS**
- ✅ **Day 5**: Live Video Recognition (Enhanced) - **COMPLETED**
- ✅ **Day 6**: Blink Detection (MediaPipe + Face Quality) - **COMPLETED** 🆕
- ⏳ **Day 7**: Liveness Integration (Multi-stage Pipeline)

### Phase 3: Attendance Logging (Days 8-9) ⏳ **PLANNED**
- ⏳ **Day 8**: Attendance Logging (CSV)
- ⏳ **Day 9**: Confidence & Transparency (Enhanced)

### Phase 4: Dashboard Development (Days 10-14) ⏳ **PLANNED**
- ⏳ **Day 10**: Basic Dashboard Skeleton (Enhanced)
- ⏳ **Day 11**: Attendance Table View
- ⏳ **Day 12**: Analytics View
- ⏳ **Day 13**: User Registration Page
- ⏳ **Day 14**: Gamified Features

### Phase 5: Deployment & Demo (Days 15-16) ⏳ **PLANNED**
- ⏳ **Day 15**: Local Demo Video
- ⏳ **Day 16**: Streamlit Cloud Deployment

## 🎯 **Current Status: 37.5% Complete (6/16 Days)**

### ✅ **What's Working Now:**
- **Complete face registration system** with webcam and image upload
- **Robust face database** with efficient embedding storage
- **Advanced face recognition** with confidence scoring
- **Live video recognition** with real-time webcam processing
- **Multi-stage detection pipeline** (MediaPipe + OpenCV fallback)
- **Comprehensive testing suite** (16 tests passing)
- **Performance optimized** (sub-millisecond comparisons)
- **Advanced liveness detection** with blink detection and face quality assessment 🆕
- **Enhanced face mesh visualization** and debugging capabilities 🆕
- **Configurable parameters** for runtime optimization 🆕
- **Face alignment assessment** and quality grading 🆕

### 🚀 **Enhanced Features Implemented:**
- **Multi-stage detection pipeline** (MediaPipe primary + OpenCV fallback)
- **Configurable confidence thresholds**
- **Real-time performance monitoring** (FPS display)
- **Live video recognition** with visual overlays
- **Robust error handling and logging**
- **Database integrity verification**
- **Interactive webcam controls** (save, reload, quit)
- **Advanced liveness detection** with MediaPipe FaceMesh 🆕
- **Eye Aspect Ratio (EAR) calculation** for blink detection 🆕
- **Comprehensive face quality assessment** (resolution, brightness, contrast, sharpness) 🆕
- **Face mesh visualization** and eye landmark highlighting 🆕
- **Runtime configuration management** system 🆕
- **Face alignment assessment** (symmetry, pose, centering) 🆕
- **Advanced quality algorithms** (lighting analysis, exposure detection) 🆕
- **Quality grading system** (A+ to F scale) 🆕

### Phase 3: Attendance Logging (Days 8-9)
- ⏳ **Day 8**: Attendance Logging (CSV)
- ⏳ **Day 9**: Confidence & Transparency

### Phase 4: Dashboard Development (Days 10-14)
- ⏳ **Day 10**: Basic Dashboard Skeleton
- ⏳ **Day 11**: Attendance Table View
- ⏳ **Day 12**: Analytics View
- ⏳ **Day 13**: User Registration Page
- ⏳ **Day 14**: Gamified Features

### Phase 5: Deployment & Demo (Days 15-16)
- ⏳ **Day 15**: Local Demo Video
- ⏳ **Day 16**: Streamlit Cloud Deployment

## 🔧 Development

### Running Tests
```bash
# Test dependencies
python test_dependencies.py

# Test Day 5 functionality
python src/tests/test_day5_live_video.py

# Test Day 6 functionality
python src/tests/test_day6_blink_detection.py

# Run main application with liveness testing
python main.py
```

### Project Status
- **Current Day**: 6
- **Phase**: Recognition + Liveness
- **Next Milestone**: Liveness Integration (Day 7)

## 📊 Demo & Results

*Coming soon after Day 15*

## 🤝 Contributing

This is a learning project. Feel free to fork and experiment!

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- MediaPipe team for liveness detection
- DeepFace for facial recognition
- Streamlit for the web framework
- OpenCV community for computer vision tools

---

**👁️ EyeD** - Making attendance smart, secure, and simple! 🚀
