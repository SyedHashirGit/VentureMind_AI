# VentureMind AI

An AI startup incubator that turns raw ideas into board-grade blueprints. A founder enters one idea; an AI boardroom of seven expert agents validates it, debates it, stress-tests it, and returns an investor-ready blueprint, a live investor grilling (Shark Tank Live), and a five-year forecast (Startup Time Machine).

Built for **Build Beyond Limits 2.0** (Track B, "Valkey for AI"). Powered by Gemini, Valkey, and Breeth.

![VentureMind AI Concept](https://img.shields.io/badge/Status-Hackathon_Complete-success?style=for-the-badge)

## 🚀 Features

VentureMind AI is more than a chatbot; it's a dedicated workspace for startup ideation. 

* **The Boardroom:** Watch specialized agents (CEO, CTO, PM, Investor, Marketing, Competitor, Legal) analyze your idea, stream their reasoning live, and resolve disagreements to build a consensus.
* **Validation Center:** Receive four critical scores (viability, market opportunity, execution difficulty, funding attractiveness) with detailed rationales and market analysis.
* **Shark Tank Live:** Face a virtual investor panel (YC Partner, Sequoia Partner, etc.) with distinct personas. Answer their hard questions and get scored on confidence, funding probability, and pitch quality.
* **Startup Time Machine:** Fast-forward into the future with 1-month to 5-year forecasts across optimistic, realistic, and worst-case scenarios on a visual timeline.
* **Founder Memory:** Powered by Breeth, the system remembers your profile, risk tolerance, and past ideas, personalizing future interactions and getting smarter over time.

## 🏗 Architecture

The platform separates a high-performance Python reasoning backend from a premium React frontend.

* **Frontend (`apps/web`)** — Next.js 15 (App Router), React 19, TypeScript, Tailwind v4, Framer Motion, Firebase Auth.
* **Backend (`apps/api`)** — FastAPI (Python). Acts as the agent orchestrator, managing token verification, rate limiting, and integrations.
* **Gemini** — The reasoning engine powering every agent (using structured JSON schema validation and self-repair).
* **Valkey** — The hot-path architecture. Used as a semantic cache (HNSW vector search) to cut Gemini costs, agent working memory, shared boardroom state, Pub/Sub for the live debate stream, and real-time telemetry.
* **Breeth** — Long-term founder graph memory connected via MCP to personalize analyses for returning founders.
* **Firebase** — Realtime Database acts as the durable system of record, strictly protected by owner-scoped security rules.

## 🏃 Run Locally

### 1. Start Valkey (with valkey-search)
```bash
docker compose -f infra/docker-compose.yml up -d
```

### 2. Start the Backend (FastAPI)
```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Fill GEMINI_API_KEY, BREETH_API_KEY, FIREBASE_DB_URL in .env
# Place your Firebase service-account JSON at apps/api/secrets/serviceAccount.json

uvicorn app.main:app --reload --port 8000
```

### 3. Start the Frontend (Next.js)
```bash
cd apps/web
npm install

# Configure environment variables
cp .env.example .env.local
# Fill NEXT_PUBLIC_FIREBASE_* and NEXT_PUBLIC_API_BASE_URL in .env.local

npm run dev
```

### 4. Setup Database Rules
Publish the security rules for Firebase Realtime Database:
```bash
firebase deploy --only database
```

## 🧪 Testing

The backend includes a comprehensive suite of pure-logic unit tests (mocking network and native dependencies). Tests cover prompt-injection sanitization, schema validation/self-repair, semantic-cache vector packing, Breeth MCP parsing, and telemetry aggregation.

```bash
cd apps/api
pip install -r requirements-dev.txt
pytest
```

For live smoke testing instructions, see [SMOKE_TEST.md](./SMOKE_TEST.md).

## 💡 Cost Optimization (Free Tier Friendly)

VentureMind AI is designed to run efficiently on Gemini's free tier. A full analysis takes ~10 Gemini calls, and a Shark Tank session takes ~7. 
* **Semantic Caching:** Valkey uses vector embeddings to match repeat or similar ideas, returning a cached analysis with **zero** Gemini calls.
* **Rate Limiting:** A token-bucket limiter in Valkey paces requests under the free RPM limit. 
* **Live Telemetry:** You can monitor cache hits, Gemini calls saved, and live agent activity directly from the Founder Dashboard.

## 📖 Documentation

* [PROJECT_SPEC.md](./PROJECT_SPEC.md) - The single source of truth for the product spec, user stories, data model, and architecture decisions.
* [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment runbook (Vercel, Render, Firebase).
