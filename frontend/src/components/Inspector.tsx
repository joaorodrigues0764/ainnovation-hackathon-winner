import type { ReactNode } from "react";
import type { Exchange, LoggedEvent } from "@/lib/chat";

// Modo verboso: tudo o que a API devolveu para uma troca, para depurar e para o harness.

const ms = (t?: number) => (t === undefined ? "—" : t < 1000 ? `${Math.round(t)} ms` : `${(t / 1000).toFixed(1)} s`);

function Metric({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border border-line bg-panel px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-muted">{label}</div>
      <div className="font-mono text-sm">{value}</div>
    </div>
  );
}

function Section({ title, count, open = false, children }: { title: string; count?: number; open?: boolean; children: ReactNode }) {
  return (
    <details open={open} className="group rounded-lg border border-line">
      <summary className="flex cursor-pointer select-none items-center justify-between px-3 py-2 text-sm font-medium">
        <span>
          {title}
          {count !== undefined && <span className="ml-1.5 text-muted">({count})</span>}
        </span>
        <span className="text-muted transition group-open:rotate-90" aria-hidden>›</span>
      </summary>
      <div className="border-t border-line px-3 py-2">{children}</div>
    </details>
  );
}

function Json({ value }: { value: unknown }) {
  return (
    <pre className="max-h-72 overflow-auto whitespace-pre-wrap break-words rounded-md bg-code p-2 font-mono text-xs leading-snug">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

/** Junta deltas seguidos numa linha, senão o registo fica com centenas de linhas. */
function collapse(events: LoggedEvent[]) {
  const rows: { t: number; t2?: number; event: string; n: number; data?: unknown }[] = [];
  for (const e of events) {
    const last = rows.at(-1);
    if (e.event === "delta" && last?.event === "delta") {
      last.n += 1;
      last.t2 = e.t;
    } else {
      rows.push({ t: e.t, event: e.event, n: 1, data: e.event === "delta" ? undefined : e.data });
    }
  }
  return rows;
}

const BADGE: Record<string, string> = {
  streaming: "bg-accent-soft text-accent",
  done: "bg-ok-soft text-ok",
  error: "bg-bad-soft text-bad",
  stopped: "bg-panel text-muted",
};

export function Inspector({ x }: { x: Exchange }) {
  const cited = new Set(x.sources.map((s) => s.n));
  return (
    <div className="mt-4 space-y-3 border-t border-dashed border-line pt-4 text-sm">
      <div className="flex flex-wrap items-center gap-1.5 text-xs">
        <span className={`rounded-full px-2 py-0.5 font-medium ${BADGE[x.status]}`}>{x.status}</span>
        <span className="rounded-full bg-panel px-2 py-0.5">jornada: {x.request.journey ?? "—"}</span>
        <span className="rounded-full bg-panel px-2 py-0.5">histórico: {x.request.history?.length ?? 0} msg</span>
        {x.scope.map((s) => (
          <span key={s} className="rounded-full bg-warn-soft px-2 py-0.5 text-warn">guardrail: {s}</span>
        ))}
        {x.warning?.pii.map((p) => (
          <span key={p} className="rounded-full bg-bad-soft px-2 py-0.5 text-bad">PII tapado: {p}</span>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <Metric label="fontes" value={ms(x.timings.sources)} />
        <Metric label="1.º texto" value={ms(x.timings.firstDelta)} />
        <Metric label="total" value={ms(x.timings.end)} />
        <Metric label="deltas" value={x.deltas} />
      </div>

      {x.error && <div className="rounded-lg bg-bad-soft px-3 py-2 font-mono text-xs text-bad">{x.error}</div>}

      <Section title="Juiz de completude" open={x.judge?.complete === false}>
        {!x.judge ? (
          <p className="text-muted">Não correu (guardrail ativo ou JUDGE=0).</p>
        ) : (
          <div className="space-y-1.5 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 font-medium ${x.judge.complete ? "bg-ok-soft text-ok" : "bg-warn-soft text-warn"}`}>
                {x.judge.complete ? "completa" : "faltam dados"}
              </span>
              <span className="font-mono text-muted">{ms(x.judge.ms)}</span>
              {x.judge.error && <span className="text-bad">erro (seguiu sem clarificação): {x.judge.error}</span>}
            </div>
            {x.judge.reason && <p>{x.judge.reason}</p>}
            {x.judge.missing.length > 0 && <p><span className="text-muted">Em falta:</span> {x.judge.missing.join("; ")}</p>}
            {x.judge.questions.length > 0 && (
              <ul className="list-disc pl-5">{x.judge.questions.map((q) => <li key={q}>{q}</li>)}</ul>
            )}
          </div>
        )}
      </Section>

      <Section title="Calculadoras" count={x.tools.length} open={x.tools.length > 0}>
        {x.tools.length === 0 ? (
          <p className="text-muted">Nenhuma calculadora foi chamada.</p>
        ) : (
          <div className="space-y-3">
            {x.tools.map((tool, i) => (
              <div key={i}>
                <div className="mb-1 font-mono text-xs font-medium">{tool.name}</div>
                <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                  <div className="min-w-0">
                    <div className="mb-1 text-[11px] uppercase text-muted">argumentos (do LLM)</div>
                    <Json value={tool.args} />
                  </div>
                  <div className="min-w-0">
                    <div className="mb-1 text-[11px] uppercase text-muted">resultado (Python)</div>
                    <Json value={tool.result} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section title="Chunks recuperados" count={x.chunks.length} open={x.chunks.length > 0}>
        {x.chunks.length === 0 ? (
          <p className="text-muted">A pesquisa não encontrou nada na KB.</p>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="text-muted">
              <tr><th className="py-1 pr-2 font-medium">#</th><th className="py-1 pr-2 font-medium">ficheiro</th><th className="py-1 pr-2 font-medium">secção</th><th className="py-1 text-right font-medium">RRF</th></tr>
            </thead>
            <tbody className="font-mono">
              {x.chunks.map((c, i) => (
                <tr key={i} className="border-t border-line">
                  <td className="py-1 pr-2 text-muted">{i + 1}</td>
                  <td className="break-all py-1 pr-2">{c.file}</td>
                  <td className="py-1 pr-2 font-sans">{c.section || "(intro)"}</td>
                  <td className="py-1 text-right">{c.score.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      <Section title="Fontes no prompt" count={x.allSources.length}>
        <ul className="space-y-1 text-xs">
          {x.allSources.map((s) => (
            <li key={s.n} className="flex gap-2">
              <span className="font-mono">[{s.n}]</span>
              <span className={cited.has(s.n) && x.status === "done" ? "" : "text-muted"}>
                {s.title} · {s.source}
                {x.status === "done" && (cited.has(s.n) ? " · citada" : " · não citada")}
              </span>
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Pedido enviado">
        <Json value={x.request} />
      </Section>

      <Section title="Eventos SSE" count={x.events.length}>
        <ol className="space-y-1 font-mono text-xs">
          {collapse(x.events).map((r, i) => (
            <li key={i}>
              <div className="flex gap-2">
                <span className="w-16 shrink-0 text-right text-muted">{ms(r.t)}</span>
                <span className="font-medium">{r.event}{r.n > 1 && ` ×${r.n}`}</span>
                {r.t2 !== undefined && <span className="text-muted">até {ms(r.t2)}</span>}
              </div>
              {r.data !== undefined && r.event !== "sources" && (
                <div className="ml-[4.5rem] mt-1 min-w-0"><Json value={r.data} /></div>
              )}
            </li>
          ))}
        </ol>
      </Section>
    </div>
  );
}
