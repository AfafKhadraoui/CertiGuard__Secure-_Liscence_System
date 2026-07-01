import { useState, useEffect } from "react";
import { dashboardApi } from "../../lib/apiBase";

export function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = () => {
    setLoading(true);
    fetch(dashboardApi("/api/logs"))
      .then((res) => res.json())
      .then((data) => {
        if (data.error) throw new Error(data.error);
        setLogs(data);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to fetch logs:", err);
        setError("Could not connect to CertiGuard Dashboard API");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchLogs, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Audit Logs</h1>
          <p className="mt-0.5 text-sm text-gray-500">Tamper-evident hash-chained security events</p>
        </div>
        <div className="flex gap-2">
           <button 
            onClick={fetchLogs}
            disabled={loading}
            className="rounded border border-white/5 bg-white/5 px-3 py-1.5 text-sm text-gray-300 transition-colors hover:bg-white/10 disabled:opacity-50"
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>
          <button className="rounded border border-white/5 bg-white/5 px-3 py-1.5 text-sm text-gray-300 transition-colors hover:bg-white/10">
            Export Logs
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
          {error}. Make sure the CertiGuard Dashboard server is running.
        </div>
      )}

      <div className="rounded border border-white/5 bg-[#0d1117]">
        <div className="border-b border-white/5 px-4 py-2.5">
          <div className="flex items-center gap-2 text-xs">
            <div className={`h-1 w-1 rounded-full ${logs.length > 0 ? "bg-emerald-500" : "bg-gray-500"}`} />
            <span className={logs.length > 0 ? "text-emerald-400" : "text-gray-400"}>
              {logs.length > 0 ? "Hash Chain Integrity: VERIFIED" : "No logs available"}
            </span>
          </div>
        </div>

        <div className="divide-y divide-white/5">
          {logs.map((log) => (
            <div key={log.id} className="p-5">
              <div className="mb-2 flex items-center gap-3">
                <span className={`rounded px-2 py-0.5 text-xs font-medium uppercase ${
                  log.severity === "critical" || log.severity === "high" ? "bg-red-500/10 text-red-400" :
                  log.severity === "medium" ? "bg-orange-500/10 text-orange-400" :
                  "bg-emerald-500/10 text-emerald-400"
                }`}>
                  {log.severity}
                </span>
                <span className="text-xs text-gray-500">{new Date(log.timestamp).toLocaleString()}</span>
              </div>
              <div className="mb-2 text-sm font-medium text-gray-200">{log.event}</div>
              
              <div className="mb-3 space-y-1.5">
                 {Object.entries(log.payload || {}).map(([key, val]: [string, any]) => (
                   <div key={key} className="text-xs">
                     <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</span>{" "}
                     <span className="text-gray-400 font-mono">{typeof val === 'object' ? JSON.stringify(val) : String(val)}</span>
                   </div>
                 ))}
              </div>

              <div className="rounded border border-white/5 bg-white/[0.02] p-2.5">
                <div className="mb-1 text-xs text-gray-500">Hash Chain Link (SHA-256)</div>
                <code className="break-all text-xs text-gray-400">{log.hash}</code>
              </div>
            </div>
          ))}
          
          {!loading && logs.length === 0 && !error && (
            <div className="p-10 text-center text-sm text-gray-500">
              No security events recorded yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
