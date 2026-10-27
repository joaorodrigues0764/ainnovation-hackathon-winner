// Estado de cada troca (pergunta → resposta) construído a partir dos eventos SSE.
import type { ChatRequest, Chunk, Judge, Source, StreamEvent, ToolCall, Turn } from "./api";

export type ExchangeStatus = "streaming" | "done" | "error" | "stopped";

export interface LoggedEvent {
  t: number; // ms desde o início do pedido
  event: string;
  data: unknown;
}

export interface Exchange {
  id: string;
  question: string;
  request: ChatRequest;
  status: ExchangeStatus;
  answer: string;
  /** Fontes citadas na resposta (depois de `done`); antes disso, todas as recuperadas. */
  sources: Source[];
  allSources: Source[];
  chunks: Chunk[];
  scope: string[];
  tools: ToolCall[];
  warning?: { text: string; pii: string[] };
  /** Juiz de completude: se faltarem dados, a resposta termina com perguntas para os obter. */
  judge?: Judge;
  error?: string;
  events: LoggedEvent[];
  timings: { sources?: number; firstDelta?: number; end?: number };
  deltas: number;
}

export function newExchange(id: string, request: ChatRequest): Exchange {
  return {
    id, request, question: request.question, status: "streaming", answer: "",
    sources: [], allSources: [], chunks: [], scope: [], tools: [], events: [], timings: {}, deltas: 0,
  };
}

export function applyEvent(x: Exchange, ev: StreamEvent, t: number): Exchange {
  const next: Exchange = { ...x, events: [...x.events, { t, event: ev.event, data: ev.data }] };
  switch (ev.event) {
    case "warning":
      next.warning = ev.data;
      break;
    case "judge":
      next.judge = ev.data;
      break;
    case "sources":
      next.sources = next.allSources = ev.data.sources;
      next.chunks = ev.data.chunks;
      next.scope = ev.data.scope ?? [];
      next.timings = { ...next.timings, sources: t };
      break;
    case "tool":
      next.tools = [...x.tools, ev.data];
      break;
    case "delta":
      next.answer = x.answer + ev.data.text;
      next.deltas = x.deltas + 1;
      if (x.timings.firstDelta === undefined) next.timings = { ...next.timings, firstDelta: t };
      break;
    case "done":
      next.answer = ev.data.answer;
      next.sources = ev.data.sources;
      next.status = "done";
      next.timings = { ...next.timings, end: t };
      break;
    case "error":
      next.error = ev.data.detail;
      next.status = "error";
      next.timings = { ...next.timings, end: t };
      break;
  }
  return next;
}

const MAX_TURN_CHARS = 4000; // limite por mensagem do histórico na API

/** Histórico para a API: só trocas terminadas, da mais antiga para a mais recente. */
export function historyFrom(exchanges: Exchange[]): Turn[] {
  return exchanges
    .filter((x) => x.status === "done" && x.answer)
    .flatMap((x): Turn[] => [
      { role: "user", content: x.question.slice(0, MAX_TURN_CHARS) },
      { role: "assistant", content: x.answer.slice(0, MAX_TURN_CHARS) },
    ]);
}
