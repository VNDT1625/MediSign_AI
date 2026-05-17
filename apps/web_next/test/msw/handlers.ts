// MSW v2 handlers + fixture builders for the MediSign FastAPI surface.
//
// These handlers mock the endpoints that the web client (apps/web_next)
// consumes during unit / integration tests. They are intentionally
// permissive about the request origin: the URL patterns are prefixed
// with `*` so the same handlers work whether tests hit
// `http://localhost:8000/api/v1/...` (the default `NEXT_PUBLIC_API_BASE_URL`)
// or any other base URL a future Playwright run configures.
//
// FastAPI mounting (verified against `apps/backend_fastapi/app/api/router.py`
// and `apps/backend_fastapi/app/main.py`):
//   - `app` includes `api_router` with `prefix=settings.api_prefix` (`/api/v1`).
//   - Auth router       → `/auth/*`              → `/api/v1/auth/*`
//   - Consult router    → `/consult/*`           → `/api/v1/consult/*`
//   - Medicine router   → `/medicine/*`          → `/api/v1/medicine/*`
//   - Drug router       → `/api/drug/*`          → `/api/v1/api/drug/*`
//
// Fixture builders return values that satisfy the shared-contracts
// TypeScript types so callers can spread overrides without losing type
// safety. Tests typically import a builder and pass overrides to
// `server.use(...)` for the case being exercised.

import { http, HttpResponse } from "msw";
import type {
  ApiErrorBody,
  AuthLoginResponse,
  AuthTokenPair,
  AuthUserResponse,
  DrugSearchResponse,
  MedicineScanResponse,
  TriageResponse,
} from "@medisign/shared-contracts";

// ---------------------------------------------------------------------------
// URL helpers
// ---------------------------------------------------------------------------

/**
 * URL prefix used by every handler. The leading `*` matches any origin,
 * so tests can target the production base URL or any localhost port
 * without re-registering handlers.
 */
const API = "*/api/v1";

// ---------------------------------------------------------------------------
// Fixture builders (typed against `@medisign/shared-contracts`)
// ---------------------------------------------------------------------------

export function buildAuthUserResponse(
  overrides: Partial<AuthUserResponse> = {},
): AuthUserResponse {
  return {
    id: "00000000-0000-0000-0000-000000000001",
    email: "test.user@medisign.ai",
    phone: "+84900000001",
    username: "test_user",
    full_name: "Người Dùng Thử",
    is_email_verified: true,
    is_phone_verified: false,
    account_type: "user",
    created_at: "2024-01-01T00:00:00Z",
    ...overrides,
  };
}

export function buildAuthTokenPair(
  overrides: Partial<AuthTokenPair> = {},
): AuthTokenPair {
  return {
    access_token: "test-access-token",
    refresh_token: "test-refresh-token",
    token_type: "bearer",
    expires_in: 3600,
    ...overrides,
  };
}

export function buildAuthLoginResponse(
  overrides: Partial<AuthLoginResponse> = {},
): AuthLoginResponse {
  return {
    user: buildAuthUserResponse(),
    tokens: buildAuthTokenPair(),
    ...overrides,
  };
}

export function buildTriageResponse(
  overrides: Partial<TriageResponse> = {},
): TriageResponse {
  return {
    urgency_level: "GREEN",
    summary: "Triệu chứng nhẹ, có thể theo dõi tại nhà.",
    recommendations: [
      "Uống nhiều nước và nghỉ ngơi.",
      "Tái khám nếu sốt cao liên tục trên 48 giờ.",
    ],
    ...overrides,
  };
}

export function buildMedicineScanResponse(
  overrides: Partial<MedicineScanResponse> = {},
): MedicineScanResponse {
  return {
    normalized_name: "Paracetamol 500mg",
    risk_level: "LOW",
    warnings: [],
    guidance: "Dùng 1 viên mỗi 6 giờ, không quá 4 viên/ngày.",
    ...overrides,
  };
}

export function buildDrugSearchResponse(
  overrides: Partial<DrugSearchResponse> = {},
): DrugSearchResponse {
  return {
    status: "found",
    drug: {
      name: "Paracetamol",
      description: "Thuốc giảm đau, hạ sốt thông dụng.",
    },
    ...overrides,
  };
}

export function buildApiErrorBody(
  overrides: Partial<ApiErrorBody> = {},
): ApiErrorBody {
  return {
    code: "HTTP_ERROR",
    message: "Yêu cầu thất bại",
    details: null,
    request_id: "test-request-id",
    ...overrides,
  };
}

/**
 * Shape of the drug suggestions response. The backend builds this body
 * inline in `apps/backend_fastapi/app/routers/drug_router.py` (no Pydantic
 * schema), so the type lives here rather than in `@medisign/shared-contracts`.
 */
export interface DrugSuggestionsResponse {
  keyword: string;
  count: number;
  suggestions: Record<string, unknown>[];
}

export function buildDrugSuggestionsResponse(
  overrides: Partial<DrugSuggestionsResponse> = {},
): DrugSuggestionsResponse {
  const base: DrugSuggestionsResponse = {
    keyword: "paracetamol",
    count: 1,
    suggestions: [{ name: "Paracetamol 500mg" }],
  };
  return { ...base, ...overrides };
}

// ---------------------------------------------------------------------------
// Default handlers — happy-path responses for every endpoint the web client
// touches in Phase 1. Tests override individual handlers via `server.use(...)`
// to exercise error paths (401, 409, 5xx, network failure).
// ---------------------------------------------------------------------------

export const defaultHandlers = [
  // ---- auth -----------------------------------------------------------------

  http.post(`${API}/auth/login`, () =>
    HttpResponse.json(buildAuthLoginResponse()),
  ),

  http.post(`${API}/auth/refresh`, () =>
    HttpResponse.json(
      buildAuthTokenPair({
        access_token: "test-access-token-rotated",
        refresh_token: "test-refresh-token-rotated",
      }),
    ),
  ),

  http.post(`${API}/auth/logout`, () =>
    HttpResponse.json({ message: "Đã đăng xuất" }),
  ),

  http.get(`${API}/auth/me`, () =>
    HttpResponse.json(buildAuthUserResponse()),
  ),

  http.post(`${API}/auth/change-password`, () =>
    HttpResponse.json({ message: "Đổi mật khẩu thành công" }),
  ),

  // ---- consult / triage -----------------------------------------------------

  http.post(`${API}/consult/triage`, () =>
    HttpResponse.json(buildTriageResponse()),
  ),

  // ---- medicine -------------------------------------------------------------

  http.post(`${API}/medicine/scan`, () =>
    HttpResponse.json(buildMedicineScanResponse()),
  ),

  // ---- drug catalog (router has its own `/api/drug` prefix beneath /api/v1) -

  http.get(`${API}/api/drug/suggestions/:keyword`, ({ params }) => {
    const keyword =
      typeof params.keyword === "string" ? params.keyword : "paracetamol";
    return HttpResponse.json(buildDrugSuggestionsResponse({ keyword }));
  }),

  http.post(`${API}/api/drug/search`, () =>
    HttpResponse.json(buildDrugSearchResponse()),
  ),
];
