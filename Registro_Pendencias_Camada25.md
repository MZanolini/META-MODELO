# Registro de Pendências e Decisões Provisórias — Camada 2.5

Documento único e cumulativo. Substitui `Handoff_Adendo_Recorte2_v0_1.md`
(retirar esse arquivo do repositório real quando este for posicionado — não
faz mais sentido como documento separado).

**Não substitui** `Handoff_Curadoria_Camada25_v0_1.md` nem
`Mapa_Gap_Implementacao_Agente_Curador_v0_1.md` — esses continuam sendo a
referência de infraestrutura (commits, ambiente Cowork/FUSE, metodologia de
extração). Este documento é só o rastro de decisões pendentes e trabalho não
feito, para não precisar reler handoffs inteiros a cada sessão.

**Como usar:** duas seções, propositalmente separadas por peso cognitivo.

- **Registro de Decisões** — coisa que exige atenção e julgamento do
  consultor. Cresce devagar, cada linha some quando resolvida.
- **Checklist de Extração** — trabalho ainda não feito, sem ambiguidade.
  Só marca como feito, não exige decisão.

---

## 1. Registro de Decisões (ambiguidades genuínas e observações a decidir)

| # | Item | Tipo | Origem | Onde vive | Gatilho de revisão | Status |
|---|---|---|---|---|---|---|
| 1 | `org:ManagementDimension` | Decisão provisória | Recorte 1 (`tbox-local.ttl`, commit `820974d`) | Cabeçalho do próprio arquivo | Reconciliar quando o `gist.owl` real for importado (hoje a ontologia gist ainda não foi importada de fato) | Aberto |
| 2 | `mgmt:LeanSixSigma` + `mgmt:OKR` declarados `ref:Methodology` | Decisão provisória | Recorte 2, decidido por você em 2026-07-01 | `tbox-local.ttl`, commit `d5eaa13` (bloco `### RECORTE 2 ###`) | Reconciliar quando a Metodologia consultiva formalizar o catálogo real de frameworks (Frente C) | Aberto — **este é o ponto de abertura natural da agenda da Frente C**, o gatilho é literalmente o início dela; progresso 2026-07-23: mgmt:LeanSixSigma e mgmt:OKR completados com ref:applicableDomain e ref:applicableInDimension; Seção 1 do catálogo do Metamodelo.xlsx (7 de 97 frameworks) classificada e commitada na mesma leva. Restam 90 frameworks das demais seções. |
| 6 | `ref:applicableIndustry` (§8.2) e `ref:applicableSector` (§8.2.1) têm `rdfs:domain`/`rdfs:range` idênticos (`ref:ReferenceCapability` → `naics:Industry`) | Decisão provisória | Recorte 4, achado ao extrair §8.2/§8.2.1; decidido no checkpoint de reconciliação em 2026-07-20 | `tbox-local.ttl`, bloco `### RECORTE 3 ###` (propriedades) | Revisitar quando um setor além de Manufatura Discreta for curado e o uso real mostrar se a distinção de granularidade é necessária | Aberto — decisão: manter as duas por ora, sem fundir ou especializar range |
| 7 | Escopo de §8.8.2 (regras de roteamento semântico, SHACL+SPARQL) | Decisão provisória | Decidida por você em 2026-07-20, fora de sessão de extração | Não extraída — conteúdo permanece só na Arquitetura v1.3 §8.8.2, não migrado para shapes.ttl | Revisitar quando a Frente C convergir DMAIC/VSM (primeiro piloto planejado); o mapeamento gap→framework deve nascer validado contra metodologia real, não contra os 3 exemplos ilustrativos do documento | Aberto — decisão de adiar tomada; extração condicionada à convergência da Frente C |
| 8 | Cobertura de alinhamento rdfs:subClassOf a gist:/archimate: das classes ref:/mgmt:/pcf: da Camada 2.5, resíduo de 5 classes estruturais sem ancoragem (ref:Competence, ref:FrameworkPhase, ref:Threshold, ref:ChangeReadinessAssessment, ref:ResistanceFactor) | Observação estrutural, sem julgamento pendente hoje | Revisão de par, 2026-07-21, auditoria mecânica em 2026-07-22 (auditoria_checkpoint_2026-07-22.md, Parte 2) | tbox-local.ttl no HEAD do commit 459db50, resíduo declarado, não novo trabalho | Próxima vez que qualquer uma das 5 for substantivamente tocada em curadoria, ou importação real do gist.owl (mesmo gatilho do item 1) | Aberto, resíduo declarado |
| 9 | Preâmbulo fundacional curto (tese, princípios, o que o projeto **não** é) decidido como **seção inicial da Metodologia convergida** — não como documento avulso nem como §1 da Arquitetura v1.4. Na redação, avaliar "coerência organizacional" como conceito organizador, **com atribuição a prior art** (Teece, Rumelt, Dosi & Winter 1994, "corporate coherence"; Leinwand & Mainardi, coherence premium) e lastro cibernético da tese da compreensão em Conant & Ashby (1970, good regulator theorem), conectando ao VSM já anotado no grafo. Descartada a ambição de vocabulário proprietário ("escola de pensamento" identificada como arrasto de conversa externa, não aspiração do consultor) | Decisão de escopo, tomada em sessão | Sessão de brainstorm 2026-07-23 (julgamento técnico de conversa externa com outra IA) | Nenhum artefato criado — decisão registrada só aqui | Abertura da Frente C: o preâmbulo entra no fluxo de convergência da Metodologia, a custo marginal | Aberto — decisão de escopo tomada; redação condicionada à Frente C |
| 10 | Verificar se `tbox-local.ttl` expressa dependência lateral capability→capability e se o método diagnóstico deve usá-la para **previsão de efeitos colaterais de intervenção** (capability que performa localmente e degrada o sistema). Caminho preferido: **reuso das relações ArchiMate canônicas** (Serving, Aggregation) já disponíveis na §5 da Arquitetura, sem vocabulário novo (§2.2). §8.12 cobre prontidão e resistência, mas propagação de efeito entre capabilities não está explicitada como consulta ou regra | Decisão provisória (verificação + decisão metodológica) | Sessão de brainstorm 2026-07-23 (ponto tecnicamente fecundo do julgamento da conversa externa) | Não auditada — nenhuma mudança em `tbox-local.ttl` | Formalização do método diagnóstico na Frente C, junto ao item 7 (roteamento §8.8.2): o mapeamento gap→framework e a propagação de efeito devem nascer validados contra metodologia real | Aberto |
| 11 | Granularidade de instância mgmt: quando uma linha do Metamodelo.xlsx bundla métodos-irmãos (ex.: FWK-029 "Gestão Ágil (Scrum, Kanban, SAFe)") | Decisão provisória | Sessão 2026-07-23, decidida por Claude diante de "não sei" do consultor, registrada explicitamente como tal | tbox-local.ttl, a partir da extração da Seção 1 | Se uma curadoria específica mostrar que os métodos-irmãos de uma linha bundlada não têm domínio/maturidade distintos o suficiente para justificar instâncias separadas, essa linha vira exceção pontual documentada | Aberto — princípio adotado: granularidade fina (uma instância por método, não por linha da planilha). mgmt:LeanSixSigma mantido como instância própria além de mgmt:DMAIC e mgmt:LeanThinking (novo), pelo mesmo critério |
| 12 | Natureza de mgmt:BMM (FWK-094) e mgmt:PMVV (FWK-095) | Decisão provisória | Sessão 2026-07-23, classificação proposta por Claude, sem confirmação do consultor | tbox-local.ttl | Consultor revisar e confirmar ou corrigir a classificação | Aberto — BMM como ref:AnalyticalFramework, PMVV como ref:Technique, confiança média em ambos |

Nove linhas (1, 2, 6, 7, 8, 9, 10, 11, 12). O item 8 nasce da auditoria mecânica de 2026-07-22, que enumerou 56 classes e verificou alinhamento até profundidade 2: 35 alinhadas, sem ação necessária; das 21 não alinhadas, 4 enumerações fechadas seguem o gatilho do item 1, 1 reificação não precisa de ação, a taxonomia pcf: inteira é decisão pragmática documentada, e as 5 classes estruturais acima são o resíduo real. Os itens 9 (preâmbulo fundacional como seção inicial da Metodologia convergida) e 10 (dependência lateral capability→capability para previsão de efeitos colaterais) nascem da sessão de brainstorm de 2026-07-23, ambos com gatilho na Frente C. Os itens 11 (granularidade de instância mgmt: para linhas que bundlam métodos-irmãos) e 12 (natureza de mgmt:BMM e mgmt:PMVV) nascem da extração da Seção 1 do catálogo do Metamodelo.xlsx em 2026-07-23, ambos como decisões provisórias de curadoria a confirmar pelo consultor.

---

## 2. Checklist de Extração — Frente A (TBox), o que falta

Cada bloco é um candidato a recorte. Sequência sugerida, não vinculante —
posso agrupar diferente se fizer mais sentido ao chegar lá.

| Bloco | Seção da Arquitetura v1.3 | Status | Recorte alvo (proposto) |
|---|---|---|---|
| SHACL shapes (16) | §9, §8.9.3, §8.10.2 | ✅ Extraído — `shapes.ttl`, commit `6c10576`. Contagem reconferida no checkpoint de 2026-07-20: 16 confirmado (grep bruto acusa 17 por uma ocorrência dentro do comentário de cabeçalho do próprio arquivo, que não é shape real). | Recorte 1 |
| Vocabulário local base (`org:`, `ref:`, `demo:`, `vsm:`) — **inclui §8.9.1 `ref:Competence`** | — (§8.9.1) | ✅ Extraído — `tbox-local.ttl`, commit `820974d`, linhas 77-85 | Recorte 1 |
| `pcf:`, `naics:`, `mgmt:`, `Microactivity`/`FrameworkPhase` | §8.3, §8.4, §8.7, §8.11, parte de §8.12.8 | ✅ Commitado — hash `d5eaa13`, mesclado em `tbox-local.ttl` (429 triplas totais). Conteúdo preservado no bloco `### RECORTE 2 — Mesclado em 2026-07-01 ###`. | Recorte 2 — concluído em 2026-07-01 |
| `MaturityLevel`, `GapType`, `Artifact` | §8.1.1, §8.8.1, §8.5 | ✅ Commitado — hash `52f701749dae12345c4dc0301e0ef0835f1fa460` (`52f7017`), bloco `### RECORTE 3 — Mesclado em 2026-07-08 ###` em `tbox-local.ttl` (429 → 522 triplas). rdflib parse OK; pyshacl `advanced=True` Conforms. **`Competence` (§8.9.1) NÃO fez parte deste recorte — já estava no Recorte 1.** | Recorte 3 — concluído em 2026-07-08 |
| `ReferenceCapability` completa + propriedades que apontam para `pcf:`/`naics:` | §8.2, §8.2.1 | ✅ Extraído — commit `f09dc6a`, substituiu o stub do Recorte 3. Exemplo `ref:cap_RiscoOperacionalBancario` (naics:522110) não migrado — ver linha de anotação abaixo. | Recorte 4 — concluído em 2026-07-20 |
| Restante do vocabulário de mudança organizacional (papéis, status, fatores de resistência, readiness) | §8.12 (menos §8.12.8, já feito) | ✅ Extraído — commit `f09dc6a`. §8.12 completo. | Recorte 4 — concluído em 2026-07-20 |
| Regras de roteamento semântico (SHACL+SPARQL) | §8.8.2 | 🔲 Decidido: fora do escopo da Frente A por ora — ver Registro §1, item 7 | Adiado para a Frente C (convergência DMAIC/VSM) |
| Anotação em §8.2 da Arquitetura: marcar exemplo `naics:522110` (Bancos Comerciais) como "exemplo de sintaxe, não recomendação de posicionamento" | §8.2 (`Arquitetura_Ontologica_Empresarial_v1_3.docx`, fora do TBox) | ⬜ Não implementado — decisão tomada no checkpoint de 2026-07-20 (ver histórico da Seção 1, ex-item 3) | Próxima revisão da Arquitetura (v1.4) |
| Revisão ortográfica dos rdfs:label do TBox, passada única e deliberada | Todo o tbox-local.ttl, exceto §8.9.1 (resolvido) | 🟡 Parcialmente executado. §8.9.1 corrigido pelo commit 459db50 em 2026-07-22, como efeito colateral do achado descrito na nota de exatidão acima. Correção mecânica restaurou as três subclasses CHA e aplicou o relabel acentuado (incluindo ref:Competence, linha 79) na mesma passada, exceção estreita e justificada, mesmo bloco, mesmo commit, correção de perda de dado, não abertura de precedente para patch pontual no resto do arquivo. | Passada de revisão ortográfica dedicada, sem data definida, escopo reduzido por não incluir mais §8.9.1 |

⚠️ Nota de exatidão do checklist: o Recorte 3 revelou que este checklist marcava §8.9.1 ref:Competence como "não extraído", quando ele estava presente desde o Recorte 1. Corrigido. A nota de auditoria do checkpoint de 2026-07-20 registrava não ter encontrado nenhum outro descompasso do mesmo tipo, isso estava incorreto: uma auditoria complementar em 2026-07-22 encontrou dois, a ausência das três subclasses CHA de §8.9.1 (mesmo padrão do achado de Competence) e a perda de uma restrição owl:Restriction sobre org:AlgedonicAlert (§7.3), ambas por corrupção de comentário (statement na mesma linha do #). Os dois foram corrigidos no commit 459db50. Ver auditoria_checkpoint_2026-07-22.md para evidência bruta.

**Nota de auditoria (checkpoint 2026-07-20):** uma ambiguidade de
formatação na Shape 14 (`ref:CapabilityTripodShape`, propriedade
`enabledByComponent`) já estava resolvida e autodocumentada no cabeçalho
de `shapes.ttl` desde o Recorte 1. É funcionalmente inerte (`sh:minCount 0`
nunca gera violação) e não exigiu nova linha nesta seção nem na Seção 1.

**Leitura direta:** a Frente A está **completa e com o checkpoint de
reconciliação concluído** (2026-07-20). Restam só duas tarefas de
implementação sem ambiguidade (as duas últimas linhas desta tabela, sem
data definida) e quatro decisões provisórias na Seção 1, todas com gatilho
nomeado e nenhuma bloqueando o início da Frente C.

---

## 3. Checkpoint de reconciliação — concluído em 2026-07-20

Revisão feita: Seção 1 percorrida decisão por decisão com o consultor
(itens 3, 5 e 6 decididos; itens 1, 2 e 7 reconfirmados como corretamente
em aberto, com gatilho válido). Seção 2 auditada linha a linha contra o
conteúdo real de `tbox-local.ttl` e `shapes.ttl` — contagem de 16 shapes
confirmada, nenhum outro descompasso do tipo Competence/Recorte 3
encontrado. Frente A declarada madura o suficiente para iniciar a Frente C,
com o item 2 da Seção 1 como ponto de abertura natural da agenda.

Nota de 2026-07-22: uma auditoria complementar (revisão de par de 2026-07-21, seguida de auditoria mecânica via Cowork em 2026-07-22, ver auditoria_checkpoint_2026-07-22.md) encontrou dois descompassos que a auditoria de 2026-07-20 não havia identificado (ver nota de exatidão da Seção 2) e levantou uma observação estrutural nova, reaberta como item 8 da Seção 1. Os dois descompassos foram corrigidos no commit 459db50. Isso não invalida as decisões de conteúdo tomadas em 2026-07-20 (itens 3 e 6), só corrige o registro de completude da auditoria técnica daquele checkpoint.
