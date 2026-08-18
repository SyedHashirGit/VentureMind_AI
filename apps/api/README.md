# VentureMind AI — Backend (FastAPI)

The AI agent orchestrator and integration layer for VentureMind AI. Built with FastAPI (Python), this backend powers the core intelligence of the startup incubator.

## 🏗 Architecture

The backend handles all heavy lifting, orchestrating Gemini agents, caching with Valkey, managing Breeth memory, and persisting data to Firebase.

- `app/core` — Application configuration, environment variables, Firebase token verification middleware, and error handling.
- `app/services` — External service integrations:
  - **Firebase:** Realtime Database system of record.
  - **Valkey:** High-performance GLIDE client for semantic caching (vector search), Pub/Sub, and token-bucket rate limiting.
  - **Gemini:** The reasoning engine behind the agents.
  - **Breeth:** Long-term founder memory (MCP integration) to personalize analyses.
- `app/agents` — The intelligence layer. Contains the seven-member board (CEO, CTO, PM, Investor, Marketing, Competitor, Legal) and the orchestrator that manages debate rounds (independent analysis, cross-examination, synthesis).
- `app/routers` — REST endpoints for workspaces, validation, memory, Shark Tank sessions, and the Startup Time Machine.
- `app/realtime` — Valkey Pub/Sub to browser Server-Sent Events (SSE) relay for live boardroom streaming.

## 🚀 Run Locally

### 1. Start Dependencies
You need Valkey running locally with the `valkey-search` module.
```bash
docker compose -f ../../infra/docker-compose.yml up -d
```

### 2. Configure Secrets
All secrets are strictly loaded from environment variables and never committed to version control.
```bash
cp .env.example .env
```
Edit `.env` and provide:
- `GEMINI_API_KEY`
- `BREETH_API_KEY`
- `FIREBASE_DB_URL`

Additionally, download your Firebase service-account JSON key and place it at:
`./secrets/serviceAccount.json`

### 3. Install and Run
It is highly recommended to use a virtual environment.
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health`

## 🧪 Testing

The test suite runs pure-logic unit tests with no network or external services (native/network dependencies are stubbed).

```bash
pip install -r requirements-dev.txt
pytest
```

**Coverage includes:**
- Prompt-injection sanitization
- Agent schema validation and bounds checking
- Validation engine self-repair fallback
- Semantic-cache vector packing and `FT.SEARCH` parsing
- Breeth MCP text and SSE parsing
- Telemetry aggregation

## 🔐 Security Posture

- **No Secrets in Source:** Secrets load from `.env` only. Nothing sensitive is committed.
- **Token Verification:** Firebase Auth ID tokens are verified server-side via the Firebase Admin SDK on every protected API call.
- **Rate Limiting:** Every AI endpoint is protected by a token-bucket Valkey rate limiter to prevent abuse and manage Gemini API spend.
