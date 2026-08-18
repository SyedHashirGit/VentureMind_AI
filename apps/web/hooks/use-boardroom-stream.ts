"use client";

import { useEffect, useRef, useState } from "react";
import { auth } from "@/lib/firebase";
import { api } from "@/lib/api";

export type BoardroomMessage = {
  agent: string;
  role: "analysis" | "challenge" | "rebuttal" | "consensus";
  content: unknown;
  ts: number;
};

/** Subscribes to the live boardroom SSE stream for a workspace. */
export function useBoardroomStream(workspaceId: string | null) {
  const [messages, setMessages] = useState<BoardroomMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!workspaceId) return;
    let closed = false;

    (async () => {
      let token = await auth.currentUser?.getIdToken();
      // Fall back to mock token when signed in via demo mode
      if (!token && typeof window !== "undefined") {
        const mockUser = localStorage.getItem("mock_user");
        if (mockUser) token = "mock-token-123";
      }
      if (closed || !token) return;
      // EventSource cannot set headers; pass the token as a query param the relay validates.
      const url = `${api.apiBase}/boardroom/${workspaceId}/stream?access_token=${token}`;
      const es = new EventSource(url);
      sourceRef.current = es;
      es.addEventListener("open", () => setConnected(true));
      es.addEventListener("boardroom", (e) => {
        try { setMessages((prev) => [...prev, JSON.parse((e as MessageEvent).data)]); } catch {}
      });
      es.addEventListener("error", () => setConnected(false));
    })();

    return () => { closed = true; sourceRef.current?.close(); setConnected(false); };
  }, [workspaceId]);

  return { messages, connected };
}
