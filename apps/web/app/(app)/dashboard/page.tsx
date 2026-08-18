"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, type Workspace } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Plus, ArrowRight } from "lucide-react";
import { TelemetryPanel } from "@/components/telemetry/telemetry-panel";

export default function Dashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [workspaces, setWorkspaces] = useState<Workspace[] | null>(null);
  const [title, setTitle] = useState("");
  const [idea, setIdea] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listWorkspaces().then(setWorkspaces).catch((e) => setError(e.message));
  }, []);

  const create = async () => {
    if (idea.trim().length < 10) { setError("Describe the idea in a sentence or two."); return; }
    setCreating(true); setError(null);
    try {
      const ws = await api.createWorkspace({ title: title.trim() || "Untitled idea", ideaPrompt: idea.trim() });
      router.push(`/workspace/${ws.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not create the workspace.");
    } finally {
      setCreating(false);
    }
  };

  const firstName = (user?.displayName || user?.email || "founder").split(/[ @]/)[0];

  return (
    <div className="mx-auto max-w-4xl">
      <p className="eyebrow">Founder dashboard</p>
      <h1 className="serif mt-1 text-3xl text-paper">Welcome back, {firstName}.</h1>

      <div className="mt-6"><TelemetryPanel /></div>

      <section className="glass mt-8 rounded-2xl p-6">
        <p className="eyebrow mb-4">New idea</p>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Name it (optional)"
          className="mb-3 w-full rounded-lg border border-line bg-ink-850 px-4 py-3 text-sm text-paper outline-none placeholder:text-paper-3 focus:border-gold-600"
        />
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="I want to build an AI fitness platform for college students..."
          rows={3}
          className="w-full resize-none rounded-lg border border-line bg-ink-850 px-4 py-3 text-sm text-paper outline-none placeholder:text-paper-3 focus:border-gold-600"
        />
        {error && <p className="mt-3 text-sm text-clay-400">{error}</p>}
        <button
          onClick={create}
          disabled={creating}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-gold-500 px-5 py-3 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5 disabled:opacity-60"
        >
          <Plus className="h-4 w-4" /> {creating ? "Convening..." : "Convene the board"}
        </button>
      </section>

      <section className="mt-10">
        <p className="eyebrow mb-4">Your ideas</p>
        {workspaces === null ? (
          <p className="text-sm text-paper-3">Loading...</p>
        ) : workspaces.length === 0 ? (
          <p className="text-sm text-paper-3">No ideas yet. Your first verdict is one prompt away.</p>
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2">
            {workspaces.map((w) => (
              <li key={w.id}>
                <button
                  onClick={() => router.push(`/workspace/${w.id}`)}
                  className="group flex w-full items-center justify-between rounded-xl border border-line bg-ink-850 px-5 py-4 text-left transition-colors hover:border-line-strong"
                >
                  <span>
                    <span className="block text-sm text-paper">{w.title}</span>
                    <span className="mono mt-0.5 block text-[11px] text-paper-3">{w.status}</span>
                  </span>
                  <ArrowRight className="h-4 w-4 text-paper-3 transition-transform group-hover:translate-x-0.5" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
