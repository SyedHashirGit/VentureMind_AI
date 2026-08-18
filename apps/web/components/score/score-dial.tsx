"use client";

export function ScoreDial({ value, label }: { value: number; label: string }) {
  const v = Math.max(0, Math.min(100, Math.round(value)));
  const r = 34;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - v / 100);
  const color = v >= 70 ? "var(--color-sage-400)" : v >= 40 ? "var(--color-gold-500)" : "var(--color-clay-400)";

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-24 w-24">
        <svg viewBox="0 0 80 80" className="h-24 w-24 -rotate-90">
          <circle cx="40" cy="40" r={r} fill="none" stroke="var(--color-line)" strokeWidth="6" />
          <circle
            cx="40" cy="40" r={r} fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
            strokeDasharray={circumference} strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 1s cubic-bezier(.2,.7,.2,1)" }}
          />
        </svg>
        <span className="serif absolute inset-0 flex items-center justify-center text-2xl text-paper">{v}</span>
      </div>
      <span className="eyebrow text-center leading-tight">{label}</span>
    </div>
  );
}
