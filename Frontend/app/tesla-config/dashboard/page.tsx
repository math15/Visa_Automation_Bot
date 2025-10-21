'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  Play, 
  Pause, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Users,
  Calendar,
  Target,
  TrendingUp,
  Activity,
  Zap,
  Shield,
  Globe
} from 'lucide-react';

interface AutomationStats {
  totalAccounts: number;
  activeAccounts: number;
  runningAutomations: number;
  successRate: number;
  appointmentsBooked: number;
  todayBookings: number;
  avgResponseTime: number;
  wafBypassSuccess: number;
}

interface RecentActivity {
  id: number;
  account: string;
  action: string;
  status: 'success' | 'error' | 'pending';
  timestamp: string;
  details: string;
}

export default function TeslaDashboardPage() {
  const [stats, setStats] = useState<AutomationStats>({
    totalAccounts: 0,
    activeAccounts: 0,
    runningAutomations: 0,
    successRate: 0,
    appointmentsBooked: 0,
    todayBookings: 0,
    avgResponseTime: 0,
    wafBypassSuccess: 0
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    setIsRefreshing(true);
    try {
      // Mock data - replace with actual API calls
      setStats({
        totalAccounts: 25,
        activeAccounts: 18,
        runningAutomations: 12,
        successRate: 87.5,
        appointmentsBooked: 156,
        todayBookings: 8,
        avgResponseTime: 2.3,
        wafBypassSuccess: 98.2
      });

      setRecentActivity([
        {
          id: 1,
          account: 'user1@example.com',
          action: 'Appointment Booking',
          status: 'success',
          timestamp: '2025-01-19T15:30:00Z',
          details: 'Successfully booked appointment for 2025-02-15'
        },
        {
          id: 2,
          account: 'user2@example.com',
          action: 'WAF Bypass',
          status: 'success',
          timestamp: '2025-01-19T15:25:00Z',
          details: 'AWS WAF challenge solved in 1.2s'
        },
        {
          id: 3,
          account: 'user3@example.com',
          action: 'Account Creation',
          status: 'error',
          timestamp: '2025-01-19T15:20:00Z',
          details: 'Captcha solving failed'
        },
        {
          id: 4,
          account: 'user4@example.com',
          action: 'Proxy Validation',
          status: 'success',
          timestamp: '2025-01-19T15:15:00Z',
          details: 'Proxy validated successfully'
        }
      ]);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="default" className="bg-green-500">Success</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart3 className="h-8 w-8" />
            Tesla Automation Dashboard
          </h1>
          <p className="text-muted-foreground">
            Real-time monitoring and analytics for Tesla automation system
          </p>
        </div>
        <Button 
          onClick={fetchDashboardData} 
          disabled={isRefreshing}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{stats.totalAccounts}</div>
                <div className="text-sm text-muted-foreground">Total Accounts</div>
              </div>
            </div>
            <div className="mt-2">
              <div className="text-xs text-muted-foreground">
                {stats.activeAccounts} active
              </div>
              <Progress value={(stats.activeAccounts / stats.totalAccounts) * 100} className="mt-1" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-500" />
              <div>
                <div className="text-2xl font-bold">{stats.runningAutomations}</div>
                <div className="text-sm text-muted-foreground">Running</div>
              </div>
            </div>
            <div className="mt-2">
              <div className="text-xs text-muted-foreground">
                {stats.successRate}% success rate
              </div>
              <Progress value={stats.successRate} className="mt-1" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">{stats.appointmentsBooked}</div>
                <div className="text-sm text-muted-foreground">Total Bookings</div>
              </div>
            </div>
            <div className="mt-2">
              <div className="text-xs text-muted-foreground">
                {stats.todayBookings} today
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              <div>
                <div className="text-2xl font-bold">{stats.avgResponseTime}s</div>
                <div className="text-sm text-muted-foreground">Avg Response</div>
              </div>
            </div>
            <div className="mt-2">
              <div className="text-xs text-muted-foreground">
                {stats.wafBypassSuccess}% WAF success
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              System Status
            </CardTitle>
            <CardDescription>
              Current system health and performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-green-500" />
                <span className="text-sm">AWS WAF Bypass</span>
              </div>
              <Badge variant="default" className="bg-green-500">Operational</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-green-500" />
                <span className="text-sm">Proxy Network</span>
              </div>
              <Badge variant="default" className="bg-green-500">Operational</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-green-500" />
                <span className="text-sm">Account Management</span>
              </div>
              <Badge variant="default" className="bg-green-500">Operational</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-green-500" />
                <span className="text-sm">Booking System</span>
              </div>
              <Badge variant="default" className="bg-green-500">Operational</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>
              Common automation tasks and controls
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" variant="outline">
              <Play className="h-4 w-4 mr-2" />
              Start All Automations
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Pause className="h-4 w-4 mr-2" />
              Pause All Automations
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Proxy List
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Shield className="h-4 w-4 mr-2" />
              Test WAF Bypass
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Activity
          </CardTitle>
          <CardDescription>
            Latest automation activities and system events
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getStatusIcon(activity.status)}
                  <div>
                    <div className="font-medium">{activity.account}</div>
                    <div className="text-sm text-muted-foreground">{activity.action}</div>
                    <div className="text-xs text-muted-foreground">{activity.details}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(activity.status)}
                  <div className="text-xs text-muted-foreground">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Performance Trends
          </CardTitle>
          <CardDescription>
            Success rate and booking trends over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-muted rounded-lg">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">Performance charts will be displayed here</p>
              <p className="text-sm text-muted-foreground">Integration with charting library pending</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
