-- staging: normalización HITL (sin PII; procede de raw redactado)
select
  approval_id,
  execution_id,
  tool_name,
  lower(status) as status,
  cast(organizacion_id as integer) as organizacion_id,
  proposer_type,
  cast(created_at as timestamp) as created_at,
  cast(executed_at as timestamp) as executed_at,
  case when executed_at is not null then 1 else 0 end as is_executed,
  _idempotency_key
from {{ ref('raw_approval_requests') }}
