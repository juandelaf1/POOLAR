export default function Home() {
  return (
    <section>
      <h1>Producto (MVP scaffold)</h1>
      <p>Flujo gobernado: necesidades → problemas colectivos → iniciativas → decisiones.</p>
      <ul>
        <li>Conectar auth (token) contra API POOLAR.</li>
        <li>Listar/crear con manejo de <code>pending_review</code> (HITL).</li>
        <li>Respetar scope/errores fail-closed devueltos por la API.</li>
      </ul>
      <p className="muted">Pendiente: wiring real a endpoints, formularios, estados y RBAC en UI (la autoridad sigue en backend).</p>
    </section>
  )
}
