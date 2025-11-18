export interface User {
  id: string;
  name: string;
  email: string;
  department?: string;
  role?: string;
  enrollmentDate: string;
  profileImage?: string;
  isActive: boolean;
}

export interface UserStats {
  totalAttendance: number;
  presentDays: number;
  absentDays: number;
  lateDays: number;
  attendanceRate: number;
  currentStreak: number;
  longestStreak: number;
  badges: Badge[];
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  earnedAt: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface RegisterUserRequest {
  name: string;
  email: string;
  department?: string;
  role?: string;
  frames: string[]; // Base64 encoded frames for face registration
}

export interface RegisterUserResponse {
  success: boolean;
  userId: string;
  message: string;
}

export interface LeaderboardEntry {
  rank: number;
  userId: string;
  userName: string;
  profileImage?: string;
  attendanceRate: number;
  currentStreak: number;
  totalPoints: number;
  badges: Badge[];
}
