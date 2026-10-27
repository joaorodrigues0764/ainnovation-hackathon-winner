# Passagem de testemunho entre agentes (quando os tokens acabam ou a ferramenta bloqueia)

Objetivo: qualquer agente (Claude, ChatGPT, outro) continua o trabalho de outro sem o humano ter de explicar nada.

## 1. Canal direto entre agentes
- **Canal:** issue fixa «Canal dos agentes» no GitHub. Cada agente escreve 1 linha por evento: `[<pessoa>/<ferramenta>] <o que mudou> · <branch ou PR> · <o que precisa de quem>`. Os humanos só leem o essencial.
- **Estado:** `team/STATUS.md` (quem faz o quê agora). **Histórico:** `team/TRACE.md`.
- Conversas de detalhe entre agentes vão para comentários de PR; ao humano chega 1 linha e uma pergunta de sim/não.

## 2. Quando passar (qualquer um destes)
- Tokens a ~90–95% ou limite de mensagens perto; ou a ferramenta bloqueia/falha 2 vezes; ou o humano diz «passa».

## 3. Como passar (o agente que sai faz isto sozinho, 3 passos)
1. Commit do trabalho na sua branch (nada por guardar só na conversa).
2. Escrever `team/handoff/AAAA-MM-DD_HHMM_<de>_para_<para>.md` com o modelo abaixo e fazer commit.
3. Atualizar a sua linha em `team/STATUS.md` e postar 1 linha no canal. Dizer ao humano: «Passagem feita: abre <ferramenta> e diz "continua"».

### Modelo da passagem (máx. 25 linhas)
```
# Passagem <de> → <para> · <hora>
Branch/PR: ...   Último commit: <hash>   Testes: <MEDIDO: o que correu e resultado>
Feito: (3–5 pontos, com ficheiros)
A meio: (o que está incompleto e onde parou)
Próximo passo: (1 ação concreta; comando se houver)
Decisões tomadas: (e quem as tomou)
Não tocar: (ficheiros de outros, PRs em hold)
Pedidos pendentes aos outros: ...
POR VERIFICAR: ...
```

## 4. Como retomar (o agente que entra, sem pedir nada)
Ler `AGENTS.md` → `team/AGENTES_AUTO.md` → `team/STATUS.md` → a passagem mais recente em `team/handoff/` → `git fetch` e `git log` da branch. Confirmar em 1 linha ao humano o que vai fazer e continuar. Não refazer o que já está feito (ver `team/TRACE.md`).

## 5. Entre ferramentas diferentes
Tudo é Markdown no repo: funciona igual entre Claude, ChatGPT ou um modelo local (Ollama/Obsidian lêem a mesma pasta). Segredos nunca entram na passagem (só em `.env`).
