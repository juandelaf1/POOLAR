import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { api, getToken, isPending } from '../api/client'
import type { Necesidad } from '../api/types'

export default function Necesidades() {
  const qc = useQueryClient()
  const authed = !!getToken()
  const [titulo, setTitulo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [visibilidad, setVisibilidad] = useState('privada')
  const [msg, setMsg] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['necesidades'], queryFn: () => api<Necesidad[]>('/necesidades'), enabled: authed, retry: false })
  const create = useMutation({
    mutationFn: () => {
      const p = new URLSearchParams({ titulo, descripcion, visibilidad })
      return api<any>(`/necesidades?${p.toString()}`, { method: 'POST' })
    },
    onSuccess: (res) => {
      if (isPending(res)) setMsg(`Pendiente HITL: ${res.approval_id}`)
      else setMsg('Necesidad creada')
      setTitulo(''); setDescripcion('')
      qc.invalidateQueries({ queryKey: ['necesidades'] })
    },
    onError: (e: any) => setMsg(e?.message || 'Error'),
  })

  if (!authed) return <section><h1>Necesidades</h1><p className="err">Inicia sesión.</p></section>
  return (
    <section>
      <h1>Necesidades</h1>
      <div style={{ display:'grid', gap:8, maxWidth:520, marginBottom:16 }}>
        <input placeholder="Título" value={titulo} onChange={e=>setTitulo(e.target.value)} />
        <textarea placeholder="Descripción" value={descripcion} onChange={e=>setDescripcion(e.target.value)} />
        <select value={visibilidad} onChange={e=>setVisibilidad(e.target.value)}>
          <option value="privada">privada</option>
          <option value="compartida">compartida</option>
          <option value="publica">publica</option>
        </select>
        <button onClick={()=>create.mutate()} disabled={create.isPending || !titulo.trim()}>Crear</button>
        {msg && <p className={msg.startsWith('Error') ? 'err' : 'muted'}>{msg}</p>}
      </div>
      {q.isLoading && <p>Cargando…</p>}
      {q.error && <pre className="err">{String((q.error as any)?.message || q.error)}</pre>}
      {Array.isArray(q.data) && q.data.map(n => (
        <div key={n.id} style={{ background:'#fff', border:'1px solid #e5e7eb', padding:10, marginBottom:6 }}>
          <strong>#{n.id} {n.titulo}</strong> <span className="muted">({n.estado} / {n.visibilidad})</span>
          {n.descripcion && <div className="muted">{n.descripcion}</div>}
        </div>
      ))}
    </section>
  )
}
