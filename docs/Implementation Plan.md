🧩 Modular Implementation Plan – EyeD (AI Attendance System)

(with MediaPipe for liveness detection)

Phase 1: Core Setup & Face Registration

Day 1: Project Setup

Create GitHub repo → add README.md with project idea + plan.

Setup Python virtual environment (venv/).

Install dependencies:

pip install opencv-python mediapipe deepface numpy pandas streamlit plotly


Create folder structure:

EyeD/
├── venv/                  # Virtual environment
├── src/                   # Source code
│   ├── main.py            # Entry point
│   ├── dashboard/         # Streamlit app
│   ├── modules/           # Core AI modules
│   ├── utils/             # Helper functions (db, logger, config)
│   └── tests/             # Unit tests
├── data/                  # User data + attendance logs
│   ├── faces/             # Registered selfies
│   └── attendance.csv
├── demos/                 # Demo videos/screenshots
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
└── README.md              # Project overview


Day 2: Face Registration (Selfie Capture)

Script (src/modules/registration.py) → take webcam snapshot OR allow image upload.

Save selfies → data/faces/.

Extract embeddings (DeepFace MobileNet) → store in data/faces.json or faces.csv.

Test with 2–3 users.

Day 3: Embedding Database

Create src/modules/face_db.py:

register_user(name, image) → stores embedding + metadata.

load_embeddings() → loads stored embeddings into memory.

Verify embeddings load correctly.

Phase 2: Recognition + Liveness

Day 4: Face Recognition (Basic)

Implement recognize_user(frame) in src/modules/recognition.py using DeepFace.

Match with stored embeddings → return name + confidence.

Print results for testing.

Day 5: Live Video Recognition

Capture webcam feed (main.py with OpenCV).

Detect + recognize faces per frame.

Display bounding boxes + names in real-time.

Enhanced Features:
- Multi-stage detection pipeline (OpenCV + MediaPipe fallback)
- Configurable detection parameters
- Real-time confidence scoring display
- Visual feedback for detection quality

Day 6: Blink Detection (MediaPipe)

Use MediaPipe FaceMesh (468 landmarks).

Extract eye landmarks.

Compute EAR (Eye Aspect Ratio) or track openness directly.

Detect blink events → print "Blink detected".

Enhanced Features:
- Face detection fallback using MediaPipe
- Face quality assessment (brightness, contrast, alignment)
- Minimum resolution requirements (480x480)
- Enhanced error handling and logging

Day 7: Liveness Integration

Integrate recognition (recognition.py) + blink detection (liveness.py).

A user is marked Verified Live only if:

✅ Face recognized

✅ Blink detected within session

Enhanced Features:
- Retry logic with different detection parameters
- Multi-stage verification pipeline
- Enhanced logging and debugging
- Performance optimization for real-time processing

Phase 3: Attendance Logging

Day 8: Attendance Logging (CSV)

Create data/attendance.csv with columns:

Name, ID, Date, Time, Status, Confidence, Liveness Verified


Implement log_attendance() in src/utils/database.py → 1 entry per day per user.

Day 9: Confidence & Transparency

Add DeepFace confidence score to log.

Print live confirmation (e.g., ✅ Alice logged at 10:32 AM).

Enhanced Features:
- Comprehensive confidence scoring system
- Detection failure logging and analysis
- Performance metrics and benchmarking
- Quality assessment reporting

Phase 4: Dashboard Development

Day 10: Basic Dashboard Skeleton

Streamlit app in src/dashboard/app.py with sidebar menu:

Dashboard

Attendance Logs

Analytics

Register User

Enhanced Features:
- Enhanced testing suite with various image qualities
- Debug logging and visualization tools
- Performance monitoring dashboard
- Quality assessment tools

Day 11: Attendance Table View

Load data/attendance.csv in dashboard.

Add filters (date, user, status).

Show emoji markers (✅ present, ❌ absent).

Day 12: Analytics View

Use Plotly to visualize:

Attendance % chart

Late arrivals

Weekly/monthly summary

Day 13: User Registration Page

Streamlit form → upload image + name.

Save selfie in data/faces/ + generate embedding.

Update faces.json live.

Day 14: Gamified Features

Add emoji badges:

🏆 100% attendance

🌙 Late comer

Add timeline chart → arrival times per user.

Phase 5: Deployment & Demo

Day 15: Local Demo Video

Run full system → recognition + liveness + logging.

Record screen demo → save in demos/demo.mp4.

Day 16: Streamlit Cloud Deployment

Deploy dashboard (src/dashboard/app.py).

Cloud limitation → allow video upload for demo processing.

Link repo + Streamlit Cloud in README.md.

✅ Final Deliverables (after 16 days)

EyeD Local System: Real-time recognition + MediaPipe liveness check.

Dashboard on Streamlit Cloud: Logs, analytics, registration.

Demo Video: Stored in demos/ for recruiters.

⚡ Key Change vs Old Plan

Dlib → MediaPipe for blink/liveness.

No CMake hassles, runs smoothly on CPU laptops.

Folder structure updated for EyeD instead of ai_attendance.