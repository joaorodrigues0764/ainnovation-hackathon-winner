# Guião de pitch — Caixa Explica (proposta, a ajustar pela equipa)

Duração total: **POR VERIFICAR** (confirmar com a organização). Abaixo, a divisão por peso: Problema 15% · Sistema 20% · Demo 30% · Técnica 20% · Fecho 15%.

| # | Bloco | Quem (proposta) | Mensagem-chave |
|---|---|---|---|
| 1 | Problema | Simone | Jovens decidem o primeiro crédito, salário, IRS e poupança sem fontes fiáveis, e são alvo de burlas. |
| 2 | Sistema | Guilherme | Assistente que responde só com fontes oficiais citadas [n] (BdP, Portal do Cliente Bancário, DECO, Segurança Social, AT) e encaminha, sem recomendar produtos. |
| 3 | Demo | Aless | Três perguntas ao vivo (abaixo). Resposta curta: resposta direta, explicação, próximo passo. |
| 4 | Técnica | Lamy | RAG (BM25 + embeddings, filtro por jornada), calculadoras em código (o LLM não faz contas), guardrails, máscara de dados pessoais, avaliações automáticas. |
| 5 | Fecho | João | Limites assumidos, próximos passos, pedido à CGD. |

## Demo (ordem sugerida, todas já testadas)
1. **Calcular:** "Vale a pena pedir crédito para um carro de 8 000 € a 9% em 48 meses?" → mostra o cartão de resultado (número vem da calculadora, não do modelo).
2. **Fontes:** "Qual a diferença entre TAEG e TAN?" → mostrar as citações [n] e abrir uma fonte.
3. **Segurança/limite:** "Recebi um SMS do banco a pedir o código, o que faço?" → resposta de burla; depois "Qual é a Euribor hoje?" → o assistente não inventa valores atuais e encaminha para a fonte.
4. (Se sobrar tempo) ditado por voz no botão 🎤 e o aviso "Assistente de IA, pode errar".

## Técnica: factos que se podem dizer (medidos)
- Avaliações deterministas: **16/16 OK** (`scripts/avaliar_pipeline.py`).
- Testes backend: **185 passam** na última execução local.
- Taxas aceitam 0.12, 12 ou "12%" (parser universal).
- Cada resposta cita fontes; sem fonte, não afirma.

## Fecho: limites a dizer abertamente
- É uma IA e pode errar; não substitui aconselhamento financeiro, fiscal ou jurídico.
- Valores atuais (Euribor, taxas) não são dados pelo assistente; remete para BdP/AT.
- IRS Jovem: valores **POR VERIFICAR** na fonte oficial antes de os afirmar.
- Ditado por voz usa o serviço do browser (no Chrome, áudio vai para a Google): não ditar dados pessoais.
- Próximos passos: mais fontes oficiais, avaliação com LLM real e validação com jovens.

## Antes de subir ao palco (checklist)
- [ ] `git pull` e API a correr; um ensaio completo das 3 perguntas.
- [ ] Botão de voz testado no Chrome do portátil da demo.
- [ ] Números do slide iguais aos desta página (ou atualizados com medição nova).
- [ ] Plano B se a rede falhar: capturas de ecrã das 3 respostas.
