'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Trophy, Award, Flame, Target, AlertCircle } from 'lucide-react';
import { useLeaderboard } from '@/lib/hooks/useApi';
import { formatPercentage } from '@/lib/utils/formatters';
import type { LeaderboardEntry, Badge as BadgeType } from '@/types/user';

export default function LeaderboardPage() {
  const { data: leaderboardData, isLoading, error } = useLeaderboard(10);

  if (error) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
        <div className="animate-slide-up">
          <h1 className="text-3xl font-bold text-foreground">Leaderboard</h1>
          <p className="text-muted-foreground">Top performers based on attendance and consistency</p>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error loading leaderboard</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : 'Failed to load leaderboard data. Please try again later.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const entries: LeaderboardEntry[] = leaderboardData?.data || [];
  const topPerformer = entries[0];
  const longestStreak = entries.reduce((max: LeaderboardEntry | { currentStreak: number }, entry: LeaderboardEntry) => 
    entry.currentStreak > max.currentStreak ? entry : max, 
    entries[0] || { currentStreak: 0 }
  );
  const totalBadges = entries.reduce((sum: number, entry: LeaderboardEntry) => sum + (entry.badges?.length || 0), 0);
  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div className="animate-slide-up">
        <h1 className="text-3xl font-bold text-foreground">Leaderboard</h1>
        <p className="text-muted-foreground">Top performers based on attendance and consistency</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="hover-lift transition-all duration-300 animate-slide-up stagger-1">
          <CardContent className="pt-6">
            {isLoading ? (
              <Skeleton className="h-16 w-full" />
            ) : (
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-accent/10 flex items-center justify-center transition-transform duration-200 hover:scale-110 hover:rotate-12">
                  <Trophy className="h-6 w-6 text-accent" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Top Performer</p>
                  <p className="text-lg font-bold text-foreground">{topPerformer?.userName || 'N/A'}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <Skeleton className="h-16 w-full" />
            ) : (
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-accent/10 flex items-center justify-center">
                  <Flame className="h-6 w-6 text-accent" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Longest Streak</p>
                  <p className="text-lg font-bold text-foreground">{longestStreak?.currentStreak || 0} Days</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            {isLoading ? (
              <Skeleton className="h-16 w-full" />
            ) : (
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-accent/10 flex items-center justify-center">
                  <Award className="h-6 w-6 text-accent" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Badges</p>
                  <p className="text-lg font-bold text-foreground">{totalBadges}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top Rankings</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          ) : entries.length === 0 ? (
            <p className="text-sm text-muted-foreground">No leaderboard data available</p>
          ) : (
            <div className="space-y-4">
              {entries.map((entry: LeaderboardEntry, index: number) => (
                <div
                  key={entry.userId}
                  className={`flex items-center gap-4 p-4 rounded-lg transition-all duration-300 hover:scale-[1.02] cursor-pointer animate-slide-up ${
                  entry.rank === 1
                    ? 'bg-accent/10 border-2 border-accent hover:shadow-lg'
                    : 'bg-muted/50 hover:bg-muted/70'
                }`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div
                  className={`h-12 w-12 rounded-full flex items-center justify-center font-bold text-xl ${
                    entry.rank === 1
                      ? 'bg-accent text-accent-foreground'
                      : entry.rank === 2
                      ? 'bg-primary/20 text-primary'
                      : entry.rank === 3
                      ? 'bg-secondary text-secondary-foreground'
                      : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {entry.rank}
                </div>

                <div className="flex-1">
                  <p className="font-semibold text-foreground">{entry.userName}</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {entry.badges?.map((badge: BadgeType) => (
                      <Badge key={badge.id} variant="secondary" className="text-xs">
                        {badge.name}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="text-right space-y-1">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-muted-foreground" />
                    <span className="font-semibold text-accent">{formatPercentage(entry.attendanceRate)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Flame className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">{entry.currentStreak} days</span>
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-2xl font-bold text-primary">{entry.totalPoints}</p>
                  <p className="text-xs text-muted-foreground">points</p>
                </div>
              </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

