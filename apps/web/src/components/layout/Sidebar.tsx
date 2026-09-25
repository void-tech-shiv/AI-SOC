import Link from 'next/link';
import { Shield, LayoutDashboard, AlertTriangle, FileText, Activity, ShieldAlert } from 'lucide-react';

export function Sidebar() {
  return (
    <div className="w-64 border-r border-border bg-card flex flex-col h-full">
      <div className="h-14 flex items-center px-4 border-b border-border">
        <Shield className="w-6 h-6 text-primary mr-2" />
        <span className="font-bold text-lg text-primary">AI-SOC</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-2">
          <li>
            <Link href="/" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-mutedForeground hover:text-primary hover:bg-secondary">
              <LayoutDashboard className="w-4 h-4 mr-3" />
              Dashboard
            </Link>
          </li>
          <li>
            <Link href="/incidents" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-mutedForeground hover:text-primary hover:bg-secondary">
              <ShieldAlert className="w-4 h-4 mr-3" />
              Incidents
            </Link>
          </li>
          <li>
            <Link href="/alerts" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-mutedForeground hover:text-primary hover:bg-secondary">
              <AlertTriangle className="w-4 h-4 mr-3" />
              Alerts
            </Link>
          </li>
          <li>
            <Link href="/logs" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-mutedForeground hover:text-primary hover:bg-secondary">
              <FileText className="w-4 h-4 mr-3" />
              Security Logs
            </Link>
          </li>
          <li>
            <Link href="/rules" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-mutedForeground hover:text-primary hover:bg-secondary">
              <Activity className="w-4 h-4 mr-3" />
              Detection Rules
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  );
}
