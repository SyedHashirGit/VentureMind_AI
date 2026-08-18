"use client";

import { useEffect, useState } from "react";
import { api, type Telemetry } from "@/lib/api";

const fmt = (n: number) => n.toLocaleString();

export function TelemetryPanel() {
  const [t, setT] = useState<Telemetry | null>(null);

  useEffect(() => {
    let alive = true;
    const tick = () => api.telemetry().then((d) => alive && setT(d)).catch(() => {});
    tick();
    const id = setInterval(tick, 4000);
    return () => { alive = false; clearInterval(id); };
  }, []);

  const stat = (k: string, v: string, accent?: string) => (
    <div className="flex flex-col">
      <span className="mono text-[11px] tracking-wide text-paper-3">{k}</span>
      <span className={`mono mt-0.5 text-lg ${accent ?? "text-paper"}`}>{v}</span>
    </div>
  );

  return (
    <div className="glass flex flex-wrap items-center gap-x-9 gap-y-4 rounded-xl px-5 py-4">
      <span className="flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-sage-400" />
        <span className="eyebrow">Live infrastructure</span>
      </span>
      {stat("valkey · cache hit rate", t ? `${Math.round(t.cacheHitRate * 100)}%` : "—", "text-gold-400")}
      {stat("gemini calls saved", t ? fmt(t.geminiSaved) : "—", "text-sage-400")}
      {stat("cache hits", t ? fmt(t.cacheHits) : "—")}
      {stat("pub/sub msgs", t ? fmt(t.pubsubMsgs) : "—")}
      {stat("agent runs", t ? fmt(t.agentRuns) : "—")}
    </div>
  );
}
