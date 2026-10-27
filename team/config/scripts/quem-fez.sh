#!/bin/sh
# quem-fez.sh — quem fez o quê no repo (só leitura). Uso: sh .claude/scripts/quem-fez.sh [desde, ex. "3 hours ago"]
cd "$(dirname "$0")/../.." || exit 1
desde=${1:-"12 hours ago"}
git fetch -q origin 2>/dev/null || echo "AVISO: git fetch falhou (sem rede ou sem acesso) — dados podem estar desatualizados"
echo "== Branches remotas (último commit)"
git for-each-ref --sort=-committerdate refs/remotes --format='%(refname:short) | %(authorname) | %(committerdate:format:%H:%M) | %(subject)'
echo; echo "== Commits por autor desde $desde (todas as branches)"
git shortlog -sne --all --since="$desde"
echo; echo "== Ficheiros tocados por autor"
git log --all --since="$desde" --format='@@%an' --name-only | awk '/^@@/{a=substr($0,3);next} NF{f[a]=f[a]" "$0} END{for(k in f){print k":"; n=split(f[k],x," "); delete s; for(i=1;i<=n;i++) if(!s[x[i]]++) print "   "x[i]}}'
echo; echo "== Ferramenta declarada nos commits (trailer «Ferramenta:» ou Co-Authored-By)"
git log --all --since="$desde" --format='%h %an | %(trailers:key=Ferramenta,valueonly,separator=%x2C)%(trailers:key=Co-Authored-By,valueonly,separator=%x2C)' | sed 's/ | $/ | (não declarada)/'
