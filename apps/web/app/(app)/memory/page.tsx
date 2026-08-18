"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Brain, Search } from "lucide-react";

export default function Memory() {
  const [profile, setProfile] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [results, setResults] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    api.memoryProfile().then((d) => {
      // Breeth returns a JSON string — parse it to check for not_found
      try {
        const parsed = JSON.parse(d.profile);
        if (parsed?.ok === false || parsed?.error === "not_found") {
          setProfile("");
        } else {
          setProfile(d.profile);
        }
      } catch {
        setProfile(d.profile);
      }
    }).catch(() => setProfile(""));
  }, []);

  const search = async () => {
    if (!q.trim()) return;
    setSearching(true);
    try { setResults((await api.memorySearch(q.trim())).results); } catch { setResults(""); } finally { setSearching(false); }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex items-center gap-2.5">
        <Brain className="h-5 w-5 text-gold-400" />
        <p className="eyebrow">Founder memory</p>
      </div>
      <h1 className="serif mt-1 text-3xl text-paper">What the board remembers about you</h1>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-paper-2">
        VentureMind keeps an intent-aware memory of your ideas, decisions, and preferences, so every
        new analysis is shaped by your history. The more you build, the sharper its judgment becomes.
      </p>

      <div className="glass mt-7 rounded-2xl p-6">
        <p className="eyebrow mb-3">Your founder profile</p>
        {profile === null ? (
          <p className="text-sm text-paper-3">Loading…</p>
        ) : profile ? (
          <p className="mono whitespace-pre-wrap text-sm leading-relaxed text-paper-2">{profile}</p>
        ) : (
          <p className="text-sm text-paper-3">No memory yet. Convene a board on your first idea and it starts learning.</p>
        )}
      </div>

      <div className="mt-5">
        <div className="flex gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
            placeholder="Ask your memory… e.g. what kinds of ideas do I gravitate to?"
            className="flex-1 rounded-lg border border-line bg-ink-850 px-4 py-3 text-sm text-paper outline-none placeholder:text-paper-3 focus:border-gold-600"
          />
          <button onClick={search} disabled={searching} className="rounded-lg border border-line px-4 text-paper-2 transition-colors hover:border-line-strong hover:text-paper">
            <Search className="h-4 w-4" />
          </button>
        </div>
        {results !== null && (
          <div className="glass mt-3 rounded-xl p-5">
            {results ? <p className="mono whitespace-pre-wrap text-sm text-paper-2">{results}</p>
                     : <p className="text-sm text-paper-3">Nothing relevant in memory yet.</p>}
          </div>
        )}
      </div>
    </div>
  );
}
