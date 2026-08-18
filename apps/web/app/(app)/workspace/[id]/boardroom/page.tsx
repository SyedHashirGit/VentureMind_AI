"use client";

import { use, useEffect, useMemo, useState } from "react";
import { api, type BoardroomMessage, type AgentAnalysis, type ValidationContent } from "@/lib/api";
import { useBoardroomStream } from "@/hooks/use-boardroom-stream";
import { AgentCard } from "@/components/board/agent-card";
import { VerdictCard } from "@/components/board/verdict-card";
import { ConsensusCard } from "@/components/board/consensus-card";
import { agentMeta } from "@/components/board/agents";
import { Gavel } from "lucide-react";

const ORDER = ["ceo", "cto", "pm", "investor", "marketing", "competitor", "legal"];
type Consensus = { agreements: string[]; tensions: string[]; final_recommendation: string; refined_verdict: string };

export default function Boardroom({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [history, setHistory] = useState<BoardroomMessage[]>([]);
  const [running, setRunning] = useState(false);
  const { messages: live, connected } = useBoardroomStream(id);

  useEffect(() => { api.getBoardroom(id).then(({ messages }) => setHistory(messages)).catch(() => {}); }, [id]);

  const { verdict, analyses, challenges, consensus } = useMemo(() => {
    const all = [...history, ...(live as BoardroomMessage[])];
    const analysesMap = new Map<string, BoardroomMessage>();
    let verdict: BoardroomMessage | undefined;
    let consensus: BoardroomMessage | undefined;
    const rawChallenges: BoardroomMessage[] = [];
    for (const m of all) {
      if (m.role === "analysis") {
        const prev = analysesMap.get(m.agent);
        if (!prev || (m.ts ?? 0) >= (prev.ts ?? 0)) analysesMap.set(m.agent, m);
      } else if (m.role === "verdict") {
        if (!verdict || (m.ts ?? 0) >= (verdict.ts ?? 0)) verdict = m;
      } else if (m.role === "consensus") {
        if (!consensus || (m.ts ?? 0) >= (consensus.ts ?? 0)) consensus = m;
      } else if (m.role === "challenge") rawChallenges.push(m);
    }
    const seen = new Set<string>();
    const challenges = rawChallenges.filter((c) => {
      const k = `${c.agent}-${(c.content as Record<string, unknown>).toAgent}-${(c.content as Record<string, unknown>).point}`;
      if (seen.has(k)) return false; seen.add(k); return true;
    });
    return { verdict, analyses: analysesMap, challenges, consensus };
  }, [history, live]);

  const hasAny = analyses.size > 0 || !!verdict;

  const convene = async () => {
    setRunning(true);
    try { await api.analyze(id); } catch { /* stream shows progress */ } finally { setRunning(false); }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex items-center justify-between">
        <p className="eyebrow">Boardroom</p>
        <span className="mono flex items-center gap-2 text-[11px] text-paper-3">
          <span className={`h-1.5 w-1.5 rounded-full ${connected ? "bg-sage-400" : "bg-paper-3"}`} />
          {connected ? "live" : "idle"}
        </span>
      </div>

      <button onClick={convene} disabled={running}
        className="mt-4 inline-flex items-center gap-2 rounded-lg bg-gold-500 px-5 py-3 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5 disabled:opacity-60">
        <Gavel className="h-4 w-4" /> {running ? "The board is deliberating…" : hasAny ? "Re-convene" : "Convene the board"}
      </button>

      <div className="mt-7 space-y-4">
        {verdict && <VerdictCard v={verdict.content as ValidationContent} />}
        {ORDER.map((aid) => {
          const m = analyses.get(aid);
          return m ? <AgentCard key={aid} agentId={aid} data={m.content as AgentAnalysis} cached={m.cached} /> : null;
        })}

        {challenges.length > 0 && (
          <div className="glass rounded-2xl p-5">
            <p className="eyebrow mb-3">Cross-examination</p>
            <ul className="space-y-2.5">
              {challenges.map((c, i) => {
                const ct = c.content as { toAgent: string; point: string };
                return (
                  <li key={i} className="text-sm text-paper-2">
                    <span className="text-gold-400">{agentMeta(c.agent).label}</span>
                    <span className="text-paper-3"> challenges </span>
                    <span className="text-paper">{agentMeta(ct.toAgent).label}</span>: {ct.point}
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {consensus && <ConsensusCard c={consensus.content as Consensus} />}

        {!hasAny && !running && <p className="text-sm text-paper-3">The room is empty. Convene the board to begin.</p>}
      </div>
    </div>
  );
}
