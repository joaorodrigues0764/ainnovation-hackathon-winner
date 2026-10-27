"use client";

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Composer } from "@/components/Composer";
import { ExchangeView, type Mode } from "@/components/ExchangeView";
import { ProfileForm } from "@/components/ProfileForm";
import {
  API_URL, getHealth, getJourneys, streamChat,
  type ChatRequest, type Health, type Journey, type JourneyId, type Profile,
} from "@/lib/api";
import { applyEvent, historyFrom, newExchange, type Exchange } from "@/lib/chat";
import { suggestFollowUps } from "@/lib/followups";

const FALLBACK_JOURNEYS: Journey[] = [
  { id: "credito", label: "Primeiro crédito" },
  { id: "salario", label: "Primeiro salário" },
  { id: "irs", label: "Primeiro IRS" },
  { id: "burlas", label: "Burlas e segurança" },
  { id: "poupanca", label: "Poupar para um objetivo" },
  { id: "geral", label: "Geral" },
];

const SUGGESTIONS: Record<JourneyId, string[]> = {
  credito: ["Vale a pena pedir crédito para um carro de 8 000 € a 9% em 48 meses?", "Qual a diferença entre TAEG e TAN?"],
  salario: ["Recebo 900 € por mês, como divido o dinheiro?", "Ganho 1 000 € brutos, quanto recebo?"],
  irs: ["O IRS Jovem aplica-se a mim?", "Quando tenho de entregar o IRS?"],
  burlas: ["Recebi um SMS do banco a pedir o código, o que faço?", "Pediram-me para associar um número ao MB WAY no Multibanco."],
  poupanca: ["Quero juntar 600 € em 6 meses para uma viagem, consigo guardar 80 € por mês.", "Quanto rendem 50 € por mês a 3% durante 5 anos?"],
  geral: ["O que é a inflação?", "Como começo um fundo de emergência?"],
};

const MODE_KEY = "caixa-explica:mode";

// modo guardado no browser (conveniência por pessoa); sem storage fica só em memória
let memoryMode: Mode = "user";
const modeListeners = new Set<() => void>();

function readMode(): Mode {
  try {
    return localStorage.getItem(MODE_KEY) === "verbose" ? "verbose" : memoryMode;
  } catch {
    return memoryMode;
  }
}

function subscribeMode(cb: () => void) {
  modeListeners.add(cb);
  window.addEventListener("storage", cb);
  return () => {
    modeListeners.delete(cb);
    window.removeEventListener("storage", cb);
  };
}

function useMode(): [Mode, (m: Mode) => void] {
  const mode = useSyncExternalStore<Mode>(subscribeMode, readMode, () => "user");
  const update = useCallback((m: Mode) => {
    memoryMode = m;
    try {
      localStorage.setItem(MODE_KEY, m);
    } catch {
      /* sem storage */
    }
    modeListeners.forEach((cb) => cb());
  }, []);
  return [mode, update];
}

export default function Home() {
  const [mode, setMode] = useMode();
  const [health, setHealth] = useState<Health | "down" | null>(null);
  const [journeys, setJourneys] = useState<Journey[]>(FALLBACK_JOURNEYS);
  const [journey, setJourney] = useState<JourneyId>("credito");
  const [profile, setProfile] = useState<Profile>({});
  const [showProfile, setShowProfile] = useState(false);
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const busy = exchanges.at(-1)?.status === "streaming";
  const followUps = suggestFollowUps(exchanges, journey);

  useEffect(() => {
    getHealth().then(setHealth, () => setHealth("down"));
    getJourneys().then(setJourneys, () => {});
  }, []);

  // segue a resposta enquanto chega, mas só se a pessoa estiver perto do fim da página
  useEffect(() => {
    const nearBottom = window.innerHeight + window.scrollY >= document.body.scrollHeight - 240;
    if (nearBottom) endRef.current?.scrollIntoView({ block: "end" });
  }, [exchanges]);

  const update = (id: string, f: (x: Exchange) => Exchange) =>
    setExchanges((prev) => prev.map((x) => (x.id === id ? f(x) : x)));

  const send = async (question: string, base: Exchange[] = exchanges) => {
    const request: ChatRequest = {
      question,
      journey,
      ...(Object.keys(profile).length ? { profile } : {}),
      history: historyFrom(base),
    };
    const id = crypto.randomUUID();
    setExchanges([...base, newExchange(id, request)]);

    const ctrl = new AbortController();
    abortRef.current = ctrl;
    const t0 = performance.now();
    try {
      await streamChat(request, (ev) => update(id, (x) => applyEvent(x, ev, performance.now() - t0)), ctrl.signal);
      // o stream fechou sem `done` nem `error` (ex.: servidor caiu a meio)
      update(id, (x) => (x.status === "streaming" ? { ...x, status: "error", error: "a ligação terminou sem resposta completa" } : x));
    } catch (e) {
      const end = performance.now() - t0;
      update(id, (x) =>
        ctrl.signal.aborted
          ? { ...x, status: "stopped", timings: { ...x.timings, end } }
          : { ...x, status: "error", error: `${e instanceof Error ? e.message : e} (API em ${API_URL})`, timings: { ...x.timings, end } },
      );
    } finally {
      if (abortRef.current === ctrl) abortRef.current = null;
    }
  };

  const retry = (x: Exchange) => send(x.question, exchanges.filter((e) => e.id !== x.id));

  const reset = () => {
    abortRef.current?.abort();
    setExchanges([]);
  };

  const profileSummary = [
    profile.idade && `${profile.idade} anos`,
    profile.rendimento_liquido !== undefined && `${profile.rendimento_liquido} €/mês`,
    profile.objetivo,
  ].filter(Boolean).join(" · ");

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-10 border-b border-line bg-bg/90 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-3">
          <div className="min-w-0 flex-1">
            <h1 className="text-base font-semibold leading-tight">Caixa Explica</h1>
            <p className="truncate text-xs text-muted">Literacia financeira para jovens, com fontes oficiais</p>
          </div>
          {mode === "verbose" && (
            <span className="hidden items-center gap-1.5 font-mono text-xs text-muted sm:flex" title={API_URL}>
              <span className={`size-2 rounded-full ${health === "down" ? "bg-bad" : health ? "bg-ok" : "bg-line"}`} />
              {health === "down" ? "API em baixo" : health ? `${health.model} · ${health.chunks} chunks · emb ${health.embeddings ? "on" : "off"}` : "…"}
            </span>
          )}
          <div role="radiogroup" aria-label="Modo de visualização" className="flex rounded-lg border border-line p-0.5 text-xs">
            {(["user", "verbose"] as const).map((m) => (
              <button
                key={m}
                role="radio"
                aria-checked={mode === m}
                onClick={() => setMode(m)}
                className={`min-h-9 rounded-md px-3 py-1.5 font-medium ${mode === m ? "bg-ink text-bg" : "text-muted hover:text-ink"}`}
              >
                {m === "user" ? "Utilizador" : "Verboso"}
              </button>
            ))}
          </div>
        </div>
        <p role="note" className="border-t border-line bg-card px-4 py-1.5 text-center text-xs leading-snug text-muted">
          <strong className="font-semibold text-ink">Assistente de IA, pode errar.</strong> Não é aconselhamento financeiro, fiscal ou jurídico. Confirma nas fontes citadas e não partilhes dados pessoais.
        </p>
      </header>

      <main className="mx-auto w-full max-w-3xl flex-1 px-4 pb-6 pt-4">
        <section aria-label="Jornada e perfil" className="mb-6 space-y-3">
          <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Jornada">
            {journeys.map((j) => (
              <button
                key={j.id}
                role="radio"
                aria-checked={journey === j.id}
                onClick={() => setJourney(j.id)}
                className={`min-h-11 rounded-full border px-4 py-2 text-sm ${journey === j.id ? "border-accent bg-accent-soft font-medium text-accent" : "border-line bg-card hover:border-accent"}`}
              >
                {j.label}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <button onClick={() => setShowProfile((v) => !v)} className="min-h-11 font-medium text-accent hover:underline" aria-expanded={showProfile}>
              {showProfile ? "Fechar perfil" : profileSummary ? "Editar perfil" : "Adicionar perfil (opcional)"}
            </button>
            {profileSummary && !showProfile && <span className="text-muted">{profileSummary}</span>}
            {exchanges.length > 0 && (
              <button onClick={reset} className="ml-auto min-h-11 px-2 text-muted hover:text-ink">Nova conversa</button>
            )}
          </div>
          {showProfile && (
            <div className="rounded-2xl border border-line bg-card p-4">
              <ProfileForm value={profile} onChange={(p) => { setProfile(p); setShowProfile(false); }} />
            </div>
          )}
          {health === "down" && (
            <p className="rounded-lg bg-bad-soft px-3 py-2 text-sm text-bad" role="alert">
              {API_URL.includes("localhost") ? (
                <>Não consigo falar com a API em {API_URL}. Está a correr? (<code>uvicorn api:app --port 8000</code> em <code>backend/</code>)</>
              ) : (
                <>O servidor está a acordar (pode demorar até 1 minuto). Recarrega a página daqui a pouco.</>
              )}
            </p>
          )}
        </section>

        {exchanges.length === 0 ? (
          <section aria-label="Sugestões" className="space-y-2">
            <p className="text-sm text-muted">Experimenta perguntar:</p>
            {SUGGESTIONS[journey].map((s) => (
              <button key={s} onClick={() => send(s)} className="block w-full rounded-xl border border-line bg-card px-4 py-3 text-left text-[15px] hover:border-accent">
                {s}
              </button>
            ))}
          </section>
        ) : (
          <div className="space-y-6">
            {exchanges.map((x) => (
              <ExchangeView key={x.id} x={x} mode={mode} onRetry={() => retry(x)} />
            ))}
            {followUps.length > 0 && (
              <section aria-label="Perguntas seguintes" className="flex flex-wrap gap-2">
                {followUps.map((q) => (
                  <button
                    key={q}
                    onClick={() => send(q)}
                    className="min-h-11 rounded-full border border-line bg-card px-4 py-2 text-left text-sm hover:border-accent hover:text-accent"
                  >
                    {q}
                  </button>
                ))}
              </section>
            )}
          </div>
        )}
        <div ref={endRef} />
      </main>

      <footer className="sticky bottom-0 border-t border-line bg-bg/95 backdrop-blur">
        <div className="mx-auto max-w-3xl px-4 py-3">
          <Composer busy={busy} onSend={(q) => send(q)} onStop={() => abortRef.current?.abort()} />
        </div>
      </footer>
    </div>
  );
}
