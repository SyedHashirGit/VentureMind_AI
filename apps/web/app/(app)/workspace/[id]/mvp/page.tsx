"use client";
import { use } from "react";
import { AgentDetail } from "@/components/board/agent-detail";
export default function Mvp({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <AgentDetail workspaceId={id} agentId="pm" title="MVP planner" />;
}
