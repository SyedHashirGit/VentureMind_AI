"use client";

import { motion } from "framer-motion";
import { ScoreDial } from "@/components/score/score-dial";
import type { ValidationContent } from "@/lib/api";

export function VerdictCard({ v }: { v: ValidationContent }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass rounded-2xl p-6"
    >
      <p className="eyebrow">The verdict</p>
      <p className="serif mt-2 text-2xl leading-snug text-paper">{v.verdict}</p>

      <div className="mt-7 grid grid-cols-2 gap-6 sm:grid-cols-4">
        <ScoreDial value={v.viability.score} label="Viability" />
        <ScoreDial value={v.market_opportunity.score} label="Market" />
        <ScoreDial value={v.execution_difficulty.score} label="Difficulty" />
        <ScoreDial value={v.funding_attractiveness.score} label="Fundability" />
      </div>
    </motion.div>
  );
}
