// @medisign/shared-contracts/medicine
//
// Medicine scan shapes. Maps 1-1 to
// apps/backend_fastapi/app/schemas/medicine.py.
//
// Phase 1 backend exposes only `POST /api/v1/medicine/scan` (one-shot
// analysis, not persisted). The web client persists a "cabinet" in
// `localStorage["medisign:cabinet"]` until the backend grows a CRUD
// endpoint in Phase 2.

/**
 * Body sent to `POST /api/v1/medicine/scan`. `extracted_text` is what
 * the user typed (or what an OCR step produced) for the medicine label.
 */
export interface MedicineScanRequest {
  /** 2..500 chars. */
  extracted_text: string;
  /**
   * Optional list of medicine names already in the user's cabinet. Used
   * by the backend AI service to surface interaction warnings.
   * Defaults to `[]` server-side.
   */
  current_medications?: string[];
}

/**
 * Body returned by `POST /api/v1/medicine/scan`.
 *
 * `risk_level` is `str` on the backend; the web client narrows it to a
 * known union with a string fallback for forward compatibility.
 */
export interface MedicineScanResponse {
  /** Canonical medicine name resolved from the OCR / typed text. */
  normalized_name: string;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | string;
  /** Free-form warnings (interactions, contraindications). */
  warnings: string[];
  /** Single paragraph of usage / safety guidance. */
  guidance: string;
}
