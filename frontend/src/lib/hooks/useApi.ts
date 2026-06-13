'use client';

import { useMutation, useQuery, type UseQueryOptions } from '@tanstack/react-query';
import { apiGet, apiPost } from '@/lib/api/client';
import type { ApiResponse, AnalyticsData, PaginatedResponse } from '@/types/api';
import type {
  AttendanceFilters,
  AttendanceRecord,
  AttendanceStats,
  MarkAttendanceRequest,
  MarkAttendanceResponse,
  MarkClassAttendanceRequest,
  MarkClassAttendanceResponse,
  RecognizeFaceRequest,
  RecognizeFaceResponse,
} from '@/types/attendance';
import type { LeaderboardEntry, User } from '@/types/user';
import type { RegisterUserRequest } from '@/lib/schemas/user';
import type { ReportParams } from '@/lib/schemas/api';

type MutationOptions<TData, TVariables> = {
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: Error) => void;
};

interface BackendUser {
  userId: string;
  userName: string;
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
  registrationDate: string;
  status: string;
}

interface BackendUsersResponse {
  success: boolean;
  users: BackendUser[];
  total: number;
}

interface BackendLeaderboardResponse {
  success: boolean;
  entries: Array<{
    rank: number;
    userId: string;
    userName: string;
    value: number;
    metric: string;
  }>;
  metric: string;
  totalUsers: number;
}

function mapUser(user: BackendUser): User {
  const name = [user.firstName, user.lastName].filter(Boolean).join(' ') || user.userName;
  return {
    id: user.userId,
    name,
    email: user.email || '',
    enrollmentDate: user.registrationDate,
    isActive: user.status === 'active',
  };
}

function mapLeaderboardEntry(entry: BackendLeaderboardResponse['entries'][number]): LeaderboardEntry {
  const isRate = entry.metric === 'attendance_rate';
  return {
    rank: entry.rank,
    userId: entry.userId,
    userName: entry.userName,
    attendanceRate: isRate ? entry.value : entry.value / 100,
    currentStreak: entry.metric === 'streak' ? entry.value : 0,
    totalPoints: entry.metric === 'total_badges' ? entry.value : 0,
    badges: [],
  };
}

export function useAttendanceStats() {
  return useQuery({
    queryKey: ['attendance', 'stats'],
    queryFn: () => apiGet<ApiResponse<AttendanceStats>>('/api/attendance/stats'),
  });
}

export function useAttendanceRecords(
  filters: AttendanceFilters = {},
  options?: Pick<UseQueryOptions, 'enabled'>
) {
  return useQuery({
    queryKey: ['attendance', 'records', filters],
    enabled: options?.enabled,
    queryFn: () =>
      apiGet<ApiResponse<PaginatedResponse<AttendanceRecord>>>('/api/attendance', {
        page: 1,
        pageSize: 20,
        ...filters,
      }),
  });
}

export function useLeaderboard(limit = 10) {
  return useQuery({
    queryKey: ['leaderboard', limit],
    queryFn: async () => {
      const response = await apiGet<BackendLeaderboardResponse>('/api/leaderboard', {
        limit,
        metric: 'attendance_rate',
      });
      return {
        data: response.entries.map(mapLeaderboardEntry),
        success: response.success,
      } satisfies ApiResponse<LeaderboardEntry[]>;
    },
  });
}

export function useUsers(page = 1, pageSize = 10) {
  return useQuery({
    queryKey: ['users', page, pageSize],
    queryFn: async () => {
      const response = await apiGet<BackendUsersResponse>('/api/users', {
        page,
        pageSize,
      });
      const users = response.users.map(mapUser);
      const totalPages = Math.max(1, Math.ceil(response.total / pageSize));
      return {
        data: {
          data: users,
          total: response.total,
          page,
          pageSize,
          totalPages,
        },
        success: response.success,
      } satisfies ApiResponse<PaginatedResponse<User>>;
    },
  });
}

export function useAnalytics() {
  return useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const response = await apiGet<AnalyticsData & { success: boolean }>('/api/analytics');
      const { success, ...data } = response;
      return { data, success } satisfies ApiResponse<AnalyticsData>;
    },
  });
}

export function useRecognizeFace(options?: MutationOptions<RecognizeFaceResponse, RecognizeFaceRequest>) {
  return useMutation({
    mutationFn: (request: RecognizeFaceRequest) =>
      apiPost<RecognizeFaceResponse>('/api/attendance/recognize', request),
    onSuccess: options?.onSuccess,
    onError: options?.onError,
  });
}

export function useMarkAttendance(options?: MutationOptions<MarkAttendanceResponse, MarkAttendanceRequest>) {
  return useMutation({
    mutationFn: (request: MarkAttendanceRequest) =>
      apiPost<MarkAttendanceResponse>('/api/attendance/mark', request),
    onSuccess: options?.onSuccess,
    onError: options?.onError,
  });
}

export function useMarkClassAttendance(
  options?: MutationOptions<MarkClassAttendanceResponse, MarkClassAttendanceRequest>
) {
  return useMutation({
    mutationFn: (request: MarkClassAttendanceRequest) =>
      apiPost<MarkClassAttendanceResponse>('/api/attendance/mark-class', request),
    onSuccess: options?.onSuccess,
    onError: options?.onError,
  });
}

export function useRegisterUser(
  options?: MutationOptions<{ data: { message: string } }, RegisterUserRequest>
) {
  return useMutation({
    mutationFn: async (request: RegisterUserRequest) => {
      const response = await apiPost<{
        success: boolean;
        user?: BackendUser;
        error?: string;
      }>('/api/users/register', request);

      if (!response.success) {
        throw new Error(response.error || 'Registration failed');
      }

      return {
        data: {
          message: `User ${request.userName} registered successfully`,
        },
      };
    },
    onSuccess: options?.onSuccess,
    onError: options?.onError,
  });
}

export function useGenerateReport(options?: MutationOptions<Blob, ReportParams>) {
  return useMutation({
    mutationFn: async (params: ReportParams) => {
      const recordsResponse = await apiGet<{
        data: { data: AttendanceRecord[] };
      }>('/api/attendance', {
        page: 1,
        pageSize: 1000,
        startDate: params.startDate,
        endDate: params.endDate,
        userId: params.userId,
      });

      const records = recordsResponse.data?.data || [];
      const header = 'id,userId,userName,timestamp,status,confidence,location\n';
      const rows = records
        .map((record) =>
          [
            record.id,
            record.userId,
            `"${record.userName}"`,
            record.timestamp,
            record.status,
            record.confidence ?? '',
            record.location ?? '',
          ].join(',')
        )
        .join('\n');

      const mimeType =
        params.format === 'csv'
          ? 'text/csv'
          : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

      return new Blob([header + rows], { type: mimeType });
    },
    onSuccess: options?.onSuccess,
    onError: options?.onError,
  });
}
