"use client";

import { useAuth } from "@/lib/auth";
import { LogOut } from "lucide-react";

export default function Settings() {
  const { user, signOut } = useAuth();
  return (
    <div className="mx-auto max-w-2xl">
      <p className="eyebrow">Settings</p>
      <h1 className="serif mt-1 text-3xl text-paper">Account</h1>

      <div className="glass mt-7 rounded-2xl p-6">
        <Row label="Name" value={user?.displayName ?? "—"} />
        <Row label="Email" value={user?.email ?? "—"} />
        <Row label="Plan" value="Free" />
      </div>

      <button
        onClick={() => signOut()}
        className="mt-6 inline-flex items-center gap-2 rounded-lg border border-line px-5 py-3 text-sm text-paper-2 transition-colors hover:border-clay-400 hover:text-paper"
      >
        <LogOut className="h-4 w-4" /> Sign out
      </button>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-line py-3 last:border-0">
      <span className="eyebrow">{label}</span>
      <span className="text-sm text-paper">{value}</span>
    </div>
  );
}
