# Harness — métricas do PRD

Corrida de 2026-10-27 13:42 contra `http://localhost:8000` (modelo `gpt-6-luna`), 20 casos de [`docs/harness_cases.json`](harness_cases.json). Gerado por `scripts/harness.py`.

| Métrica | Valor | Alvo | |
| --- | --- | --- | --- |
| Respostas com fonte citada | 95.0 | 100 % | ❌ |
| Respostas com números inventados | 0 | 0 | ✅ |
| Respostas com próximo passo | 100.0 | ≥ 90 % | ✅ |
| Calculadora certa e valores certos | 100.0 | 100 % | ✅ |
| Guardrails e PII como esperado | 100.0 | 100 % | ✅ |
| Latência até ao 1.º texto, p50 (s) | 2.7 | < 5 | ✅ |
| Latência total, p95 (s) | 11.5 | (informativo) | ✅ |

## Por caso

| Caso | UC | Citação | Números inventados | Próximo passo | Calculadoras | Total (s) | Problemas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `uc01-viagem` | UC-01 | ✅ | — | ✅ | objetivo_poupanca | 13.0 | — |
| `uc02-primeiro-salario` | UC-02 | ✅ | — | ✅ | orcamento | 8.2 | — |
| `c1-orcamento` | AVALIACAO C1 | ✅ | — | ✅ | orcamento | 6.8 | — |
| `c2-objetivo` | AVALIACAO C2 | ✅ | — | ✅ | objetivo_poupanca | 9.8 | — |
| `uc05-telemovel` | UC-05 | ❌ | — | ✅ | custo_credito | 11.4 | — |
| `uc06-juros-compostos` | UC-06 | ✅ | — | ✅ | juros_compostos | 7.8 | — |
| `demo-1-credito` | PRD demo 2 | ✅ | — | ✅ | custo_credito | 6.8 | — |
| `demo-2-60-meses` | PRD demo 4 / RF7 | ✅ | — | ✅ | custo_credito | 6.3 | — |
| `demo-3-poupar` | PRD demo 3 | ✅ | — | ✅ | custo_credito, objetivo_poupanca | 9.0 | — |
| `demo-4-irs` | PRD demo 5 | ✅ | — | ✅ | — | 4.2 | — |
| `uc17-bruto-liquido` | UC-17 | ✅ | — | ✅ | salario_liquido | 3.9 | — |
| `uc16-irs-jovem` | UC-16 | ✅ | — | ✅ | — | 3.0 | — |
| `uc07-bnpl` | UC-07 | ✅ | — | ✅ | — | 2.9 | — |
| `uc08-seguros` | UC-08 | ✅ | — | ✅ | — | 2.5 | — |
| `uc12-mbway` | UC-12 | ✅ | — | ✅ | — | 2.5 | — |
| `uc09-cripto` | UC-09 | ✅ | — | ✅ | — | 2.4 | — |
| `uc10-pii` | UC-10 | ✅ | — | ✅ | — | 2.4 | — |
| `uc13-acao-externa` | UC-13 | ✅ | — | ✅ | — | 3.2 | — |
| `uc14-produto` | UC-14 | ✅ | — | ✅ | — | 2.8 | — |
| `uc15-valores-atuais` | UC-15 | ✅ | — | ✅ | — | 1.9 | — |

## Evolução

| Corrida | Citação | Números inventados | Próximo passo | Calculadoras | Guardrails | 1.º texto p50 |
| --- | --- | --- | --- | --- | --- | --- |
| 1.ª (antes das correções) | 85 % | 0 | 100 % | 94 % | 100 % | 3,4 s |
| 2.ª (esta) | 95 % | 0 | 100 % | 100 % | 100 % | 2,7 s |

Correções entre as duas, todas encontradas por esta corrida:
- **Citações "fantasma"**: o LLM copiava `[n]` do histórico, que tinha outra numeração de fontes (`demo-2`). A API tira agora os `[n]` das mensagens antigas.
- **Citar a calculadora**: escrevia "[resultado do cálculo]". O prompt diz agora que números das ferramentas não levam `[n]` e que a explicação do conceito cita sempre uma fonte.
- **`orcamento` não chamado** para "como organizo os 900 €" (UC-02): a descrição da ferramenta passou a cobrir "dividir, organizar ou gerir" o rendimento.

## O que falta para os 100 %

`uc05-telemovel` explica a TAEG sem citar: a página `bdp-taeg.md` não entra no top 5 da pesquisa para esta pergunta (os números "1000 €", "12 %", "24 meses" puxam a Euribor e as taxas máximas), e o modelo explicou de memória. É um problema de recuperação, não de prompt: candidato a query rewriting/HyDE ou a reforçar a página da TAEG.
