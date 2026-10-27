---
name: hackathon-sprint
description: Operar um hackathon contra o relógio com o rigor do workflow da Saints — blocos de tempo, MVP ponta-a-ponta primeiro, portões de qualidade curtos, demo ensaiada e entrega a horas. Usar em todas as tarefas deste repo até à entrega.
---

# Hackathon sprint (adaptado de `workflow-agentes-base` + `saints-operacao`, 27/10/2026)

O workflow da Saints foi desenhado para semanas. Aqui há 4 horas. Mantém-se o rigor (Regra Zero, testes, segredos fora, revisão), corta-se a cerimónia (sem canais com lock, sem comités de lentes, sem maestros múltiplos).

## 1. O relógio manda
| Bloco | Hora | Saída obrigatória |
|---|---|---|
| 0. Arranque | 11:00–11:20 | repo ligado, stack decidida, âmbito do MVP escrito (`docs/PLANO_HACKATHON.md`) |
| 1. Esqueleto | 11:20–12:00 | API a responder + página de chat a falar com a API + LLM ligado (mesmo com prompt simples) |
| 2. Núcleo | 12:00–12:45 | **MVP ponta-a-ponta**: pergunta do jovem → agente → ferramenta de cálculo → resposta explicada. Portão 1 |
| 3. Valor | 12:45–13:45 | 2–3 funcionalidades que ganham pontos (ver §3), guardrails, testes de cálculo |
| 4. Prova | 13:45–14:15 | correr `docs/AVALIACAO.md`, corrigir o que falha. Portão 2. **Congelar funcionalidades às 14:15** |
| 5. Demo | 14:15–14:40 | README, guião da demo (3 min), pitch, plano B se a API cair. **Congelar código às 14:40** |
| 6. Entrega | 14:40–14:55 | último commit, push (OK do Aless), submissão; 5 min de folga |

Atrasado mais de 15 min num bloco → cortar âmbito, nunca empurrar o relógio. Diz ao Aless o que se corta numa linha.

## 2. Ordem de trabalho em cada tarefa
1. `date` → em que bloco estamos? A tarefa cabe no bloco?
2. Plano em 3–5 linhas (ficheiros, dependências). O que já funciona tem de continuar a funcionar.
3. Implementar o mínimo que fecha a tarefa.
4. Verificar a correr (não só ler): teste, `curl`, ou abrir a página. MEDIDO, não DEDUZIDO.
5. Commit pequeno com mensagem clara. Push só com OK do Aless.
6. Uma linha ao Aless: feito / o que falta / o que precisa dele.

## 3. Onde estão os pontos (prioridade)
1. **Funciona na demo** (fluxo ponta-a-ponta estável).
2. **Utilidade real para jovens** (casos concretos: primeiro salário, mesada, poupar para algo, cartão, burlas).
3. **Confiança:** respostas corretas, contas certas (ferramentas, não o LLM), fontes oficiais, limites claros (não é aconselhamento).
4. **Experiência:** linguagem simples PT-PT, curta, com exemplos em euros, um próximo passo.
5. **Diferenciação:** ex. simulador de objetivo de poupança, quiz curto, deteção de burlas, «modo explica-me como se tivesse 15 anos».

## 4. Portões (curtos)
- **Portão 1 (12:45):** a demo mínima corre 3 vezes seguidas sem erro. Se não, nada novo até corrigir.
- **Portão 2 (14:15):** `docs/AVALIACAO.md` passa nos casos de segurança (todos) e ≥80% dos restantes; contas com testes verdes; nenhum segredo no repo (`git grep -nE 'sk-|api[_-]?key *='`).
- **Revisão** (`senior-engineer-review`) antes de juntar código de duas pessoas em `main`.

## 5. Equipa e git (grupo de 5, ferramentas diferentes)
- Rever tudo, alterar nada dos outros sem decisão do grupo. Regras completas: `CLAUDE.md` §7.
- Antes de rever ou integrar: `sh .claude/scripts/quem-fez.sh` (quem fez o quê). Revisões pelo agente `revisor-equipa` → `docs/revisoes/` (local); o Aless decide se partilha.
- O nosso trabalho em branches `aless/<coisa>`; `main` só por merge combinado com o grupo.
- Commits pelo Claude; push pelo Aless. Nunca `--force`, rebase ou merge sobre trabalho alheio; conflito → parar e avisar.

## 6. Plano B da demo
- Respostas de exemplo gravadas (modo `DEMO_OFFLINE=1`) para mostrar o fluxo se a API do LLM falhar.
- Vídeo/screenshots do fluxo a funcionar, feitos às 14:15.

## 7. O que NÃO se faz hoje
Autenticação completa, base de dados complexa, deploy elaborado, refactors bonitos, funcionalidades fora do §3. Se surgir a ideia, vai para «Depois do hackathon» no README.

## 8. Modelos e agentes (método Saints)
Opus 5.5 low/medium (`planeador`, `revisor-final`) → planeia e revê no fim. Sonnet 5.5 medium (sessão principal) → orquestra e distribui. Haiku 5.5 low (`batedor`, `escritor`, `medidor`) → todo o trabalho bruto: procurar ficheiros, escrever código e testes, correr testes. Tabela completa e ciclo: `CLAUDE.md` §6. No relógio: `planeador` no início de cada bloco (≤5 min); `revisor-final` antes de cada merge e no Portão 2.
