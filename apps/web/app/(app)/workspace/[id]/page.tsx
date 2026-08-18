"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, type Workspace } from "@/lib/api";
import { ScoreDial } from "@/components/score/score-dial";
import { Gavel } from "lucide-react";

export default function WorkspaceOverview({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [ws, setWs] = useState<Workspace | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => { api.getWorkspace(id).then(setWs).catch(() => {}); }, [id]);

  const convene = async () => {
    setRunning(true);
    router.push(`/workspace/${id}/boardroom`);
    try { await api.analyze(id); } catch { /* surfaced in boardroom */ }
  };

  const s = ws?.scores;
  return (
    <div className="mx-auto max-w-3xl">
      <p className="eyebrow">Startup workspace</p>
      <h1 className="serif mt-1 text-3xl text-paper">{ws?.title ?? "…"}</h1>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-paper-2">{ws?.ideaPrompt}</p>

      <button
        onClick={convene}
        disabled={running}
        className="mt-6 inline-flex items-center gap-2 rounded-lg bg-gold-500 px-5 py-3 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5 disabled:opacity-60"
      >
        <Gavel className="h-4 w-4" /> {running ? "Convening…" : ws?.status === "complete" ? "Re-convene the board" : "Convene the board"}
      </button>

      {s && (s.viability || s.marketOpportunity || s.executionDifficulty || s.fundingAttractiveness) ? (
        <div className="glass mt-9 grid grid-cols-2 gap-6 rounded-2xl p-6 sm:grid-cols-4">
          <ScoreDial value={s.viability} label="Viability" />
          <ScoreDial value={s.marketOpportunity} label="Market" />
          <ScoreDial value={s.executionDifficulty} label="Difficulty" />
          <ScoreDial value={s.fundingAttractiveness} label="Fundability" />
        </div>
      ) : null}
    </div>
  );
}
