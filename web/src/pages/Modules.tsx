import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export default function Modules() {
  const q = useQuery({
    queryKey: ['modules-capabilities'],
    queryFn: () => api<any>('/modules/capabilities'),
    retry: false,
  })
  return (
    <section>
      <h1>Módulos / Capacidades</h1>
      <p>Descubrimiento read-only (C1-02). Módulos autoejecutables aislados, componibles; sin autoridad de ejecución.</p>
      {q.isLoading && <p>Cargando…</p>}
      {q.error && <pre className="err">{String((q.error as any)?.message || q.error)} (requiere auth/config)</pre>}
      {q.data && <pre>{JSON.stringify(q.data, null, 2)}</pre>}
    </section>
  )
}
