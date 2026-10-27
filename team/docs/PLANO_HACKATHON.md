# Plano do hackathon — 27/10/2026, 11:00 → 15:00

## 1. Problema e proposta (rascunho, ajustar às regras oficiais do desafio)
- **Problema:** muitos jovens chegam à primeira mesada, part-time ou salário sem saber fazer um orçamento, poupar para um objetivo, perceber o custo de um crédito ou reconhecer uma burla.
- **Proposta:** um agente conversacional em PT-PT que responde às dúvidas deles com exemplos em euros, faz as contas com ferramentas fiáveis (não «de cabeça»), e dá sempre um próximo passo. Educa; não vende nem recomenda produtos.
- Público: 14–25 anos. Canal da demo: web (chat).

## 2. Decisões a tomar às 11:15 (Aless + luislamy)
| Decisão | Opção por omissão | Alternativa |
|---|---|---|
| Linguagem/back-end | Python + FastAPI | Node/TypeScript |
| LLM | o que o hackathon fornecer; senão um com chamadas de ferramentas (function calling) | — |
| Front-end | página HTML/JS única servida pela API | Streamlit (mais rápido, menos bonito) |
| Persistência | nenhuma (memória da sessão) | SQLite se sobrar tempo |
| Regras oficiais do desafio | **POR VERIFICAR**: critérios de avaliação, formato de entrega, tecnologias obrigatórias | — |

## 3. Âmbito
**MVP (até 12:45):** chat → agente com prompt de sistema → 3 ferramentas (`orcamento`, `objetivo_poupanca`, `juros_compostos`) → resposta explicada.
**Valor (12:45–13:45, escolher 2–3):** custo do crédito / «compre agora pague depois»; detetor de sinais de burla; quiz de 3 perguntas no fim; modo «explica como se eu tivesse 15 anos»; perfil curto (idade aproximada, objetivo) sem dados sensíveis.
**Fora:** login, base de dados, apps móveis, deploy complexo.

## 4. Divisão de trabalho (proposta)
| Quem | Bloco 1–2 | Bloco 3 |
|---|---|---|
| Aless + Claude | API, agente, ferramentas de cálculo com testes | guardrails, avaliação |
| luislamy | página de chat, ligação à API | funcionalidade de valor visível (quiz/simulador), pitch |

## 5. Portões e horas-limite
- 12:45 Portão 1 — demo mínima 3× sem erro.
- 14:15 Portão 2 — `docs/AVALIACAO.md` (limites 100%, restantes ≥80%), testes de cálculo verdes, sem segredos no repo. **Congelar funcionalidades.**
- 14:40 congelar código · 14:55 entregue.

## 6. Demo (3 min, ensaiar às 14:20)
1. O problema numa frase + um número de contexto (confirmar fonte).
2. «Recebi 400 € do part-time, como divido?» → orçamento.
3. «Quero 600 € para a viagem de finalistas em 8 meses» → objetivo de poupança.
4. «Uma loja oferece pagar em 4 vezes» → custo real / perguntas a fazer.
5. «Recebi SMS do banco a pedir o código» → alerta de burla e passos.
6. Fecho: impacto, limites responsáveis, próximos passos.
Plano B: `DEMO_OFFLINE=1` + capturas feitas às 14:15.

## 7. Depois do hackathon (ideias que não entram hoje)
(acrescentar aqui em vez de as fazer agora)
