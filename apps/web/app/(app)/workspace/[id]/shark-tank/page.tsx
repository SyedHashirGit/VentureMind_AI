"use client";

import { use, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, type SharkRound, type SharkResult, type SharkInvestor } from "@/lib/api";
import { ScoreDial } from "@/components/score/score-dial";
import { Mic, ArrowRight } from "lucide-react";

type Phase = "intro" | "pitch" | "verdict";

export default function SharkTank({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [phase, setPhase] = useState<Phase>("intro");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [investors, setInvestors] = useState<SharkInvestor[]>([]);
  const [rounds, setRounds] = useState<SharkRound[]>([]);
  const [idx, setIdx] = useState(0);
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<SharkResult | null>(null);

  const answered = rounds.filter((r) => r.scoreBreakdown);
  const running = useMemo(
    () => (answered.length ? Math.round(answered.reduce((s, r) => s + (r.scoreBreakdown?.overall ?? 0), 0) / answered.length) : 0),
    [answered],
  );

  const enter = async () => {
    setBusy(true);
    try {
      const s = await api.startSharkTank(id);
      setSessionId(s.sessionId); setInvestors(s.investors); setRounds(s.rounds); setPhase("pitch");
    } finally { setBusy(false); }
  };

  const submit = async () => {
    if (!sessionId || answer.trim().length < 2) return;
    setBusy(true);
    const round = rounds[idx];
    try {
      const { scoreBreakdown } = await api.answerSharkTank({ sessionId, roundId: round.roundId, answer: answer.trim() });
      setRounds((rs) => rs.map((r, i) => (i === idx ? { ...r, answer, scoreBreakdown } : r)));
      setAnswer("");
      if (idx + 1 < rounds.length) setIdx(idx + 1);
    } finally { setBusy(false); }
  };

  const finish = async () => {
    if (!sessionId) return;
    setBusy(true);
    try { setResult((await api.finishSharkTank(sessionId)).result); setPhase("verdict"); }
    finally { setBusy(false); }
  };

  const persona = (iid: string) => investors.find((i) => i.id === iid)?.persona ?? iid;

  return (
    <div className="mx-auto max-w-2xl">
      <div className="flex items-center gap-2.5">
        <Mic className="h-5 w-5 text-gold-400" />
        <p className="eyebrow">Shark Tank Live</p>
      </div>

      {phase === "intro" && (
        <div className="mt-2">
          <h1 className="serif text-3xl text-paper">Five investors. No easy questions.</h1>
          <p className="mt-3 max-w-lg text-sm leading-relaxed text-paper-2">
            Face a panel of investor personas, each with their own way of finding the weak point in your
            pitch. Answer in your own words. Every answer is scored, and at the end you get a funding
            verdict and the exact gaps to close.
          </p>
          <button onClick={enter} disabled={busy}
            className="mt-7 inline-flex items-center gap-2 rounded-lg bg-gold-500 px-5 py-3 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5 disabled:opacity-60">
            {busy ? "The panel is taking their seats…" : "Enter the tank"} <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {phase === "pitch" && rounds[idx] && (
        <div className="mt-3">
          <div className="mb-4 flex items-center justify-between">
            <span className="mono text-xs text-paper-3">question {idx + 1} of {rounds.length}</span>
            <span className="mono text-xs text-paper-3">running confidence <span className="text-gold-400">{running || "—"}</span></span>
          </div>
          <AnimatePresence mode="wait">
            <motion.div key={rounds[idx].roundId}
              initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -16 }}
              className="glass rounded-2xl p-6">
              <p className="eyebrow mb-2">{persona(rounds[idx].investorId)}</p>
              <p className="serif text-xl text-paper">{rounds[idx].question}</p>
              <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} rows={4}
                placeholder="Answer like you mean it…"
                className="mt-4 w-full resize-none rounded-lg border border-line bg-ink-850 px-4 py-3 text-sm text-paper outline-none placeholder:text-paper-3 focus:border-gold-600" />
              {rounds[idx].scoreBreakdown && (
                <p className="mt-3 text-sm text-paper-2">
                  <span className="text-gold-400">{rounds[idx].scoreBreakdown!.overall}/100</span> — {rounds[idx].scoreBreakdown!.feedback}
                </p>
              )}
              <div className="mt-4 flex items-center gap-3">
                <button onClick={submit} disabled={busy}
                  className="rounded-lg bg-gold-500 px-4 py-2.5 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5 disabled:opacity-60">
                  {busy ? "Scoring…" : "Submit answer"}
                </button>
                {answered.length === rounds.length && (
                  <button onClick={finish} disabled={busy}
                    className="rounded-lg border border-line px-4 py-2.5 text-sm text-paper-2 transition-colors hover:border-line-strong hover:text-paper">
                    Get the verdict
                  </button>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      )}

      {phase === "verdict" && result && (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="mt-3">
          <div className="glass rounded-2xl p-6">
            <p className="eyebrow">Funding verdict</p>
            <div className="mt-5 grid grid-cols-3 gap-6">
              <ScoreDial value={result.confidenceScore} label="Confidence" />
              <ScoreDial value={result.fundingProbability} label="Funding odds" />
              <ScoreDial value={result.pitchQuality} label="Pitch quality" />
            </div>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Panel title="Weaknesses" items={result.weaknesses} tone="risk" />
            <Panel title="How to improve" items={result.improvements} tone="rec" />
          </div>
        </motion.div>
      )}
    </div>
  );
}

function Panel({ title, items, tone }: { title: string; items: string[]; tone: "risk" | "rec" }) {
  const dot = tone === "risk" ? "bg-clay-400" : "bg-sage-400";
  return (
    <div className="glass rounded-xl p-5">
      <p className="eyebrow mb-2">{title}</p>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm text-paper-2"><span className={`mt-1.5 h-1 w-1 shrink-0 rounded-full ${dot}`} />{it}</li>
        ))}
      </ul>
    </div>
  );
}
