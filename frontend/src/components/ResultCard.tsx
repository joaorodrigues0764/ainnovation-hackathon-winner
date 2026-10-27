import type { CardBlock } from "@/lib/card";

// Os números do cartão vêm só das calculadoras (evento `tool`), nunca do texto do LLM.
export function ResultCard({ blocks }: { blocks: CardBlock[] }) {
  if (!blocks.length) return null;
  return (
    <div className={`mb-4 grid gap-3 ${blocks.length > 1 ? "sm:grid-cols-2" : ""}`}>
      {blocks.map((b, i) => (
        <section key={i} className="min-w-0 rounded-xl border border-accent/25 bg-accent-soft/60 p-3.5" aria-label={b.title}>
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-xs font-medium text-muted">{b.title}</h3>
            <span className="shrink-0 rounded-full bg-card px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-accent">
              calculado
            </span>
          </div>
          <div className="mt-1.5">
            <div className="text-xs text-muted">{b.main.label}</div>
            <div className="text-2xl font-semibold tabular-nums text-ink">{b.main.value}</div>
          </div>
          {b.others.length > 0 && (
            <dl className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
              {b.others.map((f) => (
                <div key={f.label} className="min-w-0">
                  <dt className="truncate text-xs text-muted">{f.label}</dt>
                  <dd className="font-medium tabular-nums">{f.value}</dd>
                </div>
              ))}
            </dl>
          )}
          {b.note && <p className="mt-2 text-[11px] leading-snug text-muted">{b.note}</p>}
        </section>
      ))}
    </div>
  );
}
