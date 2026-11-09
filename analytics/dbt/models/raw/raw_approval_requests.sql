-- raw: approval_requests export (medallion). Fuente: analytics/local/raw/approval_requests.jsonl
-- Ejemplo DuckDB: select * from read_json_auto('analytics/local/raw/approval_requests.jsonl');
select
  approval_id,
  execution_id,
  tool_name,
  status,
  organizacion_id,
  proposer_type,
  created_at,
  executed_at,
  _idempotency_key,
  _provenance
from {{ source('poolar_raw', 'approval_requests') }}
where _idempotency_key is not null
