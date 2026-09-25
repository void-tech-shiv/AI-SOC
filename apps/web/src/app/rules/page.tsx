import { fetcher, DetectionRule, CorrelationRule } from "@/lib/api";
import { Activity, Shield } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function RulesPage() {
  let detectionRules: DetectionRule[] = [];
  let correlationRules: CorrelationRule[] = [];
  
  let detectionError: string | null = null;
  let correlationError: string | null = null;

  try {
    const detectionData = await fetcher<DetectionRule[]>("/api/v1/detection-rules");
    if (Array.isArray(detectionData)) {
      detectionRules = detectionData;
    } else {
      throw new Error("Invalid format");
    }
  } catch (error) {
    console.error("Failed to fetch detection rules", error);
    detectionError = "Unable to load detection rules";
  }

  try {
    const correlationData = await fetcher<CorrelationRule[]>("/api/v1/correlation-rules");
    if (Array.isArray(correlationData)) {
      correlationRules = correlationData;
    } else {
      throw new Error("Invalid format");
    }
  } catch (error) {
    console.error("Failed to fetch correlation rules", error);
    correlationError = "Unable to load correlation rules";
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Activity className="h-6 w-6 text-primary" />
          Detection & Correlation Rules
        </h2>
      </div>
      
      <div className="space-y-4">
        <h3 className="text-xl font-semibold border-b pb-2">Detection Rules</h3>
        {detectionError ? (
          <div className="p-4 border border-red-500/20 bg-red-500/10 rounded-md">
            <p className="text-red-500">{detectionError}</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {detectionRules.length > 0 ? (
              detectionRules.map((rule) => (
                <div key={rule.rule_id} className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
                  <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
                    <h3 className="tracking-tight text-sm font-bold flex items-center gap-2">
                      <Shield className="h-4 w-4 text-primary" />
                      {rule.rule_id}
                    </h3>
                    <span className="inline-flex items-center rounded-full border border-green-500/20 bg-green-500/10 text-green-500 px-2.5 py-0.5 text-xs font-semibold">
                      active
                    </span>
                  </div>
                  <div className="p-6 pt-0 space-y-2">
                    <h4 className="font-semibold text-lg">{rule.rule_name}</h4>
                    {rule.description && <p className="text-sm text-mutedForeground">{rule.description}</p>}
                    <div className="pt-4 flex items-center text-xs text-mutedForeground">
                      {rule.severity && <div><span className="font-medium mr-1">Severity:</span> {rule.severity}</div>}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-mutedForeground">No detection rules found.</p>
            )}
          </div>
        )}
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold border-b pb-2">Correlation Rules</h3>
        {correlationError ? (
          <div className="p-4 border border-red-500/20 bg-red-500/10 rounded-md">
            <p className="text-red-500">{correlationError}</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {correlationRules.length > 0 ? (
              correlationRules.map((rule) => (
                <div key={rule.rule_id} className="rounded-xl border border-border bg-card text-cardForeground shadow-sm">
                  <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
                    <h3 className="tracking-tight text-sm font-bold flex items-center gap-2">
                      <Shield className="h-4 w-4 text-primary" />
                      {rule.rule_id}
                    </h3>
                    <span className="inline-flex items-center rounded-full border border-green-500/20 bg-green-500/10 text-green-500 px-2.5 py-0.5 text-xs font-semibold">
                      active
                    </span>
                  </div>
                  <div className="p-6 pt-0 space-y-2">
                    <h4 className="font-semibold text-lg">{rule.rule_name}</h4>
                    {rule.description && <p className="text-sm text-mutedForeground">{rule.description}</p>}
                    <div className="pt-4 flex items-center text-xs text-mutedForeground space-x-4">
                      {rule.severity && <div><span className="font-medium mr-1">Severity:</span> {rule.severity}</div>}
                      {rule.time_window_minutes !== undefined && (
                        <div><span className="font-medium mr-1">Time Window:</span> {rule.time_window_minutes !== null ? `${rule.time_window_minutes}m` : "N/A"}</div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-mutedForeground">No correlation rules found.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
