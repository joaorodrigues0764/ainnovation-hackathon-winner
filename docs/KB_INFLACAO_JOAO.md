# Contexto de base: inflação em conversas novas

27/10/2026. Base: `46f9aaf` de `main`. Problema reportado pelo João: num chat novo, o assistente respondeu que não sabia o que era inflação.

## Diagnóstico medido

Antes desta alteração, a pesquisa BM25 para «Sabes o que é inflação?» e «O que é a inflação?» devolveu zero chunks nas jornadas `credito` e `geral`. A KB não tinha um documento sobre inflação, embora já existisse a calculadora `efeito_inflacao`.

O prompt do produto exige apoio nas fontes e instrui o modelo a admitir quando as fontes não chegam. A ausência de conteúdo é uma explicação plausível para a resposta observada pelo utilizador; não foi reproduzida uma chamada ao modelo real nesta sessão.

## Fontes consultadas e conteúdos preparados

Todas as páginas foram abertas e lidas em 27/10/2026; um resumo por página, com URL exata e `journey: geral`. Assim o contexto é elegível em qualquer jornada, incluindo o crédito que a interface seleciona por omissão.

| Ficheiro em `backend/kb/` | Fonte oficial | Contexto |
| --- | --- | --- |
| `bdp-inflacao.md` | [Banco de Portugal — Inflação: o que é](https://clientebancario.bportugal.pt/pt-pt/inflacao-o-que-e) | Definição, IPC, taxas mensal e homóloga |
| `bdp-inflacao-poder-compra.md` | [Banco de Portugal — Como a inflação influencia a sua vida](https://clientebancario.bportugal.pt/pt-pt/como-inflacao-influencia-sua-vida) | Poder de compra, salário, poupança e orçamento |
| `bce-inflacao-cabaz.md` | [BCE — O que é a inflação?](https://www.ecb.europa.eu/ecb-and-you/explainers/tell-me-more/html/what_is_inflation.pt.html) | Cabaz, pesos dos produtos, IHPC e diferenças entre famílias |

São conteúdos conceptuais: não apresentam uma taxa de inflação atual, previsões ou contas feitas pelo modelo. Não foram alterados o prompt, o filtro de jornadas ou os conteúdos dos colegas.

## Verificação

- Pesquisa real: oito formulações, em seis jornadas e sem filtro, total de 56 verificações aprovadas. A fonte específica esperada aparece nos cinco primeiros chunks.
- Preparação do prompt: sete verificações com histórico vazio asseguram que existem fontes citáveis sobre inflação no contexto enviado ao modelo.
- Total dos testes específicos: 63 passaram. Suite completa do backend com estes conteúdos: 158 testes passaram em 1,44 s.
- Conjunto anterior de pesquisa: 12/12 regressões e 12/12 casos novos continuaram a passar.
- Formato: campos obrigatórios, data, URL específica e secções autónomas conforme `docs/KB_CONTRACT.md`.

Reproduzir:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_kb_inflacao.py -q
backend/.venv/bin/python scripts/avaliar_kb.py --group regressao --group novo
```

Os testes validam pesquisa e contexto disponível, não a redação ou as citações da resposta gerada. Após integração, reiniciar a API: o índice da KB é construído no arranque. A resposta do fornecedor real deve ser confirmada na conversa nova.

## Limitação ortográfica

A pergunta «O que é infllação?» (com um `l` adicional) continuou sem resultados em BM25 nas jornadas `credito` e `geral`. Não foram introduzidos erros ortográficos nos documentos para contornar a pesquisa. O responsável pelo RAG deve avaliar normalização ou reformulação da pergunta; o comportamento com embeddings não foi testado.

## Próximo passo

Publicar as três fontes e os testes após autorização, obter revisão cruzada e repetir «Sabes o que é inflação?» num chat novo com a API reiniciada. Para outros conceitos gerais, aplicar a mesma verificação de contexto por jornada antes de acrescentar documentos.
