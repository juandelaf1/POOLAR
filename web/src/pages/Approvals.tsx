import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export default function Approvals() {
  const q = useQuery({
    queryKey: ['approvals-pending'],
    queryFn: () => api<any>('/approvals/pending'),
    retry: false,
  })
  return (
    <section>
      <h1>HITL / Aprobaciones</h1>
      <p>Consola gobernada: ver/aprobar/rechazar/retirar según rol y política (POOLAR decide).</p>
      {q.isLoading && <p>Cargando…</p>}
      {q.error && <pre className="err">{String((q.error as any)?.message || q.error)} (requiere auth/config)</pre>}
      {q.data && <pre>{JSON.stringify(q.data, null, 2)}</pre>}
    </section>
  )
}
