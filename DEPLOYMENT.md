# Deployment

Two deployables: the FastAPI backend (Docker, on Render or Railway) and the Next.js frontend (Vercel).
Valkey runs locally for the demo (or a managed instance in production). Firebase is already hosted.

## Backend environment variables

| Variable | Required | Notes |
|---|---|---|
| FIREBASE_DB_URL | yes | The Realtime Database URL |
| FIREBASE_SERVICE_ACCOUNT_JSON | yes (managed) | Full service-account JSON as a single env value |
| GOOGLE_APPLICATION_CREDENTIALS | yes (local) | Path to the JSON file (use this OR the one above) |
| GEMINI_API_KEY | yes | Free-tier key |
| GEMINI_MAX_RPM | no | Default 12; lower if throttled |
| BREETH_API_KEY | yes | The ck_live_ project key |
| CORS_ORIGINS | yes (prod) | JSON list, e.g. ["https://your-app.vercel.app"] |
| CORS_ORIGIN_REGEX | no | e.g. https://.*\.vercel\.app for preview deploys |
| VALKEY_HOST / VALKEY_PORT / VALKEY_USE_TLS / VALKEY_PASSWORD | yes | Your Valkey instance |

## Frontend environment variables (Vercel)

| Variable | Notes |
|---|---|
| NEXT_PUBLIC_FIREBASE_API_KEY | Public web config (not a secret) |
| NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN | venturemind-ca40a.firebaseapp.com |
| NEXT_PUBLIC_FIREBASE_PROJECT_ID | venturemind-ca40a |
| NEXT_PUBLIC_FIREBASE_DATABASE_URL | The RTDB URL |
| NEXT_PUBLIC_FIREBASE_APP_ID | From Firebase console |
| NEXT_PUBLIC_API_BASE_URL | The deployed backend URL (e.g. https://venturemind-api.onrender.com) |

## Deploy the backend (Render)

1. Push the repo to GitHub.
2. In Render: New > Blueprint, point at `infra/render.yaml`. It builds `apps/api/Dockerfile`.
3. Fill the `sync: false` env vars in the dashboard. Paste the service-account JSON into
   FIREBASE_SERVICE_ACCOUNT_JSON.
4. Set CORS_ORIGINS to your Vercel URL once the frontend is deployed.
5. Health check is `/health`.

Railway is equivalent: new service from the repo, root `apps/api`, it detects the Dockerfile; set the
same env vars; Railway injects `$PORT`.

## Deploy the frontend (Vercel)

1. Import the repo in Vercel. Set the Root Directory to `apps/web` (it detects Next.js).
2. Add the NEXT_PUBLIC_* env vars and NEXT_PUBLIC_API_BASE_URL (the backend URL).
3. Deploy. Add the resulting domain to the backend's CORS_ORIGINS and redeploy the backend.

## Firebase (once)

- Authentication: enable Google sign-in; add the Vercel domain to Authorized domains.
- Realtime Database: publish rules with `firebase deploy --only database` (uses `database.rules.json`).

## Valkey

- Demo: `docker compose -f infra/docker-compose.yml up -d` on the demo machine (valkey-bundle ships
  valkey-search for vector queries). Point VALKEY_HOST at it.
- Production: a managed Valkey 8.2+ (with search) instance; set host/port/TLS/password envs.

## Pre-demo runbook

1. Start Valkey; confirm `valkey-cli ping` and `FT._LIST` shows the indexes after the API boots.
2. Backend up; `GET /health` returns ok.
3. Frontend up; sign in works; `/users/{uid}` created.
4. Walk SMOKE_TEST.md end to end with the real keys.
5. Warm the cache: run your two demo ideas once each so the live run is instant and the telemetry
   panel already shows a healthy hit rate and Gemini-calls-saved.
6. Keep the dashboard telemetry panel visible while presenting; it proves Valkey + Breeth are live.
