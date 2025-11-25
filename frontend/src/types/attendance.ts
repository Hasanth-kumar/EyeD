export interface AttendanceRecord {
  id: string;
  userId: string;
  userName: string;
  timestamp: string;
  status: 'present' | 'absent' | 'late';
  confidence?: number;
  imageUrl?: string;
  location?: string;
}

export interface AttendanceStats {
  totalPresent: number;
  totalAbsent: number;
  totalLate: number;
  attendanceRate: number;
  averageCheckInTime?: string;
}

export interface AttendanceFilters {
  startDate?: string;
  endDate?: string;
  status?: 'present' | 'absent' | 'late';
  userId?: string;
}

/**
 * Request type for Phase 2: Liveness Verification and Attendance Marking
 * Requires user info from Phase 1 recognition
 */
export interface MarkAttendanceRequest {
  frames: string[]; // Base64 encoded frames for liveness verification (minimum 3)
  landmarks?: number[][][]; // Optional landmarks: [[[x, y], ...], ...] - one per frame
  userId: string; // REQUIRED - from Phase 1 recognition
  userName: string; // REQUIRED - from Phase 1 recognition
  faceImage: string; // REQUIRED - Base64 encoded single frame from Phase 1
  confidence: number; // REQUIRED - Recognition confidence from Phase 1 (0-1)
  faceQualityScore?: number; // Optional - Quality score from Phase 1 (0-1), will be recalculated if not provided
  location?: string; // Optional - Location where attendance is being marked
  blinkCount?: number; // Optional - Blink count from frontend (trusted if >= 3)
}

export interface MarkAttendanceResponse {
  success: boolean;
  userId: string;
  userName: string;
  timestamp: string;
  confidence: number;
  message: string;
}

/**
 * Request type for Phase 1: Face Recognition
 * Sends a single base64-encoded frame for recognition
 */
export interface RecognizeFaceRequest {
  frame: string; // Base64 encoded single frame
}

/**
 * Response type for Phase 1: Face Recognition
 * Returns user info if recognized, or error message if not
 */
export interface RecognizeFaceResponse {
  success: boolean;
  userId?: string; // Present when success is true
  userName?: string; // Present when success is true
  confidence?: number; // Present when success is true, between 0 and 1
  message: string; // Success or error message
  dailyLimitReached: boolean; // True if user has reached daily attendance limit
}

/**
 * Request type for marking class attendance from a single photo
 */
export interface MarkClassAttendanceRequest {
  classImage: string; // Base64 encoded class photo
  location?: string; // Optional location
}

/**
 * Individual attendance result in class attendance response
 */
export interface IndividualAttendanceResult {
  userId: string;
  userName: string;
  confidence: number;
  success: boolean;
  error?: string | null;
  timestamp: string;
}

/**
 * Response type for marking class attendance
 */
export interface MarkClassAttendanceResponse {
  success: boolean;
  results: IndividualAttendanceResult[];
  totalDetected: number;
  totalRecognized: number;
  totalMarked: number;
  message: string;
}
