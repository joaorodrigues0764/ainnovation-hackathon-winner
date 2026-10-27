#!/bin/sh
# Instala a configuração do grupo na pasta local (sem tocar no .gitignore; nada disto sobe para o git).
# Não sobrescreve ficheiros que já existem. Uso: sh team/instalar.sh
set -e
cd "$(git rev-parse --show-toplevel)"
mkdir -p .claude/skills .claude/agents .claude/scripts docs/revisoes
for s in team/skills/*/; do n=$(basename "$s"); [ -d ".claude/skills/$n" ] || cp -R "$s" ".claude/skills/$n"; done
for f in team/config/agents/*.md; do b=".claude/agents/$(basename "$f")"; [ -f "$b" ] || cp "$f" "$b"; done
for f in team/config/scripts/*; do b=".claude/scripts/$(basename "$f")"; [ -f "$b" ] || cp "$f" "$b"; done
[ -f .claude/settings.json ] || cp team/config/settings.json .claude/settings.json
[ -f CLAUDE.md ] || cp team/config/CLAUDE.contrato.md CLAUDE.md
for f in team/docs/*.md; do b="docs/$(basename "$f")"; [ -f "$b" ] || cp "$f" "$b"; done
echo "instalado. Skills: $(ls .claude/skills | tr '\n' ' ')"
