// Sugestões de follow-up depois de uma resposta: deterministas, a partir das calculadoras que correram,
// dos guardrails e da jornada. Sem chamada extra ao LLM (instantâneas, sem tokens, previsíveis na demo).
import type { JourneyId } from "./api";
import type { Exchange } from "./chat";

const MAX = 3;
const eur = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0, useGrouping: "always" });
const n = (v: unknown) => (typeof v === "number" && Number.isFinite(v) ? v : undefined);
const money = (v: number) => `${eur.format(v)} €`;

const BY_JOURNEY: Record<JourneyId, string[]> = {
  credito: ["O que devo comparar numa proposta de crédito?", "Qual a diferença entre TAEG e TAN?",
            "O que acontece se falhar uma prestação?"],
  salario: ["Quanto devia ter num fundo de emergência?", "Como corto gastos que nem dou por eles?",
            "Qual a diferença entre salário bruto e líquido?"],
  irs: ["O que são deduções à coleta?", "Quando tenho de entregar o IRS?", "O IRS Jovem aplica-se a mim?"],
  burlas: ["Como reconheço uma mensagem falsa do banco?", "O que faço se já dei os meus dados?",
           "Pagar em 4 vezes sem juros tem riscos?"],
  poupanca: ["Quanto devia ter num fundo de emergência?", "O que são juros compostos?",
             "Quanto rendem 50 € por mês a 3% durante 5 anos?"],
  geral: ["O que é a inflação?", "Como começo um fundo de emergência?", "Qual a diferença entre TAEG e TAN?"],
};

const BY_SCOPE: Record<string, string[]> = {
  investimento: ["Como começo um fundo de emergência?", "Que riscos tem investir?"],
  acao_externa: ["O que devo preparar antes de falar com o banco?", "O que acontece se falhar uma prestação?"],
  produto: ["O que devo comparar numa conta bancária?", "O que é a ficha de informação normalizada?"],
};

function fromTools(x: Exchange, all: Exchange[]): string[] {
  const out: string[] = [];
  // prazos de crédito já calculados nesta conversa não voltam a ser sugeridos
  const doneTerms = new Set(all.flatMap((e) => e.tools).filter((t) => t.name === "custo_credito").map((t) => n(t.args.prestacoes)));
  for (const t of x.tools) {
    const a = t.args, r = t.result;
    if (!r || "erro" in r) continue;
    switch (t.name) {
      case "custo_credito": {
        const meses = n(a.prestacoes), montante = n(a.montante);
        for (const m of meses ? [meses + 12, meses - 12] : []) {
          if (m >= 6 && !doneTerms.has(m)) out.push(`E se for a ${m} meses?`);
        }
        if (!x.tools.some((o) => o.name === "objetivo_poupanca") && montante) {
          out.push(`E se eu poupar os ${money(montante)} em vez de pedir crédito?`);
        }
        break;
      }
      case "objetivo_poupanca": {
        const mensal = n(a.mensal_disponivel), meses = n(a.meses);
        if (mensal) out.push(`E se conseguir guardar ${money(mensal + 20)} por mês?`);
        else if (meses) out.push(`E se tiver mais ${meses >= 12 ? 6 : 2} meses?`);
        out.push("Como começo um fundo de emergência?");
        break;
      }
      case "juros_compostos": {
        const anos = n(a.anos);
        if (anos) out.push(`E se for durante ${anos * 2} anos?`);
        out.push("O que são juros compostos?");
        break;
      }
      case "orcamento":
        out.push("Quanto devia ter num fundo de emergência?", "Como corto gastos que nem dou por eles?");
        break;
      case "salario_liquido": {
        const liquido = n(r.apos_seguranca_social);
        if (liquido) out.push(`Como divido ${money(liquido)} por mês?`);
        out.push("O IRS Jovem aplica-se a mim?");
        break;
      }
      case "efeito_inflacao":
        out.push("Como protejo as minhas poupanças da inflação?");
        break;
    }
  }
  return out;
}

const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^\w ]/g, "").trim();

/** Até 3 perguntas para a última troca terminada; nunca repete perguntas já feitas na conversa. */
export function suggestFollowUps(exchanges: Exchange[], journey: JourneyId): string[] {
  const last = exchanges.at(-1);
  // se o juiz achou que faltam dados, a resposta já está a fazer perguntas: não distrair com outras
  if (!last || last.status !== "done" || last.judge?.complete === false) return [];
  const asked = new Set(exchanges.map((x) => norm(x.question)));
  const pool = [
    ...fromTools(last, exchanges),
    ...last.scope.flatMap((s) => BY_SCOPE[s] ?? []),
    ...(last.warning ? ["Como funciona o IRS Jovem?"] : []),
    ...BY_JOURNEY[journey],
  ];
  const out: string[] = [];
  for (const q of pool) {
    const k = norm(q);
    if (!asked.has(k) && !out.some((o) => norm(o) === k)) out.push(q);
    if (out.length === MAX) break;
  }
  return out;
}
