# Caixa Explica — Métricas do projeto

AInnovation Hackathon 2026 · medido a 27/10/2026, 14:31 (Lisboa), no `main` (`f7883cd`). Pontos fracos reverificados às 14:34: o `main` não mudou.

Cada número aqui é **MEDIDO** (corrido por nós) ou **LIDO** (fonte + data). Nada é estimado.

---

## 1. Resumo para o júri

| Métrica | Valor | Alvo | |
|---|---|---|---|
| Respostas com fonte oficial citada | **100%** | 100% | ✅ |
| Números inventados pelo modelo | **0** | 0 | ✅ |
| Guardrails e proteção de dados a funcionar | **100%** | 100% | ✅ |
| Pede contexto quando faltam dados (e só então) | **100%** | 100% | ✅ |
| Respostas com próximo passo concreto | **100%** | ≥ 90% | ✅ |
| Calculadora certa com valores certos | **95,2%** | 100% | ❌ (1 caso instável) |
| Tempo até ao 1.º texto (mediana) | **3,0 s** | < 5 s | ✅ |
| Testes automáticos do backend | **188/188** | todos | ✅ |
| Avaliações deterministas por caso de uso | **16/16** | todas | ✅ |
| Fontes oficiais na base de conhecimento | **79%** (27/34 páginas) | — | |

---

## 2. Porque estas métricas: o que se pede

O desafio pede **um assistente de literacia financeira para jovens**. O pitch é avaliado em cinco blocos (Problema 15%, Sistema 20%, Demo 30%, Técnica 20%, Fecho 15%). Num assistente financeiro, uma resposta errada ou inventada é pior do que nenhuma resposta, por isso escolhemos métricas que provam **confiança, segurança e utilidade**, e não só que "funciona".

| O que se pede | Risco se falhar | Métricas que o provam |
|---|---|---|
| **Literacia financeira**: ensinar conceitos corretos | Ensinar um conceito errado | Fonte citada 100%, números inventados 0, KB com 79% de fontes oficiais |
| **Contas certas** (crédito, poupança, juros) | Um jovem decide com uma prestação errada | Calculadora certa 95,2%, 16/16 evals, 188 testes |
| **Para jovens**: proteger quem tem menos experiência | Burlas, dados pessoais expostos, conselhos de investimento | Guardrails e PII 100% |
| **Assistente útil**, não uma enciclopédia | Respostas genéricas que não ajudam a decidir | Próximo passo 100%, pede contexto 100% |
| **Experiência** adequada a jovens | Abandono se a resposta demorar | 1.º texto em 3,0 s |
| **Demo estável** (30% da nota) | Falhar ao vivo | Harness em 24 casos, 7 corridas de melhoria |

---

## 3. Qualidade das respostas (harness)

**Como se mede:** `scripts/harness.py` corre 24 perguntas reais (os casos de uso e o guião da demo) contra a API a funcionar e verifica cada resposta automaticamente. Última corrida: 14:17, modelo `gpt-6-luna`.

| Métrica | Valor | Alvo | Porque é pertinente |
|---|---|---|---|
| **Respostas com fonte citada** | 100% | 100% | Quem lê pode confirmar tudo na fonte oficial. É a diferença entre um assistente de confiança e um chatbot genérico. |
| **Números inventados** | 0 | 0 | Num tema financeiro, um número inventado (uma taxa, um limite) pode levar a uma má decisão. Tem de ser zero. |
| **Calculadora certa e valores certos** | 95,2% | 100% | O LLM não faz contas: prestações, juros e poupança vêm de código testado. A falha é o caso do primeiro salário, que nalgumas corridas não chama a calculadora do orçamento. |
| **Guardrails e PII** | 100% | 100% | Não recomenda produtos (recomendação de investimento é regulada pela CMVM), recusa agir em nome do utilizador e tapa NIF e IBAN antes de chegarem ao modelo. |
| **Pede contexto quando faltam dados** | 100% | 100% | Um plano de poupança sem prazo nem valor seria genérico. O agente pergunta, mas só quando é preciso, para não irritar. |
| **Próximo passo** | 100% | ≥ 90% | Literacia financeira é passar à ação: cada resposta termina com uma coisa concreta para fazer. |
| **Tempo até ao 1.º texto (mediana)** | 3,0 s | < 5 s | Os jovens desistem de respostas lentas; o texto começa a aparecer em streaming. |
| **Tempo total (p95)** | 6,8 s | informativo | Mesmo as respostas com calculadora ficam abaixo de 7 s. |

**Evolução em 7 corridas** (mostra método, não sorte):

| Corrida | Fonte citada | Números inventados | Calculadora | Pede contexto |
|---|---|---|---|---|
| 1 (antes das correções) | 85% | 0 | 94% | — |
| 3 (juiz de completude) | 91% | 0 | 95% | 80% |
| 5 | 91% | 1 | 100% | 100% |
| **7 (atual)** | **100%** | **0** | 95% | **100%** |

O harness apanhou dois casos em que o modelo fazia contas de cabeça (a regra 50/30/20 e a taxa de esforço). As duas contas passaram para Python.

---

## 4. Engenharia e fiabilidade

| Métrica | Valor | Como se mede | Porque é pertinente |
|---|---|---|---|
| **Testes do backend** | 188/188 | `pytest` em `backend/tests` (calculadoras, API, guardrails, privacidade, juiz, KB) | Garante que as contas e as proteções não se partem quando alguém muda o código. |
| **Avaliações deterministas** | 16/16 | `scripts/avaliar_pipeline.py` (calculadoras, guardrails e máscara por caso de uso, sem LLM) | Prova a parte do sistema que **não** depende do modelo: as contas e as regras dão sempre o mesmo resultado. |
| **Pesquisa na KB (retrieval)** | 24/24 | `scripts/avaliar_kb.py`: a página certa aparece nas 5 primeiras | Se a pesquisa não encontra a fonte, o modelo não a pode citar. |
| Limites conhecidos da pesquisa | 0/2 | perguntas que misturam duas jornadas (ex.: IRS + Euribor) | Mostramos também o que falha: é um limite assumido, não escondido. |

---

## 5. Base de conhecimento e fontes

| Métrica | Valor | Porque é pertinente |
|---|---|---|
| Páginas | 34 (117 secções) | Cobertura dos temas que os jovens enfrentam: crédito, salário, IRS, burlas, poupança. |
| Jornadas | 6: crédito 10, poupança 6, geral 6, salário 5, IRS 4, burlas 3 | O agente responde dentro de um percurso guiado, não com perguntas soltas. |
| **Fontes oficiais** | **79%** (Banco de Portugal, BCE, Autoridade Tributária, gov.pt, Todos Contam/CMVM) | O resto é CGD (Saldo Positivo) e DECO. Todas portuguesas. |
| Valores numéricos com período | 40/40 | Taxas e limites mudam: cada valor diz a que trimestre ou ano se refere. |
| Citações confirmadas (auditoria das 13:45, 25 páginas) | 72% (18/25); 5 links a corrigir | Abrimos cada link para confirmar que existe e diz o que a página afirma. |
| Valores confirmados (mesma auditoria) | 78% (31/40) | Inclui TAEG máxima do T4 2026 (18,5%) e teto do IRS Jovem 2026 (29 542,15 €). |
| Casos de uso com apoio na KB | 19/21 | Os 2 restantes (pedido vago, resumo final) são comportamento do agente, não precisam de KB. |

---

## 6. O problema em números (contexto para o pitch)

**LIDO:** Banco de Portugal, *Boletim Económico* de março de 2026, "Um retrato da literacia financeira em Portugal" (inquérito a 1 510 adultos em 2023; PISA 2022 com 4 075 alunos de 15 anos). Valores lidos em notícias que citam o Boletim (Jornal Económico, Sábado, Forbes, março de 2026). Confirmar no PDF antes do slide.

| Estatística | Valor | Porque é pertinente |
|---|---|---|
| Adultos com o nível essencial de conhecimentos financeiros | **13%** (zona euro: 17,9%) | Mostra que o problema é real e maior do que na média europeia. |
| Acertam juros simples **e** compostos | **25%** | É exatamente o que as nossas calculadoras explicam. |
| Calculam bem 100 € a 2% ao ano | **40%** | Contas simples falham: daí as calculadoras com o pressuposto explicado. |
| Pouparam no último ano | **54,8%**, e cerca de 60% deixam tudo na conta à ordem ou em casa | Justifica as jornadas de poupança e de taxa real. |
| Jovens de 15 anos abaixo do nível básico | **15,5%** (só 6,6% no topo) | O problema começa cedo e chega ao primeiro salário. |
| Jovens sem competências básicas que acham que gerem bem o dinheiro | **74%** | Excesso de confiança: daí as perguntas de contexto e os alertas de burla. |
| Faixa com melhores resultados | **30–59 anos** | Os mais novos ficam atrás: justifica o público 18–35. |

---

## 7. Pontos fracos: estado às 14:34

Verificado depois do último pull. **Nenhum foi tratado ainda.**

| Ponto fraco | Estado | Dono | Correção (se houver tempo) |
|---|---|---|---|
| Calculadora a 95,2%: o caso do primeiro salário nem sempre chama o orçamento | ❌ por tratar | Lamy | Não mexer antes das 14:40; na demo, não usar essa pergunta |
| 🔴 MB WAY: frase "os bancos não assumem a responsabilidade" | ❌ por tratar | Aless | "Podes não ser reembolsado, mas reclama sempre no banco e no Portal do Cliente Bancário" |
| Fundo de emergência: "seis salários" contra "3 a 6 meses de despesas" do UC-03 | ❌ por tratar | Aless | Trocar para "3 a 6 meses de despesas fixas" |
| 5 links partidos ou genéricos (`bdp-taeg`, `saldopositivo-irs-jovem`, `deco-compre-agora-pague-depois`, 2 PDFs Todos Contam) | ❌ por tratar | Lamy, Aless | Links corretos em `docs/KB_RESUMO.md` §5 |
| `bdp-central-responsabilidades-credito` cita a página em inglês | ❌ por tratar | Aless | Usar a versão `/pt-pt/` |
| Rodapé só diz "Informação educativa, não é aconselhamento financeiro" (não avisa que pode ter erros) | ❌ por tratar | Lamy | Acrescentar "Pode conter erros: confirma sempre na fonte oficial." |
| Perguntas com duas jornadas (0/2) | ❌ limite assumido | Lamy | Não usar na demo; fica para depois do hackathon |

Só o rodapé e as frases da KB são alterações de texto, com baixo risco. Tudo o resto fica como limite assumido.

---

## 8. Limites destas métricas (dizer antes que o júri pergunte)

- O harness tem **24 casos**: é um teste de regressão, não uma estimativa de precisão em produção.
- O modelo **varia entre corridas**: o caso do primeiro salário passa nalgumas e falha noutras. Convém correr o harness mais de uma vez.
- A pesquisa foi medida só com **BM25**; com embeddings não foi medida à parte.
- A auditoria das citações foi feita às 13:45 sobre 25 páginas; as 9 páginas novas (inflação, glossário, depósitos) não foram auditadas link a link.
- Os valores que mudam (taxas máximas até 31/12/2026, IRS Jovem e IAS de 2026) têm de ser revistos depois desta data.

---

## 9. Como reproduzir

Na raiz do repositório:

```bash
cd backend && python3 -m pytest -q          # 188 testes
cd .. && python3 scripts/avaliar_pipeline.py  # 16 avaliações deterministas
python3 scripts/avaliar_kb.py                 # pesquisa na KB
python3 scripts/harness.py                    # 24 casos contra a API (precisa da API a correr e da chave do LLM)
```

Detalhe: `docs/HARNESS.md` (harness), `docs/KB_RESUMO.md` (base de conhecimento), `docs/KB_COBERTURA_JOAO.md` (casos de uso).
