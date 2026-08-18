"use client";

import { use, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api, type TimeMachine, type TMStage } from "@/lib/api";
import { Clock, Sparkles } from "lucide-react";

const SCENARIOS = [
  { key: "optimistic", label: "Optimistic", color: "text-sage-400" },
  { key: "realistic", label: "Realistic", color: "text-gold-400" },
  { key: "worstCase", label: "Worst case", color: "text-clay-400" },
] as const;

export default function TimeMachinePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [tm, setTm] = useState<TimeMachine | null | undefined>(undefined);
  const [scenario, setScenario] = useState<(typeof SCENARIOS)[number]["key"]>("realistic");
  const [busy, setBusy] = useState(false);

  useEffect(() => { api.getTimeMachine(id).then((d) => setTm(d.scenarios)).catch(() => setTm(null)); }, [id]);

  const run = async () => {
    setBusy(true);
    try { setTm((await api.runTimeMachine(id)).scenarios); } catch { /* noop */ } finally { setBusy(false); }
  };

  const active = tm?.[scenario];

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex items-center gap-2.5">
        <Clock className="h-5 w-5 text-gold-400" />
        <p className="eyebrow">Startup Time Machine</p>
      </div>
      <h1 className="serif mt-1 text-3xl text-paper">See five years out, before you build.</h1>

      {tm === undefined ? (
        <p className="mt-6 text-sm text-paper-3">Loading…</p>
      ) : !tm ? (
        <div className="mt-4">
          <p className="max-w-lg text-sm leading-relaxed text-paper-2">
            Project your startup across Month 1 to Year 5, in three futures: if everything breaks right,
            the realistic path, and if the market turns against you.
          </p>
          <button onClick={run} disabled={busy}
            className="mt-7 inline-flex items-center gap-2 rounded-lg bg-gold-500 px-5 py-3 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5 disabled:opacity-60">
            <Sparkles className="h-4 w-4" /> {busy ? "Running the simulation…" : "Run the simulation"}
          </button>
        </div>
      ) : (
        <div className="mt-6">
          <div className="flex gap-2">
            {SCENARIOS.map((sc) => (
              <button key={sc.key} onClick={() => setScenario(sc.key)}
                className={`rounded-lg border px-4 py-2 text-sm transition-colors ${scenario === sc.key ? "border-line-strong bg-ink-800 text-paper" : "border-line text-paper-2 hover:text-paper"}`}>
                {sc.label}
              </button>
            ))}
            <button onClick={run} disabled={busy} className="ml-auto rounded-lg border border-line px-3 py-2 text-xs text-paper-3 hover:text-paper">
              {busy ? "…" : "re-run"}
            </button>
          </div>

          {active?.summary && <p className="mt-5 max-w-2xl text-sm leading-relaxed text-paper-2">{active.summary}</p>}

          <div className="mt-6 space-y-3 border-l border-line pl-6">
            {active?.stages.map((s, i) => <StageCard key={s.stage} stage={s} delay={i * 0.06} />)}
          </div>
        </div>
      )}
    </div>
  );
}

function StageCard({ stage, delay }: { stage: TMStage; delay: number }) {
  return (
    <motion.div initial={{ opacity: 0, x: 14 }} animate={{ opacity: 1, x: 0 }} transition={{ delay, duration: 0.4 }}
      className="glass relative rounded-2xl p-5">
      <span className="absolute -left-[31px] top-6 h-2.5 w-2.5 rounded-full bg-gold-500 ring-4 ring-ink-900" />
      <p className="serif text-lg text-gold-400">{stage.stage}</p>
      <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-4">
        <Metric k="Users" v={stage.users} /><Metric k="Revenue" v={stage.revenue} />
        <Metric k="Growth" v={stage.growth} /><Metric k="Team" v={stage.teamSize} />
      </div>
      <p className="mono mt-3 text-xs text-paper-3">funding: {stage.fundingNeeds}</p>
      {(stage.risks?.length || stage.opportunities?.length) ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          {stage.risks?.length ? <MiniList title="Risks" items={stage.risks} dot="bg-clay-400" /> : null}
          {stage.opportunities?.length ? <MiniList title="Openings" items={stage.opportunities} dot="bg-sage-400" /> : null}
        </div>
      ) : null}
    </motion.div>
  );
}

function Metric({ k, v }: { k: string; v: string }) {
  return <div><p className="eyebrow">{k}</p><p className="mono text-sm text-paper">{v}</p></div>;
}
function MiniList({ title, items, dot }: { title: string; items: string[]; dot: string }) {
  return (
    <div>
      <p className="eyebrow mb-1">{title}</p>
      <ul className="space-y-1">
        {items.map((it, i) => <li key={i} className="flex gap-2 text-xs text-paper-2"><span className={`mt-1.5 h-1 w-1 shrink-0 rounded-full ${dot}`} />{it}</li>)}
      </ul>
    </div>
  );
}
