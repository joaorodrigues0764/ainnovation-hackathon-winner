import { Fragment, type ReactNode } from "react";
import type { Source } from "@/lib/api";

// O LLM responde em markdown simples: parágrafos, listas, **negrito** e citações [n].
// Renderiza-se só isso, sem biblioteca e sem HTML vindo do modelo.

const INLINE = /(\*\*[^*\n]+\*\*|\[\d+\])/g;
const LIST_ITEM = /^\s*(?:[-*•]|\d+[.)])\s+/;

function inline(text: string, exchangeId: string, sources: Source[]): ReactNode[] {
  return text.split(INLINE).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>;
    }
    const cite = /^\[(\d+)\]$/.exec(part);
    if (cite) {
      const n = Number(cite[1]);
      const src = sources.find((s) => s.n === n);
      return (
        <a
          key={i}
          href={`#src-${exchangeId}-${n}`}
          title={src ? `${src.title} — ${src.source}` : `Fonte ${n}`}
          className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-accent-soft px-1.5 align-text-top text-[11px] font-medium text-accent no-underline hover:bg-accent hover:text-white"
        >
          {n}
        </a>
      );
    }
    return <Fragment key={i}>{part}</Fragment>;
  });
}

export function Answer({ text, exchangeId, sources }: { text: string; exchangeId: string; sources: Source[] }) {
  const blocks = text.trim().split(/\n{2,}/).filter(Boolean);
  return (
    <div className="space-y-3 leading-relaxed">
      {blocks.map((block, i) => {
        const lines = block.split("\n").filter((l) => l.trim());
        if (lines.length && lines.every((l) => LIST_ITEM.test(l))) {
          const ordered = /^\s*\d/.test(lines[0]);
          const Tag = ordered ? "ol" : "ul";
          return (
            <Tag key={i} className={`space-y-1 pl-5 ${ordered ? "list-decimal" : "list-disc"}`}>
              {lines.map((l, j) => <li key={j}>{inline(l.replace(LIST_ITEM, ""), exchangeId, sources)}</li>)}
            </Tag>
          );
        }
        return (
          <p key={i}>
            {lines.map((l, j) => (
              <Fragment key={j}>
                {j > 0 && <br />}
                {inline(l, exchangeId, sources)}
              </Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
}
