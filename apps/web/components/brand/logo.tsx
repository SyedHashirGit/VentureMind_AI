import { clsx } from "clsx";

/** VentureMind mark: minds rising and converging to a single decision (the apex node). */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={clsx("h-7 w-7", className)} aria-hidden="true">
      <defs>
        <linearGradient id="vm-mark" x1="0" y1="32" x2="0" y2="0" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#bc8222" />
          <stop offset="1" stopColor="#f4cd78" />
        </linearGradient>
      </defs>
      <path d="M7 25 L16 8 L25 25" fill="none" stroke="url(#vm-mark)" strokeWidth="2.6"
            strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 25 L16 16" fill="none" stroke="url(#vm-mark)" strokeWidth="2.6"
            strokeLinecap="round" opacity="0.55" />
      <circle cx="16" cy="8" r="3" fill="#f4cd78" />
    </svg>
  );
}

export function Logo({ className }: { className?: string }) {
  return (
    <span className={clsx("inline-flex items-center gap-2.5", className)}>
      <LogoMark />
      <span className="text-[15px] tracking-tight">
        <span className="font-semibold text-paper">Venture</span>
        <span className="font-normal text-paper-2">Mind</span>
        <span className="ml-1 align-super text-[9px] tracking-[0.18em] text-gold-500">AI</span>
      </span>
    </span>
  );
}
