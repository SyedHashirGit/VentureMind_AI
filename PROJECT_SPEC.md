# PROJECT_SPEC.md — VentureMind AI

> Single source of truth. Updated every phase. Last updated: Phase 1.

## 0. Status & Changelog

| Phase | Title | Status |
|------:|-------|--------|
| 1 | Product spec, user stories, flows, data model, folder structure | **DONE (this doc)** |
| 2 | Backend architecture | **DONE** |
| 3 | Frontend architecture | **DONE** |
| 4 | Firebase integration | **DONE** |
| 5 | Gemini integration | **DONE** |
| 6 | Valkey integration | **DONE** |
| 7 | Breeth integration | **DONE** |
| 8 | Dashboard implementation | **DONE** |
| 9 | Hero features | **DONE** |
| 10 | Testing | **DONE** |
| 11 | Deployment | **DONE** |

Changelog:
* v0.1 (Phase 1): Initial spec, scoping, data model, agent design.
* v0.2 (Phase 2): Confirmed decisions and backend architecture. Name = VentureMind AI. Solo submission, submitter = Syed Dilawar Hashir. Database = Firebase Realtime Database (not Firestore). Valkey = local (Docker) with valkey-search for dev/demo. MVP scope (Shark Tank Live flagship) confirmed. Data model rewritten for RTDB. Backend skeleton, config, security, services, orchestrator contract added.
* v0.3 (Phase 3): API keys revoked by founder (added later via env only). Frontend architecture + design system. Next.js 15 App Router, Tailwind v4 token system, warm-ink/electrum-gold brand, three-voice typography, logo + favicon, Firebase Auth client, API client with token injection, boardroom SSE hook, route map for all 15 pages.
* v1.0 (Phase 11): Deployment ready. Production API Dockerfile + .dockerignore; Render blueprint (infra/render.yaml); Vercel config; deploy-friendly Firebase creds (FIREBASE_SERVICE_ACCOUNT_JSON env for managed hosts); production CORS with optional regex for Vercel previews. DEPLOYMENT.md (env checklists, Render/Vercel steps, pre-demo runbook) and the filled Build Beyond Limits submission at submissions/venturemind-ai_syed-dilawar-hashir.md. All 11 phases complete.
* v0.10 (Phase 10): Test suite + docs. 20 pytest unit tests over pure logic (sanitization, schema validation + self-repair, score mapping, semantic-cache packing/parse in both reply shapes, MCP text + SSE parsing, telemetry aggregation), all green with native/network deps stubbed. Telemetry aggregation extracted to a pure, tested helper. Root README (run + test + free-tier notes) and SMOKE_TEST.md (live checklist for Valkey vector, Gemini, Breeth MCP, auth/rules, SSE, hero features, telemetry).
* v0.9 (Phase 9): Both flagships live. Shark Tank Live (one Gemini call generates all five investors' opening questions; each founder answer scored against rubrics with live running confidence; a final funding verdict with confidence/funding-odds/pitch-quality dials plus weaknesses and improvements). Startup Time Machine (one call forecasts Month 1 to Year 5 across optimistic/realistic/worst-case on an animated timeline). Boardroom rounds 2-3 added via a single synthesis call (cross-examination challenges + consensus card), streamed and cached. New routers (time-machine; shark-tank finish/get) and frontend pages. All 30 frontend files parse clean; hero schemas tested.
* v0.8 (Phase 8): Authenticated product built on live data. Workspace overview (score dials), live Boardroom (SSE verdict + seven streaming agent cards with Framer Motion), Validation Center (four dials + rationale + market/demand/competition/feasibility/risk), Competitor/MVP/Investor detail pages (render persisted agent role_output), Founder Memory dashboard (Breeth profile + search), Settings. Live telemetry panel on the dashboard polling /analytics/telemetry. Backend GET endpoints for workspace + boardroom; memory router. Sidebar derives workspace nav from the route. All 27 frontend files parse clean.
* v0.7 (Phase 6+7): Valkey + Breeth integrated. Semantic cache (HNSW vector index) short-circuits a full boardroom on a near-match idea with zero Gemini calls; Valkey token-bucket limiter paces Gemini under the free-tier RPM with min-interval spacing; event-log STREAM per workspace for replay; shared boardroom HASH; live analytics counters (cache hits/misses, Gemini calls saved, pub/sub volume) exposed at /analytics/telemetry. Breeth graph memory wired over its MCP endpoint: per-founder group isolation, recall before analysis to personalize prompts, fire-and-forget write after each run. All memory + cache ops are non-fatal (degrade to miss/skip), so neither can break the product. Free-tier note: cache + limiter keep request volume safe.
* v0.5 (Phase 5): Gemini reasoning live. Seven role briefs with strict JSON schemas, the four-score validation engine (each score carries a rationale plus market/demand/competition/feasibility/risk analysis and an editorial verdict), schema-validated generation with one self-repair pass, exponential backoff on rate limits, per-agent graceful degradation, prompt-injection hardening (<idea> delimiting + sanitization), and embeddings ready for Valkey. Orchestrator now writes scores and streams the verdict + each agent live.
* v0.4 (Phase 4): Firebase auth wired end to end. Backend token verification helpers (header + SSE query), `/auth/bootstrap` user provisioning on first login, SSE route now verifies `access_token` and workspace ownership. RTDB security rules authored (`database.rules.json`, default-deny, owner-scoped, indexed). Frontend: sign-in page, `(app)` auth-guard layout, app shell (sidebar + topbar), working guarded dashboard with create/list.

## 1. Hackathon Context & Hard Constraints

Event: Build Beyond Limits 2.0, hosted by React Hyderabad, powered by Valkey and Breeth AI. Dates: June 20 to 21, 2026; grace period to July 5. In-person demo day June 21 at Amazon HYD13.

Mapped track: **Track B, Project #66 — "Valkey for AI"** (build/extend AI apps showcasing Valkey vector search, semantic caching, agent memory).

Hard rules (non-negotiable):
1. Valkey MUST be used (core, not decorative).
2. Breeth AI SHOULD be used.
3. Frontend MUST be React (Next.js 15 satisfies this).

Judging signals (from the rules): understand a real business problem, think from a business perspective, use the right tools, ship a working solution, present it clearly. Bonus recognition if work is merged upstream as an open-source contribution.

Submission mechanics: project code lives in OUR OWN public GitHub repo. We submit a markdown file via PR to `reacthyderabad/build-beyond-limits-2.0` under `submissions/` named `venturemind-ai_<name-or-team>.md`, using `SUBMISSION_TEMPLATE.md`. PR title: `Submission: VentureMind AI - <Name/Team>`. Submit even if incomplete.

## 2. Security Posture (read first, always)

Incident: three live credentials (Gemini key, Firebase URL, Breeth `ck_live_` key) were exposed in plaintext during planning. The founder has chosen not to rotate them for now. That choice is respected, but it raises residual risk: the keys exist in chat logs, so they should be rotated before the repo is made public if feasible. Regardless of rotation, secrets are NEVER committed to source.

Rules we enforce in code:
* No secret is ever hardcoded or committed. All secrets load from environment variables.
* `.env` is git-ignored. A committed `.env.example` holds placeholder names only.
* Server-side secrets (Gemini, Breeth, Firebase Admin, Valkey auth) live ONLY in the FastAPI backend, never in the Next.js client bundle. The browser never sees an AI or DB key.
* Firebase Auth ID tokens are verified server-side via the Firebase Admin SDK on every protected API call.
* Firestore Security Rules restrict each document to its owner `uid`. Default deny.
* Valkey is reached only from the backend, over TLS, with AUTH (or ACL user), never exposed publicly.
* Rate limiting on every AI endpoint (Valkey-backed) to cap Gemini spend and abuse.

## 3. Product Overview & Positioning

One-liner: VentureMind AI is an AI startup incubator. A founder enters one idea; an AI boardroom of expert agents validates it, debates it, stress-tests it, and returns a complete, investor-ready startup blueprint in minutes.

Positioning vs a chatbot: this is a *workspace*, not a chat box. The deliverable is structured artifacts (scores, blueprint, pitch deck, forecasts) and two immersive experiences (a live investor grilling, and a future simulator). The "wow" is watching specialized agents disagree and converge, then receiving a board-grade document.

Why it fits the track: every core loop is powered by Valkey (semantic cache to cut Gemini cost, agent memory + shared boardroom state, vector knowledge retrieval, pub/sub for the live boardroom, session + event queue + analytics) and Breeth (durable founder memory that makes the product smarter on return visits).

## 4. Personas & User Stories

Primary persona: "Aspiring Founder" (student or early builder, idea-stage, no formal business training, time-poor, wants credible validation and an investor-ready story).
Secondary: "Returning Founder" (iterating across multiple ideas; benefits from Breeth long-term memory).

User stories (P0 = MVP must-have, P1 = strong add, P2 = stretch):

Validation:
* P0: As a founder, I enter an idea and get four scores (viability, market opportunity, execution difficulty, funding attractiveness) with written rationale, so I know if the idea is worth pursuing.
* P0: As a founder, I see market, demand, competition, feasibility, and risk analysis, so my decision is grounded.

Boardroom:
* P0: As a founder, I watch specialized agents (CEO, CTO, PM, Investor, Marketing, Competitor, Legal) analyze my idea and stream their reasoning live, so it feels like a real board meeting.
* P1: As a founder, I see agents challenge each other and resolve disagreements, so weaknesses surface.

Blueprint & artifacts:
* P0: As a founder, I generate a startup blueprint (exec summary, business model, tech strategy, roadmap, MVP) and export it to PDF.
* P1: As a founder, I generate a pitch deck and a financial forecast.
* P1: As a founder, I get a competitor SWOT and market-gap report.

Hero — Shark Tank Live:
* P0 (chosen flagship): As a founder, I enter a virtual investor panel with distinct personas who ask hard questions, I answer, and I receive confidence/funding-probability/pitch-quality scores plus a weakness report.

Hero — Time Machine:
* P1: As a founder, I see month-1 to year-5 forecasts across optimistic/realistic/worst-case scenarios on a visual timeline.

Memory:
* P1: As a returning founder, the system recalls my profile, risk tolerance, and past ideas (Breeth) and tailors recommendations.

Account:
* P0: As a user, I sign in (Firebase Auth) and my workspaces persist (Firestore).

## 5. Core User Flows

Flow A — Idea to Blueprint (the spine):
1. Sign in (Firebase Auth) → land on Founder Dashboard.
2. Create a Startup Workspace, enter the idea prompt.
3. Backend checks Valkey semantic cache. Hit → return cached analysis instantly. Miss → orchestrate agents via Gemini.
4. Boardroom page opens; agent reasoning streams in live over Valkey pub/sub (relayed to the browser via SSE/WebSocket).
5. Scores + analysis persist to Firestore; embeddings + outputs cached in Valkey; founder signals stored in Breeth.
6. Founder opens Validation Center, then generates Blueprint / Pitch Deck / Forecast; exports PDF.

Flow B — Shark Tank Live (flagship):
1. From a workspace, launch Shark Tank Live.
2. Backend generates 3 to 5 investor personas (cached/seeded), opens a session in Valkey.
3. Investors ask questions (turn-based, streamed). Founder answers (text, optional voice-to-text later).
4. Each answer is scored by Gemini against rubrics; running scores update live.
5. Session ends with confidence, funding probability, pitch quality, weakness report, improvement plan. Persist to Firestore + Breeth.

Flow C — Returning Founder personalization:
1. On login, backend loads founder memory from Breeth.
2. New analyses are conditioned on stored risk tolerance, interests, and prior ideas/decisions.
3. After each session, new memories are written back to Breeth.

## 6. System Architecture (high level)

```
                         ┌──────────────────────────────────────┐
                         │  Next.js 15 (React/TS, Tailwind,      │
   Browser  ───────────► │  shadcn/ui, Framer Motion)  Vercel    │
                         │  - Firebase Auth (client SDK)         │
                         │  - SSE/WebSocket for live boardroom    │
                         └───────────────┬──────────────────────┘
                                         │  HTTPS + Firebase ID token
                                         ▼
                         ┌──────────────────────────────────────┐
                         │  FastAPI (Python)   Railway/Render     │
                         │  - Verifies ID token (Admin SDK)       │
                         │  - Agent Orchestrator                  │
                         │  - Rate limiting (Valkey)              │
                         └───┬───────────┬──────────┬────────────┘
                             │           │          │
              ┌──────────────▼──┐  ┌─────▼─────┐ ┌──▼──────────┐
              │ Valkey          │  │ Gemini    │ │ Breeth      │
              │ (valkey-search) │  │ API       │ │ (memory)    │
              │ cache/state/    │  │           │ │             │
              │ pubsub/vector   │  └───────────┘ └─────────────┘
              └────────┬────────┘
                       │ system of record
              ┌────────▼────────┐
              │ Firebase        │
              │ Firestore +     │
              │ Storage         │
              └─────────────────┘
```

Division of responsibility:
* Firestore = durable system of record (users, workspaces, analyses, sessions, artifacts). Survives forever.
* Valkey = hot path: semantic cache, agent working memory, shared boardroom state, vector knowledge, pub/sub, sessions, event queue, analytics counters. Fast, ephemeral or TTL'd.
* Breeth = long-term founder memory across sessions and ideas (personalization layer).
* Gemini = the reasoning engine behind every agent.

## 7. Data Model

### 7.1 Firebase Realtime Database (system of record)

RTDB is a single JSON tree. We denormalize and keep an index node so a user's workspaces are listable by key (RTDB has no collection-group queries). All access is by key (uid, workspaceId, sessionId), which RTDB serves fast. Database URL is read from `FIREBASE_DB_URL` env (the given `venturemind-ca40a` instance).

```
/users/{uid}
  displayName, email, photoURL, createdAt, lastActiveAt, plan

/userWorkspaces/{uid}/{workspaceId}: true        // index: list a user's workspaces

/workspaces/{workspaceId}
  ownerUid, title, ideaPrompt, industry, stage, status, createdAt, updatedAt
  scores: { viability, marketOpportunity, executionDifficulty, fundingAttractiveness }   // 0-100
  analyses/{analysisId}: { type, payload, model, cacheHit, createdAt }
  boardroom/{messageId}: { agent, role, content, replyToMessageId, createdAt }

/sharktankSessions/{sessionId}
  ownerUid, workspaceId, status, createdAt, endedAt
  investors/{investorId}: { persona, riskProfile, style }
  rounds/{roundId}: { investorId, question, answer, scoreBreakdown }
  result: { confidenceScore, fundingProbability, pitchQuality, weaknesses, improvements }

/timemachineRuns/{runId}
  ownerUid, workspaceId, createdAt
  scenarios: { optimistic: {...}, realistic: {...}, worstCase: {...} }   // each: stages map

/artifacts/{artifactId}
  ownerUid, workspaceId, kind, storagePath|inline, createdAt
```

Security: RTDB Rules, default-deny, owner-scoped. Examples: `/workspaces/$wid` readable/writable only when `auth.uid === data.child('ownerUid').val()` (and on create, when the incoming `ownerUid === auth.uid`). `/users/$uid` only when `auth.uid === $uid`. Indexes declared with `.indexOn` where needed.

Writes happen server-side via the Firebase Admin SDK (RTDB), which bypasses rules; rules protect any direct client reads. PDF exports default to direct backend-streamed download (no Storage bucket required); Firebase Storage is optional and used only if a bucket is configured.

### 7.2 Valkey Keyspace (hot path)

Client: `valkey-glide` (Python, async) on the backend. Vector features require the `valkey-search` module (FT.CREATE/FT.SEARCH). Patterns are taken directly from the `valkeyforai` cookbooks.

Semantic cache (cut Gemini cost; match by meaning, not string):
```
FT.CREATE analysis_cache_idx SCHEMA
  prompt TEXT  agent TAG  payload TEXT
  embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 768 DISTANCE_METRIC COSINE
HASH  cache:analysis:{sha}  -> { prompt, agent, payload, embedding }   EX 3600
# Flow: embed prompt -> FT.SEARCH KNN -> distance < threshold ? HIT : MISS -> call Gemini -> HSET
```

Agent working memory & checkpointing (resume on failure, avoid recompute):
```
HASH    agent:state:{workspaceId}:{agent}   -> { current_step, status, result_step_n }  EX 86400
STRING  tool:cache:{hash}                   -> cached external tool output               EX 1800
STREAM  agent:log:{workspaceId}             -> ordered event log (replay/debug)
```

Shared boardroom state (single context all agents read/write):
```
HASH  boardroom:ctx:{workspaceId}  -> { idea, scores, open_questions, consensus }
```

Vector knowledge base (semantic retrieval of startup playbooks, prior analyses):
```
FT.CREATE kb_idx SCHEMA
  text TEXT  source TAG
  embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 768 DISTANCE_METRIC COSINE
HASH  kb:{docId}  -> { text, source, embedding }
```

Real-time boardroom comms (live debate to the browser):
```
PUBLISH  boardroom:{workspaceId}  <agent message json>
SUBSCRIBE boardroom:{workspaceId}        # backend relay -> SSE/WebSocket -> client
```

Sessions, queue, analytics:
```
STRING  session:{sessionId}              -> uid  EX 7200       # active user sessions
STREAM  jobs:agents                      -> agent workflow tasks (consumer groups)
HASH    analytics:global                 -> { cache_hits, cache_misses, gemini_calls, sessions }
ZSET    analytics:agent_activity         -> agent -> activity count
# Rate limiting (token/fixed window) per uid to cap Gemini spend
STRING  ratelimit:{uid}:{window}         -> count  EX <window>
```

### 7.3 Breeth Memory (long-term founder layer)

Stores and recalls across sessions: founder profile, goals, personality, interests, industry preferences, funding preferences, risk tolerance, previous startup ideas, previous decisions, long-term journey. Read on login to condition agent prompts; written back after each meaningful session so the product gets smarter for returning founders. (Exact Breeth API surface confirmed in Phase 7 against current docs; backend wraps it behind a `MemoryService` interface so the rest of the app is decoupled.)

## 8. AI Agent Design

Seven agents, each a structured Gemini call with a role system-prompt, a strict JSON output schema, access to the shared boardroom context (Valkey), relevant KB vectors (Valkey), and founder memory (Breeth).

| Agent | Produces |
|-------|----------|
| CEO | mission, vision, strategic roadmap |
| CTO | system architecture, data design, API structure, deployment plan |
| Product Manager | roadmap, feature prioritization, user journeys, MVP scope |
| Investor | funding score, investment risk, recommendations |
| Marketing | GTM, growth plan, brand positioning |
| Competitor Analyst | competitor list, SWOT, market gaps |
| Legal Advisor | compliance checklist, legal risks |

Orchestration (the "boardroom"):
1. Round 1 (parallel analysis): each agent analyzes the idea independently; outputs stream live and write to shared context.
2. Round 2 (cross-examination): agents read peers' outputs and raise challenges (e.g., Investor challenges CTO's scalability cost; Legal flags Marketing's claims).
3. Round 3 (consensus): a synthesizer pass reconciles into final scores + blueprint.

Every Gemini call is preceded by a semantic-cache lookup and protected by rate limiting. Outputs are validated against JSON schemas before persistence.

## 9. Hero Features

### 9.1 Shark Tank Live (chosen MVP flagship)
Investor personas (distinct personality, risk profile, questioning style): YC Partner, Sequoia Partner, a16z Partner, Angel, Corporate VC. Turn-based grilling with streamed questions; founder answers; Gemini scores each answer against rubrics (clarity, defensibility, market understanding, traction story, ask). Final output: investor confidence, funding probability, pitch quality, weakness report, improvement plan. Immersive boardroom UI. Session state and turn order in Valkey; transcript and result in Firestore; outcome summarized to Breeth.

### 9.2 Startup Time Machine (strong P1)
Forecasts for month 1/3/6, year 1/3/5 across optimistic/realistic/worst-case, predicting users, revenue, growth, team size, competition, risks, opportunities, funding needs, with explanations. Visual timeline interface (animated). Results cached in Valkey, persisted in Firestore.

## 10. Feature → Tool Mapping (proves meaningful usage)

| Capability | Valkey | Breeth | Gemini |
|-----------|--------|--------|--------|
| Cut AI cost / speed | semantic cache (vector) | — | reasoning |
| Agent memory | HASH checkpoints, STREAM log | founder long-term memory | — |
| Shared boardroom | HASH ctx + Pub/Sub | — | debate generation |
| Knowledge retrieval | vector KB (HNSW/KNN) | — | grounded answers |
| Live debate stream | Pub/Sub → SSE | — | per-agent output |
| Sessions/queue | STRING/STREAM | — | — |
| Personalization | — | profile + history recall | tailored prompts |
| Analytics | counters/ZSET | — | — |

## 11. Monorepo Folder Structure

```
venturemind-ai/
├─ apps/
│  ├─ web/                      # Next.js 15 (App Router), React, TS, Tailwind, shadcn/ui, Framer Motion
│  │  ├─ app/                   # routes: landing, auth, dashboard, workspace, boardroom,
│  │  │                         #         validation, competitors, mvp, financials,
│  │  │                         #         time-machine, shark-tank, pitch-deck,
│  │  │                         #         investor-readiness, memory, settings
│  │  ├─ components/            # ui (shadcn), charts, agent cards, boardroom stream
│  │  ├─ lib/                   # firebase client, api client, sse hooks
│  │  ├─ public/                # favicon, logo, og image
│  │  └─ .env.example
│  └─ api/                      # FastAPI (Python)
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ core/               # config, security (token verify), logging
│     │  ├─ services/           # gemini, valkey, breeth (MemoryService), firestore, pdf
│     │  ├─ agents/             # ceo, cto, pm, investor, marketing, competitor, legal, orchestrator
│     │  ├─ routers/            # workspaces, boardroom, sharktank, timemachine, artifacts
│     │  ├─ schemas/            # pydantic request/response + agent JSON schemas
│     │  └─ realtime/           # pubsub relay -> SSE/WebSocket
│     ├─ requirements.txt
│     └─ .env.example
├─ packages/
│  └─ shared-types/             # TS types mirrored from pydantic (generated)
├─ infra/                       # Dockerfiles, deploy configs (Railway/Render, Vercel)
├─ firestore.rules
├─ storage.rules
├─ .gitignore                   # includes .env, service-account json
├─ .env.example                 # placeholders only, no real secrets
├─ PROJECT_SPEC.md              # this file
└─ README.md
```

## 12. Hackathon Scope: Ship-to-Win Core vs Full Vision

Ship-to-win MVP (build first, must be flawless):
* Auth + dashboard + create workspace.
* Idea → 4 scores + validation analysis, with Valkey semantic cache demonstrably reducing Gemini calls (show the cache-hit counter live).
* Live multi-agent boardroom with at least 4 agents streaming over Valkey Pub/Sub.
* Shark Tank Live flagship, end to end, with scored result.
* Breeth: store founder profile + idea history; show personalization on a second run.
* PDF export of the blueprint.
* A live "Valkey + Breeth telemetry" panel (cache hits/misses, agents active, pub/sub messages) so judges literally see the infra working.

Defer if time-constrained: full Time Machine visualization, competitor center depth, financial engine depth, pitch-deck export. Stubs/links acceptable; mark clearly as in-progress in the submission per hackathon rules.

## 13. "Wow" Additions for Judges (proposed, low-cost, high-impact)
1. Live infra telemetry panel (above): turns "we used Valkey" into something judges can watch.
2. Cache-savings meter: estimated Gemini cost saved by semantic cache, in INR, updating live.
3. "Replay the boardroom": rebuild the debate from the Valkey STREAM event log to prove durable agent memory.
4. Upstream-contribution angle: package the Valkey agent-memory pattern as a small reusable module and offer a PR to `valkeyforai`, which the hackathon explicitly rewards.

## 14. Architecture Decisions & Tradeoffs (Phase 1)

* Next.js 15 + FastAPI split rather than a single framework: keeps AI/secret logic server-side in Python (best Gemini/Valkey/Breeth ergonomics) while giving a premium React UI. Tradeoff: two deploy targets (Vercel + Railway/Render) and CORS to manage. Worth it for security and clean separation.
* Firestore as system of record, Valkey as hot path, rather than Valkey-only: durability and queryable history live in Firestore; Valkey stays fast and cheap. Tradeoff: dual writes; mitigated by writing to Firestore on completion and using Valkey for in-flight state.
* GLIDE client for Valkey: it is the client the hackathon and `valkeyforai` recommend, with cluster/multiplexing support. Tradeoff: async-first API; our FastAPI is async anyway.
* Semantic cache keyed on embeddings, not exact strings: far higher hit rate and the headline cost story for judges. Tradeoff: needs the `valkey-search` module and an embedding call per request (cheap, and itself cacheable).
* Pub/Sub relayed to the browser via SSE rather than direct client-to-Valkey: Valkey never faces the public internet; the browser holds no DB credentials. Tradeoff: backend maintains relay connections.
* MemoryService interface wrapping Breeth: decouples the app from Breeth's exact API, which we will verify against live docs in Phase 7. Tradeoff: a thin abstraction layer; cheap insurance.

## 15. Decisions (resolved)
1. Product name: **VentureMind AI**.
2. Submission: **solo**, submitter **Syed Dilawar Hashir**. Submission file: `submissions/venturemind-ai_syed-dilawar-hashir.md`.
3. Database: **Firebase Realtime Database** (the given `venturemind-ca40a` instance), not Firestore.
4. MVP scope (section 12), Shark Tank Live as the single flagship: **confirmed**.
5. Valkey: **local via Docker with the valkey-search module** for dev and demo day (vector search live, zero network risk on stage). A managed instance is the production path; the backend connection string is env-driven so switching is a one-line change.

## 16. Design System (Phase 3)

Thesis: the boardroom, rendered as an investment memo. The product turns a raw idea into a board-grade verdict, so the visual language borrows from venture's own artifacts (the memo, the score card, the term sheet).

Palette (warm ink + electrum gold; deliberately not the cold blue/purple or acid-green AI defaults):
* Ink base: `#15110C` (app), surfaces `#211C15` / `#2B2419`, lines `#352D20`.
* Paper text: `#F2EDE3` primary, `#BCB2A1` secondary, `#7E7568` muted.
* Electrum gold (value/decision): `#DDA02F` primary, `#F4CD78` light, `#BC8222` deep.
* Functional: sage `#8CB67F` (positive score), clay `#D08A66` (risk/caution), slate `#8AA0B2` (neutral data).
Background is a single warm gold spotlight, never a multi-hue gradient.

Typography (three voices mapped to the product's three logics):
* Serif = human judgment: Newsreader, used with restraint for hero lines, verdicts, big score numbers.
* Sans = interface: Geist, all UI text and labels.
* Mono = machine data: Geist Mono, for live telemetry, score breakdowns, term-sheet figures.

Motion: orchestrated page-load (hero rises, board assembles, verdict resolves last), hover micro-interactions on agent cards, scroll reveals. Sleek, restrained, `prefers-reduced-motion` respected.

Logo: a minimal upward mark, two strokes rising and converging to a glowing apex node (minds rising to one decision), electrum-gold gradient on ink. Wordmark "VentureMind" with a muted "AI" tag. Favicon is the mark on a rounded ink tile (`public/favicon.svg`).

Signature element: the live boardroom, agent cards streaming reasoning and resolving into a single editorial verdict card. Boldness is spent here; everything else stays quiet.

## 17. Frontend Architecture (Phase 3)

Stack: Next.js 15 (App Router), React 19, TypeScript, Tailwind v4 (CSS-first `@theme` tokens in `globals.css`), Framer Motion, Firebase Auth (client SDK), Geist + Newsreader fonts.

Route map (App Router, route groups):
```
app/
  (marketing)/page.tsx                              # 1  Landing
  (auth)/sign-in/page.tsx                           # 2  Authentication
  (app)/layout.tsx                                  #    App shell (left rail + glass topbar, auth guard)
  (app)/dashboard/page.tsx                          # 3  Founder Dashboard
  (app)/workspace/[id]/page.tsx                     # 4  Startup Workspace
  (app)/workspace/[id]/boardroom/page.tsx           # 5  Multi-Agent Boardroom
  (app)/workspace/[id]/validation/page.tsx          # 6  Validation Center
  (app)/workspace/[id]/competitors/page.tsx         # 7  Competitor Intelligence
  (app)/workspace/[id]/mvp/page.tsx                 # 8  MVP Planner
  (app)/workspace/[id]/financials/page.tsx          # 9  Financial Forecast
  (app)/workspace/[id]/time-machine/page.tsx        # 10 Startup Time Machine
  (app)/workspace/[id]/shark-tank/page.tsx          # 11 Shark Tank Live (flagship)
  (app)/workspace/[id]/pitch-deck/page.tsx          # 12 Pitch Deck Generator
  (app)/workspace/[id]/investor-readiness/page.tsx  # 13 Investor Readiness
  (app)/memory/page.tsx                             # 14 Founder Memory
  (app)/settings/page.tsx                           # 15 Settings
```

Component inventory: brand (`Logo`, `LogoMark`), shell (`Sidebar`, `Topbar`, `NavItem`), primitives (`Button`, `Card`, `Glass`, `Badge`, `Stat`), scoring (`ScoreDial`, `VerdictCard`), boardroom (`AgentCard`, `DebateStream`, `BoardroomRing`), telemetry (`TelemetryPanel` for live Valkey/Breeth stats), shark-tank (`InvestorCard`, `QuestionPanel`), charts (recharts wrappers, Phase 8/9).

Data flow: auth via React Context (`AuthProvider`/`useAuth`). API calls via `lib/api.ts`, which injects the Firebase ID token as a Bearer. Live boardroom via `hooks/use-boardroom-stream.ts` (SSE), token passed as `access_token` query since EventSource cannot set headers (the relay must validate this in Phase 4). Server data fetching adds React Query in Phase 8. Dark-only theming through CSS tokens.

Foundation shipped this phase: `globals.css` (tokens), `layout.tsx` (fonts + metadata + favicon + AuthProvider), `logo.tsx`, `favicon.svg`, `lib/firebase.ts`, `lib/auth.tsx`, `lib/api.ts`, `hooks/use-boardroom-stream.ts`, and a real branded landing `page.tsx`. The remaining 14 pages are built in Phase 8 (dashboards) and Phase 9 (hero features).

## 18. Status: complete
All eleven phases are done. Remaining founder actions before the demo: create the GitHub repo and fill the three placeholders in the submission file (GitHub username, LinkedIn, repo URL); deploy per DEPLOYMENT.md; run SMOKE_TEST.md once with real keys; open the submission PR to reacthyderabad/build-beyond-limits-2.0.

Phase 4 deployment note: publish the database rules with `firebase deploy --only database` (or paste `database.rules.json` into the console). The backend writes via the Admin SDK and bypasses rules; the rules protect any direct client access as defense in depth.
