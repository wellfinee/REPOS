# StudiumX LMS (Frontend + Backend auth notes)

## How auth works

1. **Login**: `POST /api/auth/login/` with `identifier`, `password`, `remember_me`.
   - Response body: `{ success, access }`.
   - Server also sets `refresh_token` into **HttpOnly cookie**.
2. **Access token storage**:
   - Access JWT is kept in Redux (`auth.accessToken`) and mirrored to `sessionStorage`/`localStorage` only according to `rememberMe` policy.
3. **Refresh token storage**:
   - Refresh JWT stays only in `HttpOnly` cookie (`withCredentials: true` in axios).
4. **Authenticated requests**:
   - Main axios client attaches `Authorization: Bearer <access>` from Redux.
5. **401 handling**:
   - For requests that were originally Bearer-authenticated, interceptor calls `POST /api/auth/refresh/` through isolated `refreshClient`.
   - New access token is written to store, queued requests are replayed once refresh finishes.
   - Infinite loops are prevented with `_retry` guard and no refresh on `login/refresh/logout` endpoints.
6. **Profile and roles source of truth**:
   - Right after login, frontend calls `/api/auth/me/` and stores result in `auth.me`.
   - UI role checks (e.g. `SCHOOL_ADMIN`) use `auth.me.roles`.
   - `localStorage` roles are used only as optional cache fallback, not as source of truth.

## Common issues & troubleshooting

### Set-Cookie blocked in dev
- Cause: mixed hosts (`127.0.0.1` vs `localhost`) produce cross-site cookie behavior.
- Fix:
  - Frontend API URL must be `http://localhost:8000` (`VITE_API_URL`).
  - Frontend app should run on `http://localhost:5173`.
  - Backend CORS defaults now prioritize localhost.

### `No refresh cookie`
- Verify `withCredentials: true` on axios clients.
- Verify browser actually receives `Set-Cookie` from login response.
- Verify host consistency (`localhost` everywhere).

### Refresh loop on 401
- Refresh now runs only if:
  - response status is 401,
  - original request had Bearer token,
  - request is not auth endpoint.
- Requests without Authorization will not trigger refresh/hard logout.

### `401 credentials not provided`
- Main axios client now always attaches Bearer token from Redux for non-auth endpoints.
- Ensure requests use shared `http` instance (`src/shared/api/http.js`).

### `Token has no id` / SimpleJWT conflicts
- DRF default auth switched to custom `studiumx_main.authentication.AccessJWTAuthentication`.
- SimpleJWT is excluded from auth chain to avoid token format mismatch with custom JWT.

### 401 vs 403
- `401` = missing/invalid/expired auth token.
- `403` = authenticated user lacks permission (e.g. wrong school/role).

## DB SQL (Docker)

> `dbschema` app is used as ORM/model layer. **Schema changes are not managed via Django migrations** for critical tables; apply them directly in PostgreSQL inside Docker.

### Idempotent SQL

```sql
ALTER TABLE refresh_tokens
  ADD COLUMN IF NOT EXISTS is_persistent boolean NOT NULL DEFAULT false;

CREATE UNIQUE INDEX IF NOT EXISTS uq_refresh_tokens_jti ON refresh_tokens (jti);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_expires_at ON refresh_tokens (expires_at);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS ix_refresh_tokens_active ON refresh_tokens (user_id, expires_at)
  WHERE revoked_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_students_user_id ON students (user_id);
CREATE INDEX IF NOT EXISTS ix_teachers_user_id ON teachers (user_id);
CREATE INDEX IF NOT EXISTS ix_parents_user_id ON parents (user_id);
```

### PowerShell: run SQL directly

```powershell
docker exec <postgres_container> psql -U <db_user> -d <db_name> -c "ALTER TABLE refresh_tokens ADD COLUMN IF NOT EXISTS is_persistent boolean NOT NULL DEFAULT false;"

docker exec <postgres_container> psql -U <db_user> -d <db_name> -c "CREATE UNIQUE INDEX IF NOT EXISTS uq_refresh_tokens_jti ON refresh_tokens (jti);"
```

### PowerShell: run from `.sql` file

```powershell
Get-Content .\db\auth_indexes.sql | docker exec -i <postgres_container> psql -U <db_user> -d <db_name>
```

## Post-change verification checklist

- Login request returns `success` and `access`, and Network shows `Set-Cookie: refresh_token=...`.
- `POST /api/auth/refresh/` receives cookie and returns new access token.
- `GET /api/users/<uuid>/` works with `Authorization: Bearer <access>`.
- Expired access token triggers automatic refresh and original request retry.
- Roles from `/api/auth/me/` toggle UI elements (e.g. `Настроить`) via store.
- No React warning about state update/navigation during render in `LoginPage`.
