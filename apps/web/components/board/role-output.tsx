"use client";

function render(value: unknown): React.ReactNode {
  if (value == null) return <span className="text-paper-3">—</span>;
  if (Array.isArray(value))
    return (
      <ul className="space-y-1">
        {value.map((v, i) => <li key={i} className="text-sm text-paper-2">• {String(typeof v === "object" ? JSON.stringify(v) : v)}</li>)}
      </ul>
    );
  if (typeof value === "object")
    return (
      <div className="space-y-2">
        {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
          <div key={k}>
            <p className="eyebrow mb-1">{k.replace(/_/g, " ")}</p>
            {render(v)}
          </div>
        ))}
      </div>
    );
  return <span className="text-sm text-paper">{String(value)}</span>;
}

export function RoleOutput({ data }: { data: Record<string, unknown> }) {
  const entries = Object.entries(data ?? {});
  if (!entries.length) return null;
  return (
    <div className="glass rounded-2xl p-6">
      <p className="eyebrow mb-4">Detailed analysis</p>
      <div className="grid gap-5 sm:grid-cols-2">
        {entries.map(([k, v]) => (
          <div key={k}>
            <p className="mb-1.5 text-sm font-medium text-paper">{k.replace(/_/g, " ")}</p>
            {render(v)}
          </div>
        ))}
      </div>
    </div>
  );
}
