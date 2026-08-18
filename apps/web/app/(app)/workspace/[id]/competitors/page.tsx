"use client";
import { use } from "react";
import { AgentDetail } from "@/components/board/agent-detail";
export default function Competitors({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <AgentDetail workspaceId={id} agentId="competitor" title="Competitor intelligence" />;
}
