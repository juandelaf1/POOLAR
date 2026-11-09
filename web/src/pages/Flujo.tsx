import { isPending } from '../api/client'

export function PendingBanner({ res }: { res: unknown }) {
  if (!isPending(res)) return null
  const r = res as { approval_id?: string; nota?: string }
  return <div role="status" aria-live="polite" style={{ background:'#fef3c7', border:'1px solid #f59e0b', padding:10, margin:'8px 0' }}>
    <strong>HITL pendiente:</strong> <code>{r.approval_id}</code> — {r.nota || 'Revisión humana requerida. Sin efecto ejecutado.'}
  </div>
}

export default function Flujo() {
  return (
    <section>
      <h1>Flujo gobernado</h1>
      <p>Secuencia: <strong>Necesidades → Problemas colectivos → Iniciativas → Decisiones</strong>. Toda acción sensible pasa por política/HITL; si la API devuelve <code>pending_review</code>, no hay efecto hasta aprobación autorizada.</p>
      <ol>
        <li><a href="/necesidades">Necesidades</a> (implementado MVP)</li>
        <li>Problemas colectivos (conectar POST /problemas-colectivos, JSON, synthetic_pilot)</li>
        <li>Iniciativas (conectar POST /iniciativas, requiere necesidad/responsable/criterios)</li>
        <li>Decisiones (POST /decisiones o /iniciativas/:id/decisiones)</li>
      </ol>
      <p className="muted">Pendiente de wiring UI: formularios completos + manejo uniforme de <code>pending_review</code>/403/404 fail-closed.</p>
    </section>
  )
}
