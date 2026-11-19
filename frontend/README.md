# FinPilot-AI Frontend

A light-mode React + TypeScript showcase UI for the FastAPI backend. It intentionally integrates with the routes and request/response contracts shared for this project rather than inventing API responses.

## Included screens

- Sign in and create account
- Workspace overview and FastAPI root health check
- Agent task submission (`POST /agent-tasks`)
- Merchant CSV import (`POST /merchants/import`)
- Per-merchant financial CSV import (`POST /merchants/{merchant_id}/transactions/import`)
- Multi-file document upload (`POST /documents/UploadDocument`)
- Task result retrieval (`GET /reports/{task_id}/result`)
- Saved report listing (`GET /reports/tasks/{task_id}?merchant_id=...`)

The current backend snippets do not include endpoints to list merchants, list transactions, return dashboard aggregates, list reconciliation cases, or show task history. The UI does not fabricate those datasets. Add those endpoints later to unlock richer tables and charts.

## Requirements

- Node.js 20.19+ or 22.12+ recommended
- npm
- The FinPilot-AI FastAPI backend running separately

## Setup

1. Put this folder inside your repository, for example:

   ```text
   FinPilot-AI/
   ├── backend/
   └── frontend/  # copy this folder's contents here
   ```

2. Open a terminal in `frontend/` and install packages:

   ```bash
   npm install
   ```

3. Copy `.env.example` to `.env`:

   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```

   The value is the FastAPI origin only. Do not append `/api/v1` unless you add that prefix to the routers in FastAPI. The route snippets shared so far are mounted directly at `/auth`, `/agent-tasks`, `/documents`, `/merchants`, and `/reports`.

4. Start FastAPI on port 8000, then run the frontend:

   ```bash
   npm run dev
   ```

5. Open `http://localhost:5173`.

6. Register using the Create account tab, then sign in. Use the same test user that exists in your backend.

## Backend CORS configuration

Because Vite runs on port 5173 and FastAPI typically runs on port 8000, configure CORS in your FastAPI app. Add the middleware before starting the app (and before the app starts serving requests):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

`allow_credentials=True` is important because the refresh endpoint reads the `refresh_token` cookie. Do not use `allow_origins=["*"]` together with credentials.

## Important backend contract notes

1. **Login:** the UI sends `POST /auth/token` as `application/x-www-form-urlencoded` with `email` and `password`, matching your `LoginRequest` fields declared with `Form()`.
2. **Register:** the UI sends JSON `{ "username": "...", "email": "...", "password": "..." }`, matching the route's explicit `Body()` parameter. Confirm this against `/openapi.json`; `Form()` metadata inside your `signupUser` model may need adjustment depending on your FastAPI/Pydantic version.
3. **Refresh:** refresh is attempted on a 401 response from protected routes. Browser cookies are sent with `credentials: "include"`. This relies on the backend setting the refresh cookie with suitable `SameSite` and `Secure` values for the environment.
4. **Merchant imports:** `/merchants/import` currently has no authentication dependency in the snippet. Protect it with an admin/write dependency before deploying beyond local demo use.
5. **Merchant import response:** your `MerchantUploadResponse` `TypedDict` defines `{message, result}`, but your endpoint currently constructs it with `MerchantUploadResponse(message=..., **result)`. Make sure the actual returned response matches the declared schema, or FastAPI response validation may fail. A safer response shape is `{"message": "...", "result": result}`.
6. **Financial CSV import:** the endpoint requires a merchant UUID in the URL. Import one CSV per merchant unless you extend the CSV with a merchant key and implement multi-merchant routing in the backend. Your `Transaction` TypedDict also defines `{message, result}`, so return `{"message": "...", "result": result}` instead of spreading `**result` at the top level. Commit the SQLAlchemy session after a successful import if your `get_db` dependency does not commit automatically.
7. **Reports:** the list route needs `merchant_id` as a query parameter. The task result route currently has no `require_read_user` dependency in the shared snippet; add authentication and merchant ownership checks before exposing financial reports.
8. **Task submission:** the UI sends `Idempotency-Key` and the `AgentTaskCreate` fields `merchant_id`, `task_type`, `prompt`, and `input_data`.
9. **Documents:** the UI sends repeated multipart fields named `files`, as expected by `files: list[UploadFile]`.

## Build for deployment

```bash
npm run build
npm run preview
```

The production build is written to `dist/`. Serve it with Nginx or another static-file server. Configure `VITE_API_BASE_URL` at build time to point to your deployed FastAPI origin.

## Authentication note

For this portfolio/demo scaffold, the access token is stored in `localStorage` so the browser can attach it as a Bearer token. For a production application, prefer a carefully designed Secure, HttpOnly cookie-based session architecture and review CSRF protections. Never use real customer financial data in a public demo environment.
