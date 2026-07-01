import { Outlet, Link, useLocation } from "react-router";
import { Shield, Users, AlertTriangle, FileText, TrendingUp, Settings, Search } from "lucide-react";

const navigation = [
  { name: "Overview", href: "/" },
  { name: "Clients", href: "/clients" },
  { name: "Blacklist", href: "/blacklist" },
  { name: "Audit Logs", href: "/audit-logs" },
  { name: "Risk Analysis", href: "/risk-analysis" },
  { name: "Settings", href: "/settings" },
];

export function RootLayout() {
  const location = useLocation();

  return (
    <div className="flex min-h-screen bg-[#0a0e1a] text-white">
      <aside className="fixed left-0 top-0 z-40 h-screen w-56 border-r border-white/5 bg-[#0d1117]">
        <div className="flex h-14 items-center gap-2.5 border-b border-white/5 px-5">
          <div className="flex h-7 w-7 items-center justify-center rounded bg-emerald-500/10">
            <Shield className="h-4 w-4 text-emerald-500" strokeWidth={2.5} />
          </div>
          <span className="text-sm font-semibold tracking-tight">CertiGuard</span>
        </div>

        <nav className="space-y-0.5 p-3">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href ||
              (item.href !== "/" && location.pathname.startsWith(item.href));

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`block rounded px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-emerald-500/10 text-emerald-400"
                    : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="ml-56 flex-1">
        <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-white/5 bg-[#0a0e1a]/80 px-6 backdrop-blur-sm">
          <div className="relative w-80">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="Search clients..."
              className="w-full rounded border border-white/5 bg-white/5 py-1.5 pl-9 pr-3 text-sm text-white placeholder-gray-500 transition-colors focus:border-emerald-500/30 focus:bg-white/10 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              <span className="text-gray-400">System Online</span>
            </div>
          </div>
        </header>

        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
