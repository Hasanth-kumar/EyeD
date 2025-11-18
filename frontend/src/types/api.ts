export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  code: string;
  details?: any;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface AnalyticsData {
  success: boolean;
  dailyAttendance: DailyAttendance[];
  weeklyTrend?: WeeklyTrend[];
  departmentStats?: DepartmentStats[];
  peakHours?: PeakHour[];
  arrivalPatterns?: ArrivalPatterns;
  periodSummary?: PeriodSummary;
  weeklyAttendanceRate?: number;
  error?: string;
}

export interface DailyAttendance {
  date: string;
  total_entries: number;
  unique_users: number;
  average_confidence: number;
  liveness_verification_rate: number;
}

export interface PeriodSummary {
  total_entries: number;
  unique_users: number;
  average_confidence: number;
  liveness_verification_rate: number;
}

export interface ArrivalPatterns {
  peak_hour: number;
  average_arrival_time: string;
  late_arrivals_count: number;
  earliest_arrival_minutes: number;
  latest_arrival_minutes: number;
  hourly_distribution: Record<string, number>;
  early_bird_count: number;
  on_time_count: number;
}

export interface WeeklyTrend {
  week: string;
  attendanceRate: number;
  avgCheckInTime: string;
}

export interface DepartmentStats {
  department: string;
  totalEmployees: number;
  avgAttendanceRate: number;
  presentToday: number;
}

export interface PeakHour {
  hour: number;
  checkIns: number;
}

export interface ReportParams {
  startDate: string;
  endDate: string;
  format: 'pdf' | 'csv' | 'excel';
  type: 'summary' | 'detailed' | 'user';
  userId?: string;
}
