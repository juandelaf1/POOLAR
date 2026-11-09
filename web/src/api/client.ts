import type { ApiError, TokenResponse } from './types'

export type { ApiError } from './types'
export { isPending } from './types'

const BASE = import.meta.env.VITE_API_BASE ?? '/api'
const TOKEN_KEY = 'poolar_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}
export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
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
  let data: any = null
  try { data = text ? JSON.parse(text) : null } catch { data = text }
  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || res.statusText || 'Error'
    const err: ApiError = { status: res.status, data, message: typeof msg === 'string' ? msg : JSON.stringify(msg) }
    throw err
  }
  return data as T
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const tok = await api<TokenResponse>('/auth/token', { method: 'POST', body: JSON.stringify({ email, password }) })
  if (tok?.access_token) setToken(tok.access_token)
  return tok
}
