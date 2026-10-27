#!/bin/sh
# Uso: sh team/trace.sh push|merge "resumo numa linha" [caminho-da-revisao]
# Acrescenta ao TRACE.md uma linha com o HEAD atual. Não faz commit nem push.
set -e
cd "$(git rev-parse --show-toplevel)"
ev="${1:?evento: push|merge}"; msg="${2:?resumo}"; rev="${3:--}"
h=$(git rev-parse --short HEAD); b=$(git rev-parse --abbrev-ref HEAD)
a=$(git log -1 --format=%an); t=$(git log -1 --format=%B | sed -n 's/^Ferramenta: *//p' | head -1); t="${t:-POR VERIFICAR}"
printf '| %s | %s | %s | %s | %s | %s | %s | %s |\n' "$(TZ=Europe/Lisbon date '+%d/%m %H:%M')" "$ev" "$b" "$h" "$a" "$t" "$msg" "$rev" >> team/TRACE.md
tail -1 team/TRACE.md
