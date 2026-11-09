// Contrato UI (alineado a API POOLAR observada). La autoridad/validación final es del backend.

export type TokenResponse = { access_token: string; token_type?: string }

export type PendingReview = {
  status: 'pending_review'
  approval_id: string
  nota?: string
  governance_route?: string
  governance_reasons?: string[]
}

export type ApprovalStatus =
  | 'pendiente'
  | 'aprobada'
  | 'rechazada'
  | 'expirada'
  | 'ejecutando'
  | 'ejecutada'
  | 'fallida_reintentable'
  | string

export type ApprovalListItem = {
  approval_id: string
  execution_id: string
  tool_name: string
  status: ApprovalStatus
  proposed_by?: number | null
  organizacion_id?: number | null
  reason?: string | null
  created_at?: string | null
  expires_at?: string | null
}

export type ApprovalDetail = ApprovalListItem & {
  approved_by?: number | null
  approved_at?: string | null
  rejected_by?: number | null
  rejected_at?: string | null
  rejection_reason?: string | null
  executed_at?: string | null
  execution_result?: unknown
  execution_error?: string | null
}

export type ApiError = { status: number; data?: any; message: string }

export function isPending(x: any): x is PendingReview {
  return x && x.status === 'pending_review' && typeof x.approval_id === 'string'
}
