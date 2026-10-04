/**
 * Centralized API Gateway URL configuration.
 *
 * Handles both local development and production deployments (e.g. Vercel):
 * - If NEXT_PUBLIC_GATEWAY_URL is explicitly configured, it is prioritized.
 * - In the browser:
 *   - On localhost or 127.0.0.1: defaults to "http://localhost:8000".
 *   - On deployed domains (*.vercel.app, custom domains): returns "" (relative path),
 *     allowing requests to pass through Next.js rewrites and avoiding Mixed Content / CORS errors.
 * - On the server (Server Actions / Node.js runtime):
 *   - Reads GATEWAY_URL or NEXT_PUBLIC_GATEWAY_URL, falling back to "http://localhost:8000".
 */

export function getGatewayUrl(): string {
  if (typeof window !== "undefined") {
    if (process.env.NEXT_PUBLIC_GATEWAY_URL) {
      return process.env.NEXT_PUBLIC_GATEWAY_URL.replace(/\/$/, "")
    }

    const host = window.location.hostname
    const isLocal =
      host === "localhost" ||
      host === "127.0.0.1" ||
      host.startsWith("192.168.") ||
      host.startsWith("10.")

    if (!isLocal) {
      // In production browser, use relative paths so Next.js proxies or client connects via HTTPS
      return ""
    }

    return "http://localhost:8000"
  }

  // Server-side execution
  const serverUrl =
    process.env.GATEWAY_URL ||
    process.env.NEXT_PUBLIC_GATEWAY_URL ||
    "http://localhost:8000"

  return serverUrl.replace(/\/$/, "")
}
