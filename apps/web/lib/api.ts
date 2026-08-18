import { auth } from "./firebase";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function authedFetch(path: string, init: RequestInit = {}): Promise<Response> {
  let token = await auth.currentUser?.getIdToken();
  if (!token && typeof window !== "undefined") {
    const mockUser = localStorage.getItem("mock_user");
    if (mockUser) {
      token = "mock-token-123";
    }
  }
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  return fetch(`${BASE}${path}`, { ...init, headers });
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.error?.message ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export type FounderProfile = { uid: string; displayName: string; email: string | null; photoURL?: string | null; plan: string };
export type Scores = { viability: number; marketOpportunity: number; executionDifficulty: number; fundingAttractiveness: number };
export type Workspace = { id: string; ownerUid: string; title: string; ideaPrompt: string; status: string; scores?: Scores };

export type AgentAnalysis = {
  summary: string; key_points: string[]; risks: string[]; recommendations: string[];
  confidence: number; role_output: Record<string, unknown>;
};
export type ScoreItem = { score: number; rationale: string };
export type ValidationContent = {
  viability: ScoreItem; market_opportunity: ScoreItem; execution_difficulty: ScoreItem; funding_attractiveness: ScoreItem;
  market_size: string; demand: string; competition: string; feasibility: string; risks: string[]; verdict: string;
};
export type BoardroomMessage = {
  agent: string; role: "analysis" | "verdict" | "challenge" | "rebuttal" | "consensus";
  content: AgentAnalysis | ValidationContent | Record<string, unknown>; ts: number; cached?: boolean;
};
export type Telemetry = {
  cacheHits: number; cacheMisses: number; cacheHitRate: number;
  geminiCalls: number; geminiSaved: number; pubsubMsgs: number; agentRuns: number;
};

export type SharkInvestor = { id: string; persona: string; riskProfile: string; style: string };
export type SharkScore = { clarity: number; defensibility: number; market_understanding: number; traction: number; overall: number; feedback: string };
export type SharkRound = { roundId: string; investorId: string; persona: string; question: string; answer?: string; scoreBreakdown?: SharkScore };
export type SharkResult = { confidenceScore: number; fundingProbability: number; pitchQuality: number; weaknesses: string[]; improvements: string[] };
export type TMStage = { stage: string; users: string; revenue: string; growth: string; teamSize: string; risks: string[]; opportunities: string[]; fundingNeeds: string };
export type TMScenario = { summary: string; stages: TMStage[] };
export type TimeMachine = { optimistic: TMScenario; realistic: TMScenario; worstCase: TMScenario };

export const api = {
  bootstrap: () => authedFetch("/auth/bootstrap", { method: "POST" }).then(json<FounderProfile>),
  createWorkspace: (b: { title: string; ideaPrompt: string; industry?: string; stage?: string }) =>
    authedFetch("/workspaces", { method: "POST", body: JSON.stringify(b) }).then(json<Workspace>),
  listWorkspaces: () => authedFetch("/workspaces").then(json<Workspace[]>),
  getWorkspace: (id: string) => authedFetch(`/workspaces/${id}`).then(json<Workspace>),
  getBoardroom: (id: string) => authedFetch(`/workspaces/${id}/boardroom`).then(json<{ messages: BoardroomMessage[] }>),
  analyze: (id: string) => authedFetch(`/workspaces/${id}/analyze`, { method: "POST" }).then(json),
  telemetry: () => authedFetch("/analytics/telemetry").then(json<Telemetry>),
  memoryProfile: () => authedFetch("/memory/profile").then(json<{ profile: string }>),
  memorySearch: (q: string) => authedFetch(`/memory/search?q=${encodeURIComponent(q)}`).then(json<{ results: string }>),
  startSharkTank: (workspaceId: string) =>
    authedFetch("/shark-tank/start", { method: "POST", body: JSON.stringify({ workspaceId }) })
      .then(json<{ sessionId: string; investors: SharkInvestor[]; rounds: SharkRound[] }>),
  answerSharkTank: (b: { sessionId: string; roundId: string; answer: string }) =>
    authedFetch("/shark-tank/answer", { method: "POST", body: JSON.stringify(b) })
      .then(json<{ roundId: string; scoreBreakdown: SharkScore }>),
  finishSharkTank: (sessionId: string) =>
    authedFetch(`/shark-tank/${sessionId}/finish`, { method: "POST" }).then(json<{ sessionId: string; result: SharkResult }>),
  runTimeMachine: (workspaceId: string) =>
    authedFetch(`/time-machine/${workspaceId}/run`, { method: "POST" }).then(json<{ workspaceId: string; scenarios: TimeMachine }>),
  getTimeMachine: (workspaceId: string) =>
    authedFetch(`/time-machine/${workspaceId}`).then(json<{ workspaceId: string; scenarios: TimeMachine | null }>),
  apiBase: BASE,
};
