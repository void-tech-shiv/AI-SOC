import { fetcher } from "@/lib/api";
import { FileText, Clock, Search } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function LogsPage() {
  let logs: any[] = [];
  try {
    const data = await fetcher<{ logs: any[], total: number }>("/api/v1/logs?limit=100");
    if (data && Array.isArray(data.logs)) logs = data.logs;
  } catch (error) {
    console.error("Failed to fetch logs", error);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <FileText className="h-6 w-6 text-primary" />
          Security Logs
        </h2>
      </div>
      
      <div className="rounded-md border border-border bg-card">
        <div className="relative w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b border-border">
              <tr className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Source</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Event Type</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">User</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">IP Address</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-mutedForeground">Time</th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-4 text-center text-mutedForeground">No logs found</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                    <td className="p-4 align-middle font-mono text-xs">{log.source}</td>
                    <td className="p-4 align-middle">
                      <span className="inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs font-semibold">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="p-4 align-middle">{log.user || "-"}</td>
                    <td className="p-4 align-middle font-mono text-xs text-mutedForeground">{log.ip_address || "-"}</td>
                    <td className="p-4 align-middle text-mutedForeground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(log.timestamp).toLocaleString()}
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
