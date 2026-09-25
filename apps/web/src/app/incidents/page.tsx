import { fetcher } from "@/lib/api";
import { ShieldAlert, Clock } from "lucide-react";
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

export default async function IncidentsPage() {
  let incidents: any[] = [];
  try {
    const data = await fetcher<{ incidents: any[], total: number }>("/api/v1/incidents");
    if (data && Array.isArray(data.incidents)) incidents = data.incidents;
  } catch (error) {
    console.error("Failed to fetch incidents", error);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ShieldAlert className="h-6 w-6 text-primary" />
          Incidents
        </h2>
      </div>
      
      <div className="rounded-md border border-border bg-card">
        <div className="relative w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b border-border">
              <tr className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">ID</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Title</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Severity</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Status</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Alerts</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Time</th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {incidents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-mutedForeground">No incidents found</td>
                </tr>
              ) : (
                incidents.map((incident) => (
                  <tr key={incident.id} className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                    <td className="p-4 align-middle font-mono text-xs text-mutedForeground">
                      <Link href={`/incidents/${incident.id}`} className="hover:underline hover:text-primary">
                        {incident.incident_key}
                      </Link>
                    </td>
                    <td className="p-4 align-middle">{incident.title}</td>
                    <td className="p-4 align-middle">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${severityColor(incident.severity)}`}>
                        {incident.severity}
                      </span>
                    </td>
                    <td className="p-4 align-middle">
                      <span className="inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs font-semibold">
                        {incident.status}
                      </span>
                    </td>
                    <td className="p-4 align-middle">
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-secondary text-xs font-medium">
                        {incident.alert_count || 0}
                      </span>
                    </td>
                    <td className="p-4 align-middle text-mutedForeground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(incident.created_at).toLocaleString()}
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
