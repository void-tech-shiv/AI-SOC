export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function fetcher<T>(url: string, options?: RequestInit & { timeout?: number }): Promise<T> {
  const { timeout = 8000, ...fetchOptions } = options || {};
  
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      cache: 'no-store', // Disable caching for dynamic SOC data
      ...fetchOptions,
      headers: {
        "Content-Type": "application/json",
        ...fetchOptions?.headers,
      },
      signal: controller.signal,
    });

    clearTimeout(id);

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

export interface SecurityLog {
  id?: string | number;
  timestamp: string;
  source: string;
  event_type: string;
  severity: string;
  username?: string;
  ip_address?: string;
  message: string;
}

export interface SecurityLogListResponse {
  logs: SecurityLog[];
  total?: number;
}

export interface Alert {
  id?: string | number;
  log_id: number;
  rule_id: string;
  rule_name: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  confidence_score: number;
  evidence?: any;
  created_at?: string;
}

export interface AlertListResponse {
  alerts: Alert[];
  total?: number;
}

export interface Incident {
  id?: string | number;
  incident_key: string;
  title: string;
  description: string;
  severity: string;
  priority_score: number;
  status?: string;
  confidence_score?: number;
  alert_count?: number;
  created_at?: string;
}

export interface IncidentListResponse {
  incidents: Incident[];
  total?: number;
}

export interface DetectionRule {
  rule_id: string;
  rule_name: string;
  description: string | null;
  severity: string | null;
}

export interface CorrelationRule {
  rule_id: string;
  rule_name: string;
  description: string | null;
  severity: string | null;
  time_window_minutes: number | null;
}

export interface StatusResponse {
  status: string;
  message: string;
  database_configured: boolean;
  database_connected: boolean;
}
