import { useParams, Link } from "react-router";
import { ArrowLeft } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const clientData: any = {
  "8F3A": {
    name: "Acme Corporation",
    license: "LIC-8F3A-9B2C",
    status: "blacklisted",
    risk: 95,
    users: { max: 50, active: 48 },
    modules: ["Core", "Analytics"],
    expiry: "2026-12-31",
    hardware: {
      cpu: "Intel Xeon E5-2680 v4",
      motherboard: "ASUS Z10PE-D16 WS",
      fingerprint: "8f3a9b2c4e7d1a8f",
    },
    installation: {
      uuid: "550e8400-e29b-41d4-a716-446655440000",
      bootCounter: 1247,
      lastBoot: "2026-04-24 14:32:15",
    },
    events: [
      { id: 1, message: "License signature verification failed", time: "2m ago", severity: "critical" },
      { id: 2, message: "User count modification detected", time: "1h ago", severity: "critical" },
      { id: 3, message: "VM snapshot rollback attempt", time: "3h ago", severity: "high" },
      { id: 4, message: "Debugger attachment detected", time: "5h ago", severity: "high" },
      { id: 5, message: "Usage pattern deviation (σ=3.2)", time: "8h ago", severity: "medium" },
    ],
  },
  "B921": {
    name: "TechVault Inc",
    license: "LIC-B921-4E7D",
    status: "suspicious",
    risk: 72,
    users: { max: 120, active: 115 },
    modules: ["Core", "Security"],
    expiry: "2027-03-15",
    hardware: {
      cpu: "AMD EPYC 7542",
      motherboard: "Supermicro H11DSi",
      fingerprint: "b9214e7d1a8f6c3b",
    },
    installation: {
      uuid: "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      bootCounter: 892,
      lastBoot: "2026-04-24 09:15:42",
    },
    events: [
      { id: 1, message: "Virtual machine clone detected", time: "5m ago", severity: "high" },
      { id: 2, message: "Anomaly score increased to 72", time: "2h ago", severity: "medium" },
      { id: 3, message: "Concurrent session spike detected", time: "6h ago", severity: "medium" },
    ],
  },
};

const riskTrend = [
  { time: "6h", risk: 45 },
  { time: "5h", risk: 52 },
  { time: "4h", risk: 61 },
  { time: "3h", risk: 73 },
  { time: "2h", risk: 82 },
  { time: "1h", risk: 89 },
  { time: "now", risk: 95 },
];

export function ClientDetailPage() {
  const { clientId } = useParams();
  const client = clientData[clientId as string];

  if (!client) {
    return (
      <div className="flex h-full items-center justify-center">
        <Link to="/clients" className="text-emerald-400 hover:text-emerald-300">
          Return to Clients
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          to="/clients"
          className="flex h-8 w-8 items-center justify-center rounded border border-white/5 bg-white/5 transition-colors hover:bg-white/10"
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold">{client.name}</h1>
            {client.status === "blacklisted" && (
              <span className="rounded bg-red-500/10 px-2 py-0.5 text-xs font-medium text-red-400">
                Blacklisted
              </span>
            )}
          </div>
          <p className="mt-0.5 text-sm text-gray-500">Client-{clientId}</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-4 text-sm font-medium text-gray-400">License Information</div>
          <div className="space-y-3">
            <div>
              <div className="mb-1 text-xs text-gray-500">License ID</div>
              <code className="text-sm text-gray-300">{client.license}</code>
            </div>
            <div>
              <div className="mb-1 text-xs text-gray-500">Max Users</div>
              <div className="text-sm">{client.users.max}</div>
            </div>
            <div>
              <div className="mb-1 text-xs text-gray-500">Modules</div>
              <div className="flex gap-1">
                {client.modules.map((mod: string) => (
                  <span key={mod} className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-xs text-emerald-400">
                    {mod}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <div className="mb-1 text-xs text-gray-500">Expiration</div>
              <div className="text-sm">{client.expiry}</div>
            </div>
          </div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-4 text-sm font-medium text-gray-400">Hardware Binding</div>
          <div className="space-y-3">
            <div>
              <div className="mb-1 text-xs text-gray-500">CPU</div>
              <div className="text-sm">{client.hardware.cpu}</div>
            </div>
            <div>
              <div className="mb-1 text-xs text-gray-500">Motherboard</div>
              <div className="text-sm">{client.hardware.motherboard}</div>
            </div>
            <div>
              <div className="mb-1 text-xs text-gray-500">Fingerprint</div>
              <code className="text-xs text-gray-400">{client.hardware.fingerprint}</code>
            </div>
          </div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-4 text-sm font-medium text-gray-400">Installation</div>
          <div className="space-y-3">
            <div>
              <div className="mb-1 text-xs text-gray-500">UUID</div>
              <code className="break-all text-xs text-gray-400">{client.installation.uuid}</code>
            </div>
            <div>
              <div className="mb-1 text-xs text-gray-500">Boot Counter</div>
              <div className="text-sm">{client.installation.bootCounter}</div>
            </div>
            <div>
              <div className="mb-1 text-xs text-gray-500">Last Boot</div>
              <div className="text-sm">{client.installation.lastBoot}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="flex flex-col items-center justify-center rounded border border-white/5 bg-[#0d1117] p-8">
          <div className="mb-2 text-sm text-gray-500">Risk Score</div>
          <div className="text-5xl font-semibold">{client.risk}</div>
          <div className={`mt-3 text-xs ${client.risk >= 70 ? "text-red-400" : "text-orange-400"}`}>
            {client.risk >= 70 ? "Critical" : "High"} Risk
          </div>
        </div>

        <div className="col-span-2 rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-5">
            <h3 className="text-sm font-medium">Risk Trend</h3>
            <p className="mt-0.5 text-xs text-gray-500">Last 6 hours</p>
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={riskTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: "11px" }} tick={{ fill: '#6b7280' }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0d1117",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "4px",
                  fontSize: "12px",
                }}
              />
              <Line type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded border border-white/5 bg-[#0d1117] p-5">
        <div className="mb-5">
          <h3 className="text-sm font-medium">Security Events</h3>
          <p className="mt-0.5 text-xs text-gray-500">Recent threat detections</p>
        </div>
        <div className="space-y-2">
          {client.events.map((event: any) => (
            <div
              key={event.id}
              className="flex items-center justify-between rounded border border-white/5 bg-white/[0.02] p-3"
            >
              <div className="flex-1">
                <div className="text-sm">{event.message}</div>
                <div className="mt-0.5 text-xs text-gray-500">{event.time}</div>
              </div>
              <span className={`rounded px-2 py-0.5 text-xs font-medium ${
                event.severity === "critical" ? "bg-red-500/10 text-red-400" :
                event.severity === "high" ? "bg-orange-500/10 text-orange-400" :
                "bg-yellow-500/10 text-yellow-400"
              }`}>
                {event.severity}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
