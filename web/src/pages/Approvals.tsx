import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, getToken } from '../api/client'
import type { ApprovalListItem } from '../api/types'

export default function Approvals() {
  const qc = useQueryClient()
  const authed = !!getToken()
  const q = useQuery({
    queryKey: ['approvals-pending'],
    queryFn: () => api<ApprovalListItem[]>('/approvals/pending'),
    enabled: authed,
    retry: false,
  })

  const approve = useMutation({
    mutationFn: (id: string) => api(`/approvals/${id}/approve`, { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['approvals-pending'] }),
  })
  const reject = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => api(`/approvals/${id}/reject?reason=${encodeURIComponent(reason)}`, { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['approvals-pending'] }),
  })

  if (!authed) return <section><h1>HITL / Aprobaciones</h1><p className="err">Inicia sesión para ver aprobaciones (gobernado por backend).</p></section>

  return (
    <section>
      <h1>HITL / Aprobaciones</h1>
      <p className="muted">POOLAR decide scope/roles/no autoaprobación. La UI solo presenta acciones permitidas por la API.</p>
      {q.isLoading && <p>Cargando…</p>}
      {q.error && <pre className="err">{String((q.error as any)?.message || q.error)}</pre>}
      {(approve.error || reject.error) && <pre className="err">{String((approve.error as any)?.message || (reject.error as any)?.message)}</pre>}
      {q.data && Array.isArray(q.data) && q.data.length === 0 && <p>Sin aprobaciones pendientes visibles.</p>}
      {q.data && Array.isArray(q.data) && q.data.map(a => (
        <div key={a.approval_id} style={{ background:'#fff', border:'1px solid #e5e7eb', padding:12, marginBottom:8 }}>
          <div><strong>{a.tool_name}</strong> <span className="muted">({a.status})</span></div>
          <div className="muted" style={{ fontSize:12 }}>{a.approval_id} · {a.reason || ''}</div>
          <div style={{ display:'flex', gap:8, marginTop:8 }}>
            <button onClick={() => approve.mutate(a.approval_id)} disabled={approve.isPending}>Aprobar</button>
            <button onClick={() => { const r = prompt('Motivo de rechazo',''); if (r !== null) reject.mutate({ id: a.approval_id, reason: r }) }} disabled={reject.isPending}>Rechazar</button>
          </div>
        </div>
      ))}
    </section>
  )
}
