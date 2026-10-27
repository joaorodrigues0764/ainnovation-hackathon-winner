import type { Source } from "@/lib/api";

export function Sources({ sources, exchangeId }: { sources: Source[]; exchangeId: string }) {
  if (!sources.length) return null;
  return (
    <div className="mt-4 border-t border-line pt-3">
      <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted">Fontes</h3>
      <ol className="space-y-1.5 text-sm">
        {sources.map((s) => (
          <li key={s.n} id={`src-${exchangeId}-${s.n}`} className="flex gap-2 scroll-mt-24 target:text-accent">
            <span className="mt-0.5 inline-flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full bg-accent-soft px-1.5 text-[11px] font-medium text-accent">
              {s.n}
            </span>
            <span className="min-w-0">
              {s.url ? (
                <a href={s.url} target="_blank" rel="noopener noreferrer" className="font-medium text-ink underline decoration-line underline-offset-2 hover:decoration-accent">
                  {s.title}
                </a>
              ) : (
                <span className="font-medium">{s.title}</span>
              )}
              {s.source && <span className="text-muted"> · {s.source}</span>}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
