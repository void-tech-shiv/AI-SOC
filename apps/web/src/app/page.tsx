import { fetcher, IncidentListResponse, AlertListResponse, SecurityLogListResponse, StatusResponse } from "@/lib/api";
import { ShieldAlert, AlertTriangle, CheckCircle, Clock, FileText } from "lucide-react";

export const dynamic = "force-dynamic";

async function getStats() {
  try {
    const [incidentsRes, alertsRes, logsRes, statusRes] = await Promise.all([
      fetcher<IncidentListResponse>("/api/v1/incidents"),
      fetcher<AlertListResponse>("/api/v1/alerts"),
      fetcher<SecurityLogListResponse>("/api/v1/logs"),
      fetcher<StatusResponse>("/api/v1/status"),
    ]);

    const safeIncidents = incidentsRes?.incidents || [];
    const safeAlerts = alertsRes?.alerts || [];

    const openIncidents = safeIncidents.filter(i => i.status !== "closed" && i.status !== "resolved").length;
    const criticalIncidents = safeIncidents.filter(i => i.severity === "critical").length;
    const openAlerts = safeAlerts.filter(a => a.status === "open").length;
    const criticalAlerts = safeAlerts.filter(a => a.severity === "critical").length;

    return {
      openIncidents,
      criticalIncidents,
      openAlerts,
      criticalAlerts,
      totalLogs: logsRes.total || (logsRes.logs && logsRes.logs.length) || 0,
      status: statusRes,
    };
  } catch (error) {
    console.error("Failed to fetch stats", error);
    return null;
  }
}

export default async function Home() {
  const stats = await getStats();

  if (!stats) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold tracking-tight text-red-500">Unable to load dashboard stats</h2>
        <a href="/" className="inline-block px-4 py-2 bg-primary text-primaryForeground rounded border border-border hover:bg-muted">Retry</a>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">Overview</h2>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">Total Logs</h3>
            <FileText className="h-4 w-4 text-blue-400" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold">{stats.totalLogs}</div>
            <p className="text-xs text-mutedForeground">Processed events</p>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">Open Alerts</h3>
            <Clock className="h-4 w-4 text-blue-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold">{stats.openAlerts}</div>
            <p className="text-xs text-mutedForeground">Require triage</p>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">Critical Alerts</h3>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold">{stats.criticalAlerts}</div>
            <p className="text-xs text-mutedForeground">Needs immediate attention</p>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">Open Incidents</h3>
            <ShieldAlert className="h-4 w-4 text-destructive" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold">{stats.openIncidents}</div>
            <p className="text-xs text-mutedForeground">{stats.criticalIncidents} Critical Incidents</p>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">System Health</h3>
            <CheckCircle className={`h-4 w-4 ${stats.status.database_connected ? 'text-green-500' : 'text-red-500'}`} />
          </div>
          <div className="p-6 pt-0">
            <div className="text-xl font-bold">{stats.status.status === 'operational' ? 'Online' : 'Degraded'}</div>
            <p className="text-xs text-mutedForeground">{stats.status.database_connected ? 'DB Connected' : 'DB Disconnected'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
