# Prompt de arranque (colar uma vez na IA de cada pessoa)

Passos: `git clone https://github.com/luislamy/ainnovation-hackathon-2026 && cd ainnovation-hackathon-2026`, abrir a pasta na IA, colar o prompt. Claude Code: `sh team/instalar.sh`.

```
Estás a trabalhar no repo do Hackathon AInnovation 2026 (assistente de literacia financeira para jovens em Portugal; entrega hoje 15:00 Lisboa). Sou [O MEU NOME], o meu papel é [KB | casos de uso | backend | front].
1) Lê AGENTS.md, depois team/INDEX.md, team/OPERACAO.md, team/AGENTES_AUTO.md, team/PLANO_EQUIPA.md e team/TRACE.md. Segue team/AGENTES_AUTO.md sem me pedir: eu só converso contigo.
2) Faz git pull --ff-only e diz-me em 3 linhas o que já existe e o que me falta fazer no meu papel.
3) Trabalha numa branch minha (nome/coisa). Nunca em main, nunca --force, nunca alterar trabalho de outros sem decisão do grupo.
4) Cada commit acaba com "Ferramenta: <a tua ferramenta>". Antes de qualquer push ou PR pergunta-me só "Sim ou não?" com um resumo de 3 linhas.
5) Depois de cada push/merge acrescenta uma linha ao team/TRACE.md.
6) Segredos só em .env. O LLM não faz contas (usa backend/calculators.py). Factos só MEDIDOS, LIDOS (fonte+data) ou POR VERIFICAR.
7) Respostas curtas: veredicto primeiro, máximo 5 linhas ou tabela.
8) Se os tokens ficarem a 95%, prepara a passagem em team/handoff/ para outra IA continuar.
```
