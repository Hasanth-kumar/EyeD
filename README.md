# 👁️ EyeD - AI Attendance System with Liveness Detection

A modern, AI-powered attendance system that uses facial recognition and MediaPipe-based liveness detection to ensure authentic user verification.

## 🚀 Features

- **Facial Recognition**: Deep learning-based face identification using DeepFace
- **Liveness Detection**: MediaPipe-powered blink detection to prevent spoofing
- **Real-time Processing**: Live webcam feed with instant recognition
- **Attendance Logging**: Automated CSV-based attendance tracking
- **Modern Dashboard**: Streamlit-powered web interface with analytics
- **User Registration**: Simple selfie-based user onboarding

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

## 📅 Implementation Timeline

### Phase 1: Core Setup & Face Registration (Days 1-3)
- ✅ **Day 1**: Project Setup (Current)
- 🔄 **Day 2**: Face Registration (Selfie Capture)
- ⏳ **Day 3**: Embedding Database

### Phase 2: Recognition + Liveness (Days 4-7)
- ⏳ **Day 4**: Face Recognition (Basic)
- ⏳ **Day 5**: Live Video Recognition
- ⏳ **Day 6**: Blink Detection (MediaPipe)
- ⏳ **Day 7**: Liveness Integration

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
python test_dependencies.py
```

### Project Status
- **Current Day**: 1
- **Phase**: Core Setup & Face Registration
- **Next Milestone**: Face Registration (Day 2)

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
