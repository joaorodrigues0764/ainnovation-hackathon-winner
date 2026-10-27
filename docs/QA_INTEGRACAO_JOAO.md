# Verificação da integração — João / Codex

27/10/2026, 13:40 Lisboa. Versão testada: `a3cf2a9` (inclui PRs #12 e #15). Corpus: 25 ficheiros, 91 chunks. Nenhuma alteração ao código de colegas.

## Resultado medido

| Verificação | Resultado | Limite |
| --- | --- | --- |
| Instalação do frontend | `npm ci --ignore-scripts`: concluída, 364 pacotes | Primeira tentativa anterior falhou por timeout de rede |
| Backend | 82 testes passaram em 1,02 s | Suite usa LLM falso; a execução no isolamento ficou presa no primeiro teste da API; fora dele passou |
| Frontend: lint | `npm run lint`: passou | Não é uma verificação visual |
| Frontend: tipos | `npx tsc --noEmit`: passou após iniciar o Next.js | Antes de gerar os tipos, falhou por `LayoutProps` inexistente |
| Frontend: build | Não concluído neste ambiente | Primeira tentativa: download de fontes bloqueado; repetição com acesso escalado: Turbopack falhou ao criar processo/abrir porta (`Operation not permitted`) |
| Pesquisa BM25 | 24/26 casos passaram | Duas falhas entre jornadas continuam reproduzíveis |
| Interface no browser | Quatro percursos concluídos; resposta e fontes visíveis; consola sem erros | Respostas simuladas, sem avaliação do modelo real |

Dependências locais da API e dos testes instaladas na `.venv`: FastAPI, Uvicorn, pytest e HTTPX. Não foram alterados os ficheiros de dependências do projeto.

O erro do build não demonstra uma falha funcional do código; também não permite declarar o build de produção aprovado. Deve ser repetido no ambiente habitual do responsável pelo frontend. A interface foi efetivamente aberta e testada com o servidor de desenvolvimento.

## Percursos observados na interface

Frontend real em `localhost:3000`; API real em `localhost:8000`, com substituição temporária do cliente LLM por uma simulação em `/tmp/qa_api_joao.py`. Pesquisa BM25 e calculadoras do repositório reais. A simulação está identificada como `SIMULADO-QA-sem-servico-externo`, e todas as respostas mostram `[TESTE SIMULADO]`. Não houve chamadas a um serviço de modelo externo nem utilização de credenciais para essas chamadas.

| Cenário fictício | Observação no browser |
| --- | --- |
| Orçamento: primeiro salário de 900 € | `orcamento` executado; 450/270/180 € no resultado Python e na resposta; fonte apresentada; estado `done` |
| Crédito: 1000 €, TAN 12%, 24 meses | `custo_credito` recebeu taxa `0.12`; prestação 47,07 €, total 1129,76 € e juros 129,76 €; pressupostos e fonte visíveis; estado `done` |
| IRS Jovem e deduções à coleta | Chunks das fontes oficiais da AT recuperados; resposta e ligação de fonte apresentadas; sem calculadora; estado `done` |
| Burla MB WAY | Fonte específica recuperada; texto simulado de alerta e ligação apresentados; sem calculadora; estado `done` |

Entre cenários, «Nova conversa» limpou as trocas; o inspetor mostrou histórico enviado com zero mensagens. Foram usados os modos Utilizador e Verboso. Não apareceram erros ou avisos na consola do browser durante estes percursos.

**O teste demonstra o transporte, apresentação e execução de ferramentas na UI.** As respostas do guião foram escritas para o teste: não provam escolha correta das ferramentas pelo modelo, qualidade das respostas, segurança das recusas ou suporte factual de cada citação. Esses pontos continuam a precisar de teste com o fornecedor real e autorização para usar as credenciais.

Provas visuais locais: `/tmp/qa-credito-joao.png`, `/tmp/qa-irs-joao.png` e `/tmp/qa-burlas-joao.png`. A simulação vive apenas em `/tmp`, fora do código da aplicação.

## Dois exemplos para o Lamy

O filtro de `backend/rag.py:197` admite a jornada pedida e `geral`. Assim, com `journey="irs"`, o conteúdo `bdp-euribor-spread.md` (`credito`) fica excluído.

1. **Pergunta:** «Quanto está hoje a Euribor?»; jornada `irs`. Resultado: o ficheiro da Euribor não surge. O objetivo é recuperar o conceito e a ausência de cotação atual na KB, não inventar a taxa do dia.
2. **Pergunta:** «O que é o IRS Jovem e que relação tem a Euribor com a prestação da casa?»; jornada `irs`. Resultado: fontes de IRS Jovem presentes, fonte da Euribor ausente. O pedido tem dois temas.

Em ambos os exemplos, repetir a pesquisa com `journey=None` recuperou `bdp-euribor-spread.md`; no segundo, recuperou também `at-irs-jovem-conceito.md`. Isto é uma observação em dois exemplos, não uma validação geral de remover o filtro. A decisão sobre deteção de temas, pesquisa em várias jornadas ou outro comportamento cabe ao responsável pelo RAG.

Reprodução, na raiz do projeto:

```bash
backend/.venv/bin/python scripts/avaliar_kb.py --group limite-integracao
```

O comando termina com código 1 e identifica `euribor-jornada-irs` e `duas-jornadas`. Para os outros casos:

```bash
backend/.venv/bin/python scripts/avaliar_kb.py --group regressao --group novo
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 backend/.venv/bin/python -m pytest backend/tests -q
```

## Revisão cruzada ainda necessária

O aviso do Alessandro no [canal dos agentes](https://github.com/luislamy/ainnovation-hackathon-2026/issues/8#issuecomment-6442441187) refere explicitamente quatro ficheiros do PR #12. Não há uma confirmação explícita de revisão dos quatro conteúdos finais: `at-deducoes-coleta.md`, `at-irs-jovem-conceito.md`, `bdp-euribor-spread.md` e `bdp-comissoes-contas.md`. As fontes e datas de consulta estão em `docs/KB_COBERTURA_JOAO.md`; a revisão independente continua pendente.

## Mensagem preparada para o canal (não enviada)

> [João/Codex] KB integrada: 25 ficheiros/91 chunks; 82 testes backend passam; 4 percursos UI com LLM simulado concluídos. Pesquisa: 24/26; `journey=irs` exclui Euribor em duas perguntas reproduzíveis. Lamy: avaliar tratamento de vários temas; Aless: confirmar revisão dos quatro conteúdos finais do PR #12. Detalhes: `docs/QA_INTEGRACAO_JOAO.md` e `scripts/avaliar_kb.py --group limite-integracao`.
