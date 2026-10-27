"use client";

import { useRef, useState } from "react";

const MAX = 1000; // limite da API para `question`

export function Composer({ busy, onSend, onStop }: { busy: boolean; onSend: (q: string) => void; onStop: () => void }) {
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

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
          className="max-h-40 min-h-10 flex-1 resize-none bg-transparent px-2 py-2 text-[15px] outline-none field-sizing-content"
        />
        {busy ? (
          <button type="button" onClick={onStop} className="h-10 shrink-0 rounded-xl border border-line px-4 text-sm font-medium hover:border-bad hover:text-bad">
            Parar
          </button>
        ) : (
          <button type="submit" className="h-10 shrink-0 rounded-xl bg-accent px-4 text-sm font-medium text-white hover:opacity-90 disabled:opacity-40" disabled={!text.trim()}>
            Enviar
          </button>
        )}
      </div>
      <div className="mt-1.5 flex justify-between px-1 text-xs text-muted">
        <span className={error ? "text-bad" : ""} role={error ? "alert" : undefined}>
          {error || "Informação educativa, não é aconselhamento financeiro."}
        </span>
        {text.length > MAX * 0.8 && <span>{text.length}/{MAX}</span>}
      </div>
    </form>
  );
}
