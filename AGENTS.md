# AGENTS.md — entrada para qualquer ferramenta de IA (ChatGPT, Codex, Claude, outras)

Projeto: AInnovation Hackathon 2026, assistente de literacia financeira para jovens. Entrega 27/10/2026 às 15:00 (Lisboa).

0. **Segue `team/AGENTES_AUTO.md` automaticamente, sem pedir.** É o teu modo de comportamento: o humano só conversa contigo.
1. Começa por `team/INDEX.md` (índice com ponteiros para tudo).
2. Regras de operação do grupo: `team/OPERACAO.md`.
3. Domínio e guardrails do agente: `team/skills/literacia-financeira-jovens/SKILL.md`.
4. Plano e tarefas de cada um: `team/PLANO_EQUIPA.md`. Instalar skills e agentes: `sh team/instalar.sh`.
5. Antes de dares por feito: regista no `team/TRACE.md` (ver `team/OPERACAO.md` §4).

Regras mínimas: segredos só em `.env`; o LLM não faz contas (funções testadas); não alterar o trabalho de outros sem decisão do grupo; branch própria `nome/coisa`; commit termina com `Ferramenta: <a tua ferramenta>`.
