// Cliente da API do backend (backend/api.py). Os tipos seguem os eventos de /chat/stream.

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export type JourneyId = "credito" | "salario" | "irs" | "burlas" | "poupanca" | "geral";

export interface Journey {
  id: JourneyId;
  label: string;
}

export interface Profile {
  idade?: number;
  rendimento_liquido?: number;
  objetivo?: string;
}

export interface Turn {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  question: string;
  journey?: JourneyId;
  profile?: Profile;
  history?: Turn[];
}

export interface Source {
  n: number;
  title: string;
  url: string;
  source: string;
}

export interface Chunk {
  file: string;
  section: string;
  score: number;
}

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface Judge {
  complete: boolean;
  missing: string[];
  questions: string[];
  reason: string;
  ms: number;
  error?: string | null;
}

export interface Health {
  status: string;
  chunks: number;
  embeddings: boolean;
  model: string;
}

export type StreamEvent =
  | { event: "warning"; data: { text: string; pii: string[] } }
  | { event: "judge"; data: Judge }
  | { event: "sources"; data: { sources: Source[]; chunks: Chunk[]; scope: string[] } }
  | { event: "tool"; data: ToolCall }
  | { event: "delta"; data: { text: string } }
  | { event: "done"; data: { answer: string; sources: Source[] } }
  | { event: "error"; data: { detail: string } };

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export const getHealth = () => getJSON<Health>("/health");
export const getJourneys = () => getJSON<Journey[]>("/journeys");

/** Um bloco SSE ("event: x\ndata: {...}") → evento tipado; blocos estranhos são ignorados. */
function parseBlock(block: string): StreamEvent | null {
  let event = "";
  const data: string[] = [];
  for (const line of block.split(/\r?\n/)) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
  }
  if (!event || !data.length) return null;
  try {
    return { event, data: JSON.parse(data.join("\n")) } as StreamEvent;
  } catch {
    return null;
  }
}

/**
 * POST /chat/stream. O EventSource do browser só faz GET, por isso lê-se o corpo à mão.
 * Chama onEvent por cada evento, pela ordem em que chegam. Cancela-se com `signal`.
 */
export async function streamChat(
  body: ChatRequest,
  onEvent: (ev: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
    } catch {
      /* corpo sem JSON: fica o código HTTP */
    }
    throw new Error(detail);
  }

  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    let sep: RegExpExecArray | null;
    while ((sep = /\r?\n\r?\n/.exec(buffer))) {
      const ev = parseBlock(buffer.slice(0, sep.index));
      buffer = buffer.slice(sep.index + sep[0].length);
      if (ev) onEvent(ev);
    }
  }
  const last = parseBlock(buffer);
  if (last) onEvent(last);
}
