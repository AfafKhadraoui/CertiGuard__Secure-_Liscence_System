export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Settings</h1>
        <p className="mt-0.5 text-sm text-gray-500">Configure security enforcement and monitoring</p>
      </div>

      <div className="space-y-4">
        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-4 text-sm font-medium">Security Enforcement</div>
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded border border-white/5 bg-white/[0.02] p-3">
              <div>
                <div className="text-sm">License Signature Verification</div>
                <div className="text-xs text-gray-500">Ed25519 cryptographic validation</div>
              </div>
              <label className="relative inline-flex cursor-pointer items-center">
                <input type="checkbox" className="peer sr-only" defaultChecked />
                <div className="peer h-5 w-9 rounded-full bg-white/10 after:absolute after:left-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
              </label>
            </div>
            <div className="flex items-center justify-between rounded border border-white/5 bg-white/[0.02] p-3">
              <div>
                <div className="text-sm">Hardware Fingerprinting</div>
                <div className="text-xs text-gray-500">CPU + Motherboard binding</div>
              </div>
              <label className="relative inline-flex cursor-pointer items-center">
                <input type="checkbox" className="peer sr-only" defaultChecked />
                <div className="peer h-5 w-9 rounded-full bg-white/10 after:absolute after:left-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
              </label>
            </div>
            <div className="flex items-center justify-between rounded border border-white/5 bg-white/[0.02] p-3">
              <div>
                <div className="text-sm">VM Clone Detection</div>
                <div className="text-xs text-gray-500">Detect snapshot rollback</div>
              </div>
              <label className="relative inline-flex cursor-pointer items-center">
                <input type="checkbox" className="peer sr-only" defaultChecked />
                <div className="peer h-5 w-9 rounded-full bg-white/10 after:absolute after:left-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
              </label>
            </div>
            <div className="flex items-center justify-between rounded border border-white/5 bg-white/[0.02] p-3">
              <div>
                <div className="text-sm">Debugger Detection</div>
                <div className="text-xs text-gray-500">Block reverse engineering</div>
              </div>
              <label className="relative inline-flex cursor-pointer items-center">
                <input type="checkbox" className="peer sr-only" defaultChecked />
                <div className="peer h-5 w-9 rounded-full bg-white/10 after:absolute after:left-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all peer-checked:bg-emerald-500 peer-checked:after:translate-x-full"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-4 text-sm font-medium">AI Anomaly Detection</div>
          <div className="space-y-4">
            <div className="rounded border border-white/5 bg-white/[0.02] p-3">
              <div className="mb-3 flex items-center justify-between">
                <div>
                  <div className="text-sm">Risk Score Threshold</div>
                  <div className="text-xs text-gray-500">Trigger alerts when exceeded</div>
                </div>
                <span className="font-semibold text-orange-400">70</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                defaultValue="70"
                className="h-1 w-full cursor-pointer appearance-none rounded-full bg-white/10"
              />
            </div>
            <div className="rounded border border-white/5 bg-white/[0.02] p-3">
              <div className="mb-3 flex items-center justify-between">
                <div>
                  <div className="text-sm">Anomaly Sensitivity</div>
                  <div className="text-xs text-gray-500">Standard deviations from baseline</div>
                </div>
                <span className="font-semibold text-emerald-400">2.5σ</span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                step="0.5"
                defaultValue="2.5"
                className="h-1 w-full cursor-pointer appearance-none rounded-full bg-white/10"
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="rounded border border-white/5 bg-[#0d1117] p-5">
            <div className="mb-4 text-sm font-medium">Audit Log Retention</div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Retention Period</span>
                <span>365 days</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Current Storage</span>
                <span className="text-emerald-400">2.4 GB</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Chain Integrity</span>
                <span className="text-emerald-400">VERIFIED</span>
              </div>
            </div>
          </div>

          <div className="rounded border border-white/5 bg-[#0d1117] p-5">
            <div className="mb-4 text-sm font-medium">Monitoring Intervals</div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">License Check</span>
                <span>Every 5 min</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Hardware Scan</span>
                <span>Every 15 min</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Anomaly Analysis</span>
                <span>Every 1 hour</span>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-4 text-sm font-medium">Alert Notifications</div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-2 block text-sm text-gray-400">Email Alerts</label>
              <input
                type="email"
                placeholder="security@company.com"
                className="w-full rounded border border-white/5 bg-white/5 px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500/30 focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-2 block text-sm text-gray-400">Webhook URL</label>
              <input
                type="url"
                placeholder="https://api.company.com/alerts"
                className="w-full rounded border border-white/5 bg-white/5 px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-emerald-500/30 focus:outline-none"
              />
            </div>
          </div>
        </div>

        <div className="rounded border border-white/5 bg-[#0d1117] p-5">
          <div className="mb-4 text-sm font-medium">Cryptographic Keys</div>
          <div className="space-y-3">
            <div className="rounded border border-white/5 bg-white/[0.02] p-3">
              <div className="mb-2 text-xs text-gray-500">Public Key Fingerprint</div>
              <code className="break-all text-sm text-gray-400">
                SHA256:nThbg6kXUpJWGl7E1IGOCspRomTxdCARLviKw6E5SY8
              </code>
            </div>
            <div className="flex gap-3">
              <button className="flex-1 rounded border border-white/5 bg-white/5 px-4 py-2 text-sm text-gray-300 transition-colors hover:bg-white/10">
                Rotate Keys
              </button>
              <button className="flex-1 rounded border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-400 transition-colors hover:bg-red-500/20">
                Revoke Key
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
