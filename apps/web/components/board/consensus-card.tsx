"use client";

import { motion } from "framer-motion";
import { Handshake } from "lucide-react";

type Consensus = { agreements: string[]; tensions: string[]; final_recommendation: string; refined_verdict: string };

export function ConsensusCard({ c }: { c: Consensus }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass rounded-2xl border-gold-600/40 p-6">
      <div className="flex items-center gap-2.5">
        <Handshake className="h-4 w-4 text-gold-400" />
        <p className="eyebrow">Board consensus</p>
      </div>
      <p className="serif mt-3 text-xl leading-snug text-paper">{c.refined_verdict}</p>
      <p className="mt-3 text-sm leading-relaxed text-paper-2">{c.final_recommendation}</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {c.agreements?.length ? (
          <div><p className="eyebrow mb-1.5">Agreements</p>
            <ul className="space-y-1">{c.agreements.map((a, i) => <li key={i} className="flex gap-2 text-sm text-paper-2"><span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-sage-400" />{a}</li>)}</ul></div>
        ) : null}
        {c.tensions?.length ? (
          <div><p className="eyebrow mb-1.5">Open tensions</p>
            <ul className="space-y-1">{c.tensions.map((a, i) => <li key={i} className="flex gap-2 text-sm text-paper-2"><span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-clay-400" />{a}</li>)}</ul></div>
        ) : null}
      </div>
    </motion.div>
  );
}
