# POOLAR Web (React + Vite + TS)

Frontend **fino** sobre la API POOLAR. **No duplica gobernanza**: authz, tenant, HITL/aprobaciones y ejecución las decide el backend.

## Dev
```powershell
cd poolar/web
npm install
npm run dev
```
- UI: http://127.0.0.1:5173
- Proxy `/api` → `http://127.0.0.1:8000` (config en `vite.config.ts`). Levanta FastAPI antes.

## Env
- `VITE_API_BASE` (opcional): base de API; por defecto `/api` (proxy dev).

## MVP
- Producto: necesidades → problemas → iniciativas → decisiones (manejar `pending_review`).
- HITL: `/approvals/*` según rol/política.
- Módulos: `/modules/capabilities` (read-only).
