/**
 * API Client
 * ──────────
 * Typed HTTP client for the FastAPI backend.
 * All functions throw on non-2xx responses.
 */

import type {
  IoC, PaginatedIoCs, Alert, DashboardSummary,
  IoCTypeStats, CountryStats, TimelinePoint,
} from '@/types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

// ── Fetch helper ──────────────────────────────────────────────────────

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

// ── Auth ──────────────────────────────────────────────────────────────

export async function login(email: string, password: string) {
  return apiFetch<{ access_token: string; role: string }>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

// ── IoCs ──────────────────────────────────────────────────────────────

export async function getIoCs(params?: {
  page?:       number
  size?:       number
  ioc_type?:   string
  risk_level?: string
  source?:     string
}): Promise<PaginatedIoCs> {
  const qs = new URLSearchParams()
  if (params?.page)       qs.set('page', String(params.page))
  if (params?.size)       qs.set('size', String(params.size))
  if (params?.ioc_type)   qs.set('ioc_type', params.ioc_type)
  if (params?.risk_level) qs.set('risk_level', params.risk_level)
  return apiFetch<PaginatedIoCs>(`/api/v1/iocs?${qs}`)
}

export async function getIoC(eventId: string): Promise<IoC> {
  return apiFetch<IoC>(`/api/v1/iocs/${eventId}`)
}

// ── Alerts ────────────────────────────────────────────────────────────

export async function getAlerts(limit = 20): Promise<{ items: Alert[]; total: number }> {
  return apiFetch(`/api/v1/alerts?limit=${limit}`)
}

// ── Stats ─────────────────────────────────────────────────────────────

export async function getSummary(): Promise<DashboardSummary> {
  return apiFetch('/api/v1/stats/summary')
}

export async function getStatsByType(): Promise<IoCTypeStats[]> {
  return apiFetch('/api/v1/stats/by-type')
}

export async function getStatsByCountry(): Promise<CountryStats[]> {
  return apiFetch('/api/v1/stats/by-country')
}

export async function getTimeline(): Promise<TimelinePoint[]> {
  return apiFetch('/api/v1/stats/timeline')
}

// ── SSE stream ────────────────────────────────────────────────────────

export function createIoCStream(
  onEvent: (ioc: Partial<IoC>) => void,
  onError?: (err: Event) => void,
): EventSource {
  const es = new EventSource(`${BASE_URL}/api/v1/stream/iocs`)
  es.onmessage = (e) => {
    try {
      onEvent(JSON.parse(e.data))
    } catch { /* ignore parse errors */ }
  }
  if (onError) es.onerror = onError
  return es
}
