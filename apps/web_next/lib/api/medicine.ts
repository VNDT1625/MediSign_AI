/**
 * `lib/api/medicine.ts` — typed wrappers around the FastAPI medicine and
 * drug surface used by `/app/medicine` (Phase 1).
 *
 * Surface:
 *   - `POST /medicine/scan`                  (auth required) — analyse OCR text
 *   - `GET  /api/drug/suggestions/{keyword}` (auth required) — autocomplete
 *   - `POST /api/drug/search`                (auth required) — full lookup
 *
 * URL routing note:
 * The drug router on the FastAPI side declares its own `/api/drug` prefix,
 * so when mounted under the global `/api/v1` prefix the resolved upstream
 * URL is `/api/v1/api/drug/...` (yes, double `/api/` — that is what the
 * backend exposes). The fetcher's `resolveUrl()` only short-circuits paths
 * starting with `/api/auth/` (the Next.js Route Handler proxies); every
 * other leading-`/` path is forwarded to `NEXT_PUBLIC_API_BASE_URL`. So
 * passing `"/api/drug/..."` here resolves to
 * `${API_BASE}/api/drug/...` → `http://localhost:8000/api/v1/api/drug/...`,
 * which is exactly what FastAPI mounts.
 *
 * The MSW handlers in `apps/web_next/test/msw/handlers.ts` use the
 * pattern `*‍/api/v1/api/drug/...` which matches the resolved URL.
 *
 * @see Requirements 2.3.2 (medicine cabinet wiring), 2.5.1 (shared
 *   contracts).
 */

import type {
  DrugSearchRequest,
  DrugSearchResponse,
  MedicineScanRequest,
  MedicineScanResponse,
} from "@medisign/shared-contracts";

import { apiFetch } from "./fetcher";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/**
 * Body returned by `GET /api/drug/suggestions/{keyword}`.
 *
 * The backend builds this response inline in
 * `apps/backend_fastapi/app/routers/drug_router.py` (no Pydantic schema),
 * so the type lives here rather than in `@medisign/shared-contracts`.
 * The opaque `Record<string, unknown>` matches the same conservative
 * stance taken by `DrugSearchResponse.suggestions` until a canonical
 * Pydantic model is defined upstream.
 */
export interface DrugSuggestionsResponse {
  /** Echo of the lookup keyword (URL path segment, server-decoded). */
  keyword: string;
  /** Number of `suggestions` returned (≤ `limit`, default 5 server-side). */
  count: number;
  /** Catalog rows; shape follows `MedicineRegistry` columns. */
  suggestions: Record<string, unknown>[];
}

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

/**
 * Submit a medicine label / OCR text to the AI scan service.
 *
 * Returns a normalized name plus risk level, warnings, and guidance. The
 * web client persists results locally in `localStorage["medisign:cabinet"]`
 * until the backend grows a CRUD endpoint (Phase 2).
 *
 * Endpoint: `POST /api/v1/medicine/scan`
 *
 * @param input `extracted_text` (2..500 chars) and optional
 *   `current_medications` for interaction analysis.
 * @see Requirements 2.3.2.
 */
export function scan(
  input: MedicineScanRequest,
): Promise<MedicineScanResponse> {
  return apiFetch<MedicineScanResponse>("/medicine/scan", {
    method: "POST",
    body: input,
  });
}

/**
 * Autocomplete drug names against the local catalog.
 *
 * The keyword is interpolated into the URL path, so it must be safe
 * for path use — we apply `encodeURIComponent` to defend against
 * accidental `/`, `?`, or unicode characters in user input.
 *
 * Endpoint: `GET /api/v1/api/drug/suggestions/{keyword}` (the inner
 * `/api/drug/...` belongs to the FastAPI drug router itself; see the
 * "URL routing note" in this file's header).
 *
 * @param keyword Free-text search prefix (2+ chars recommended).
 * @see Requirements 2.3.2.
 */
export function drugSuggestions(
  keyword: string,
): Promise<DrugSuggestionsResponse> {
  return apiFetch<DrugSuggestionsResponse>(
    `/api/drug/suggestions/${encodeURIComponent(keyword)}`,
    { method: "GET" },
  );
}

/**
 * Full drug lookup. Returns one of three shapes per `status`
 * (`"found"`, `"ambiguous"`, `"not_found"`) — see `DrugSearchResponse`
 * in `@medisign/shared-contracts`.
 *
 * Endpoint: `POST /api/v1/api/drug/search` (the inner `/api/drug/...`
 * belongs to the FastAPI drug router itself; see the "URL routing
 * note" in this file's header).
 *
 * @param input Drug name (≥ 2 chars, server-validated) and optional
 *   response language.
 * @see Requirements 2.3.2.
 */
export function drugSearch(
  input: DrugSearchRequest,
): Promise<DrugSearchResponse> {
  return apiFetch<DrugSearchResponse>("/api/drug/search", {
    method: "POST",
    body: input,
  });
}
