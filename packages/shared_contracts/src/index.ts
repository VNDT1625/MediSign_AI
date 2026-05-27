// @medisign/shared-contracts
//
// Public entry point re-exporting all TypeScript shape modules used by the
// web client (apps/web_next) and any other TS consumers. Each submodule maps
// 1-1 to a FastAPI Pydantic schema in apps/backend_fastapi/app/schemas
// (or, for drug catalog endpoints, to the response shape produced inline in
// apps/backend_fastapi/app/routers/drug.py).
//
// Consumers can either import the namespaced barrel:
//     import type { LoginInput, TriageResponse } from "@medisign/shared-contracts";
// or reach into a specific submodule via the package's subpath export:
//     import type { ApiErrorBody } from "@medisign/shared-contracts/common";

export type {
  LoginInput,
  RegisterInput,
  AuthTokenPair,
  AuthUserResponse,
  AuthLoginResponse,
  ChangePasswordRequest,
} from "./auth";

export type { TriageRequest, TriageResponse } from "./triage";

export type { MedicineScanRequest, MedicineScanResponse, CabinetItemCreate, CabinetItemUpdate, CabinetItem, CabinetListResponse } from "./medicine";

export type { DrugSearchRequest, DrugSearchResponse } from "./drug";

export type { ApiErrorBody } from "./common";
