#!/usr/bin/env python3
# painel-agentes.py — Cowork 19/10/2026 (pedido do Aless): agentes vivos com MODELO real (campo model do JSONL) e CONSUMO de tokens,
# incluindo os subagentes de cada sessão. Só leitura. Uso: python3 .claude/painel-agentes.py [--vivo] [--todos]
import json, subprocess, sys, glob, os, time, re, collections
EF = re.compile(r'"effort":"(low|medium|high|xhigh|max)"')
P = os.path.expanduser('~/.claude/projects')
def k(n): return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k"
def ler(f, tot, efs=None):
    ef = collections.Counter()
    try:
        for l in open(f, errors='ignore'):
            for x in EF.findall(l): ef[x] += 1
            if '"usage"' not in l: continue
            try: e = json.loads(l)
            except Exception: continue
            m = e.get('message') or {}; u = m.get('usage') or {}
            if not u: continue
            mod = m.get('model', '?'); d = tot.setdefault(mod, [0, 0, 0])
            d[0] += u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0)
            d[1] += u.get('cache_read_input_tokens', 0); d[2] += u.get('output_tokens', 0)
            if efs is not None: efs.setdefault(mod, collections.Counter())
    except FileNotFoundError: pass
    if efs is not None and ef:
        for m in list(efs): efs[m].update(ef)
    return ef.most_common(1)[0][0] if ef else '?'
def painel(todos):
    try: ags = json.loads(subprocess.run(['claude', 'agents', '--json'], capture_output=True, text=True, timeout=20).stdout or '[]')
    except Exception as ex: print('sem claude agents:', ex); return
    if not todos: ags = [a for a in ags if a.get('state') != 'done']
    print(time.strftime('%H:%M:%S'), '— agentes', len(ags), '(modelo real e tokens: novos | cache lida | saída)\n')
    print(f"{'agente':24} {'estado':9} {'modelo principal':16} {'effort':7} {'novos':>7} {'cache':>7} {'saída':>7}  subagentes (modelo/effort saída)")
    G = [0, 0, 0]
    for a in ags:
        sid = a.get('sessionId') or a.get('id'); tot = {}; sub = {}; sefs = {}; ef = '?'
        for f in glob.glob(f'{P}/*/{sid}.jsonl'): ef = ler(f, tot)
        for f in glob.glob(f'{P}/*/{sid}/**/*.jsonl', recursive=True):
            antes = set(sub); e2 = ler(f, sub)
            for m in sub:
                if m not in antes or m not in sefs: sefs.setdefault(m, collections.Counter())
                sefs[m][e2] += 1
        mp = max(tot, key=lambda m: tot[m][2], default='?')
        t = [sum(v[i] for v in tot.values()) for i in range(3)]
        s = ' · '.join(f"{m.replace('claude-','')}/{sefs.get(m, collections.Counter({'?':1})).most_common(1)[0][0]} {k(v[2])}" for m, v in sorted(sub.items(), key=lambda x: -x[1][2])) or '—'
        for i in range(3): G[i] += t[i] + sum(v[i] for v in sub.values())
        print(f"{a.get('name','?')[:24]:24} {str(a.get('state'))[:9]:9} {mp.replace('claude-','')[:16]:16} {ef:7} {k(t[0]):>7} {k(t[1]):>7} {k(t[2]):>7}  {s}")
    print(f"\nTOTAL (com subagentes): novos {k(G[0])} · cache lida {k(G[1])} · saída {k(G[2])}")
if '--vivo' in sys.argv:
    while True:
        os.system('clear'); painel('--todos' in sys.argv); time.sleep(15)
else: painel('--todos' in sys.argv)
