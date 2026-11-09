// Cliente API fino. No duplica gobernanza; POOLAR decide permisos/HITL/ejecución.
export type PendingReview = { status: 'pending_review'; approval_id: string; nota?: string; governance_route?: string }

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

function getToken(): string | null {
  return localStorage.getItem('poolar_token')
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken()
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers || {}),
    },
  })
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if (!res.ok) throw Object.assign(new Error(data?.detail || res.statusText), { status: res.status, data })
  return data as T
}

export function isPending(x: any): x is PendingReview {
  return x && x.status === 'pending_review' && typeof x.approval_id === 'string'
}
