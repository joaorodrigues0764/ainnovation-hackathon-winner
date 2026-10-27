# Índice do projeto (ponteiros — não duplicar conteúdo aqui)

Regra: cada coisa vive num só sítio; este ficheiro só aponta. Quem cria ou move um ficheiro atualiza a linha respetiva no mesmo commit.

| O quê | Onde | Dono | Estado |
|---|---|---|---|
| Comportamento automático dos agentes (qualquer ferramenta) | `team/AGENTES_AUTO.md` | grupo | v1 |
| Como operamos (branches, commits, revisão, tokens) | `team/OPERACAO.md` | grupo | v1 |
| Registo de pushes e merges (trace) | `team/TRACE.md` | todos (append) | ativo |
| Domínio + guardrails do agente | `team/skills/literacia-financeira-jovens/SKILL.md` | grupo | v1 |
| Operar contra o relógio (blocos, portões) | `team/skills/hackathon-sprint/SKILL.md` | grupo | v1 |
| Revisão de código | `team/skills/senior-engineer-review/SKILL.md` | grupo | v1 |
| Plano inicial, âmbito, demo (parcialmente ultrapassado pelo quadro) | `team/docs/PLANO_HACKATHON.md` | grupo | rascunho |
| Casos de teste do agente | `team/docs/AVALIACAO.md` | grupo | rascunho |
| Plano da equipa (quadro de 27/10): arquitetura, tarefas, quem | `team/PLANO_EQUIPA.md` (foto: `team/assets/quadro-planeamento-2026-10-27.jpg`) | grupo | v1, POR CONFIRMAR |
| Instalar a configuração do grupo (skills, agentes, modelos) | `sh team/instalar.sh` (fontes: `team/skills/`, `team/config/`, `team/docs/`) | Aless mantém | v1 |
| Agentes e modelos (Opus planeia/revê, Sonnet orquestra, Haiku bruto) | `team/config/agents/`, `team/config/CLAUDE.contrato.md` §6 | Aless mantém | v1 |
| KB (base de conhecimento) | `kb/` POR CRIAR | Aless, Guilherme, João | — |
| Contributo KB do João: cartões, extratos, FIN e prevenção do incumprimento | `docs/KB_JOAO_VALIDACAO.md` → ficheiros em `backend/kb/` | João | fontes verificadas em 27/10/2026; validação no relatório |
| Cobertura dos 21 UCs e reforço oficial da KB (IRS, Euribor, contas) | `docs/KB_COBERTURA_JOAO.md`; casos: `docs/kb_retrieval_cases.json`; avaliador: `scripts/avaliar_kb.py` | João | 24 perguntas passaram; 2 limites entre jornadas documentados; segunda entrega local |
| Pipeline RAG | POR CRIAR | luislamy | — |
| Quem faz o quê | `team/OPERACAO.md` §2 | grupo | POR CONFIRMAR |
| Backend (FastAPI) + ferramentas de cálculo | POR CRIAR | POR DECIDIR | — |
| Front-end (Next.js, chat) | POR CRIAR | POR DECIDIR | — |
| Revisões de código | `docs/revisoes/` (locais; partilha decidida pelo Aless) | — | — |
