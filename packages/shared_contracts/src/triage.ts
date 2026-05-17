// @medisign/shared-contracts/triage
//
// Consult / triage shapes. Maps 1-1 to
// apps/backend_fastapi/app/schemas/triage.py.
//
// `POST /api/v1/consult/triage` is anonymous-friendly on the backend but
// the web client always sends the Bearer access token to keep parity
// with mobile and to enable history association in future phases.

/**
 * Body sent to `POST /api/v1/consult/triage`.
 */
export interface TriageRequest {
  /** Free-form symptom description. 3..1000 chars (server-validated). */
  symptom_text: string;
  /** BCP-47 locale; backend default `"vi-VN"`. 2..10 chars. */
  locale?: string;
}

/**
 * Body returned by `POST /api/v1/consult/triage`.
 *
 * `urgency_level` is a free-form string on the backend, but the AI
 * service is contracted to emit one of `GREEN | YELLOW | RED`. The
 * fallback `string` keeps the type forward-compatible with new tiers
 * without requiring an immediate contract bump.
 */
export interface TriageResponse {
  urgency_level: "GREEN" | "YELLOW" | "RED" | string;
  /** Short narrative summary of the assessment. */
  summary: string;
  /** Ordered list of next-step recommendations rendered as bullets. */
  recommendations: string[];
}
