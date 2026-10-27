# Comportamento automático dos agentes (Claude, ChatGPT, Codex, outras)

Objetivo: o humano só conversa; tu fazes o resto. Segue isto sem pedir autorização, exceto onde diz «pergunta sim/não».

## 1. Ao começar (sempre, sem te pedirem)
1. Hora e bloco: corre `date` (Lisboa). Prazo 27/10 15:00; congelar funcionalidades 14:15, código 14:40, entrega 14:55 (`team/skills/hackathon-sprint/SKILL.md`).
2. Estado real: `git fetch` e `git status`; lê `team/INDEX.md`, `team/STATUS.md`, `team/TRACE.md`, a passagem mais recente em `team/handoff/` (se existir) e `team/PLANO_EQUIPA.md` e a lista de PRs abertos. Diz em 2 linhas o que mudou desde a última vez.
3. Confirma a tua branch (`nome/coisa`). Nunca trabalhes em `main`.
4. Se faltar a configuração: `sh team/instalar.sh`. Sem acesso ao shell: lê `team/skills/` como instruções.

## 2. Enquanto trabalhas
- Zero suposições: cada facto é MEDIDO (corri/vi), LIDO (fonte + data) ou POR VERIFICAR. Nunca dês uma dedução como medição.
- O LLM não faz contas: cálculos em funções testadas. Segredos só em `.env` (nunca na linha de comandos nem no repo).
- Domínio: segue `team/skills/literacia-financeira-jovens/SKILL.md` (sem aconselhamento financeiro, sem pedir dados pessoais, atenção a menores).
- Verifica a correr (teste, `curl`, abrir a página) antes de dares algo por feito.
- Trabalho dos outros: só leitura. Não edites, não reverts, não apagues. Propõe.
- Commits pequenos; última linha: `Ferramenta: <a tua ferramenta>`.

## 3. Quando acabas uma tarefa (automático)
1. Commit na tua branch. 2. Atualiza a tua linha em `team/STATUS.md`, acrescenta 1 linha ao fim de `team/TRACE.md` (ou `sh team/trace.sh push|merge "resumo"`) e atualiza a linha respetiva de `team/INDEX.md` se criaste ou moveste um ficheiro. 3. Responde ao humano: veredicto primeiro, máximo 5 linhas ou uma tabela, o que falta e o que precisas dele.

## 4. Pergunta sim/não ao humano antes de
- fazer push ou abrir/fundir um PR;
- qualquer coisa fora da tua branch; instalar com permissões de administrador; usar segredos.
Nunca: `--force`, rebase, apagar branches ou ficheiros de outros, resolver conflitos por cima do trabalho alheio (pára e avisa).

## 5. Quando alguém faz push ou abre PR (revisão automática)
1. Identifica o autor pelo commit/PR (se não der, «autor POR VERIFICAR»).
2. Lê o diff contra `main`; corre os testes ou o arranque se der sem instalar nada novo.
3. Relatório curto e simples (termos simples, sem culpar pessoas): **Em 1 linha · Está bem · Problemas (alta/média/baixa, ficheiro:linha) · Sugestões pequenas · Choques de integração · Para decidir em grupo · Não verifiquei**.
4. Gravidade alta sempre: segurança, dados de menores, contas feitas pelo LLM, segredos no código.
5. Publica o relatório como comentário no PR só depois de o humano dizer sim.

## 6. Tokens a acabar (≈90–95%)
Faz a passagem sozinho, sem esperar: `team/HANDOFF.md` §3. O humano só abre a outra ferramenta e diz «continua».

## 7. Como responder (todas as respostas)
Veredicto primeiro. Máximo 5 linhas ou tabela; o detalhe vai para um ficheiro e a resposta aponta para ele. Português de Portugal, termos simples. Se a decisão é do grupo, escreve-a como pergunta fechada.

## 8. Colar no ChatGPT / outras ferramentas (instruções do projeto)
«Lê `AGENTS.md` e `team/AGENTES_AUTO.md` do repositório do projeto e segue-os sempre, sem eu pedir. Respostas curtas, veredicto primeiro.»
