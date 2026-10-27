import { cardBlocks, splitNextStep } from "@/lib/card";
import type { Exchange } from "@/lib/chat";
import { Answer } from "./Answer";
import { Inspector } from "./Inspector";
import { ResultCard } from "./ResultCard";
import { Sources } from "./Sources";

export type Mode = "user" | "verbose";

function Pending({ x }: { x: Exchange }) {
  const label = x.tools.length ? "A fazer as contas…" : x.timings.sources !== undefined ? "A escrever…" : "A procurar nas fontes…";
  return (
    <div className="flex items-center gap-2 text-sm text-muted">
      <span className="flex gap-1" aria-hidden>
        {[0, 1, 2].map((i) => (
          <span key={i} className="size-1.5 animate-pulse rounded-full bg-muted" style={{ animationDelay: `${i * 150}ms` }} />
        ))}
      </span>
      {label}
    </div>
  );
}

export function ExchangeView({ x, mode, onRetry }: { x: Exchange; mode: Mode; onRetry: () => void }) {
  // enquanto chega em stream fica tudo no corpo; o próximo passo só se separa no fim
  const { body, next } = x.status === "done" ? splitNextStep(x.answer) : { body: x.answer, next: undefined };
  return (
    <article className="space-y-3" aria-busy={x.status === "streaming"}>
      <div className="flex justify-end">
        <p className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-accent px-4 py-2.5 text-[15px] text-white">
          {x.question}
        </p>
      </div>

      <div className="rounded-2xl rounded-bl-md border border-line bg-card px-4 py-3.5 shadow-sm">
        {x.warning && (
          <div className="mb-3 rounded-lg border border-warn/30 bg-warn-soft px-3 py-2 text-sm text-warn" role="alert">
            {x.warning.text}
          </div>
        )}

        <div aria-live="polite">
          <ResultCard blocks={cardBlocks(x.tools)} />
          {x.answer ? (
            <Answer text={body} exchangeId={x.id} sources={x.allSources} />
          ) : (
            x.status === "streaming" && <Pending x={x} />
          )}
          {x.status === "streaming" && x.answer && <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-accent align-middle" aria-hidden />}
          {next && (
            <div className="mt-4 rounded-xl border border-ok/25 bg-ok-soft px-3.5 py-2.5">
              <div className="mb-0.5 text-xs font-medium uppercase tracking-wide text-ok">Próximo passo</div>
              <Answer text={next} exchangeId={x.id} sources={x.allSources} />
            </div>
          )}
        </div>

        {x.status === "error" && (
          <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
            <span className="text-bad">Não foi possível responder{mode === "user" ? "." : `: ${x.error}`}</span>
            <button onClick={onRetry} className="rounded-lg border border-line px-3 py-1 font-medium hover:border-accent">
              Tentar outra vez
            </button>
          </div>
        )}
        {x.status === "stopped" && <p className="mt-2 text-sm text-muted">Parado.</p>}

        {x.status === "done" && <Sources sources={x.sources} exchangeId={x.id} />}

        {mode === "verbose" && <Inspector x={x} />}
      </div>
    </article>
  );
}
