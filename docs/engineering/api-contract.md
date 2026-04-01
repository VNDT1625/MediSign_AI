# API Contract v1

API base prefix: `/api/v1`

## Core endpoints

1. `GET /api/v1/health`
2. `POST /api/v1/consult/triage`
3. `POST /api/v1/medicine/scan`
4. `POST /api/v1/auth/login`
5. `POST /api/v1/auth/refresh`

## Error envelope

Tat ca loi 4xx/5xx tra ve schema:

```json
{
  "code": "AUTH_INVALID_CREDENTIALS",
  "message": "Sai email hoac mat khau",
  "details": null,
  "request_id": "d9f8..."
}
```

## Rule

- Khong doi ten field neu chua chot voi mobile.
- Moi thay doi phai cap nhat OpenAPI va file nay.
- Truoc PR phai qua contract validation trong quality gate.
