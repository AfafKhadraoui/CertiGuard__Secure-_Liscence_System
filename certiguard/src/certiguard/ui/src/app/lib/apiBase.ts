/**
 * Base URL for CertiGuard dashboard API.
 * Empty string = same origin (Flask serving the built UI, or Vite dev server with /api proxy).
 */
export const DASHBOARD_API_BASE =
  import.meta.env.VITE_DASHBOARD_API_BASE?.replace(/\/$/, "") ?? "";

export function dashboardApi(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${DASHBOARD_API_BASE}${p}`;
}
