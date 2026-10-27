"use client";

import { useRef, useState, useSyncExternalStore } from "react";

// Ditado por voz: Web Speech API do browser (grátis, sem chave). Só aparece onde existe (Chrome, Edge, Safari).
type Rec = {
  lang: string; interimResults: boolean; continuous: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onend: (() => void) | null; onerror: (() => void) | null;
  start: () => void; stop: () => void;
};
type RecCtor = new () => Rec;
const getRec = (): RecCtor | null => {
  if (typeof window === "undefined") return null;
  const w = window as unknown as { SpeechRecognition?: RecCtor; webkitSpeechRecognition?: RecCtor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
};

const MAX = 1000; // limite da API para `question`

export function Composer({ busy, onSend, onStop }: { busy: boolean; onSend: (q: string) => void; onStop: () => void }) {
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);
  const canDictate = useSyncExternalStore(() => () => {}, () => getRec() !== null, () => false);
  const [listening, setListening] = useState(false);
  const rec = useRef<Rec | null>(null);

  const dictate = () => {
    if (listening) {
      rec.current?.stop();
      return;
    }
    const Ctor = getRec();
    if (!Ctor) return;
    const r = new Ctor();
    r.lang = "pt-PT";
    r.interimResults = true;
    r.continuous = false;
    const base = text ? text.trimEnd() + " " : "";
    r.onresult = (e) => {
      const said = Array.from(e.results).map((x) => x[0].transcript).join("");
      setText((base + said).slice(0, MAX));
      setError("");
    };
    r.onend = () => setListening(false);
    r.onerror = () => {
      setListening(false);
      setError("Não consegui ouvir. Tenta outra vez ou escreve.");
    };
    rec.current = r;
    setListening(true);
    r.start();
  };

  const submit = () => {
    const q = text.trim();
    if (!q) {
      setError("Escreve uma pergunta primeiro.");
      ref.current?.focus();
      return;
    }
    if (busy) return;
    onSend(q);
    setText("");
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <div className="flex items-end gap-2 rounded-2xl border border-line bg-card p-2 shadow-sm focus-within:border-accent">
        <label htmlFor="question" className="sr-only">Pergunta</label>
        <textarea
          id="question"
          ref={ref}
          rows={1}
          enterKeyHint="send"
          maxLength={MAX}
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            setError("");
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Pergunta, por exemplo: e se for a 60 meses?"
          className="max-h-40 min-h-11 flex-1 resize-none bg-transparent px-2 py-2 text-[15px] outline-none field-sizing-content"
        />
        {canDictate && !busy && (
          <button
            type="button"
            onClick={dictate}
            aria-pressed={listening}
            aria-label={listening ? "Parar de ouvir" : "Ditar a pergunta por voz"}
            className={`h-11 w-11 shrink-0 rounded-xl border text-lg ${listening ? "border-bad bg-bad-soft text-bad" : "border-line hover:border-accent"}`}
          >
            {listening ? "■" : "🎤"}
          </button>
        )}
        {busy ? (
          <button type="button" onClick={onStop} className="h-11 shrink-0 rounded-xl border border-line px-4 text-sm font-medium hover:border-bad hover:text-bad">
            Parar
          </button>
        ) : (
          <button type="submit" className="h-11 shrink-0 rounded-xl bg-accent px-4 text-sm font-medium text-white hover:opacity-90 disabled:opacity-40" disabled={!text.trim()}>
            Enviar
          </button>
        )}
      </div>
      <div className="mt-1.5 flex justify-between px-1 text-xs text-muted">
        <span className={error ? "text-bad" : ""} role={error ? "alert" : undefined}>
          {error || (listening ? "A ouvir… fala a tua pergunta (sem dados pessoais)." : "Informação educativa, não é aconselhamento financeiro.")}
        </span>
        {text.length > MAX * 0.8 && <span>{text.length}/{MAX}</span>}
      </div>
    </form>
  );
}
