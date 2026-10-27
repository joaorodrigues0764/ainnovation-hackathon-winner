# Cobertura da KB face aos casos de uso

Leitura e medições em 27/10/2026. Âmbito: os 21 casos de `USE_CASES.md`, KB de `origin/main` em `1416dd9`, quatro conteúdos do PR #12 e quatro novos conteúdos locais. O merge local `606a05b` trouxe a API e a KB aprovadas em `main`. A avaliação final correu novamente com o RAG dessa versão.

**Resultado:** há texto de apoio para a maioria dos temas; isso não significa que os casos de uso passem. Foram acrescentadas fontes oficiais para deduções à coleta, IRS Jovem, Euribor e comparação de contas. A pesquisa passou 24 perguntas e falhou duas verificações de integração entre jornadas.

## Mapa dos 21 casos

Os caminhos dos conteúdos abaixo são relativos a `backend/kb/`. «Apoio» significa existência de texto relevante após leitura, não certificação das respostas do agente.

| Caso | Apoio na KB | Falta verificar ou decidir |
| --- | --- | --- |
| UC-01: objetivo de poupança | `todoscontam-poupanca-juros.md`, `todoscontam-orcamento.md` | Perguntas de clarificação e chamada de `objetivo_poupanca` na conversa |
| UC-02: primeiro salário | `todoscontam-orcamento.md`, `deco-fundo-emergencia.md` | A KB não explica a regra 50/30/20; a calculadora contém essa referência. Validar apresentação adaptável e valores calculados |
| UC-03: fundo de emergência | `deco-fundo-emergencia.md` | Pergunta sobre despesas e adequação da expressão «sem risco»; não certificar uma garantia absoluta |
| UC-04: gastos invisíveis | `bdp-extratos-saldos.md`, `todoscontam-orcamento.md` | Resposta com categorias e método concreto, sem pedir extratos reais |
| UC-05: crédito | `bdp-taeg.md`, `bdp-fin-credito-consumidores.md` | Calculadora, pressuposto TAN e custos excluídos; URL do conteúdo antigo de TAEG é genérico |
| UC-06: juros compostos | `todoscontam-poupanca-juros.md` | Cálculo, separação de depósitos/juros e pressupostos |
| UC-07: BNPL | `deco-compre-agora-pague-depois.md` | Tom equilibrado, acumulação de prestações e confirmação das condições |
| UC-08: seguros | `cgd-seguros-franquia-premio.md` | Linguagem simples e exemplo coerente; não recomendar seguradora |
| UC-09: ações/cripto | KB não substitui recusa; `guardrails.py` tem regra e encaminhamento | Testar a recusa na resposta final e o encaminhamento para materiais específicos da CMVM |
| UC-10: dados pessoais | `privacy.py` e tratamento na API; apoio fiscal em `at-irs-jovem-conceito.md` | Aviso, não repetição dos dados e afirmações sobre conservação de dados dependem da implementação |
| UC-11: renegociação | `bdp-prevencao-incumprimento.md`; regra em `guardrails.py` | Recusa de agir em nome do utilizador, empatia e encaminhamento |
| UC-12: MB WAY | `mbway-burla-venda-online.md`, `bdp-burlas-seguranca-online.md` | Resposta urgente e próximos passos se a operação já começou |
| UC-13: crédito + IRS | `bdp-prevencao-incumprimento.md`, `at-irs-jovem-conceito.md`; regra de ação externa | Tratar ambas as intenções; uma única jornada pode excluir parte da KB |
| UC-14: escolher banco/cartão | Novo `bdp-comissoes-contas.md`, `bdp-cartoes-debito-credito.md`, FIN | Recusar recomendação comercial e apresentar critérios; comparador não escolhe pelo utilizador |
| UC-15: escalões/Euribor atuais | Novo `bdp-euribor-spread.md` | Falta conteúdo conceptual específico de escalões de IRS; sem cotações em tempo real; filtro entre jornadas falha nos testes abaixo |
| UC-16: IRS Jovem e deduções | Novos `at-irs-jovem-conceito.md`, `at-deducoes-coleta.md` | O ficheiro antigo de IRS Jovem continua a poder trazer percentagens sem período explícito; decisão sobre revisão cabe ao autor/equipa |
| UC-17: bruto/líquido | `ss-descontos-salario-bruto-liquido.md` | Calculadora não apura IRS final; esclarecer situação pessoal e confirmar tabelas |
| UC-18: modo simples | Conceito em `todoscontam-poupanca-juros.md` | Analogia e adaptação do tom são comportamento do modelo |
| UC-19: perfil | `todoscontam-orcamento.md`; perfil/histórico na API | Continuidade da conversa e campos necessários do perfil requerem teste ponta a ponta |
| UC-20: pedido vago | Não se resolve acrescentando documentos | Validar uma ou duas perguntas curtas em vez de resposta genérica |
| UC-21: resumo | Não se resolve acrescentando documentos | Validar exatamente três passos coerentes com o histórico |

## Novos conteúdos e fontes

As páginas foram consultadas em 27/10/2026. Os resumos não incluem tabelas fiscais nem cotações atuais.

| Conteúdo | Fonte oficial | Jornada |
| --- | --- | --- |
| `at-deducoes-coleta.md` | [AT — Deduções à coleta](https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Rendimentos/Declaracao/Deducoes_a_coleta/Paginas/default.aspx) | irs |
| `at-irs-jovem-conceito.md` | [AT — Código do IRS, artigo 12.º-B](https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs_rep/Pages/irs12b.aspx) | irs |
| `bdp-euribor-spread.md` | [BdP — Taxas de juro no crédito à habitação](https://clientebancario.bportugal.pt/pt-pt/taxas-de-juro-no-credito-habitacao) | credito |
| `bdp-comissoes-contas.md` | [BdP — Encargos](https://clientebancario.bportugal.pt/pt-pt/encargos) | geral |

## Pesquisa: medições e limites

Conjunto fixado em `docs/kb_retrieval_cases.json`: 12 paráfrases de temas anteriores, 12 perguntas dos novos temas e duas verificações de integração. Cada caso regista a jornada e os ficheiros esperados. A métrica exige que **todos os ficheiros esperados** apareçam nos cinco primeiros chunks; não mede a qualidade do texto de cada chunk nem da resposta gerada.

| Grupo | Antes: 14 ficheiros / 52 chunks | Depois: 18 ficheiros / 65 chunks |
| --- | --- | --- |
| Regressão de temas anteriores | 12/12 | 12/12 |
| Novas fontes oficiais esperadas | 0/12 | 12/12 |
| Limites de integração | Não incluídos na medição inicial | 0/2 |

Os 0/12 iniciais indicam ausência das novas fontes específicas; não provam que nenhuma resposta anterior fosse possível. Os exemplos serviram também para verificar os conteúdos escritos: não são um conjunto independente de avaliação nem uma estimativa da precisão em produção. A comparação inicial foi feita numa pasta temporária que combinava os ficheiros de `main` com os do PR #12; após o merge, a avaliação final foi repetida na pasta real `backend/kb/` com os mesmos resultados para os 24 casos.

Falhas mantidas no conjunto para a equipa reproduzir:

- `euribor-jornada-irs`: «Quanto está hoje a Euribor?» com jornada `irs` não recupera `bdp-euribor-spread.md`, pois esse conteúdo pertence a `credito`.
- `duas-jornadas`: pergunta sobre IRS Jovem e Euribor com jornada `irs` encontra a fonte de IRS Jovem, mas exclui a de Euribor. Falta decidir na integração como pesquisar pedidos com vários temas. Não foi alterado o filtro do RAG.

A execução usou BM25, sem embeddings ou chamadas ao LLM. Campos obrigatórios e tamanho dos 13 novos chunks foram verificados; todos ficam abaixo de 1200 caracteres incluindo cabeçalhos. `git diff --check` não encontrou erros. A suite geral `pytest backend/tests -q` não correu porque `pytest` não está instalado nesta `.venv`; não foram instaladas dependências.

## Reproduzir

Na raiz do projeto, com as dependências de retrieval disponíveis no ambiente:

```bash
backend/.venv/bin/python scripts/avaliar_kb.py --group regressao --group novo
backend/.venv/bin/python scripts/avaliar_kb.py --group limite-integracao
backend/.venv/bin/python scripts/avaliar_kb.py --output /tmp/kb-resultados.json
```

O primeiro comando termina com código 0 nesta versão. Os restantes terminam com código 1 devido às duas falhas documentadas. O avaliador não altera a KB e não oculta falhas. Pode usar `--kb` para avaliar outro diretório e `--cases` para um conjunto diferente de perguntas.

## Passagem à equipa

1. Revisão cruzada dos quatro conteúdos novos, com prioridade às duas fontes da AT.
2. Backend/RAG: decidir como tratar perguntas com várias jornadas e verificar ausência de cotações atuais na resposta.
3. Donos dos conteúdos antigos: rever URL de TAEG e contextualização temporal dos números de IRS Jovem. Equipa de casos de uso: avaliar os pontos de comportamento da tabela acima com o agente real.

Publicação desta segunda entrega ainda não autorizada. O PR #12 publicado contém a primeira entrega; os novos conteúdos, o avaliador e este relatório estão apenas na branch local até nova confirmação.
