import { fetcher } from "@/lib/api";
import { Activity, Shield } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function RulesPage() {
  let rules: any[] = [];
  try {
    const data = await fetcher<any[]>("/api/v1/correlation-rules");
    if (Array.isArray(data)) rules = data;
  } catch (error) {
    console.error("Failed to fetch correlation rules", error);
  }

  // Fallback to static rules if API fails or isn't fully implemented yet
  if (rules.length === 0) {
    rules = [
      { id: "CORR-001", name: "Multiple Alerts for Same User", description: "Correlates different alert types that involve the same user account within a time window.", status: "active", priority: 1 },
      { id: "CORR-002", name: "Brute Force Followed by Success", description: "Correlates login failures followed by a successful login from the same IP.", status: "active", priority: 2 },
      { id: "CORR-003", name: "Network Anomaly to Data Access", description: "Correlates network anomalies with subsequent suspicious data access.", status: "active", priority: 2 },
      { id: "CORR-004", name: "Malware with Network Activity", description: "Correlates malware detection with outbound network anomalies.", status: "active", priority: 1 },
      { id: "CORR-005", name: "Fallback Incident Creation", description: "Creates standalone incidents for critical/high alerts that don't match specific correlation scenarios.", status: "active", priority: 99 }
    ];
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Activity className="h-6 w-6 text-primary" />
          Detection & Correlation Rules
        </h2>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {rules.map((rule) => (
          <div key={rule.id} className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
            <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-bold flex items-center gap-2">
                <Shield className="h-4 w-4 text-primary" />
                {rule.id}
              </h3>
              <span className="inline-flex items-center rounded-full border border-green-500/20 bg-green-500/10 text-green-500 px-2.5 py-0.5 text-xs font-semibold">
                {rule.status}
              </span>
            </div>
            <div className="p-6 pt-0 space-y-2">
              <h4 className="font-semibold text-lg">{rule.name}</h4>
              <p className="text-sm text-mutedForeground">{rule.description}</p>
              <div className="pt-4 flex items-center text-xs text-mutedForeground">
                <span className="font-medium mr-2">Priority:</span> {rule.priority}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
