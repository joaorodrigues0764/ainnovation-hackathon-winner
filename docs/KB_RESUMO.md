# Knowledge Base — FinJovem (AInnovation Hackathon 2026)

Estado medido a 27/10/2026, 13:50 (Lisboa), no `main` do repositório (`feb8c2a`, depois do merge do PR #15).

---

## 1. Em 30 segundos

A Knowledge Base (KB) é a memória de factos do agente. Quando um jovem faz uma pergunta, o pipeline RAG procura na KB as secções mais relevantes, entrega-as ao LLM e o LLM responde **com base nesses textos, citando o link oficial de onde vieram**.

| | |
|---|---|
| **Páginas** | 25 |
| **Secções (chunks)** | 91 |
| **Texto** | cerca de 5 200 palavras, todas em PT-PT e reescritas por nós |
| **Jornadas** | 6 (crédito, salário, IRS, burlas, poupança, geral) |
| **Fontes oficiais** | 19 de 25 páginas (76%) |
| **Valores numéricos** | 40 menções, todas com período e sem contradições; **78% confirmados** na fonte (31/40) |
| **Citações (links)** | **72% confirmadas** (18/25), 8% prováveis, **20% com problema** (5/25, ver §5) |
| **Pesquisa (retrieval)** | 32 de 32 perguntas encontram a página certa no top 5 |
| **Casos de uso com apoio na KB** | 19 de 21 (os outros 2 são comportamento do agente, não precisam de KB) |

---

## 2. Como funciona

```
Pergunta do jovem
   → máscara de dados pessoais (privacy.py)
   → RAG: procura híbrida BM25 + embeddings, filtrada pela jornada (+ "geral")
   → top 5 secções da KB + resultados das calculadoras
   → LLM explica em linguagem simples e cita o `url` da página
```

Regras de ouro do desenho:

- **A KB explica, o código calcula.** Valores como "TAEG máxima 18,5%" vivem na KB. Prestações, juros e poupanças são calculados em `backend/calculators.py`, nunca pelo LLM.
- **Cada secção faz sentido sozinha**, porque é cortada e recuperada isoladamente.
- **Cada página tem `url` exato**, que é o que aparece citado na resposta ao jovem.
- **Números sempre com período** (ex.: "no 4.º trimestre de 2026"), porque taxas e limites mudam.

Formato de cada página (`docs/KB_CONTRACT.md`):

```markdown
---
title: Taxas máximas (TAEG) no crédito aos consumidores — 4.º trimestre de 2026
source: Portal do Cliente Bancário (Banco de Portugal)
url: https://clientebancario.bportugal.pt/pt-pt/taxas-de-juro-no-credito-aos-consumidores
journey: credito
collected: 2026-10-27
---
## Cartões de crédito e descobertos (4.º trimestre de 2026)
...
```

---

## 3. Números da KB

### Por jornada

| Jornada | Páginas | Temas |
|---|---|---|
| crédito | 8 | TAEG, taxas máximas, FIN, cartões, Euribor/spread, BNPL, prevenção do incumprimento, PERSI/RACE |
| salário | 5 | começar a trabalhar, bruto vs líquido, extratos e saldos, orçamento, serviços mínimos bancários |
| IRS | 4 | IRS Jovem (conceito, regras 2026, elegibilidade), deduções à coleta |
| burlas | 3 | burla MB WAY, segurança online, fraude em investimentos/cripto (CMVM) |
| geral | 3 | cartão roubado/fraude, comissões das contas, seguros (prémio e franquia) |
| poupança | 2 | fundo de emergência, juros simples e compostos |

### Por tipo de fonte

| Tipo | Páginas | Fontes |
|---|---|---|
| **Oficial** | 19 (76%) | Banco de Portugal / Portal do Cliente Bancário (12), Todos Contam / CMVM (4), Autoridade Tributária (2), gov.pt (1) |
| Banco público (CGD, Saldo Positivo) | 4 (16%) | seguros, MB WAY, IRS Jovem (antigo), bruto vs líquido (com Segurança Social e PwC) |
| Associação de consumidores (DECO) | 2 (8%) | BNPL, fundo de emergência |

Todas as fontes são portuguesas. Não há valores de outros países na KB.

### Por autor

| Autor | Páginas |
|---|---|
| João | 8 |
| Aless (com Claude) | 8 |
| Gummi | 7 |
| Lamy | 2 |

---

## 4. Valores-chave verificados

Todos LIDOS em fonte oficial a 27/10/2026.

| Valor | Período | Fonte | Página |
|---|---|---|---|
| TAEG máxima cartões de crédito e descobertos: **18,5%** | 4.º trimestre 2026 | Banco de Portugal | `bdp-taxas-maximas-credito` |
| TAEG máxima crédito pessoal: **15,0%** (8,2% educação, saúde, energia) | 4.º trimestre 2026 | Banco de Portugal | `bdp-taxas-maximas-credito` |
| TAEG máxima crédito automóvel: **5,4% a 14,3%** | 4.º trimestre 2026 | Banco de Portugal | `bdp-taxas-maximas-credito` |
| IRS Jovem: isenção **100% / 75% / 50% / 25%**, até aos 35 anos, máx. 10 anos | 2026 | gov.pt | `gov-irs-jovem-2026` |
| Teto do IRS Jovem: **29 542,15 €** (= 55 × IAS) | rendimentos de 2026 | Portal das Finanças (Newsletter AT n.º 39) | `gov-irs-jovem-2026` |
| IAS: **537,13 €** | 2026 | Portal das Finanças + Governo | `gov-irs-jovem-2026` |
| Serviços mínimos bancários: máx. **5,37 €/ano** (1% do IAS) | 2026 | Banco de Portugal | `bdp-servicos-minimos-bancarios` |
| Cartão usado sem autorização: perdes no máx. **50 €** antes de avisar o banco | regra em vigor 2026 | Banco de Portugal | `bdp-cartoes-fraude-direitos` |
| Prazo para pedir correção de movimento: **13 meses** | regra em vigor 2026 | Banco de Portugal | `bdp-cartoes-fraude-direitos` |
| Segurança Social: trabalhador **11%**, empresa 23,75% (total 34,75%) | 2025–2026 | Segurança Social, PwC | `ss-descontos-salario-bruto-liquido` |

**A rever se a demo for repetida mais tarde:** as taxas máximas mudam a 1 de janeiro de 2027; as regras do IRS Jovem mudam com o Orçamento do Estado de cada ano.

---

## 5. Qualidade medida

### Pesquisa (retrieval, BM25, sem embeddings)

| Teste | Resultado |
|---|---|
| Regressão de temas antigos (`scripts/avaliar_kb.py`) | 12/12 |
| Temas novos do João | 12/12 |
| Temas novos do Gummi (taxas máximas, IRS Jovem 2026, PERSI, cartão roubado, conta barata, cripto, primeiro emprego) | 8/8 |
| **Total** | **32/32** encontram a página certa no top 5 |
| Perguntas que misturam duas jornadas (ex.: IRS + Euribor) | 0/2, limitação conhecida do filtro por jornada |

Isto mede se a página certa é encontrada, não se a resposta final do agente está correta. A resposta final testa-se com `docs/AVALIACAO.md`.

### Auditoria das citações (27/10/2026, 13:45)

Abri o `url` de cada página. Quando o site bloqueava a leitura direta, confirmei por pesquisa que o endereço exato existe.

| Resultado | Páginas | % |
|---|---|---|
| ✅ Link certo e conteúdo confirma o que a página diz | 13 | 52% |
| ✅ Link exato confirmado (conteúdo não relido) | 5 | 20% |
| ⚠️ Provável, não confirmado | 2 | 8% |
| ❌ Link com problema | 5 | 20% |
| **Total utilizável com confiança** | **18 de 25** | **72%** |

✅ Confirmadas com conteúdo: `bdp-taxas-maximas-credito`, `bdp-cartoes-fraude-direitos`, `bdp-servicos-minimos-bancarios`, `bdp-persi-rede-apoio`, `gov-irs-jovem-2026`, `todoscontam-comecar-trabalhar`, `cmvm-fraude-investimentos`, `bdp-comissoes-contas`, `bdp-euribor-spread`, `bdp-extratos-saldos`, `bdp-fin-credito-consumidores`, `bdp-prevencao-incumprimento`, `bdp-cartoes-debito-credito`.

✅ Link exato confirmado: `at-deducoes-coleta`, `cgd-seguros-franquia-premio`, `mbway-burla-venda-online`, `ss-descontos-salario-bruto-liquido`, `deco-fundo-emergencia`.

⚠️ Prováveis: `at-irs-jovem-conceito` (o padrão do endereço do Código do IRS existe, mas não consegui abrir o artigo 12.º-B) e `bdp-burlas-seguranca-online` (a brochura existe, mas o PDF citado é de 2022-03 e o BdP já publicou uma versão de 2026-09).

❌ Com problema:

| Página | Problema | Correção proposta |
|---|---|---|
| `bdp-taeg` | Link é a página inicial do BdP, não a do tema | `https://clientebancario.bportugal.pt/pt-pt/como-contratar` (fala de TAN, TAEG e MTIC) |
| `saldopositivo-irs-jovem` | O endereço não aparece no site da CGD | `https://www.cgd.pt/Site/Saldo-Positivo/leis-e-impostos/Pages/guia-preencher-irs-jovem.aspx` |
| `deco-compre-agora-pague-depois` | Caminho errado (`orcamento-familiar` em vez de `direitos-consumidor`) | `https://www.deco.proteste.pt/familia-consumo/direitos-consumidor/noticias/compre-agora-pague-depois-cautela` |
| `todoscontam-orcamento` | O ficheiro real termina em `_1.pdf` | `https://www.todoscontam.pt/sites/default/files/biblioteca/plano_de_aula_todos_contam_-_orcamento_familiar_-_3_ciclo_e_secundario_1.pdf` |
| `todoscontam-poupanca-juros` | O ficheiro mudou de pasta | `https://www.todoscontam.pt/sites/default/files/taxonomy_file/cadernoeducacaofinanceira3_1.pdf` |

### Auditoria dos valores numéricos

| Resultado | Valores | % |
|---|---|---|
| ✅ Confirmados por mim na fonte oficial (taxas máximas, IRS Jovem 2026, IAS, serviços mínimos, 50 €, 13 meses) | 18 | 45% |
| ✅ Iguais a um valor já confirmado (percentagens do IRS Jovem na página antiga) | 4 | 10% |
| ✅ Exemplos de cálculo com aritmética certa (seguros: 1 500 − 300 = 1 200 €, 10% de 2 000 = 200 €) | 9 | 22,5% |
| ⚠️ Lidos pelo autor, não reconfirmados por mim (Segurança Social 11% / 23,75% / 34,75%; a aritmética do exemplo está certa) | 7 | 17,5% |
| ❌ Desatualizados (comissões do BNPL, DECO 2022) | 2 | 5% |
| **Confirmados** | **31 de 40** | **78%** |

### Coerência

- 40 valores numéricos, todos com período.
- Nenhuma contradição entre páginas (ex.: as duas páginas de IRS Jovem dão as mesmas percentagens).
- Nenhuma página pede ou guarda dados pessoais.

---

## 6. Cobertura dos 21 casos de uso

| UC | Tema | Página(s) na KB |
|---|---|---|
| 01 | Poupar para um objetivo | `todoscontam-poupanca-juros`, `todoscontam-orcamento` + calculadora |
| 02 | Primeiro salário (50/30/20) | `todoscontam-orcamento`, `todoscontam-comecar-trabalhar` + calculadora |
| 03 | Fundo de emergência | `deco-fundo-emergencia` |
| 04 | Gastos invisíveis | `bdp-extratos-saldos`, `todoscontam-orcamento` |
| 05 | Crédito e TAEG | `bdp-taeg`, `bdp-fin-credito-consumidores`, `bdp-taxas-maximas-credito` + calculadora |
| 06 | Juros compostos | `todoscontam-poupanca-juros` + calculadora |
| 07 | Compre agora, pague depois | `deco-compre-agora-pague-depois` |
| 08 | Seguros (prémio, franquia) | `cgd-seguros-franquia-premio` |
| 09 | Ações / cripto (recusa) | `cmvm-fraude-investimentos` + guardrails |
| 10 | Dados pessoais | `privacy.py` (não é KB) |
| 11 | Renegociar crédito (balcão) | `bdp-prevencao-incumprimento`, `bdp-persi-rede-apoio` |
| 12 | Burla MB WAY | `mbway-burla-venda-online`, `bdp-burlas-seguranca-online`, `bdp-cartoes-fraude-direitos` |
| 13 | Crédito + IRS na mesma mensagem | `bdp-persi-rede-apoio`, `at-irs-jovem-conceito` |
| 14 | "Qual o melhor banco?" (recusa) | `bdp-comissoes-contas`, `bdp-servicos-minimos-bancarios` |
| 15 | Valores atuais (não inventar) | `bdp-taxas-maximas-credito`, `bdp-euribor-spread` |
| 16 | IRS Jovem e deduções | `gov-irs-jovem-2026`, `at-irs-jovem-conceito`, `at-deducoes-coleta` |
| 17 | Bruto vs líquido | `ss-descontos-salario-bruto-liquido`, `todoscontam-comecar-trabalhar` + calculadora |
| 18 | "Explica como se tivesse 15 anos" | `todoscontam-poupanca-juros` (o resto é tom do modelo) |
| 19–21 | Perfil, pedido vago, resumo | comportamento do agente, não precisam de KB |

---

## 7. O que mostrar a todos (pitch e demo)

### O problema, em números

Fonte original: Banco de Portugal, *Boletim Económico* de março de 2026, artigo "Um retrato da literacia financeira em Portugal" (inquérito a 1 510 adultos em 2023 e PISA 2022 com 4 075 alunos de 15 anos). Valores lidos em três notícias que citam o Boletim (Jornal Económico, Sábado, Forbes, março 2026). Confirmar no PDF do Banco de Portugal antes de pôr no slide.

| Estatística | Valor |
|---|---|
| Adultos com o nível essencial de conhecimentos financeiros | **13%** (zona euro: 17,9%) |
| Acertam juros simples **e** compostos | **25%** |
| Calculam bem o saldo de 100 € a 2% ao ano | **40%** |
| Pouparam no último ano | **54,8%**, e cerca de 60% desses deixam tudo na conta à ordem ou em casa |
| Investem em ações ou fundos | **7,3%** |
| Jovens de 15 anos abaixo do nível básico | **15,5%** (só 6,6% no nível de topo) |
| Jovens sem competências básicas que acham que gerem bem o dinheiro | **74%** |
| Faixa etária com melhores resultados | **30–59 anos**: os mais novos ficam atrás, por isso o nosso público é 18–35 |

### A frase do pitch

> 1 em cada 8 adultos portugueses tem o nível essencial de literacia financeira, e os jovens estão abaixo dos adultos de 30 a 59 anos. O FinJovem responde às perguntas reais de quem tem entre 18 e 35 anos, com os números oficiais deste trimestre e a fonte citada em cada resposta.

### O que nos diferencia

O site da CGD já tem uma assistente de IA. O que mostramos que ela não faz:

1. **Jornadas guiadas** (crédito, salário, IRS, burlas, poupança), em vez de perguntas soltas.
2. **Contas feitas com os números do próprio jovem**, por calculadoras testadas, não pelo modelo.
3. **Fontes oficiais citadas em cada resposta**, com o período do valor (ex.: "BdP, 4.º trimestre 2026").
4. **Limites claros**: não recomenda bancos nem produtos, não pede dados pessoais, encaminha para o balcão ou para entidades oficiais quando é preciso.

### Momentos para a demo (3 minutos)

| # | Pergunta para fazer ao vivo | O que mostra |
|---|---|---|
| 1 | "Quero comprar um telemóvel de 1000 € a 12% em 24 meses. Quanto pago?" | Calculadora + TAEG máxima do trimestre citada do BdP |
| 2 | "Comecei a trabalhar este ano. O IRS Jovem aplica-se a mim?" | Regras 2026, teto de 29 542,15 € e fonte oficial |
| 3 | "Um comprador pediu-me para ir ao multibanco associar o número dele ao meu MB WAY." | Deteção de burla e passos imediatos |
| 4 | "Tenho 200 €. Compro Bitcoin?" | Recusa simpática + 5 cuidados da CMVM |
| 5 | Escrever um IBAN no chat | Máscara de dados pessoais antes do LLM |

---

## 8. Limitações de âmbito

O que a KB e o agente **não** fazem, por decisão ou por falta de tempo. Convém dizê-lo no pitch antes que o júri pergunte.

### Por decisão (guardrails)

| Limite | Porquê |
|---|---|
| Não é aconselhamento financeiro: não recomenda bancos, cartões, ações, cripto nem produtos concretos | Recomendação personalizada de investimento é atividade regulada (CMVM) |
| O LLM não faz contas | Contas em `backend/calculators.py`, com testes |
| Não pede nem guarda IBAN, cartões, NIF, passwords | `privacy.py` mascara antes do LLM |
| Não age em nome do utilizador (renegociar crédito, entregar IRS) | Encaminha para o banco, a AT ou a rede RACE |
| Só Portugal | Regras, taxas e entidades são portuguesas |
| Público 18–35 | Alinhado com o IRS Jovem e a garantia pública; menores recebem respostas gerais e conselho para falar com um adulto |

### Por falta de cobertura (a KB ainda não tem)

| Tema em falta | Impacto |
|---|---|
| Habitação jovem (garantia pública 18–35, Porta 65, isenção de IMT) | Muito relevante para 18–35; nenhuma jornada o cobre |
| Escalões de IRS e tabelas de retenção | O agente só pode encaminhar para o Portal das Finanças (UC-15, UC-17) |
| Trabalho independente (recibos verdes, Segurança Social dos independentes) | Só referido de passagem |
| PPR, certificados de aforro, fundos | Só conceitos gerais |
| Euribor e cotações do dia | Sem dados em tempo real: o agente tem de dizer onde consultar |

### Limitações técnicas

- Perguntas com dois temas de jornadas diferentes (ex.: IRS + Euribor) só recuperam uma jornada (0/2 nos testes).
- Retrieval testado só com BM25; os embeddings não foram medidos.
- A KB mede-se por página encontrada, não pela qualidade da resposta final.

---

## 9. Dados que podem estar desatualizados

| Dado | Válido até | O que pode mudar |
|---|---|---|
| Taxas máximas (18,5%, 15,0%, 8,2%, automóvel) | **31/12/2026** | O BdP publica novos limites para o 1.º trimestre de 2027 em dezembro |
| IRS Jovem (percentagens, teto 29 542,15 €) | rendimentos de **2026** | O Orçamento do Estado para 2027 está em discussão e pode mudar regras e teto |
| IAS 537,13 € e serviços mínimos 5,37 €/ano | **2026** | O IAS é atualizado todos os anos em janeiro |
| Segurança Social 11% / 23,75% | 2025–2026 | Estável há anos, mas não reconfirmado hoje |
| BNPL (comissões 0,3%–1%) | **desatualizado** (2022) | Nova diretiva europeia do crédito ao consumo aplica-se a partir de 20/11/2026 e pode abranger o BNPL (POR VERIFICAR a transposição em Portugal) |
| Burla MB WAY | fontes de 2019 e 2021 | O mecanismo da burla mantém-se; as regras de reembolso dos bancos podem ter mudado |
| Segurança online (BdP) | brochura de 2018 | Há versão nova de 2026 |
| Orçamento e juros (Todos Contam) | materiais escolares de 2018 | Conceitos estáveis; público é mais novo que o nosso |
| Estatísticas do pitch | inquérito de 2023, PISA 2022 | Os próximos inquéritos ainda não saíram; são os dados mais recentes |

---

## 10. Riscos e pendentes

| Gravidade | Página | Problema | Dono |
|---|---|---|---|
| 🔴 alta | `mbway-burla-venda-online` | Diz que "os bancos não assumem a responsabilidade", o que pode levar a vítima a não reclamar. Deve dizer "reclama sempre no banco e no Portal do Cliente Bancário". | Aless |
| 🟠 média | `deco-fundo-emergencia` | Diz 4–6 salários, mas o UC-03 exige "3 a 6 meses de despesas fixas": o teste vai falhar. | Aless |
| 🟠 média | `deco-compre-agora-pague-depois` | Fonte única DECO de 2022; as comissões citadas estão desatualizadas. | Aless |
| 🟠 média | RAG | Perguntas com duas jornadas (ex.: IRS + Euribor) só recuperam uma (0/2 nos testes). | Lamy |
| 🟠 média | 5 links com problema | `bdp-taeg`, `saldopositivo-irs-jovem`, `deco-compre-agora-pague-depois`, `todoscontam-orcamento`, `todoscontam-poupanca-juros` (correções em §5) | Lamy, Aless |
| 🟡 baixa | `saldopositivo-irs-jovem` | Fala de teto sem dar o valor (a página `gov-irs-jovem-2026` complementa). | Lamy |
| 🟡 baixa | `todoscontam-orcamento`, `todoscontam-poupanca-juros`, `bdp-burlas-seguranca-online` | Material escolar do 3.º ciclo e brochura de 2018 | Aless |
| ❓ grupo | `USE_CASES.md` | Os UCs dizem 18–25 anos; o público decidido é 18–35. | grupo |

---

## 11. Fontes

**Oficiais usadas na KB**
- [BdP — Taxas de juro no crédito aos consumidores](https://clientebancario.bportugal.pt/pt-pt/taxas-de-juro-no-credito-aos-consumidores)
- [BdP — Direitos e deveres na utilização de cartões](https://clientebancario.bportugal.pt/pt-pt/direitos-e-deveres-na-utilizacao-de-cartoes)
- [BdP — Serviços mínimos bancários](https://clientebancario.bportugal.pt/pt-pt/o-que-sao)
- [BdP — Rede de apoio ao cliente bancário](https://clientebancario.bportugal.pt/pt-pt/rede-de-apoio-ao-cliente-bancario)
- [BdP — Novas regras na prevenção e gestão do incumprimento](https://clientebancario.bportugal.pt/pt-pt/noticias/novas-regras-na-prevencao-e-na-gestao-do-incumprimento-de-contratos-de-credito)
- [gov.pt — Pedir o IRS Jovem](https://www.gov.pt/servicos/pedir-o-irs-jovem)
- [Portal das Finanças — Newsletter AT n.º 39 (jan. 2026)](https://info.portaldasfinancas.gov.pt/pt/at/Divulgacao/publicacoes_internas/Newsletter_AT/Documents/Newsletter-39-janeiro-2026.pdf)
- [Governo — O que muda em 2026](https://www.portugal.gov.pt/pt/gc25/comunicacao/noticia?i=o-que-muda-em-2026)
- [Todos Contam — Começar a trabalhar](https://www.todoscontam.pt/pt-pt/comecar-trabalhar)
- [Todos Contam — 5 cuidados da CMVM contra a fraude digital](https://www.todoscontam.pt/pt-pt/noticias/cmvm-identifica-5-cuidados-ter-para-evitar-fraude-digital-em-investimentos-financeiros)

**Estatísticas do problema**
- [BdP — Boletim Económico, março 2026 (PDF)](https://www.bportugal.pt/sites/default/files/documents/2026-03/Boletim%20Economico_mar%C3%A7o2026.pdf)
- [Jornal Económico (16/03/2026)](https://jornaleconomico.sapo.pt/?p=1388785) · [Sábado (16/03/2026)](https://www.sabado.pt/dinheiro/detalhe/genero-escolaridade-e-rendimento-explicam-baixos-niveis-de-literacia-financeira-diz-estudo) · [Forbes Portugal (29/03/2026)](https://www.forbespt.com/?p=183347)
- [Todos Contam — Relatório do 4.º Inquérito à Literacia Financeira (2023)](https://www.todoscontam.pt/sites/default/files/2024-04/relatorio4ilf2023.pdf)

**Verificação das citações**
- [BdP — Prevenção do incumprimento](https://clientebancario.bportugal.pt/pt-pt/prevencao-do-incumprimento) · [O que são e tipos de cartões](https://clientebancario.bportugal.pt/pt-pt/o-que-sao-e-tipos-de-cartoes) · [Encargos](https://clientebancario.bportugal.pt/pt-pt/encargos) · [Taxas de juro no crédito à habitação](https://clientebancario.bportugal.pt/pt-pt/taxas-de-juro-no-credito-habitacao) · [Extratos e saldos](https://clientebancario.bportugal.pt/pt-pt/extratos-e-saldos) · [Como contratar](https://clientebancario.bportugal.pt/pt-pt/como-contratar)
- [BdP — Brochura #ficaadica (versão 2026)](https://clientebancario.bportugal.pt/en/material/5-tips-staying-safer-online-toptip)
- [AT — Deduções à coleta](https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Rendimentos/Declaracao/Deducoes_a_coleta/Paginas/default.aspx)
- [CGD — Franquia no seguro](https://www.cgd.pt/Site/Saldo-Positivo/protecao/Pages/consultorio-leitor-franquia.aspx) · [Fuja das burlas com o MB WAY](https://www.cgd.pt/Site/Saldo-Positivo/protecao/Pages/Fuja-das-burlas.aspx) · [Descontos para a Segurança Social](https://www.cgd.pt/Site/Saldo-Positivo/trabalho/Pages/descontos-seguranca-social.aspx) · [Guia IRS Jovem](https://www.cgd.pt/Site/Saldo-Positivo/leis-e-impostos/Pages/guia-preencher-irs-jovem.aspx)
- [DECO — Compras online em prestações](https://www.deco.proteste.pt/familia-consumo/direitos-consumidor/noticias/compre-agora-pague-depois-cautela) · [Fundo de emergência](https://www.deco.proteste.pt/investe/depositos-certificados/poupanca/depositos-prazo/2026/06/fundo-emergencia-quanto-guardar-onde-aplicar)
- [Todos Contam — Plano de aula orçamento familiar](https://www.todoscontam.pt/sites/default/files/biblioteca/plano_de_aula_todos_contam_-_orcamento_familiar_-_3_ciclo_e_secundario_1.pdf) · [Caderno de Educação Financeira 3](https://www.todoscontam.pt/pt-pt/caderno-de-educacao-financeira-3)

**Contexto (pitch)**
- [CGD — Saldo Positivo, ficha técnica](https://www.cgd.pt/Site/Saldo-Positivo/Pages/Saldo-Positivo-Ficha-Tecnica.aspx)
- [CGD — Literacia Financeira](https://www.cgd.pt/Sustentabilidade/Responsabilidade-Social/Pages/Literacia-Financeira.aspx)
