-- raw (bronze): approval_requests from JSONL export (read-only, no HITL).
-- Reproducible locally: defaults to sample data. Override with --vars '{"raw_path":"analytics/local/raw"}'
{% set raw_path = var('raw_path', 'analytics/sample/raw') %}
select
  approval_id,
  execution_id,
  tool_name,
  status,
  try_cast(organizacion_id as integer) as organizacion_id,
  proposer_type,
  try_cast(created_at as timestamp) as created_at,
  try_cast(executed_at as timestamp) as executed_at,
  _idempotency_key,
  _provenance
from read_json_auto('{{ raw_path }}/approval_requests.jsonl', union_by_name=true, ignore_errors=true)
where _idempotency_key is not null or approval_id is not null
