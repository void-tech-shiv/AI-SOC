import { fetcher, Alert, AlertListResponse } from "@/lib/api";
import { AlertTriangle, Clock, Shield } from "lucide-react";
import Link from "next/link";

function severityColor(severity: string) {
  switch (severity.toLowerCase()) {
    case "critical": return "text-red-500 bg-red-500/10 border-red-500/20";
    case "high": return "text-orange-500 bg-orange-500/10 border-orange-500/20";
    case "medium": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
    case "low": return "text-blue-500 bg-blue-500/10 border-blue-500/20";
    default: return "text-mutedForeground bg-muted border-border";
  }
}

export const dynamic = "force-dynamic";

export default async function AlertsPage() {
  let alerts: Alert[] = [];
  let errorMsg: string | null = null;
  try {
    const data = await fetcher<AlertListResponse>("/api/v1/alerts");
    if (data && Array.isArray(data.alerts)) {
      alerts = data.alerts;
    } else {
      throw new Error("Invalid response format");
    }
  } catch (error) {
    console.error("Failed to fetch alerts", error);
    errorMsg = "Unable to load alerts";
  }

  if (errorMsg) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold tracking-tight text-red-500">{errorMsg}</h2>
        <a href="/alerts" className="inline-block px-4 py-2 bg-primary text-primaryForeground rounded border border-border hover:bg-muted">Retry</a>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <AlertTriangle className="h-6 w-6 text-primary" />
          Alerts
        </h2>
      </div>
      
      <div className="rounded-md border border-border bg-card">
        <div className="relative w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b border-border">
              <tr className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">ID</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Severity</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Rule</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Status</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Confidence</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Time</th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-mutedForeground">No alerts found</td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.id} className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                    <td className="p-4 align-middle font-mono text-xs text-mutedForeground">AL-{alert.id}</td>
                    <td className="p-4 align-middle">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${severityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="p-4 align-middle">{alert.rule_id}</td>
                    <td className="p-4 align-middle">
                      <span className="inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs font-semibold">
                        {alert.status}
                      </span>
                    </td>
                    <td className="p-4 align-middle">{(alert.confidence_score * 100).toFixed(0)}%</td>
                    <td className="p-4 align-middle text-mutedForeground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {alert.created_at ? new Date(alert.created_at).toLocaleString() : 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
