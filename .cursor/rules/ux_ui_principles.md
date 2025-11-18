# UI/UX Principles - Next.js Frontend

## Overview
This document defines clean UI/UX patterns for the Next.js frontend application. All UI components must follow Clean Architecture principles with strict separation between presentation and business logic.

## Core Principles

### 1. Separation of Concerns
- **UI Components**: Only handle presentation and user interaction
- **Business Logic**: Lives in use cases/services (NOT in frontend)
- **Data Access**: Through REST API only (NOT direct repository access)
- **State Management**: UI state only (filters, selections, form state)

### 2. Component Structure
Each React component should:
- Be **self-contained** and **reusable**
- Accept **data** as props (not fetch it)
- Handle **user interactions** only
- Delegate **business operations** to API calls
- Use **TypeScript** for type safety

### 3. State Management
- **Zustand stores**: For UI state only (filters, selections, form state)
- **React state**: For component-local UI state
- **NO business state**: Business state lives in backend (domain/services)
- **Server state**: Fetch from API, cache with React Query (optional)

## Component Patterns

### Standard Component Structure

**✅ CORRECT:**
```typescript
// frontend/components/attendance/AttendanceTable.tsx
'use client'

import { AttendanceRecord } from '@/types/attendance'
import { Table } from '@/components/ui/table'

interface AttendanceTableProps {
  records: AttendanceRecord[]
  filters?: AttendanceFilters
  onFilterChange?: (filters: AttendanceFilters) => void
}

export function AttendanceTable({ 
  records, 
  filters, 
  onFilterChange 
}: AttendanceTableProps) {
  if (records.length === 0) {
    return <div>No attendance records found.</div>
  }
  
  // Apply filters if provided (UI filtering only, not business logic)
  const filteredRecords = filters 
    ? applyUIFilters(records, filters)
    : records
  
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Date</TableHead>
          <TableHead>Time</TableHead>
          <TableHead>User</TableHead>
          <TableHead>Confidence</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {filteredRecords.map((record) => (
          <TableRow key={record.id}>
            <TableCell>{formatDate(record.date)}</TableCell>
            <TableCell>{formatTime(record.time)}</TableCell>
            <TableCell>{record.user_name}</TableCell>
            <TableCell>{(record.confidence * 100).toFixed(1)}%</TableCell>
            <TableCell>{record.status}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

// UI-only filtering (not business logic)
function applyUIFilters(
  records: AttendanceRecord[],
  filters: AttendanceFilters
): AttendanceRecord[] {
  return records.filter(record => {
    if (filters.startDate && record.date < filters.startDate) return false
    if (filters.endDate && record.date > filters.endDate) return false
    if (filters.minConfidence && record.confidence < filters.minConfidence) return false
    return true
  })
}
```

**❌ WRONG:**
```typescript
// ❌ Component doing business logic and data access
export function AttendanceTable() {
  // ❌ Direct API access in component
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  
  useEffect(() => {
    // ❌ Business logic in component
    fetch('/api/attendance')
      .then(res => res.json())
      .then(data => {
        // ❌ Business rule in UI!
        const filtered = data.filter(r => r.confidence > 0.6)
        setRecords(filtered)
      })
  }, [])
  
  return <Table>{/* ... */}</Table>
}
```

### Component Communication

**✅ CORRECT:**
```typescript
// frontend/app/(dashboard)/attendance/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { AttendanceTable } from '@/components/attendance/AttendanceTable'
import { AttendanceFilters } from '@/components/attendance/AttendanceFilters'
import { apiClient } from '@/lib/api/client'
import { AttendanceRecord } from '@/types/attendance'

export default function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [filters, setFilters] = useState<AttendanceFilters>({})
  const [isLoading, setIsLoading] = useState(false)
  
  useEffect(() => {
    const fetchRecords = async () => {
      setIsLoading(true)
      try {
        // Call API - business logic is in backend
        const data = await apiClient.getAttendanceRecords(filters)
        setRecords(data)
      } catch (error) {
        console.error('Failed to fetch records:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchRecords()
  }, [filters])
  
  return (
    <div>
      <h1>Attendance Management</h1>
      <AttendanceFilters 
        filters={filters}
        onFiltersChange={setFilters}
      />
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <AttendanceTable records={records} filters={filters} />
      )}
    </div>
  )
}
```

## Page Organization

### Page Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (dashboard)/             # Route group
│   │   ├── layout.tsx           # Dashboard layout
│   │   ├── page.tsx             # Dashboard overview
│   │   ├── attendance/
│   │   │   └── page.tsx        # Attendance page
│   │   ├── analytics/
│   │   │   └── page.tsx        # Analytics page
│   │   └── register/
│   │       └── page.tsx        # Registration page
├── components/                  # React components
│   ├── attendance/
│   │   ├── AttendanceTable.tsx
│   │   ├── AttendanceFilters.tsx
│   │   └── MarkAttendanceForm.tsx
│   ├── camera/
│   │   ├── CameraCapture.tsx
│   │   └── FrameCollector.tsx
│   └── layout/
│       ├── Sidebar.tsx
│       └── Header.tsx
└── lib/                         # Utilities
    ├── api/                     # API client
    ├── hooks/                   # Custom hooks
    └── schemas/                 # Zod schemas
```

### Page Pattern

**✅ CORRECT:**
```typescript
// frontend/app/(dashboard)/attendance/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { AttendanceTable } from '@/components/attendance/AttendanceTable'
import { AttendanceFilters } from '@/components/attendance/AttendanceFilters'
import { apiClient } from '@/lib/api/client'
import { AttendanceRecord } from '@/types/attendance'

export default function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [filters, setFilters] = useState<AttendanceFilters>({})
  
  useEffect(() => {
    const loadRecords = async () => {
      try {
        // API call - business logic in backend
        const data = await apiClient.getAttendanceRecords(filters)
        setRecords(data)
      } catch (error) {
        // Handle error (UI only)
        console.error('Failed to load records:', error)
      }
    }
    
    loadRecords()
  }, [filters])
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Attendance Management</h1>
      
      <AttendanceFilters 
        filters={filters}
        onFiltersChange={setFilters}
      />
      
      <AttendanceTable records={records} />
    </div>
  )
}
```

## User Interaction Patterns

### Form Handling

**✅ CORRECT:**
```typescript
// frontend/components/attendance/MarkAttendanceForm.tsx
'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { markAttendanceSchema } from '@/lib/schemas/attendance'
import { apiClient } from '@/lib/api/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface MarkAttendanceFormData {
  device_info: string
  location: string
  frames: Blob[]
  landmarks: number[][]
}

export function MarkAttendanceForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const { register, handleSubmit, formState: { errors } } = useForm<MarkAttendanceFormData>({
    resolver: zodResolver(markAttendanceSchema)
  })
  
  const onSubmit = async (data: MarkAttendanceFormData) => {
    setIsSubmitting(true)
    setError(null)
    
    try {
      // Validate input (Zod schema - UI validation only)
      const validated = markAttendanceSchema.parse(data)
      
      // Call API - business logic is in backend
      const response = await apiClient.markAttendance(validated)
      
      if (response.success) {
        // Success - show message (UI only)
        alert('Attendance marked successfully!')
      } else {
        setError(response.error || 'Failed to mark attendance')
      }
    } catch (err) {
      // Handle error (UI only)
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred')
      }
    } finally {
      setIsSubmitting(false)
    }
  }
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input
        {...register('device_info')}
        placeholder="Device Information"
        error={errors.device_info?.message}
      />
      
      <Input
        {...register('location')}
        placeholder="Location"
        error={errors.location?.message}
      />
      
      {error && <div className="text-red-500">{error}</div>}
      
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Mark Attendance'}
      </Button>
    </form>
  )
}
```

### Camera Capture Pattern

**✅ CORRECT:**
```typescript
// frontend/components/camera/CameraCapture.tsx
'use client'

import { useEffect, useRef, useState } from 'react'
import { useCamera } from '@/lib/hooks/useCamera'
import { Button } from '@/components/ui/button'

export function CameraCapture() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { stream, startCamera, stopCamera, captureFrame } = useCamera()
  const [frames, setFrames] = useState<Blob[]>([])
  const [isCollecting, setIsCollecting] = useState(false)
  
  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream
    }
    
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])
  
  const handleStartCollection = async () => {
    await startCamera()
    setIsCollecting(true)
    
    // Collect frames at intervals (UI logic only)
    const interval = setInterval(() => {
      if (videoRef.current && canvasRef.current) {
        const frame = captureFrame(videoRef.current)
        setFrames(prev => [...prev, frame])
      }
    }, 1000) // 1 frame per second
    
    // Stop after 30 seconds
    setTimeout(() => {
      clearInterval(interval)
      setIsCollecting(false)
      stopCamera()
    }, 30000)
  }
  
  return (
    <div>
      <video ref={videoRef} autoPlay playsInline />
      <canvas ref={canvasRef} className="hidden" />
      
      <Button 
        onClick={handleStartCollection}
        disabled={isCollecting}
      >
        {isCollecting ? 'Collecting...' : 'Start Camera'}
      </Button>
      
      <div>Frames collected: {frames.length}</div>
    </div>
  )
}
```

### Error Handling

**✅ CORRECT:**
```typescript
export function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  useEffect(() => {
    const loadRecords = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        const data = await apiClient.getAttendanceRecords()
        setRecords(data)
      } catch (err) {
        // Handle different error types (UI only)
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError('No records found')
          } else if (err.status === 500) {
            setError('Server error. Please try again later.')
          } else {
            setError(err.message)
          }
        } else {
          setError('An unexpected error occurred')
        }
      } finally {
        setIsLoading(false)
      }
    }
    
    loadRecords()
  }, [])
  
  if (error) {
    return <div className="text-red-500">{error}</div>
  }
  
  if (isLoading) {
    return <div>Loading...</div>
  }
  
  return <AttendanceTable records={records} />
}
```

## Styling and Layout

### Component Styling

**✅ CORRECT:**
```typescript
// Use Tailwind CSS with shadcn/ui components
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export function AttendanceCard({ record }: { record: AttendanceRecord }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{record.user_name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Date: {formatDate(record.date)}</p>
        <p>Time: {formatTime(record.time)}</p>
        <p>Confidence: {(record.confidence * 100).toFixed(1)}%</p>
      </CardContent>
    </Card>
  )
}
```

### Responsive Design

**✅ CORRECT:**
```typescript
// Use Tailwind responsive classes
export function AttendanceLayout() {
  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AttendanceCard />
        <AttendanceCard />
        <AttendanceCard />
      </div>
    </div>
  )
}
```

## Data Visualization

### Chart Components

**✅ CORRECT:**
```typescript
// frontend/components/analytics/AnalyticsCharts.tsx
'use client'

import { AttendanceRecord } from '@/types/attendance'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

interface AnalyticsChartsProps {
  records: AttendanceRecord[]
}

export function AnalyticsCharts({ records }: AnalyticsChartsProps) {
  if (records.length === 0) {
    return <div>No data to display</div>
  }
  
  // Prepare data for visualization (UI formatting only)
  const chartData = records.map(record => ({
    date: formatDate(record.date),
    count: 1
  }))
  
  const dailyCounts = chartData.reduce((acc, item) => {
    acc[item.date] = (acc[item.date] || 0) + item.count
    return acc
  }, {} as Record<string, number>)
  
  const chartDataPoints = Object.entries(dailyCounts).map(([date, count]) => ({
    date,
    count
  }))
  
  return (
    <LineChart width={600} height={300} data={chartDataPoints}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="count" stroke="#8884d8" />
    </LineChart>
  )
}
```

## Anti-Patterns from Old Code

### 1. Business Logic in UI
**❌ OLD:**
```typescript
export function AttendanceTable() {
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  
  useEffect(() => {
    fetch('/api/attendance')
      .then(res => res.json())
      .then(data => {
        // ❌ Business logic in UI!
        const filtered = data.filter(r => r.confidence > 0.6)
        const sorted = filtered.sort((a, b) => b.date - a.date)
        setRecords(sorted)
      })
  }, [])
  
  return <Table>{/* ... */}</Table>
}
```

**✅ NEW:**
```typescript
export function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [filters, setFilters] = useState<AttendanceFilters>({
    minConfidence: 0.6,
    sortBy: 'date'
  })
  
  useEffect(() => {
    // Business logic in backend API
    apiClient.getAttendanceRecords(filters)
      .then(setRecords)
  }, [filters])
  
  return <AttendanceTable records={records} />
}
```

### 2. Direct Service Access
**❌ OLD:**
```typescript
// ❌ Frontend accessing services directly
import { AttendanceService } from '@/services/attendance'

export function AttendancePage() {
  const service = new AttendanceService()
  const data = service.getAttendanceReport('overview')
  // ...
}
```

**✅ NEW:**
```typescript
// ✅ Frontend calls API only
import { apiClient } from '@/lib/api/client'

export function AttendancePage() {
  const data = await apiClient.getOverview()
  // ...
}
```

### 3. Data Fetching in Components
**❌ OLD:**
```typescript
export function AttendanceTable() {
  // ❌ Component fetches data
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  
  useEffect(() => {
    fetch('/api/attendance').then(res => res.json()).then(setRecords)
  }, [])
  
  return <Table>{/* ... */}</Table>
}
```

**✅ NEW:**
```typescript
// ✅ Component receives data as prop
export function AttendanceTable({ records }: { records: AttendanceRecord[] }) {
  return <Table>{/* ... */}</Table>
}

// ✅ Page fetches data
export default function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  
  useEffect(() => {
    apiClient.getAttendanceRecords().then(setRecords)
  }, [])
  
  return <AttendanceTable records={records} />
}
```

## Future Agent Instructions

When creating UI components:

1. **Keep components stateless**: Use props, not internal state for data
2. **Accept data as props**: Don't fetch data in components
3. **Delegate business operations**: Use API client for all business operations
4. **Handle errors gracefully**: Show user-friendly error messages
5. **Use consistent layout**: Follow established layout patterns
6. **Make components reusable**: Components should work with any data
7. **Separate concerns**: UI handles presentation, API handles communication
8. **Test components**: Test with mock data, not real API
9. **Document props**: Clearly document what data/components expect
10. **Follow Next.js best practices**: Use App Router, Server/Client Components properly
11. **NO business logic**: All business rules must be in backend
12. **Type safety**: Use TypeScript for all components and API calls
