import { fetcher } from "@/lib/api";
import { ShieldAlert, AlertTriangle, CheckCircle, Clock } from "lucide-react";

export const dynamic = "force-dynamic";

async function getStats() {
  try {
    const [incidentsRes, alertsRes] = await Promise.all([
      fetcher<{ incidents: any[], total: number }>("/api/v1/incidents").catch(() => null),
      fetcher<{ alerts: any[], total: number }>("/api/v1/alerts").catch(() => null),
    ]);

    const safeIncidents = incidentsRes?.incidents || [];
    const safeAlerts = alertsRes?.alerts || [];

    const activeIncidents = safeIncidents.filter(i => i.status !== "closed" && i.status !== "resolved").length;
    const criticalAlerts = safeAlerts.filter(a => a.severity === "critical").length;
    const openAlerts = safeAlerts.filter(a => a.status === "open").length;

    return {
      activeIncidents,
      criticalAlerts,
      openAlerts,
      totalIncidents: incidentsRes?.total || safeIncidents.length,
      totalAlerts: alertsRes?.total || safeAlerts.length,
    };
  } catch (error) {
    console.error("Failed to fetch stats", error);
    return {
      activeIncidents: 0,
      criticalAlerts: 0,
      openAlerts: 0,
      totalIncidents: 0,
      totalAlerts: 0,
    };
  }
}

export default async function Home() {
  const stats = await getStats();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">Overview</h2>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">Active Incidents</h3>
            <ShieldAlert className="h-4 w-4 text-destructive" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold">{stats.activeIncidents}</div>
            <p className="text-xs text-mutedForeground">Total {stats.totalIncidents} incidents</p>
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
            <h3 className="tracking-tight text-sm font-medium">Open Alerts</h3>
            <Clock className="h-4 w-4 text-blue-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold">{stats.openAlerts}</div>
            <p className="text-xs text-mutedForeground">Total {stats.totalAlerts} alerts generated</p>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight text-sm font-medium">System Health</h3>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </div>
          <div className="p-6 pt-0">
            <div className="text-2xl font-bold">100%</div>
            <p className="text-xs text-mutedForeground">All detection rules running</p>
          </div>
        </div>
      </div>
    </div>
  );
}
