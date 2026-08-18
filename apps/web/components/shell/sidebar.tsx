"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";
import { Logo } from "@/components/brand/logo";
import {
  LayoutDashboard, Gavel, Target, Swords, Hammer,
  TrendingUp, Clock, Mic, Presentation, Brain, Settings,
} from "lucide-react";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/memory", label: "Founder memory", icon: Brain },
];

const WORKSPACE_NAV = [
  { seg: "", label: "Overview", icon: Target },
  { seg: "boardroom", label: "Boardroom", icon: Gavel },
  { seg: "validation", label: "Validation", icon: Target },
  { seg: "competitors", label: "Competitors", icon: Swords },
  { seg: "mvp", label: "MVP planner", icon: Hammer },
  { seg: "financials", label: "Financials", icon: TrendingUp },
  { seg: "time-machine", label: "Time machine", icon: Clock },
  { seg: "shark-tank", label: "Shark Tank Live", icon: Mic },
  { seg: "pitch-deck", label: "Pitch deck", icon: Presentation },
];

export function Sidebar() {
  const pathname = usePathname();
  const workspaceId = pathname.match(/\/workspace\/([^/]+)/)?.[1];

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-line bg-ink-950/40 px-3 py-5">
      <div className="px-2 pb-6"><Logo /></div>

      <nav className="space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => (
          <NavLink key={href} href={href} active={pathname === href} icon={<Icon className="h-4 w-4" />}>
            {label}
          </NavLink>
        ))}
      </nav>

      {workspaceId && (
        <>
          <p className="eyebrow px-3 pb-2 pt-7">Workspace</p>
          <nav className="space-y-1">
            {WORKSPACE_NAV.map(({ seg, label, icon: Icon }) => {
              const href = `/workspace/${workspaceId}${seg ? `/${seg}` : ""}`;
              return (
                <NavLink key={label} href={href} active={pathname === href} icon={<Icon className="h-4 w-4" />}>
                  {label}
                </NavLink>
              );
            })}
          </nav>
        </>
      )}

      <Link
        href="/settings"
        className="mt-auto flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-paper-3 transition-colors hover:text-paper"
      >
        <Settings className="h-4 w-4" /> Settings
      </Link>
    </aside>
  );
}

function NavLink({
  href, active, icon, children,
}: { href: string; active: boolean; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className={clsx(
        "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
        active ? "bg-ink-800 text-paper" : "text-paper-2 hover:bg-ink-850 hover:text-paper",
      )}
    >
      <span className={clsx(active ? "text-gold-500" : "text-paper-3")}>{icon}</span>
      {children}
    </Link>
  );
}
