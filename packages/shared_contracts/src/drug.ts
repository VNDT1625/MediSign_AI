// @medisign/shared-contracts/drug
//
// Drug catalog lookup shapes for the `/api/drug/*` router. The backend
// has no Pydantic schema file for these endpoints (responses are built
// inline in `apps/backend_fastapi/app/routers/drug.py`); the shapes
// below are the canonical TS contract used by the web client and are
// mirrored from design.md "Data Models".

/**
 * Body sent to `POST /api/drug/search`.
 */
export interface DrugSearchRequest {
  /** Drug name (or synonym) to look up in the catalog. */
  drug_name: string;
  /** Preferred response language. Backend default: `"vi"`. */
  language?: "vi" | "en";
}

/**
 * Body returned by `POST /api/drug/search`.
 *
 * The backend returns one of three shapes depending on `status`:
 *  - `"found"`     → `drug` populated with full details.
 *  - `"ambiguous"` → `suggestions` populated with candidate matches.
 *  - `"not_found"` → `message` populated with a user-facing string.
 *
 * The opaque `Record<string, unknown>` shapes intentionally avoid
 * locking down the catalog entry until a Pydantic schema is defined
 * upstream.
 */
export interface DrugSearchResponse {
  status: "found" | "not_found" | "ambiguous";
  drug?: Record<string, unknown>;
  suggestions?: Record<string, unknown>[];
  message?: string;
}
