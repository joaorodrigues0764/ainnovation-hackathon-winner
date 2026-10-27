# Harness — métricas do PRD

Corrida de 2026-10-27 14:17 contra `http://localhost:8000` (modelo `gpt-6-luna`), 24 casos de [`docs/harness_cases.json`](harness_cases.json). Gerado por `scripts/harness.py`.

| Métrica | Valor | Alvo | |
| --- | --- | --- | --- |
| Respostas com fonte citada | 100.0 | 100 % | ✅ |
| Respostas com números inventados | 0 | 0 | ✅ |
| Respostas com próximo passo | 100.0 | ≥ 90 % | ✅ |
| Calculadora certa e valores certos | 95.2 | 100 % | ❌ |
| Guardrails e PII como esperado | 100.0 | 100 % | ✅ |
| Pede contexto quando faltam dados (e só então) | 100.0 | 100 % | ✅ |
| Latência até ao 1.º texto, p50 (s) | 3.0 | < 5 | ✅ |
| Latência total, p95 (s) | 6.8 | (informativo) | ✅ |

## Por caso

| Caso | UC | Citação | Números inventados | Próximo passo | Calculadoras | Total (s) | Problemas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `uc01-viagem` | UC-01 | ✅ | — | ✅ | objetivo_poupanca | 6.8 | — |
| `uc02-primeiro-salario` | UC-02 | ✅ | — | ✅ | — | 3.5 | orcamento não foi chamada |
| `c1-orcamento` | AVALIACAO C1 | ✅ | — | ✅ | orcamento | 5.0 | — |
| `c2-objetivo` | AVALIACAO C2 | ✅ | — | ✅ | objetivo_poupanca | 5.4 | — |
| `uc05-telemovel` | UC-05 | ✅ | — | ✅ | custo_credito | 5.2 | — |
| `uc06-juros-compostos` | UC-06 | ✅ | — | ✅ | juros_compostos | 5.0 | — |
| `demo-1-credito` | PRD demo 2 | ✅ | — | ✅ | custo_credito | 6.0 | — |
| `demo-2-60-meses` | PRD demo 4 / RF7 | ✅ | — | ✅ | custo_credito | 4.8 | — |
| `demo-3-poupar` | PRD demo 3 | ✅ | — | ✅ | custo_credito, objetivo_poupanca | 7.8 | — |
| `demo-4-irs` | PRD demo 5 | ✅ | — | ✅ | — | 4.5 | — |
| `uc17-bruto-liquido` | UC-17 | ✅ | — | ✅ | salario_liquido | 6.4 | — |
| `uc16-irs-jovem` | UC-16 | ✅ | — | ✅ | — | 3.9 | — |
| `uc07-bnpl` | UC-07 | ✅ | — | ✅ | — | 4.2 | — |
| `uc08-seguros` | UC-08 | ✅ | — | ✅ | — | 3.9 | — |
| `uc12-mbway` | UC-12 | ✅ | — | ✅ | — | 3.7 | — |
| `uc09-cripto` | UC-09 | ✅ | — | ✅ | — | 2.7 | — |
| `uc10-pii` | UC-10 | ✅ | — | ✅ | — | 4.4 | — |
| `uc13-acao-externa` | UC-13 | ✅ | — | ✅ | — | 3.4 | — |
| `uc14-produto` | UC-14 | ✅ | — | ✅ | — | 2.7 | — |
| `uc15-valores-atuais` | UC-15 | ✅ | — | ✅ | — | 3.7 | — |
| `clar-viagem-sem-dados` | UC-01 entrada 1 | ✅ | — | ✅ | — | 4.4 | — |
| `clar-vago` | UC-20 | ✅ | — | ✅ | — | 3.7 | — |
| `clar-rendimento-sem-despesas` | pedido do Luís | ✅ | — | ✅ | orcamento | 6.0 | — |
| `clar-fundo-emergencia` | UC-03 | ✅ | — | ✅ | — | 3.9 | — |

## Evolução

| Corrida | Casos | Citação | Números inventados | Próximo passo | Calculadoras | Guardrails | Pede contexto | 1.º texto p50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 (PR #19, antes das correções) | 20 | 85 % | 0 | 100 % | 94 % | 100 % | — | 3,4 s |
| 2 (PR #19) | 20 | 95 % | 0 | 100 % | 100 % | 100 % | — | 2,7 s |
| 3 (juiz de completude, 1.ª versão) | 24 | 91 % | 0 | 100 % | 95 % | 100 % | 80 % | 3,8 s |
| 4 (regras do juiz mais estritas) | 24 | 91 % | 1 | 100 % | 100 % | 100 % | 90 % | 3,4 s |
| 5 (comissões não contam como em falta) | 24 | 91 % | 1 | 100 % | 100 % | 100 % | **100 %** | 2,9 s |
| 6 (50/30/20 do que sobra em Python) | 24 | 96 % | 1 | 100 % | 95 % | 100 % | 100 % | 3,2 s |
| 7 (esta: taxa de esforço em Python) | 24 | **100 %** | **0** | 100 % | 95 % | 100 % | 100 % | 3,0 s |

O que o harness apanhou nestas corridas, e como ficou:
- **Juiz a perguntar demais** (corrida 3): pedia o tipo de taxa, o capital inicial ou o montante quando a pergunta já dizia "carro de 8 000 €". As regras passaram a dizer que um dado só falta se sem ele a resposta ficasse genérica ou errada; dados com valor óbvio não contam.
- **LLM a fazer contas de cabeça** (RF2): 50/30/20 do que sobra (C1) e "a prestação é ~15 % do rendimento" (demo 2). As duas contas passaram para Python (`regra_do_que_sobra` no orçamento, `taxa_esforco_pct` no crédito com o rendimento do perfil).
- **Variação do modelo**: `uc02-primeiro-salario` chama o `orcamento` nalgumas corridas e não noutras (passou na 5, falhou na 6 e na 7). Correr o harness mais de uma vez antes de tirar conclusões sobre um caso.
