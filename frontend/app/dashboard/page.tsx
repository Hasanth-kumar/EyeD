'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Users, UserCheck, Clock, TrendingUp, AlertCircle } from 'lucide-react';
import { useAttendanceStats, useAttendanceRecords, useLeaderboard } from '@/lib/hooks/useApi';
import { formatNumber, formatPercentage } from '@/lib/utils/formatters';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { formatDistanceToNow } from 'date-fns';

export default function DashboardPage() {
  const { data: statsData, isLoading: statsLoading, error: statsError } = useAttendanceStats();
  const { data: recordsData, isLoading: recordsLoading } = useAttendanceRecords({}, { enabled: true });
  const { data: leaderboardData, isLoading: leaderboardLoading } = useLeaderboard(5);

  const stats = statsData?.data;
  const recentRecords = recordsData?.data?.data?.slice(0, 4) || [];
  const topPerformers = leaderboardData?.data?.slice(0, 4) || [];

  const isLoading = statsLoading || recordsLoading || leaderboardLoading;

  if (statsError) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="animate-slide-up">
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Overview of attendance system metrics</p>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error loading dashboard</AlertTitle>
          <AlertDescription>
            {statsError instanceof Error ? statsError.message : 'Failed to load dashboard data. Please try again later.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Present Today',
      value: stats?.totalPresent ? formatNumber(stats.totalPresent) : '0',
      change: stats?.attendanceRate ? formatPercentage(stats.attendanceRate) : 'N/A',
      icon: UserCheck,
    },
    {
      title: 'Absent Today',
      value: stats?.totalAbsent ? formatNumber(stats.totalAbsent) : '0',
      change: stats?.totalAbsent ? `${formatNumber(stats.totalAbsent)} absent` : 'N/A',
      icon: Users,
    },
    {
      title: 'Late Today',
      value: stats?.totalLate ? formatNumber(stats.totalLate) : '0',
      change: stats?.averageCheckInTime || 'N/A',
      icon: Clock,
    },
    {
      title: 'Attendance Rate',
      value: stats?.attendanceRate ? formatPercentage(stats.attendanceRate) : '0%',
      change: stats?.totalPresent && stats?.totalAbsent 
        ? `${formatNumber(stats.totalPresent)} / ${formatNumber(stats.totalPresent + stats.totalAbsent + (stats.totalLate || 0))}`
        : 'N/A',
      icon: TrendingUp,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="animate-slide-up">
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Overview of attendance system metrics</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => (
          <Card 
            key={stat.title} 
            className={`hover-lift transition-all duration-300 animate-slide-up stagger-${(index % 4) + 1}`}
          >
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground transition-transform duration-200 group-hover:scale-110" />
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <>
                  <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                  <p className="text-xs text-accent mt-1">{stat.change}</p>
                </>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="hover-lift transition-all duration-300">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : recentRecords.length === 0 ? (
              <p className="text-sm text-muted-foreground">No recent activity</p>
            ) : (
              <div className="space-y-4">
                {recentRecords.map((record) => (
                  <div 
                    key={record.id}
                    className="flex items-center gap-4 p-3 rounded-lg bg-muted/50 hover:bg-muted/70 transition-all duration-200 cursor-pointer hover:scale-[1.02]"
                  >
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center transition-transform duration-200 hover:scale-110">
                      <UserCheck className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-foreground">{record.userName}</p>
                      <p className="text-sm text-muted-foreground">Marked attendance</p>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {formatDistanceToNow(new Date(record.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="hover-lift transition-all duration-300">
          <CardHeader>
            <CardTitle>Top Performers</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : topPerformers.length === 0 ? (
              <p className="text-sm text-muted-foreground">No leaderboard data available</p>
            ) : (
              <div className="space-y-4">
                {topPerformers.map((entry) => (
                  <div 
                    key={entry.userId}
                    className="flex items-center gap-4 p-3 rounded-lg bg-muted/50 hover:bg-muted/70 transition-all duration-200 cursor-pointer hover:scale-[1.02]"
                  >
                    <div className="h-10 w-10 rounded-full bg-accent/10 flex items-center justify-center text-accent font-bold transition-transform duration-200 hover:scale-110">
                      #{entry.rank}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-foreground">{entry.userName}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatPercentage(entry.attendanceRate)} attendance
                      </p>
                    </div>
                    <span className="text-sm font-medium text-accent">{entry.currentStreak} days</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

