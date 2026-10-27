# Contributo do João — base de conhecimento

Estado em 27/10/2026: quatro fontes acrescentadas na branch `joao/kb`, com formato e pesquisa local verificados. Branch publicada e [PR #12](https://github.com/luislamy/ainnovation-hackathon-2026/pull/12) aberto após autorização do João. Revisão cruzada por outra ferramenta pendente.

## Âmbito e fontes

Conteúdo educativo em PT-PT, reescrito a partir das páginas do Banco de Portugal consultadas em 27/10/2026. Cada ficheiro contém quatro secções autónomas e os campos exigidos por `docs/KB_CONTRACT.md`.

| Ficheiro em `backend/kb/` | Jornada | Fonte exata | Utilidade |
| --- | --- | --- | --- |
| `bdp-cartoes-debito-credito.md` | credito | [Tipos de cartões](https://clientebancario.bportugal.pt/pt-pt/o-que-sao-e-tipos-de-cartoes) | Débito/crédito, pagamento parcial e cash advance |
| `bdp-extratos-saldos.md` | salario | [Extratos e saldos](https://clientebancario.bportugal.pt/pt-pt/extratos-e-saldos) | Ler movimentos e custos; apoio ao UC-04 |
| `bdp-fin-credito-consumidores.md` | credito | [Como contratar crédito ao consumo](https://clientebancario.bportugal.pt/pt-pt/como-contratar) | Informação pré-contratual; apoio ao UC-05 |
| `bdp-prevencao-incumprimento.md` | credito | [Prevenção do incumprimento](https://clientebancario.bportugal.pt/pt-pt/prevencao-do-incumprimento) | Encaminhamento para o banco; apoio ao UC-11 |

Os conteúdos complementam os cinco ficheiros já integrados em `main` e os cinco novos ficheiros do PR #10 (`aless/kb2`). Não foram alterados os ficheiros de conteúdo de outros autores nem o pipeline.

## Verificação executada

Ambiente: Python de `backend/.venv`, classe `RAG` do projeto, `use_embeddings=False`. Sem chamadas ao LLM, sem leitura de valores de segredos e sem instalação de dependências.

- Campos obrigatórios preenchidos, URL de página específica, data de recolha e jornada válidas: quatro ficheiros aprovados.
- Carregamento pelo `load_kb` real: dezasseis novos chunks, quatro por ficheiro; todos abaixo de 1200 caracteres incluindo o cabeçalho.
- Corpus local: nove ficheiros, 35 chunks; fonte esperada encontrada entre os cinco primeiros resultados em oito de oito perguntas.
- Simulação de integração em pasta temporária, adicionando apenas os ficheiros novos do PR #10: catorze ficheiros, 52 chunks; oito de oito perguntas novas e cinco de cinco perguntas de regressão passaram. A branch desse PR não foi modificada.
- `git diff --check`: sem erros.

| Pergunta testada | Jornada | Ficheiro esperado | Hit@5 local e com PR #10 |
| --- | --- | --- | --- |
| Qual é a diferença entre um cartão de débito e de crédito? | credito | `bdp-cartoes-debito-credito.md` | Passou |
| Se pagar só parte do cartão de crédito, pago juros? | credito | `bdp-cartoes-debito-credito.md` | Passou |
| O que é cash advance? | credito | `bdp-cartoes-debito-credito.md` | Passou |
| Qual é a diferença entre saldo disponível e saldo contabilístico? | salario | `bdp-extratos-saldos.md` | Passou |
| Como consultar os movimentos e as comissões da conta? | salario | `bdp-extratos-saldos.md` | Passou |
| O que é a FIN de um crédito ao consumo? | credito | `bdp-fin-credito-consumidores.md` | Passou |
| Que produtos associados devo verificar na proposta de crédito? | credito | `bdp-fin-credito-consumidores.md` | Passou |
| Não vou conseguir pagar a prestação. O que é o PARI? | credito | `bdp-prevencao-incumprimento.md` | Passou |

Regressão no corpus combinado: orçamento mensal, juros simples/compostos, TAEG, elegibilidade do IRS Jovem e burla MB WAY numa venda online. Em cada pergunta, o ficheiro correspondente continuou a surgir nos cinco primeiros resultados. Isto verifica pesquisa, não a correção factual desses conteúdos existentes.

## Limites e próximos passos

- Os resultados medem pesquisa BM25 de ficheiros, não respostas finais, pertinência de cada chunk ou citações produzidas pelo modelo. Embeddings e conversa ponta a ponta não foram testados.
- As perguntas são uma amostra de verificação manual, não uma avaliação representativa de todas as formulações possíveis.
- O filtro atual admite apenas a jornada pedida e `geral`. Por isso, perguntas sobre cartões encaminhadas para `salario` não recuperam o novo ficheiro de `credito`; a seleção da jornada continua a ser responsabilidade da integração.
- A cobertura acima apoia partes dos casos de uso; não certifica a aprovação integral desses casos.
- Observações sobre conteúdo existente, sem alterações: `bdp-taeg.md` cita a página inicial em vez da página específica; o ficheiro de IRS Jovem contém valores fiscais que precisam de confirmação oficial e período explícito antes da demo.
- Próximo passo: revisão cruzada do PR #12 pela equipa; integração em `main` apenas após decisão do grupo.
