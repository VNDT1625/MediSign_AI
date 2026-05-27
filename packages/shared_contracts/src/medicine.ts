// @medisign/shared-contracts/medicine
//
// Medicine scan shapes + cabinet CRUD shapes. Maps 1-1 to
// apps/backend_fastapi/app/schemas/medicine.py.

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
 */
export interface MedicineScanResponse {
  /** Canonical medicine name resolved from the OCR / typed text. */
  normalized_name: string;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "low" | "medium" | "high" | string;
  /** Free-form warnings (interactions, contraindications). */
  warnings: string[];
  /** Single paragraph of usage / safety guidance. */
  guidance: string;
}

// ---------------------------------------------------------------------------
// Cabinet CRUD — maps to POST/GET/PATCH/DELETE /api/v1/medicine/cabinet
// ---------------------------------------------------------------------------

/** Body for POST /api/v1/medicine/cabinet */
export interface CabinetItemCreate {
  name: string;
  dosage?: string | null;
  risk_level?: string | null;
  warnings?: string[];
  guidance?: string | null;
  remaining_pills?: number | null;
  doctor_notes?: string | null;
  start_date?: string | null; // ISO date "YYYY-MM-DD"
  end_date?: string | null;
}

/** Body for PATCH /api/v1/medicine/cabinet/{id} */
export interface CabinetItemUpdate {
  dosage?: string | null;
  risk_level?: string | null;
  warnings?: string[];
  guidance?: string | null;
  remaining_pills?: number | null;
  doctor_notes?: string | null;
  is_active?: boolean;
  start_date?: string | null;
  end_date?: string | null;
}

/** Single cabinet item returned by all cabinet endpoints. */
export interface CabinetItem {
  id: string;
  name: string;
  dosage: string | null;
  risk_level: string | null;
  warnings: string[];
  guidance: string | null;
  remaining_pills: number | null;
  doctor_notes: string | null;
  is_active: boolean;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
}

/** Response for GET /api/v1/medicine/cabinet */
export interface CabinetListResponse {
  items: CabinetItem[];
  total: number;
}

