import { useState, useEffect } from "react";
import { Link } from "react-router";
import { dashboardApi } from "../../lib/apiBase";

export function ClientsPage() {
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(dashboardApi("/api/clients"))
      .then((r) => r.json())
      .then((data) => { setClients(data); setError(null); })
      .catch(() => setError("Could not connect to Dashboard API"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Clients</h1>
        <p className="mt-0.5 text-sm text-gray-500">Monitor and manage licensed clients (derived from audit log)</p>
      </div>

      {error && (
        <div className="rounded border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
          {error}. Make sure the CertiGuard Dashboard server is running.
        </div>
      )}

      <div className="rounded border border-white/5 bg-[#0d1117] overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Client ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Hardware Fingerprint</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">License</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Risk</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Events</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Last Seen</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {clients.map((client) => (
              <tr key={client.id} className="group transition-colors hover:bg-white/[0.02]">
                <td className="px-4 py-3">
                  <div className="text-sm font-medium font-mono">{client.id}</div>
                </td>
                <td className="px-4 py-3">
                  <code className="text-xs text-gray-400">{client.hardware_fingerprint?.slice(0, 20)}…</code>
                </td>
                <td className="px-4 py-3">
                  <code className="text-xs text-gray-400">{client.license}</code>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-xs ${
                    client.status === "blacklisted" ? "bg-red-500/10 text-red-400" :
                    client.status === "suspicious" ? "bg-orange-500/10 text-orange-400" :
                    "bg-emerald-500/10 text-emerald-400"
                  }`}>
                    <div className={`h-1 w-1 rounded-full ${
                      client.status === "blacklisted" ? "bg-red-400" :
                      client.status === "suspicious" ? "bg-orange-400" :
                      "bg-emerald-400"
                    }`} />
                    {client.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1 w-16 overflow-hidden rounded-full bg-white/5">
                      <div
                        className={`h-full ${client.risk >= 70 ? "bg-red-500" : client.risk >= 40 ? "bg-orange-500" : "bg-emerald-500"}`}
                        style={{ width: `${client.risk ?? 0}%` }}
                      />
                    </div>
                    <span className={`text-xs ${client.risk >= 70 ? "text-red-400" : client.risk >= 40 ? "text-orange-400" : "text-emerald-400"}`}>
                      {client.risk ?? 0}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">{client.events}</td>
                <td className="px-4 py-3 text-xs text-gray-500">
                  {client.last_seen ? new Date(client.last_seen).toLocaleString() : "—"}
                </td>
              </tr>
            ))}
            {!loading && clients.length === 0 && !error && (
              <tr>
                <td colSpan={7} className="py-10 text-center text-sm text-gray-500">
                  No clients identified in audit log yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
