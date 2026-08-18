"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { api, type BoardroomMessage, type ValidationContent } from "@/lib/api";
import { VerdictCard } from "@/components/board/verdict-card";

function Block({ title, body }: { title: string; body?: string }) {
  if (!body) return null;
  return (
    <div className="glass rounded-xl p-5">
      <p className="eyebrow mb-1.5">{title}</p>
      <p className="text-sm leading-relaxed text-paper-2">{body}</p>
    </div>
  );
}

export default function Validation({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [v, setV] = useState<ValidationContent | null | undefined>(undefined);

  useEffect(() => {
    api.getBoardroom(id)
      .then(({ messages }) => {
        const m = messages.filter((x: BoardroomMessage) => x.agent === "validation").at(-1);
        setV(m ? (m.content as ValidationContent) : null);
      })
      .catch(() => setV(null));
  }, [id]);

  return (
    <div className="mx-auto max-w-3xl">
      <p className="eyebrow">Validation center</p>
      {v === undefined ? (
        <p className="mt-6 text-sm text-paper-3">Loading…</p>
      ) : v === null ? (
        <p className="mt-6 text-sm text-paper-3">
          No verdict yet. <Link href={`/workspace/${id}/boardroom`} className="text-gold-400">Convene the board</Link> first.
        </p>
      ) : (
        <div className="mt-5 space-y-4">
          <VerdictCard v={v} />
          <div className="grid gap-3 sm:grid-cols-2">
            <Block title="Market size" body={v.market_size} />
            <Block title="Demand" body={v.demand} />
            <Block title="Competition" body={v.competition} />
            <Block title="Feasibility" body={v.feasibility} />
          </div>
          {v.risks?.length ? (
            <div className="glass rounded-xl p-5">
              <p className="eyebrow mb-2">Key risks</p>
              <ul className="space-y-1.5">
                {v.risks.map((r, i) => (
                  <li key={i} className="flex gap-2 text-sm text-paper-2">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-clay-400" />{r}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
