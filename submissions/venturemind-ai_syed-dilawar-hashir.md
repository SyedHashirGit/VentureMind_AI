# VentureMind AI

## Attendee/Team Details

**Name:** Syed Dilawar Hashir
**GitHub Username:** <add your GitHub username>
**LinkedIn Profile:** <add your LinkedIn URL>
**GitHub Project Repository:** <add your repo URL>

## Problem Statement Selected

Track B, Project 66: "Valkey for AI" (build an AI-powered application that showcases Valkey's vector
search, semantic caching, and agent memory).

## Project Description

VentureMind AI is an AI startup incubator. A founder enters a single idea, and a boardroom of seven
expert agents (CEO, CTO, Product, Investor, Marketing, Competitor, Legal) analyzes it, debates it,
challenges each other, and returns an investor-ready blueprint, all in minutes.

It is for aspiring founders, especially students and early builders, who have an idea but no easy way
to get credible, structured validation. It replaces a vague "is this a good idea?" with concrete scores,
a written verdict, a live investor grilling, and a five-year forecast, so the founder knows what to fix
before they build.

## Approach

I framed the product as "the boardroom rendered as an investment memo" and made Valkey load-bearing in
seven ways rather than decorative. The core flow: an idea is embedded once, looked up in a Valkey HNSW
vector index (semantic cache); on a near-match the whole boardroom replays from cache with zero LLM
calls, otherwise the seven agents run, each output is schema-validated, streamed live over Valkey
Pub/Sub, and persisted. A final synthesis pass produces cross-examination and a consensus verdict.
Breeth stores per-founder graph memory so returning founders get personalized analyses. Every LLM call
is paced by a Valkey token-bucket limiter to stay inside the Gemini free tier.

What makes it different: the semantic cache is both the cost lever and the demo's live story (a
telemetry panel shows cache hit rate and LLM calls saved in real time), and the two hero experiences,
Shark Tank Live (investor personas score your answers into a funding verdict) and the Startup Time
Machine (an animated five-year forecast), turn validation into something memorable.

## Tech Stack and Tools Used

**Frontend:** Next.js 15 (App Router), React 19, TypeScript, Tailwind v4, Framer Motion
**Backend:** FastAPI (Python), the agent orchestrator
**Database:** Firebase Realtime Database (owner-scoped security rules)
**AI Tools/API:** Google Gemini (schema-validated structured generation + embeddings)
**Cloud/Deployment:** Vercel (web), Render or Railway (API), Docker
**Other Tools:** Valkey + valkey-search (semantic cache, vector KB, Pub/Sub, streams, sessions,
analytics), Breeth (intent-aware graph memory over MCP), Firebase Auth

## Key Features

1. Multi-agent boardroom: seven expert agents stream live analysis, then cross-examine and reach a consensus verdict.
2. Validation engine: four calibrated scores (viability, market, difficulty, fundability), each with a written rationale.
3. Shark Tank Live: five investor personas grill the founder; answers are scored into a funding verdict with weaknesses and fixes.
4. Startup Time Machine: Month 1 to Year 5 forecasts across optimistic, realistic, and worst-case scenarios.
5. Valkey semantic cache: near-identical ideas return instantly with zero Gemini calls; live telemetry shows the savings.
6. Breeth founder memory: personalized analyses for returning founders, recalled before each run.

## What is Working?

End to end: Google sign-in and per-user provisioning; creating a workspace; the full boardroom (verdict,
seven agents, cross-examination, consensus) streaming live; the validation center; Shark Tank Live; the
Time Machine; the founder memory dashboard; and the live telemetry panel. The semantic cache, the
free-tier rate limiter, schema validation with self-repair, and prompt-injection hardening are all
implemented. A 20-test pytest suite over the pure logic passes.

## What is Still in Progress?

The three live integrations (Valkey vector round-trip, Gemini, the Breeth MCP handshake) are built and
unit-tested in isolation but need one pass through SMOKE_TEST.md with real keys in the deploy
environment. A deeper financial-projection engine (revenue/burn/LTV) is a planned addition; the
financials view currently surfaces the investor agent's funding-readiness analysis.

## Screenshots or Demo

**Deployed Link:** <add after deploy>
**Demo Video Link:** <add>
**Screenshots:** <add>

## Challenges Faced

Keeping the experience rich while respecting a free-tier Gemini budget: the answer was to make the
Valkey semantic cache and a token-bucket limiter first-class, so repeat ideas cost nothing and bursts
never trip the rate limit. Making every external call non-fatal (cache, memory) so a slow or missing
service degrades gracefully instead of breaking the demo was the other big design constraint.

## Learnings

How to use Valkey as real AI infrastructure (vector search for semantic caching, Pub/Sub for live
streaming, streams for replay) rather than a plain key-value store, and how an intent-aware memory layer
like Breeth changes a product from stateless to one that gets smarter per user.

## Future Improvements

A full financial-forecast engine, exportable pitch-deck and blueprint PDFs, a "replay the boardroom"
view driven by the Valkey event-log stream, and packaging the Valkey agent-memory pattern as a small
open-source module to contribute upstream.

## Final Note

Valkey, Breeth, and Gemini each do meaningful, distinct work here, and the live telemetry panel is
designed so you can watch the infrastructure working during the demo rather than taking it on faith.
