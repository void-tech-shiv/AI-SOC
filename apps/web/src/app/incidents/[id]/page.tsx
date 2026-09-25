import { fetcher } from "@/lib/api";
import { ShieldAlert, Clock, AlertTriangle, ChevronLeft } from "lucide-react";
import Link from "next/link";

function severityColor(severity: string) {
  switch (severity?.toLowerCase()) {
    case "critical": return "text-red-500 bg-red-500/10 border-red-500/20";
    case "high": return "text-orange-500 bg-orange-500/10 border-orange-500/20";
    case "medium": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
    case "low": return "text-blue-500 bg-blue-500/10 border-blue-500/20";
    default: return "text-mutedForeground bg-muted border-border";
  }
}

export const dynamic = "force-dynamic";

export default async function IncidentDetailPage({ params }: { params: { id: string } }) {
  let incident: any = null;
  try {
    incident = await fetcher<any>(`/api/v1/incidents/${params.id}`);
  } catch (error) {
    console.error("Failed to fetch incident details", error);
  }

  if (!incident) {
    return (
      <div className="space-y-6">
        <Link href="/incidents" className="text-sm text-mutedForeground hover:text-primary flex items-center">
          <ChevronLeft className="w-4 h-4 mr-1" />
          Back to Incidents
        </Link>
        <div className="p-12 text-center border border-border bg-card rounded-md">
          <h2 className="text-xl font-semibold text-destructive">Incident Not Found</h2>
          <p className="text-mutedForeground mt-2">The requested incident could not be loaded.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/incidents" className="text-mutedForeground hover:text-primary p-2 rounded-md hover:bg-secondary transition-colors">
          <ChevronLeft className="w-5 h-5" />
        </Link>
        <div>
          <h2 className="text-2xl font-bold tracking-tight">{incident.title}</h2>
          <p className="text-sm text-mutedForeground font-mono">{incident.id}</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm p-6">
            <h3 className="font-semibold text-lg mb-4 flex items-center">
              <ShieldAlert className="w-5 h-5 mr-2 text-primary" />
              Incident Overview
            </h3>
            <p className="text-mutedForeground">{incident.description}</p>
          </div>

          <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm p-6">
            <h3 className="font-semibold text-lg mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-primary" />
              Associated Alerts ({incident.alerts?.length || 0})
            </h3>
            <div className="space-y-4">
              {incident.alerts && incident.alerts.length > 0 ? (
                incident.alerts.map((alert: any) => (
                  <div key={alert.id} className="p-4 border border-border rounded-md bg-background flex flex-col space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${severityColor(alert.severity)}`}>
                          {alert.severity}
                        </span>
                        <span className="font-mono text-xs text-mutedForeground">{alert.id.substring(0, 8)}...</span>
                      </div>
                      <span className="text-xs text-mutedForeground flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                    </div>
                    <div className="text-sm font-medium">Rule: {alert.rule_id}</div>
                    <div className="text-sm text-mutedForeground bg-muted p-2 rounded font-mono break-all">
                      {JSON.stringify(alert.evidence, null, 2)}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-mutedForeground text-sm text-center p-4">No associated alerts found.</p>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-border bg-card text-cardForeground shadow-sm p-6">
            <h3 className="font-semibold text-lg mb-4">Properties</h3>
            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium text-mutedForeground mb-1">Severity</div>
                <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${severityColor(incident.severity)}`}>
                  {incident.severity}
                </span>
              </div>
              <div>
                <div className="text-sm font-medium text-mutedForeground mb-1">Status</div>
                <span className="inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs font-semibold capitalize">
                  {incident.status}
                </span>
              </div>
              <div>
                <div className="text-sm font-medium text-mutedForeground mb-1">Confidence Score</div>
                <div className="text-sm font-medium">
                  {((incident.confidence_score || 0) * 100).toFixed(0)}%
                </div>
              </div>
              <div>
                <div className="text-sm font-medium text-mutedForeground mb-1">Correlation Rule</div>
                <div className="text-sm font-medium font-mono">
                  {incident.correlation_rule_id}
                </div>
              </div>
              <div>
                <div className="text-sm font-medium text-mutedForeground mb-1">Created</div>
                <div className="text-sm font-medium flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {new Date(incident.created_at).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
