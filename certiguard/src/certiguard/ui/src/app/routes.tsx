import { createBrowserRouter } from "react-router";
import { RootLayout } from "./components/layouts/RootLayout";
import { OverviewPage } from "./components/pages/OverviewPage";
import { ClientsPage } from "./components/pages/ClientsPage";
import { ClientDetailPage } from "./components/pages/ClientDetailPage";
import { BlacklistPage } from "./components/pages/BlacklistPage";
import { AuditLogsPage } from "./components/pages/AuditLogsPage";
import { RiskAnalysisPage } from "./components/pages/RiskAnalysisPage";
import { SettingsPage } from "./components/pages/SettingsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: "clients", element: <ClientsPage /> },
      { path: "clients/:clientId", element: <ClientDetailPage /> },
      { path: "blacklist", element: <BlacklistPage /> },
      { path: "audit-logs", element: <AuditLogsPage /> },
      { path: "risk-analysis", element: <RiskAnalysisPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
]);
