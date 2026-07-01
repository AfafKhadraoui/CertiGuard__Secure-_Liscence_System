import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { useState, useEffect } from "react";
import { dashboardApi } from "../../lib/apiBase";

export function OverviewPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const load = () =>
      fetch(dashboardApi("/api/overview"))
        .then((r) => r.json())
        .then(setData)
        .catch(console.error);
    load();
    const iv = setInterval(load, 3000);
    return () => clearInterval(iv);
  }, []);

  const stats = data?.stats ?? { total_events: 0, blacklisted: 0, suspicious: 0, safe: 0 };
  const activityData = data?.activity_by_hour ?? [];
  const threatData = data?.threat_by_day ?? [];
  const liveEvents: any[] = data?.recent_events ?? [];
  const layerStatus: any[] = data?.layer_status ?? Array.from({ length: 10 }, (_, i) => ({
    layer: `L${i + 1}`,
    name: "Pending",
    state: "active",
    state_color: "green",
    last_code: "ACTIVE",
    last_message: "Monitoring",
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Overview</h1>
        <p className="mt-0.5 text-sm text-gray-500">Real-time license protection and threat monitoring</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Security Health Score</div>
          <div className={`text-3xl font-semibold ${stats.risk_score > 70 ? "text-red-400" : stats.risk_score > 30 ? "text-orange-400" : "text-emerald-400"}`}>
            {100 - stats.risk_score}%
          </div>
          <div className="mt-2 text-xs text-gray-400">Aggregated risk assessment</div>
        </div>
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Total Events</div>
          <div className="text-3xl font-semibold">{stats.total_events.toLocaleString()}</div>
          <div className="mt-2 text-xs text-gray-400">All-time from audit log</div>
        </div>
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Critical</div>
          <div className="text-3xl font-semibold text-red-400">{stats.blacklisted}</div>
          <div className="mt-2 text-xs text-red-400">High-severity events</div>
        </div>
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">AI Anomalies</div>
          <div className="text-3xl font-semibold text-orange-400">{data?.stats?.risk_score > 0 ? "Alert" : "Clean"}</div>
          <div className="mt-2 text-xs text-orange-400">Behavioral drift analysis</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Event Activity</h3>
            <p className="mt-0.5 text-xs text-gray-500">Events by hour of day</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={activityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <Tooltip contentStyle={{ backgroundColor: "#0d1117", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "4px", fontSize: "12px" }} />
              <Line type="monotone" dataKey="activity" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Status Distribution</h3>
            <p className="mt-0.5 text-xs text-gray-500">From audit log</p>
          </div>
          <div className="space-y-4">
            {[
              { label: "Normal", value: stats.safe, color: "bg-emerald-500", pct: stats.total_events ? (stats.safe / stats.total_events) * 100 : 0 },
              { label: "High Risk", value: stats.suspicious, color: "bg-orange-500", pct: stats.total_events ? (stats.suspicious / stats.total_events) * 100 : 0 },
              { label: "Critical", value: stats.blacklisted, color: "bg-red-500", pct: stats.total_events ? (stats.blacklisted / stats.total_events) * 100 : 0 },
            ].map((row) => (
              <div key={row.label}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-gray-400">{row.label}</span>
                  <span className="font-medium">{row.value}</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                  <div className={`h-full ${row.color}`} style={{ width: `${row.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded border border-white/5 bg-[#0d1117] p-5">
        <div className="mb-4">
          <h3 className="text-sm font-medium">Layer Status (L1-L10)</h3>
          <p className="mt-0.5 text-xs text-gray-500">Green = active, orange/red = triggered by attacks or anomalies</p>
        </div>
        <div className="grid grid-cols-5 gap-3">
          {layerStatus.map((ls) => {
            const stateClass =
              ls.state_color === "red"
                ? "border-red-500/30 bg-red-500/10 text-red-300"
                : ls.state_color === "orange"
                ? "border-orange-500/30 bg-orange-500/10 text-orange-300"
                : "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
            return (
              <div key={ls.layer} className={`rounded border p-3 ${stateClass}`}>
                <div className="flex items-center justify-between">
                  <div className="text-xs font-semibold">{ls.layer}</div>
                  <div className="text-[10px] uppercase">{ls.state}</div>
                </div>
                <div className="mt-1 text-xs text-white">{ls.name}</div>
                <div className="mt-2 text-[10px] text-gray-300">{ls.last_code}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium">Security Events</h3>
              <p className="mt-0.5 text-xs text-gray-500">Real-time threat feed from audit.log</p>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
              <span className="text-xs text-gray-400">Live</span>
            </div>
          </div>
          <div className="space-y-2">
            {liveEvents.slice(0, 5).map((event: any) => (
              <div key={event.id} className="flex items-center justify-between rounded border border-white/5 bg-white/[0.02] p-3 transition-colors hover:bg-white/5">
                <div className="flex-1">
                  <div className="text-sm">{event.message}</div>
                  <div className="mt-0.5 text-xs text-gray-400">
                    [{event.layer ?? "N/A"}] {event.code ?? event.event}
                  </div>
                  <div className="mt-0.5 text-xs text-gray-500">{new Date(event.timestamp).toLocaleTimeString()}</div>
                </div>
                <span className={`rounded px-2 py-0.5 text-xs font-medium uppercase ${
                  event.severity === "critical" ? "bg-red-500/10 text-red-400" :
                  event.severity === "high" ? "bg-orange-500/10 text-orange-400" :
                  event.severity === "medium" ? "bg-yellow-500/10 text-yellow-400" :
                  "bg-emerald-500/10 text-emerald-400"
                }`}>
                  {event.severity}
                </span>
              </div>
            ))}
            {liveEvents.length === 0 && (
              <div className="py-8 text-center text-sm text-gray-500">No events recorded yet.</div>
            )}
          </div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Threat Activity</h3>
            <p className="mt-0.5 text-xs text-gray-500">Events by day</p>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={threatData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <Tooltip contentStyle={{ backgroundColor: "#0d1117", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "4px", fontSize: "12px" }} />
              <Bar dataKey="count" fill="#10b981" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
