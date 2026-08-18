"use client";

import { motion } from "framer-motion";
import { agentMeta } from "./agents";
import type { AgentAnalysis } from "@/lib/api";

function List({ title, items, tone }: { title: string; items?: string[]; tone?: "risk" | "rec" }) {
  if (!items?.length) return null;
  const dot = tone === "risk" ? "bg-clay-400" : tone === "rec" ? "bg-sage-400" : "bg-paper-3";
  return (
    <div className="mt-3">
      <p className="eyebrow mb-1.5">{title}</p>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm text-paper-2">
            <span className={`mt-1.5 h-1 w-1 shrink-0 rounded-full ${dot}`} />
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function AgentCard({ agentId, data, cached }: { agentId: string; data: AgentAnalysis; cached?: boolean }) {
  const { label, icon: Icon } = agentMeta(agentId);
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.2, 0.7, 0.2, 1] }}
      className="glass rounded-2xl p-5"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink-700 text-gold-400">
            <Icon className="h-4 w-4" />
          </span>
          <span className="text-sm font-medium text-paper">{label}</span>
        </div>
        <span className="mono text-[11px] text-paper-3">
          {cached ? "cached · " : ""}conf {data.confidence}
        </span>
      </div>
      <p className="mt-3 text-sm leading-relaxed text-paper">{data.summary}</p>
      <List title="Key points" items={data.key_points} />
      <List title="Risks" items={data.risks} tone="risk" />
      <List title="Recommendations" items={data.recommendations} tone="rec" />
    </motion.div>
  );
}
