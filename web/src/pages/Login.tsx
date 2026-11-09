import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/client'

export default function Login() {
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErr(null); setBusy(true)
    try {
      await login(email, password)
      nav('/approvals')
    } catch (e: any) {
      setErr(e?.message || 'Error de autenticación')
    } finally { setBusy(false) }
  }

  return (
    <section>
      <h1>Ingresar</h1>
      <p className="muted">Auth contra API POOLAR (backend conserva autoridad/roles).</p>
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 8, maxWidth: 360 }}>
        <input placeholder="email" value={email} onChange={e => setEmail(e.target.value)} autoComplete="username" />
        <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" />
        <button type="submit" disabled={busy}>{busy ? 'Ingresando…' : 'Ingresar'}</button>
      </form>
      {err && <p className="err">{err}</p>}
    </section>
  )
}
