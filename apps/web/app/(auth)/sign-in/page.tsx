"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Logo } from "@/components/brand/logo";

export default function SignIn() {
  const { user, loading, signInWithGoogle, signInDemo } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [user, loading, router]);

  const handleGoogle = async () => {
    setError(null);
    setGoogleLoading(true);
    try {
      await signInWithGoogle();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      // Translate Firebase error codes into readable messages
      if (msg.includes("popup-blocked")) {
        setError("Popup was blocked. Please allow popups for this site and try again.");
      } else if (msg.includes("popup-closed-by-user") || msg.includes("cancelled-popup-request")) {
        setError("Sign-in was cancelled.");
      } else if (msg.includes("unauthorized-domain")) {
        setError("This domain is not authorised in Firebase. Use Demo Mode below.");
      } else if (msg.includes("operation-not-allowed")) {
        setError("Google sign-in is not enabled in the Firebase project. Use Demo Mode below.");
      } else {
        setError(msg);
      }
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleDemo = async () => {
    setError(null);
    setDemoLoading(true);
    try {
      await signInDemo();
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <main className="grid min-h-screen place-items-center px-6">
      <div className="glass w-full max-w-sm rounded-2xl p-8 text-center">
        <div className="mb-7 flex justify-center"><Logo /></div>
        <h1 className="serif text-2xl text-paper">Step into the boardroom</h1>
        <p className="mt-2 text-sm text-paper-2">
          Sign in to convene your board and turn an idea into a verdict.
        </p>

        <button
          onClick={handleGoogle}
          disabled={googleLoading || demoLoading}
          className="mt-7 w-full rounded-lg bg-gold-500 px-5 py-3 text-sm font-medium text-ink-950 transition-transform hover:-translate-y-0.5 disabled:opacity-60"
        >
          {googleLoading ? "Signing in…" : "Continue with Google"}
        </button>

        {error && (
          <p className="mt-3 rounded-lg border border-clay-700 bg-clay-900/40 px-4 py-2 text-left text-xs text-clay-300">
            {error}
          </p>
        )}

        <div className="mt-4 flex items-center gap-3">
          <span className="h-px flex-1 bg-line" />
          <span className="text-xs text-paper-3">or</span>
          <span className="h-px flex-1 bg-line" />
        </div>

        <button
          onClick={handleDemo}
          disabled={googleLoading || demoLoading}
          className="mt-4 w-full rounded-lg border border-line bg-ink-850 px-5 py-3 text-sm font-medium text-paper-2 transition-colors hover:border-line-strong hover:text-paper disabled:opacity-60"
        >
          {demoLoading ? "Loading…" : "Try Demo Mode"}
        </button>

        <p className="mono mt-5 text-[11px] text-paper-3">your ideas stay private to your account</p>
      </div>
    </main>
  );
}
