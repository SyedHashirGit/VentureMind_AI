"use client";

import { useAuth } from "@/lib/auth";
import { LogOut } from "lucide-react";

export function Topbar({ title }: { title?: string }) {
  const { user, signOut } = useAuth();
  const initial = (user?.displayName || user?.email || "F").charAt(0).toUpperCase();

  return (
    <header className="glass sticky top-0 z-10 flex h-14 items-center justify-between px-6">
      <span className="text-sm text-paper-2">{title ?? "VentureMind"}</span>
      <div className="flex items-center gap-3">
        <span className="hidden text-sm text-paper-3 sm:block">{user?.email}</span>
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ink-700 text-sm text-gold-400">
          {initial}
        </span>
        <button
          onClick={() => signOut()}
          aria-label="Sign out"
          className="rounded-lg p-2 text-paper-3 transition-colors hover:text-paper"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
