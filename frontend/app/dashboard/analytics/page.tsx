'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useAnalytics } from '@/lib/hooks/useApi';
import { formatDate } from '@/lib/utils/formatters';

const COLORS = ['hsl(217, 91%, 60%)', 'hsl(142, 76%, 36%)', 'hsl(38, 92%, 50%)', 'hsl(0, 84%, 60%)'];

export default function AnalyticsPage() {
  const { data: analyticsData, isLoading, error } = useAnalytics();

  if (error) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="animate-slide-up">
          <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
          <p className="text-muted-foreground">Detailed attendance insights and trends</p>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error loading analytics</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : 'Failed to load analytics data. Please try again later.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const dailyData = analyticsData?.data?.dailyAttendance?.map((item) => ({
    date: formatDate(item.date, 'short').split(',')[0],
    totalEntries: item.total_entries,
    uniqueUsers: item.unique_users,
    avgConfidence: Math.round(item.average_confidence * 100),
    livenessRate: Math.round(item.liveness_verification_rate),
  })) || [];

  const departmentData = analyticsData?.data?.departmentStats?.map((item) => ({
    name: item.department,
    value: item.totalEmployees,
  })) || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="animate-slide-up">
        <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
        <p className="text-muted-foreground">Detailed attendance insights and trends</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="hover-lift transition-all duration-300 animate-slide-up stagger-1">
          <CardHeader>
            <CardTitle>Weekly Attendance Trend</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : dailyData.length === 0 ? (
              <p className="text-sm text-muted-foreground">No data available</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="totalEntries" stroke="hsl(142, 76%, 36%)" strokeWidth={2} name="Total Entries" />
                  <Line type="monotone" dataKey="uniqueUsers" stroke="hsl(217, 91%, 60%)" strokeWidth={2} name="Unique Users" />
                  <Line type="monotone" dataKey="avgConfidence" stroke="hsl(38, 92%, 50%)" strokeWidth={2} name="Avg Confidence %" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card className="hover-lift transition-all duration-300 animate-slide-up stagger-2">
          <CardHeader>
            <CardTitle>Department Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : departmentData.length === 0 ? (
              <p className="text-sm text-muted-foreground">No data available</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={departmentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {departmentData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2 hover-lift transition-all duration-300 animate-slide-up stagger-3">
          <CardHeader>
            <CardTitle>Daily Attendance Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : dailyData.length === 0 ? (
              <p className="text-sm text-muted-foreground">No data available</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="totalEntries" fill="hsl(142, 76%, 36%)" name="Total Entries" />
                  <Bar dataKey="uniqueUsers" fill="hsl(217, 91%, 60%)" name="Unique Users" />
                  <Bar dataKey="livenessRate" fill="hsl(38, 92%, 50%)" name="Liveness Rate %" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

