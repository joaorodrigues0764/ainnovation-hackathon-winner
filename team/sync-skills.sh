#!/bin/sh
# Fonte local (.claude/, CLAUDE.md, docs/) -> versão do grupo (team/). Nome histórico: sincroniza TUDO o que é partilhado.
# Skills partilhadas: só as 3 do grupo (engenharia e deep-research ficam locais).
set -e
cd "$(git rev-parse --show-toplevel)"
for s in literacia-financeira-jovens hackathon-sprint senior-engineer-review; do
  mkdir -p "team/skills/$s" && cp -R ".claude/skills/$s/." "team/skills/$s/"
done
mkdir -p team/config/agents team/config/scripts team/docs
cp .claude/agents/*.md team/config/agents/
cp .claude/scripts/* team/config/scripts/
cp .claude/settings.json team/config/settings.json
cp CLAUDE.md team/config/CLAUDE.contrato.md
cp docs/PLANO_HACKATHON.md docs/AVALIACAO.md team/docs/
python3 .claude/sanitizar-para-grupo.py || { echo "ABORTADO: sobra informação pessoal/de outro projeto em team/ (ver linhas acima)"; exit 1; }
echo "sincronizado: skills, agents, scripts, settings, CLAUDE.md, docs"
