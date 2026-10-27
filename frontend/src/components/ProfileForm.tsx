"use client";

import { useState } from "react";
import type { Profile } from "@/lib/api";

// Perfil curto (RF1): só fica em memória nesta página; não vai para localStorage nem para logs.

interface Draft {
  idade: string;
  rendimento: string;
  objetivo: string;
}

function validate(d: Draft): { profile?: Profile; errors: Partial<Record<keyof Draft, string>> } {
  const errors: Partial<Record<keyof Draft, string>> = {};
  const profile: Profile = {};
  if (d.idade.trim()) {
    const n = Number(d.idade);
    if (!Number.isInteger(n) || n < 14 || n > 100) errors.idade = "Idade entre 14 e 100.";
    else profile.idade = n;
  }
  if (d.rendimento.trim()) {
    const n = Number(d.rendimento.replace(",", "."));
    if (!Number.isFinite(n) || n < 0) errors.rendimento = "Valor em € (0 ou mais).";
    else profile.rendimento_liquido = n;
  }
  if (d.objetivo.trim()) profile.objetivo = d.objetivo.trim().slice(0, 200);
  return { profile: Object.keys(errors).length ? undefined : profile, errors };
}

const input =
  "w-full rounded-lg border border-line bg-card px-3 py-2 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent-soft";

export function ProfileForm({ value, onChange }: { value: Profile; onChange: (p: Profile) => void }) {
  const [draft, setDraft] = useState<Draft>({
    idade: value.idade?.toString() ?? "",
    rendimento: value.rendimento_liquido?.toString() ?? "",
    objetivo: value.objetivo ?? "",
  });
  const [errors, setErrors] = useState<Partial<Record<keyof Draft, string>>>({});
  const [saved, setSaved] = useState(false);

  const set = (k: keyof Draft) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setDraft({ ...draft, [k]: e.target.value });
    setErrors({ ...errors, [k]: undefined });
    setSaved(false);
  };

  return (
    <form
      className="grid gap-3 sm:grid-cols-[6rem_9rem_1fr_auto] sm:items-start"
      onSubmit={(e) => {
        e.preventDefault();
        const r = validate(draft);
        setErrors(r.errors);
        if (r.profile) {
          onChange(r.profile);
          setSaved(true);
        }
      }}
    >
      <label className="text-sm">
        <span className="mb-1 block text-muted">Idade</span>
        <input className={input} inputMode="numeric" value={draft.idade} onChange={set("idade")} placeholder="23" aria-invalid={!!errors.idade} />
        {errors.idade && <span className="mt-1 block text-xs text-bad">{errors.idade}</span>}
      </label>
      <label className="text-sm">
        <span className="mb-1 block text-muted">Rendimento líquido/mês</span>
        <input className={input} inputMode="decimal" value={draft.rendimento} onChange={set("rendimento")} placeholder="1100" aria-invalid={!!errors.rendimento} />
        {errors.rendimento && <span className="mt-1 block text-xs text-bad">{errors.rendimento}</span>}
      </label>
      <label className="text-sm">
        <span className="mb-1 block text-muted">Objetivo</span>
        <input className={input} maxLength={200} value={draft.objetivo} onChange={set("objetivo")} placeholder="carro de 8 000 €" />
      </label>
      <div className="flex items-center gap-2 sm:pt-6">
        <button type="submit" className="rounded-lg border border-line bg-card px-3 py-2 text-sm font-medium hover:border-accent">
          Guardar
        </button>
        {saved && <span className="text-xs text-ok" role="status">Guardado</span>}
      </div>
      <p className="text-xs text-muted sm:col-span-4">
        Opcional. Fica só nesta página e é usado para personalizar as contas. Não escrevas NIF, IBAN ou contactos.
      </p>
    </form>
  );
}
