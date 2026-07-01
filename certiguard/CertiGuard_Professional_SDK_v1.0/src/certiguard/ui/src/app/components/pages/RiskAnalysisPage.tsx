import { useState, useEffect } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { dashboardApi } from "../../lib/apiBase";

export function RiskAnalysisPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(dashboardApi("/api/risk"))
      .then((r) => r.json())
      .then((d) => { setData(d); setError(null); })
      .catch(() => setError("Could not connect to Dashboard API"));
  }, []);

  const stats = data?.stats ?? { global_risk_score: 0, total_threats: 0, critical_count: 0 };
  const threatCategories: any[] = data?.threat_categories ?? [];
  const riskTrend: any[] = data?.risk_trend ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Risk Analysis</h1>
        <p className="mt-0.5 text-sm text-gray-500">Threat intelligence derived from your real audit log</p>
      </div>

      {error && (
        <div className="rounded border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
          {error}. Make sure the CertiGuard Dashboard server is running.
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Global Risk Score</div>
          <div className={`text-3xl font-semibold ${stats.global_risk_score >= 70 ? "text-red-400" : stats.global_risk_score >= 40 ? "text-orange-400" : "text-emerald-400"}`}>
            {stats.global_risk_score}
          </div>
          <div className="mt-2 text-xs text-gray-400">Computed from audit log</div>
        </div>
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Total Events</div>
          <div className="text-3xl font-semibold">{stats.total_threats}</div>
          <div className="mt-2 text-xs text-gray-400">All recorded events</div>
        </div>
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-1 text-sm text-gray-400">Critical Events</div>
          <div className="text-3xl font-semibold text-red-400">{stats.critical_count}</div>
          <div className="mt-2 text-xs text-gray-400">Debug / tamper / clone</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Event Trend</h3>
            <p className="mt-0.5 text-xs text-gray-500">Events by date</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={riskTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <Tooltip contentStyle={{ backgroundColor: "#0d1117", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "4px", fontSize: "12px" }} />
              <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Threat Categories</h3>
            <p className="mt-0.5 text-xs text-gray-500">Distribution by attack vector</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={threatCategories} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis type="number" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis dataKey="category" type="category" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} width={80} />
              <Tooltip contentStyle={{ backgroundColor: "#0d1117", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "4px", fontSize: "12px" }} />
              <Bar dataKey="count" fill="#10b981" radius={[0, 2, 2, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
