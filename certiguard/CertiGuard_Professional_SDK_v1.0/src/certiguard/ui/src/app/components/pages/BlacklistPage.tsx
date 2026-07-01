import { useState, useEffect } from "react";

import { dashboardApi } from "../../lib/apiBase";

export function BlacklistPage() {
  const [blacklist, setBlacklist] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(dashboardApi("/api/blacklist"))
      .then((r) => r.json())
      .then((data) => { setBlacklist(data); setError(null); })
      .catch(() => setError("Could not connect to Dashboard API"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Blacklist</h1>
          <p className="mt-0.5 text-sm text-gray-500">Blocked clients and enforcement actions (from audit log)</p>
        </div>
        <div className="rounded border border-white/5 bg-[#0d1117] px-4 py-2">
          <div className="text-2xl font-semibold text-red-400">{blacklist.length}</div>
          <div className="text-xs text-gray-500">Blocked</div>
        </div>
      </div>

      {error && (
        <div className="rounded border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
          {error}. Make sure the CertiGuard Dashboard server is running.
        </div>
      )}

      <div className="space-y-3">
        {blacklist.map((client) => (
          <div key={client.id} className="rounded border border-white/5 bg-[#0d1117] p-5 transition-colors hover:border-red-500/20">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="mb-3 flex items-center gap-3">
                  <h3 className="font-medium font-mono">{client.id}</h3>
                  <span className="rounded bg-red-500/10 px-2 py-0.5 text-xs font-medium text-red-400">
                    Blacklisted
                  </span>
                </div>
                <code className="text-xs text-gray-400">{client.hardware_fingerprint}</code>
                <div className="mt-3 text-sm text-gray-300">{client.reason}</div>
                <div className="mt-3 flex gap-6 text-sm">
                  <div>
                    <span className="text-gray-500">Events:</span>{" "}
                    <span className="font-medium text-red-400">{client.events}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">First seen:</span>{" "}
                    <span className="text-gray-300">{client.first_seen ? new Date(client.first_seen).toLocaleString() : "—"}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Last seen:</span>{" "}
                    <span className="text-gray-300">{client.last_seen ? new Date(client.last_seen).toLocaleString() : "—"}</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="rounded border border-white/5 bg-white/5 px-3 py-1.5 text-sm text-gray-300 transition-colors hover:bg-white/10">
                  Review
                </button>
              </div>
            </div>
          </div>
        ))}

        {!loading && blacklist.length === 0 && !error && (
          <div className="rounded border border-white/5 bg-[#0d1117] p-10 text-center text-sm text-gray-500">
            No blacklisted clients detected yet.
          </div>
        )}
      </div>
    </div>
  );
}
