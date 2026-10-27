# Contrato da Knowledge Base (equipa 2)

Um ficheiro `.md` por página/fonte, dentro de `backend/kb/`. Nome: `<fonte>-<tema>.md` (ex.: `bdp-taeg.md`).

## Formato

```markdown
---
title: O que é a TAEG
source: Portal do Cliente Bancário (BdP)
url: https://clientebancario.bportugal.pt/...
journey: credito
collected: 2026-10-27
---

## O que é
Texto em pt-PT, reescrito por palavras vossas ou resumido. Parágrafos curtos.

## Como se usa para comparar créditos
...
```

## Regras

- `journey` ∈ `credito`, `salario`, `irs`, `geral` (o pipeline filtra por isto).
- `url` obrigatório: é o que aparece citado na resposta.
- Usar `##` para secções: cada secção vira um ou mais chunks, por isso cada uma deve fazer sentido sozinha.
- Números (taxas, limites, escalões) sempre com a data ou período a que se referem.
- Nada de tabelas gigantes: converter para frases ou listas curtas.
- Resumir e reescrever; não colar artigos inteiros.

## Fontes por jornada

| Jornada | Fontes |
| --- | --- |
| credito | Portal do Cliente Bancário (TAEG, crédito aos consumidores, taxas máximas), Saldo Positivo |
| salario | Portal do Cliente Bancário (depósitos, poupança), Saldo Positivo, Todos Contam |
| irs | Portal das Finanças (IRS Jovem, retenção na fonte), Saldo Positivo (IRS Jovem, entrega do IRS) |
| geral | Todos Contam, glossário |
