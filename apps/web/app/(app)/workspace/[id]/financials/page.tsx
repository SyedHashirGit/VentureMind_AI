"use client";
import { use } from "react";
import { AgentDetail } from "@/components/board/agent-detail";
export default function Financials({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <AgentDetail workspaceId={id} agentId="investor" title="Investor & funding readiness" />;
}
