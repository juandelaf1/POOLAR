-- mart: resumen HITL por tool/estado (métrica operativa, read-only)
select
  tool_name,
  status,
  count(*) as approvals,
  sum(is_executed) as executed_count
from {{ ref('stg_approval_requests') }}
group by 1, 2
