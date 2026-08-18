"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/brand/logo";
import { useAuth } from "@/lib/auth";
import { ArrowRight } from "lucide-react";

const BOARD = ["CEO", "CTO", "Product", "Investor", "Marketing", "Competitor", "Legal"];

export default function Landing() {
  const { user, signInWithGoogle } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) router.replace("/dashboard");
  }, [user, router]);

  return (
    <main className="mx-auto max-w-6xl px-6">
      <nav className="flex items-center justify-between py-6">
        <Logo />
        <button
          onClick={() => user ? router.push("/dashboard") : signInWithGoogle()}
          className="rounded-lg border border-line px-4 py-2 text-sm text-paper-2 transition-colors hover:border-line-strong hover:text-paper"
        >
          {user ? "Open workspace" : "Sign in"}
        </button>
      </nav>

      <section className="grid items-center gap-12 pt-16 pb-24 md:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="eyebrow mb-5">AI startup incubator</p>
          <h1 className="serif text-[clamp(2.6rem,6vw,4.4rem)] leading-[1.04] text-paper">
            Walk in with an idea.
            <br />
            Leave with a <span className="italic text-gold-400">verdict</span>.
          </h1>
          <p className="mt-6 max-w-md text-[15px] leading-relaxed text-paper-2">
            Convene a boardroom of seven expert agents. They analyze, challenge each
            other, and pressure-test your idea, then hand you scores, a blueprint, and
            a pitch you can take to investors.
          </p>
          <div className="mt-8 flex items-center gap-3">
            <button
              onClick={() => user ? router.push("/dashboard") : signInWithGoogle()}
              className="group inline-flex items-center gap-2 rounded-lg bg-gold-500 px-5 py-3 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5"
            >
              Convene your board
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </button>
            <span className="mono text-xs text-paper-3">no idea is too early</span>
          </div>
        </div>

        <div className="glass rounded-2xl p-6">
          <p className="eyebrow mb-4">The board convenes</p>
          <ul className="space-y-2.5">
            {BOARD.map((role, i) => (
              <li key={role} className="flex items-center justify-between rounded-lg border border-line bg-ink-850 px-4 py-3">
                <span className="text-sm text-paper">{role}</span>
                <span className="mono text-[11px] text-paper-3">agent {String(i + 1).padStart(2, "0")}</span>
              </li>
            ))}
          </ul>
          <div className="mt-5 flex items-center justify-between border-t border-line pt-4">
            <span className="eyebrow">Verdict</span>
            <span className="serif text-3xl text-gold-400">
              82<span className="text-base text-paper-3">/100</span>
            </span>
          </div>
        </div>
      </section>
    </main>
  );
}
