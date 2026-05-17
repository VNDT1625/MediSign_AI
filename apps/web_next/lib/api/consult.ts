/**
 * `lib/api/consult.ts` — typed wrappers around the FastAPI `consult`
 * router (`apps/backend_fastapi/app/api/routes/consult.py`).
 *
 * Phase 1 surface:
 *   - `POST /consult/triage`         (anonymous — no auth required)
 *   - `GET  /consult/triage/history` (auth required, returns []  for now)
 *
 * Per design.md "Page-by-Page Wiring → /app/chat", the triage endpoint is
 * called without a bearer to keep parity with mobile and to allow the
 * public `/chat` try-it page to use the same code path. The history
 * endpoint is auth-gated on the backend (depends on `get_current_user`).
 *
 * @see Requirements 2.3.1 (chat AI wiring), 2.5.1 (shared contracts).
 */

import type {
  TriageRequest,
  TriageResponse,
} from "@medisign/shared-contracts";

import { apiFetch } from "./fetcher";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/**
 * Body returned by `GET /api/v1/consult/triage/history`.
 *
 * The backend currently declares the response as `list[TriageResponse]`
 * and returns `[]` as a placeholder until persistence is implemented
 * (see TODO in `consult.py`). The web client therefore types this as a
 * plain array of triage records — Phase 2 may expand the per-record
 * shape (timestamps, ids) without breaking this type signature, since
 * backend-side additions are forward-compatible additive changes.
 */
export type TriageHistoryResponse = TriageResponse[];

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

/**
 * Submit a free-form symptom description for AI triage.
 *
 * The backend endpoint is anonymous-friendly (`POST /consult/triage`
 * has no auth dependency), so the web client deliberately omits the
 * bearer header. This keeps the public `/chat` try-it page reusable
 * without juggling auth state.
 *
 * @param input symptom text (3..1000 chars) plus optional locale (default
 *   `"vi-VN"` server-side).
 * @returns Triage assessment with urgency, summary, and recommendations.
 */
export function triage(input: TriageRequest): Promise<TriageResponse> {
  return apiFetch<TriageResponse>("/consult/triage", {
    method: "POST",
    body: input,
    authRequired: false,
  });
}

/**
 * Fetch the authenticated user's triage history.
 *
 * Phase 1: backend returns `[]` until persistence lands. The UI renders
 * an empty-state and stitches in-session turns locally — see design.md
 * "/app/chat" sidebar wiring.
 */
export function triageHistory(): Promise<TriageHistoryResponse> {
  return apiFetch<TriageHistoryResponse>("/consult/triage/history", {
    method: "GET",
  });
}
