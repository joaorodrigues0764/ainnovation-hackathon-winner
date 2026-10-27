#!/bin/sh
# lancar-agente.sh <nome> <ficheiro-ordem> [effort]  — fonte: ~/IdeaProjects/_ferramentas/workflow (05/10/2026)
# Lança UMA sessão Opus 5.5 com nome e effort EXPLÍCITO (sem --effort o Opus 5.5 arranca em medium ou no nível gravado),
# só se não houver outra viva com o mesmo nome. Correr na raiz do projecto.
set -eu
nome=${1:?uso: lancar-agente.sh <nome> <ficheiro-ordem> [effort] [modelo]}; ordem=${2:?falta o ficheiro da ordem}; eff=${3:-medium}; mod=${4:-claude-sonnet-5-5}
case "$eff" in low|medium|high|xhigh|max) ;; *) echo "PAREI: effort inválido '$eff' (low|medium|high|xhigh|max)"; exit 1;; esac
[ -f "$ordem" ] || { echo "PAREI: não encontro $ordem (estás na raiz do projecto?)"; exit 1; }
command -v claude >/dev/null || { echo "PAREI: comando claude não encontrado"; exit 1; }
vivas=$(claude agents --json 2>/dev/null | python3 -c '
import json,sys
n=sys.argv[1]
try: d=json.load(sys.stdin)
except Exception: print("ERRO"); sys.exit()
it=d if isinstance(d,list) else (d.get("agents") or d.get("sessions") or [])
c=0
for a in it:
  nm=str(a.get("name") or a.get("title") or "")
  st=(str(a.get("status") or "")+" "+str(a.get("state") or "")).lower()
  if nm==n and not any(x in st for x in ("complete","done","stopp","finish","exit")): c+=1
print(c)' "$nome")
[ "$vivas" = "ERRO" ] && { echo "PAREI: não consegui ler claude agents --json; confirma à mão que não há outro '$nome' vivo."; exit 1; }
[ "$vivas" -gt 0 ] && { echo "PAREI: já há $vivas sessão(ões) '$nome' viva(s). Fecha a antiga (Ctrl+X em claude agents) ou deixa-a trabalhar."; exit 1; }
claude --bg -n "$nome" --model "$mod" --effort "$eff" "$(cat "$ordem")" && echo "OK: $nome lançado ($mod, effort $eff). Confirma no cabeçalho da sessão."
