// Cartão de resposta (PRD): número em destaque (das calculadoras), explicação, fonte e próximo passo.
import type { ToolCall } from "./api";

export interface Figure {
  label: string;
  value: string;
}

export interface CardBlock {
  title: string;
  main: Figure;
  others: Figure[];
  note?: string; // pressupostos devolvidos pela calculadora
}

// "always": em pt-PT o browser só agrupa a partir de 5 dígitos (8000,00 €); o PRD escreve 8 000 €
const eur = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR", useGrouping: "always" });
const num = (v: unknown) => (typeof v === "number" && Number.isFinite(v) ? v : undefined);
const money = (v: unknown) => (num(v) === undefined ? undefined : eur.format(num(v)!));

function figures(pairs: [string, string | undefined][]): Figure[] {
  return pairs.filter((p): p is [string, string] => p[1] !== undefined).map(([label, value]) => ({ label, value }));
}

/** Um bloco por calculadora que correu bem; resultados com erro não aparecem no cartão. */
export function cardBlocks(tools: ToolCall[]): CardBlock[] {
  return tools.flatMap((t): CardBlock[] => {
    const r = t.result;
    if (!r || "erro" in r) return [];
    const note = typeof r.pressupostos === "string" ? r.pressupostos : undefined;
    switch (t.name) {
      case "custo_credito":
        return [{
          title: `Crédito de ${money(r.montante)} em ${r.prestacoes} meses`,
          main: { label: "Prestação mensal", value: money(r.prestacao_mensal) ?? "—" },
          others: figures([["Total a pagar", money(r.total_a_pagar)], ["Juros", money(r.juros)]]),
          note,
        }];
      case "objetivo_poupanca": {
        // com o valor que a pessoa consegue guardar, a pergunta é "em quantos meses?"
        if (num(r.mensal_disponivel) !== undefined && num(r.meses_necessarios) !== undefined) {
          const defice = num(r.defice_por_mes) ?? 0;
          return [{
            title: `Juntar ${money(r.valor)} a guardar ${money(r.mensal_disponivel)} por mês`,
            main: { label: "Meses necessários", value: `${r.meses_necessarios} meses` },
            others: figures([
              ["Falta juntar", money(r.falta)],
              [`Para ${r.meses} meses`, `${money(r.necessario_por_mes)}/mês`],
              ...(defice > 0 ? [["Faltam por mês", money(defice)] as [string, string | undefined]] : []),
            ]),
            note,
          }];
        }
        return [{
          title: `Juntar ${money(r.valor)} em ${r.meses} meses`,
          main: { label: "Poupar por mês", value: money(r.necessario_por_mes) ?? "—" },
          others: figures([["Falta juntar", money(r.falta)]]),
          note,
        }];
      }
      case "juros_compostos":
        return [{
          title: `Poupança durante ${r.meses} meses`,
          main: { label: "Valor final", value: money(r.valor_final) ?? "—" },
          others: figures([["Depositado", money(r.depositado)], ["Juros ganhos", money(r.juros)]]),
          note,
        }];
      case "orcamento": {
        const regra = (r.regra ?? {}) as Record<string, unknown>;
        return [{
          title: `Orçamento de ${money(r.entradas)} por mês`,
          main: { label: "Sobra no mês", value: money(r.saldo) ?? "—" },
          others: figures([["Necessidades", money(regra.necessidades)], ["Desejos", money(regra.desejos)],
                           ["Poupança", money(regra.poupanca)]]),
          note,
        }];
      }
      case "salario_liquido":
        return [{
          title: `Salário bruto de ${money(r.bruto)}`,
          main: { label: "Depois da Segurança Social", value: money(r.apos_seguranca_social) ?? "—" },
          others: figures([["Segurança Social", money(r.seguranca_social)]]),
          note,
        }];
      case "efeito_inflacao":
        return [{
          title: `${money(r.valor)} no futuro`,
          main: { label: "Poder de compra", value: money(r.poder_de_compra_futuro) ?? "—" },
          others: figures([["Perda", money(r.perda)]]),
          note,
        }];
      default:
        return [];
    }
  });
}

const NEXT = /^\s*\**\s*pr[óo]xim[oa]s?\s+passos?\s*:?\s*\**\s*:?\s*/i;

/** Separa o "Próximo passo" (PRD/RF5) do resto da explicação, para o destacar no cartão. */
export function splitNextStep(answer: string): { body: string; next?: string } {
  const blocks = answer.trim().split(/\n{2,}/);
  const i = blocks.findIndex((b) => NEXT.test(b));
  if (i === -1) return { body: answer };
  const next = [blocks[i].replace(NEXT, ""), ...blocks.slice(i + 1)].join("\n\n").trim();
  return { body: blocks.slice(0, i).join("\n\n"), next: next || undefined };
}
