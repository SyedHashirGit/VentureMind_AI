"use client";

import { createContext, useContext, useEffect, useState } from "react";
import {
  GoogleAuthProvider, signInWithPopup, signOut as fbSignOut,
  onAuthStateChanged, type User,
} from "firebase/auth";
import { auth } from "./firebase";
import { api } from "./api";

type AuthState = {
  user: User | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signInDemo: () => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem("mock_user") : null;
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Inject getIdToken method into parsed mock user
        parsed.getIdToken = () => Promise.resolve("mock-token-123");
        setUser(parsed);
        setLoading(false);
        return;
      } catch {
        localStorage.removeItem("mock_user");
      }
    }

    return onAuthStateChanged(auth, async (u) => {
      setUser(u);
      setLoading(false);
      if (u) {
        try { await api.bootstrap(); } catch { /* surfaced on first authed action */ }
      }
    });
  }, []);

  const signInWithGoogle = async () => {
    if (!process.env.NEXT_PUBLIC_FIREBASE_API_KEY) {
      throw new Error("Firebase is not configured. Use Demo Mode to try the app.");
    }
    await signInWithPopup(auth, new GoogleAuthProvider());
  };

  const signInDemo = async () => {
    const mu = {
      uid: "mock-user-123",
      email: "demo@venturemind.ai",
      displayName: "Demo Founder",
      photoURL: null,
    };
    if (typeof window !== "undefined") {
      localStorage.setItem("mock_user", JSON.stringify(mu));
    }
    const muWithToken = { ...mu, getIdToken: () => Promise.resolve("mock-token-123") };
    setUser(muWithToken as any);
    setLoading(false);
    try { await api.bootstrap(); } catch { /* non-fatal */ }
  };

  const signOut = async () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("mock_user");
    }
    try {
      if (user?.uid === "mock-user-123") {
        setUser(null);
      } else {
        await fbSignOut(auth);
      }
    } catch (err) {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, signInDemo, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
