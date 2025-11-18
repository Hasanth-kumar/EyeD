# Migration Guide: Streamlit to Next.js

## Overview

This guide documents the migration from Streamlit UI to Next.js frontend with REST API backend. The Domain, Application, and Infrastructure layers remain **exactly the same** - only the Presentation Layer changes.

## Architecture Changes

### Before (Streamlit)
```
┌─────────────────────────────────────┐
│  Streamlit UI (Python)              │
│  - Direct use case calls            │
│  - Session state management         │
│  - st.camera_input for camera       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Use Cases (Python)                 │
│  - MarkAttendanceUseCase            │
│  - RegisterUserUseCase              │
└─────────────────────────────────────┘
```

### After (Next.js + REST API)
```
┌─────────────────────────────────────┐
│  Next.js Frontend (TypeScript)      │
│  - React components                 │
│  - WebRTC + Canvas for camera       │
│  - REST API client                  │
└─────────────────────────────────────┘
              ↓ HTTP/REST
┌─────────────────────────────────────┐
│  REST API (FastAPI)                 │
│  - Thin adapter layer               │
│  - DTO conversion                    │
│  - Calls use cases                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Use Cases (Python) - UNCHANGED     │
│  - MarkAttendanceUseCase            │
│  - RegisterUserUseCase              │
└─────────────────────────────────────┘
```

## Step-by-Step Migration

### Phase 1: Archive Legacy Code ✅ COMPLETED

**Status**: Legacy code was archived and has since been removed after successful migration.

**Note**: The archive folder was deleted after the migration to Clean Architecture was completed, as all functionality has been successfully migrated to the new structure.

### Phase 2: Create REST API Layer

1. **Create API directory structure**
   ```
   api/
   ├── __init__.py
   ├── main.py              # FastAPI app
   ├── dependencies.py      # DI setup
   ├── middleware/
   │   ├── __init__.py
   │   ├── cors.py
   │   ├── error_handler.py
   │   └── logging.py
   └── routes/
       ├── __init__.py
       ├── attendance.py
       ├── users.py
       ├── analytics.py
       ├── recognition.py   # Preview endpoints
       └── liveness.py     # Preview endpoints
   ```

2. **Implement FastAPI app** (`api/main.py`)
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from api.routes import attendance, users, analytics
   from api.middleware.error_handler import setup_error_handlers
   
   app = FastAPI(title="EyeD API", version="1.0.0")
   
   # CORS for frontend
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],  # Next.js dev server
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   
   # Error handling
   setup_error_handlers(app)
   
   # Routes
   app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])
   app.include_router(users.router, prefix="/api/users", tags=["users"])
   app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
   ```

3. **Implement route handlers** (`api/routes/attendance.py`)
   ```python
   from fastapi import APIRouter, Depends, HTTPException
   from pydantic import BaseModel
   from use_cases.mark_attendance import MarkAttendanceUseCase, MarkAttendanceRequest
   from api.dependencies import get_mark_attendance_use_case
   
   router = APIRouter()
   
   class MarkAttendanceRequestDTO(BaseModel):
       frames: list[bytes]  # Base64 encoded frames
       landmarks: list[list[list[float]]]
       device_info: str
       location: str
   
   class MarkAttendanceResponseDTO(BaseModel):
       success: bool
       attendance_record: dict | None = None
       error: str | None = None
       stage: str | None = None
   
   @router.post("/mark", response_model=MarkAttendanceResponseDTO)
   async def mark_attendance(
       request: MarkAttendanceRequestDTO,
       use_case: MarkAttendanceUseCase = Depends(get_mark_attendance_use_case)
   ):
       """Mark attendance endpoint."""
       # Convert DTO to use case request
       # (Decode base64 frames, convert to numpy arrays)
       use_case_request = _convert_to_use_case_request(request)
       
       # Call use case (business logic is here)
       response = use_case.execute(use_case_request)
       
       # Convert to DTO
       return MarkAttendanceResponseDTO(
           success=response.success,
           attendance_record=_convert_record_to_dict(response.attendance_record) if response.attendance_record else None,
           error=response.error,
           stage=response.stage
       )
   ```

4. **Add preview endpoints** (`api/routes/recognition.py`)
   ```python
   from fastapi import APIRouter, Depends
   from use_cases.mark_attendance import MarkAttendanceUseCase
   
   router = APIRouter()
   
   @router.post("/preview")
   async def check_recognition_preview(
       frame: bytes,  # Base64 encoded frame
       use_case: MarkAttendanceUseCase = Depends(get_mark_attendance_use_case)
   ):
       """Preview recognition for UI feedback."""
       # Convert frame to numpy array
       frame_array = _decode_frame(frame)
       
       # Call use case preview method
       result = use_case.check_recognition_for_ui(frame_array)
       
       return result
   ```

### Phase 3: Build Next.js Frontend

1. **Initialize Next.js project**
   ```bash
   cd frontend
   npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
   ```

2. **Install dependencies**
   ```bash
   npm install zustand zod react-hook-form @hookform/resolvers
   npm install -D @types/node
   ```

3. **Set up project structure**
   ```
   frontend/
   ├── app/
   │   ├── layout.tsx
   │   ├── page.tsx
   │   └── (dashboard)/
   │       ├── layout.tsx
   │       ├── page.tsx
   │       ├── attendance/
   │       │   └── page.tsx
   │       └── register/
   │           └── page.tsx
   ├── components/
   │   ├── camera/
   │   │   ├── CameraCapture.tsx
   │   │   └── FrameCollector.tsx
   │   └── attendance/
   │       └── MarkAttendanceForm.tsx
   ├── lib/
   │   ├── api/
   │   │   └── client.ts
   │   ├── hooks/
   │   │   └── useCamera.ts
   │   └── schemas/
   │       └── attendance.ts
   └── types/
       └── attendance.ts
   ```

4. **Create API client** (`frontend/lib/api/client.ts`)
   ```typescript
   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
   
   export class ApiClient {
     async markAttendance(request: MarkAttendanceRequest): Promise<MarkAttendanceResponse> {
       const response = await fetch(`${API_BASE_URL}/api/attendance/mark`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(request)
       })
       
       if (!response.ok) {
         throw new ApiError(response.status, await response.text())
       }
       
       return response.json()
     }
     
     async checkRecognitionPreview(frame: Blob): Promise<RecognitionPreviewResponse> {
       const formData = new FormData()
       formData.append('frame', frame)
       
       const response = await fetch(`${API_BASE_URL}/api/recognition/preview`, {
         method: 'POST',
         body: formData
       })
       
       return response.json()
     }
   }
   
   export const apiClient = new ApiClient()
   ```

5. **Create camera hook** (`frontend/lib/hooks/useCamera.ts`)
   ```typescript
   import { useState, useRef, useEffect } from 'react'
   
   export function useCamera() {
     const [stream, setStream] = useState<MediaStream | null>(null)
     const videoRef = useRef<HTMLVideoElement>(null)
     
     const startCamera = async () => {
       try {
         const mediaStream = await navigator.mediaDevices.getUserMedia({
           video: { width: 1280, height: 720 }
         })
         setStream(mediaStream)
         if (videoRef.current) {
           videoRef.current.srcObject = mediaStream
         }
       } catch (error) {
         console.error('Failed to start camera:', error)
         throw error
       }
     }
     
     const stopCamera = () => {
       if (stream) {
         stream.getTracks().forEach(track => track.stop())
         setStream(null)
       }
     }
     
     const captureFrame = (): Blob | null => {
       if (!videoRef.current) return null
       
       const canvas = document.createElement('canvas')
       canvas.width = videoRef.current.videoWidth
       canvas.height = videoRef.current.videoHeight
       const ctx = canvas.getContext('2d')!
       ctx.drawImage(videoRef.current, 0, 0)
       
       return new Promise<Blob>((resolve) => {
         canvas.toBlob((blob) => {
           if (blob) resolve(blob)
         }, 'image/jpeg')
       })
     }
     
     useEffect(() => {
       return () => {
         stopCamera()
       }
     }, [])
     
     return { stream, videoRef, startCamera, stopCamera, captureFrame }
   }
   ```

6. **Create mark attendance page** (`frontend/app/(dashboard)/attendance/page.tsx`)
   ```typescript
   'use client'
   
   import { useState } from 'react'
   import { CameraCapture } from '@/components/camera/CameraCapture'
   import { MarkAttendanceForm } from '@/components/attendance/MarkAttendanceForm'
   import { apiClient } from '@/lib/api/client'
   
   export default function AttendancePage() {
     const [frames, setFrames] = useState<Blob[]>([])
     const [landmarks, setLandmarks] = useState<number[][][]>([])
     
     const handleFramesCollected = (collectedFrames: Blob[], collectedLandmarks: number[][][]) => {
       setFrames(collectedFrames)
       setLandmarks(collectedLandmarks)
     }
     
     const handleSubmit = async (deviceInfo: string, location: string) => {
       // Convert frames to base64
       const framesBase64 = await Promise.all(
         frames.map(frame => 
           new Promise<string>((resolve) => {
             const reader = new FileReader()
             reader.onloadend = () => resolve(reader.result as string)
             reader.readAsDataURL(frame)
           })
         )
       )
       
       // Call API
       const response = await apiClient.markAttendance({
         frames: framesBase64,
         landmarks,
         device_info: deviceInfo,
         location
       })
       
       if (response.success) {
         alert('Attendance marked successfully!')
       } else {
         alert(`Error: ${response.error}`)
       }
     }
     
     return (
       <div>
         <h1>Mark Attendance</h1>
         <CameraCapture onFramesCollected={handleFramesCollected} />
         <MarkAttendanceForm onSubmit={handleSubmit} />
       </div>
     )
   }
   ```

### Phase 4: Migration Checklist

- [x] Archive legacy code (completed, archive later removed after successful migration)
- [ ] Create FastAPI REST API layer
- [ ] Implement all route handlers
- [ ] Add CORS middleware
- [ ] Add error handling middleware
- [ ] Initialize Next.js project
- [ ] Create API client
- [ ] Implement camera capture with WebRTC
- [ ] Build all page components
- [ ] Migrate state management to Zustand
- [ ] Add Zod validation schemas
- [ ] Test end-to-end flow
- [ ] Update documentation

## Key Differences

### State Management

**Streamlit:**
```python
st.session_state['frames'] = []
st.session_state['blink_count'] = 0
```

**Next.js:**
```typescript
const [frames, setFrames] = useState<Blob[]>([])
const [blinkCount, setBlinkCount] = useState(0)
// Or with Zustand:
const { frames, setFrames } = useAttendanceStore()
```

### Camera Capture

**Streamlit:**
```python
camera_image = st.camera_input("Camera")
frame_array = ImageConverter.camera_input_to_numpy(camera_image)
```

**Next.js:**
```typescript
const { stream, videoRef, captureFrame } = useCamera()
// In component:
<video ref={videoRef} autoPlay />
const frame = captureFrame() // Returns Blob
```

### API Calls

**Streamlit:**
```python
use_case = MarkAttendanceUseCase(...)
response = use_case.execute(request)
```

**Next.js:**
```typescript
const response = await apiClient.markAttendance(request)
```

## Testing Migration

1. **Test API endpoints** (Postman/curl)
2. **Test frontend components** (React Testing Library)
3. **Test end-to-end flow** (Playwright/Cypress)
4. **Verify no business logic in frontend**
5. **Verify API is thin adapter only**

## Rollback Plan

If migration fails:
1. ~~Keep Streamlit UI in archive~~ (Archive removed after successful migration)
2. REST API can coexist with Streamlit
3. Gradually migrate pages one by one
4. Keep both UIs running during transition

## Notes

- **Domain, Application, Infrastructure layers remain UNCHANGED**
- **Only Presentation Layer changes**
- **Business logic stays in Python backend**
- **Frontend is presentation-only (TypeScript/React)**
- **API is thin adapter (FastAPI)**

