# Trace de pushes e merges (acrescentar no fim; nunca editar linhas antigas)

| Hora (Lisboa) | Evento | Branch | Commit | Autor | Ferramenta | O que mudou (1 linha) | Revisão |
|---|---|---|---|---|---|---|---|
| 27/10 11:39 | merge | simonedossantos-ship-it-patch-1 (PR #1) | 0e65181 | simonedossantos-ship-it | POR VERIFICAR | USE_CASES.md (18 UCs) | - |
| 27/10 11:53 | merge | aless/coordenacao (PR #2) | 171dfad | AlessSaints | Claude | Índice por ponteiros, plano da equipa, skills/agentes partilhados em team/ | - |
| 27/10 11:55 | merge | feat/rag-pipeline (PR #3) | 911e513 | luislamy | Claude Code | Pipeline RAG e contrato da KB | docs/revisoes/ (local) |
| 27/10 11:57 | merge | aless/kb (PR #4) | db00e58 | AlessSaints | Claude | KB: burlas, orçamento, poupança e juros | - |
| 27/10 12:10 | merge | aless/pii (PR #6) | c538815 | AlessSaints | Claude | mask_pii antes do LLM + testes | - |
| 27/10 12:18 | merge | aless/calc (PR #9) | 9987723 | AlessSaints | Claude | Calculadoras com testes (UC-01, 02, 05, 06, 17) | - |
| 27/10 12:25 | push | feat/api (PR #5, aberto) | 33ad419 | luislamy | Claude Opus 5.5 | Calculadoras ligadas por tool calling OpenAI; calcular() removido | POR VERIFICAR |
| 27/10 12:23 | push | aless/kb2 (PR #10, aberto) | 1d33f03 | Claude | Claude | KB UC-03, 07, 08, 12, 17 (36 chunks) | - |
| 27/10 12:15 | push | aless/handoff (PR #7, aberto) | e2c4a5f | Claude | Claude | HANDOFF e STATUS | - |
| 27/10 12:35 | merge | aless/kb2 (PR #10) | 1416dd9 | luislamy | Claude | KB UC-03, 07, 08, 12, 17 em main (fundido pelo Lamy) | - |
| 27/10 12:40 | push | aless/trace (PR #11) | - | Claude | Claude | Prompt de arranque para as IAs da equipa (team/PROMPT_ARRANQUE.md) + índice | - |
| 27/10 12:50 | push | aless/calc-taxas (local) | - | Claude | Claude | Taxas 0–1 nas calculadoras, erro se >1 (pedido do Aless) | - |
| 27/10 12:56 | push | gummi/kb-fontes | 22604ac | Gummi | Claude | KB: 7 páginas com fontes oficiais (taxas máximas T4 2026, IRS Jovem 2026, PERSI/RACE, cartões, serviços mínimos, CMVM, começar a trabalhar), PR #15 | por rever |
| 27/10 13:42 | commit local (sem push) | joao/kb | 4f36984 | João Rodrigues | Codex | 82 testes backend, lint e tipos passaram; quatro percursos UI com LLM simulado; 24/26 perguntas BM25; duas falhas entre jornadas e limites do build documentados | `docs/QA_INTEGRACAO_JOAO.md`; passagem para Lamy e revisão dos quatro conteúdos finais pendentes |
| 27/10 13:45 | push + abertura de PR + aviso no canal | joao/kb | a5bcda4 (relatório: 4f36984) | João Rodrigues | Codex | QA publicada com autorização; exemplos enviados ao Lamy e pedido de revisão enviado ao Aless; coordenar com harness #19 | [PR #20](https://github.com/luislamy/ainnovation-hackathon-2026/pull/20); [canal #8](https://github.com/luislamy/ainnovation-hackathon-2026/issues/8#issuecomment-6443493781) |
| 27/10 14:25 | push | aless/evals (local) | - | Claude | Claude | scripts/avaliar_pipeline.py: 16 verificações deterministas por UC (calculadoras, guardrails, máscara) | - |
| 27/10 14:04 | commit local (sem push) | joao/kb | 29c21ae | João Rodrigues | Codex | Três fontes oficiais de inflação em geral; 63 verificações sem histórico e 158 testes backend passaram; grafia infllação sem resultados em BM25 | `docs/KB_INFLACAO_JOAO.md`; publicação e revisão cruzada pendentes |
| 27/10 14:07 | push + abertura de PR | joao/kb | 7bb0aba (conteúdo: 29c21ae) | João Rodrigues | Codex | Contexto de inflação publicado com autorização; reiniciar API após integrar para reconstruir o índice | [PR #24](https://github.com/luislamy/ainnovation-hackathon-2026/pull/24); revisão cruzada pendente |
| 27/10 14:25 | push | aless/front-ux (local) | - | Claude | Claude | UX jovens §2: alvos de toque ≥44 px, enterKeyHint, foco visível (frontend, testado a 375 px e 1280 px) | - |
| 27/10 14:21 | merge | main (PR #21, #25, #26, #28) | fb36fd5 / 4d5b11e / 5c0a302 | Lamy | Claude | UC-15 guardrail valores atuais; KB geral (7 fontes); 16 evals deterministas; UX front (alvos 44 px, foco) | merge por Lamy |
| 27/10 14:24 | regressão detetada | main | 5c0a302 | Claude | Claude | KB3 partiu 3 testes de test_kb_inflacao (duplicado de inflação + glossário "simples" a competir com bdp-inflacao.md) | corrigido no PR #30 |
| 27/10 14:27 | push + PR | aless/fix-kb-inflacao | 92d237d | Claude | Claude | Remove duplicado de inflação e reformula glossário de juros; 185 testes e 16/16 evals OK | [PR #30](https://github.com/luislamy/ainnovation-hackathon-2026/pull/30); revisão por Lamy/João |
| 27/10 14:27 | push + PR | aless/front-voz | 2edda99 | Claude | Claude | Ditado por voz (Web Speech API, pt-PT) e aviso "Assistente de IA, pode errar"; lint/tsc OK, 375 e 1280 px sem overflow | [PR #31](https://github.com/luislamy/ainnovation-hackathon-2026/pull/31); build completo a validar no Mac; voz só testada com mock |
| 27/10 14:29 | merge | main (PR #30, #31, #32) | 83b6ea9 | Lamy | Claude | Fix KB inflação, ditado por voz + aviso de IA, trace | merge por Lamy |
| 27/10 14:30 | verificação | main | 83b6ea9 | Claude | Claude | pytest 188 passam; avaliar_pipeline 16/16 OK; eslint OK; tsc só falha em LayoutProps (tipo gerado pelo Next, ausente num clone limpo; passa com .next) | `next build` completo por validar no Mac |
| 27/10 14:45 | push + PR | aless/slides | - | Claude | Claude | docs/Apresentacao-Hackathon-AINNOVATION.pdf: deck da Simone + slide de métricas (0 inventados, 100% fontes, 100% guardrails, 188 testes + 16 avaliações) | PDF estático; deck editável continua no OneDrive |
