#!/bin/sh
# Copia as skills partilhadas de .claude/skills (fonte local do Aless) para team/skills (versão do grupo).
# Só estas 3; engenharia e deep-research ficam locais (stack Saints / não necessárias ao grupo).
set -e
cd "$(git rev-parse --show-toplevel)"
for s in literacia-financeira-jovens hackathon-sprint senior-engineer-review; do
  mkdir -p "team/skills/$s" && cp -R ".claude/skills/$s/." "team/skills/$s/"
done
echo "skills sincronizadas: $(ls team/skills | tr '\n' ' ')"
