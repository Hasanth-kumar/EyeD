import { NavLink } from '@/components/NavLink';
import {
  LayoutDashboard,
  UserCheck,
  UserPlus,
  BarChart3,
  Trophy,
  Users,
  FileText,
} from 'lucide-react';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: UserCheck, label: 'Mark Attendance', path: '/dashboard/attendance' },
  { icon: UserPlus, label: 'Register User', path: '/dashboard/register' },
  { icon: BarChart3, label: 'Analytics', path: '/dashboard/analytics' },
  { icon: Trophy, label: 'Leaderboard', path: '/dashboard/leaderboard' },
  { icon: Users, label: 'Users', path: '/dashboard/users' },
  { icon: FileText, label: 'Reports', path: '/dashboard/reports' },
];

export const Sidebar = () => {
  return (
    <aside className="w-64 min-h-screen bg-sidebar border-r border-sidebar-border">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-sidebar-foreground">
          EyeD AI
        </h1>
        <p className="text-sm text-sidebar-foreground/60">Attendance System</p>
      </div>

      <nav className="px-3 space-y-1">
        {navItems.map((item, index) => (
          <NavLink
            key={item.path}
            href={item.path}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-200 hover:translate-x-1 animate-slide-up stagger-${(index % 4) + 1}`}
            activeClassName="bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary hover:text-sidebar-primary-foreground"
          >
            <item.icon className="h-5 w-5 transition-transform duration-200 group-hover:scale-110" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
