"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type AgentAnalysis, type BoardroomMessage } from "@/lib/api";
import { AgentCard } from "./agent-card";
import { RoleOutput } from "./role-output";

export function AgentDetail({ workspaceId, agentId, title }: { workspaceId: string; agentId: string; title: string }) {
  const [msg, setMsg] = useState<BoardroomMessage | null | undefined>(undefined);

  useEffect(() => {
    api.getBoardroom(workspaceId)
      .then(({ messages }) => setMsg(messages.filter((m) => m.agent === agentId).at(-1) ?? null))
      .catch(() => setMsg(null));
  }, [workspaceId, agentId]);

  return (
    <div className="mx-auto max-w-3xl">
      <p className="eyebrow">{title}</p>
      {msg === undefined ? (
        <p className="mt-6 text-sm text-paper-3">Loading…</p>
      ) : msg === null ? (
        <p className="mt-6 text-sm text-paper-3">
          No analysis yet. <Link href={`/workspace/${workspaceId}/boardroom`} className="text-gold-400">Convene the board</Link> first.
        </p>
      ) : (
        <div className="mt-5 space-y-5">
          <AgentCard agentId={agentId} data={msg.content as AgentAnalysis} cached={msg.cached} />
          <RoleOutput data={(msg.content as AgentAnalysis).role_output} />
        </div>
      )}
    </div>
  );
}
