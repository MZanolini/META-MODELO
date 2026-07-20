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
| 2 | `mgmt:LeanSixSigma` + `mgmt:OKR` declarados `ref:Methodology` | Decisão provisória | Recorte 2, decidido por você em 2026-07-01 | `tbox-local.ttl`, commit `d5eaa13` (bloco `### RECORTE 2 ###`) | Reconciliar quando a Metodologia consultiva formalizar o catálogo real de frameworks (Frente C) | Aberto — commitado como provisório, ainda não reconciliado |
| 3 | `naics:522110` (exemplo "Commercial Banking" em Arquitetura §8.2) usado como exemplo de setor regulado, fora do posicionamento do consultor | Observação de conteúdo, não decidida | Recorte 2, achado ao extrair `naics:` | Não migrado para o TBox — nota registrada no bloco `### RECORTE 2 ###` de `tbox-local.ttl`, commit `d5eaa13` | Decidir na próxima revisão da Arquitetura (Frente A): manter como exemplo de sintaxe, trocar por setor não-regulado, ou anotar explicitamente como "exemplo, não recomendação de posicionamento" | Aberto |
| 5 | Labels de §8.9.1 (`ref:Competence` + 3 subclasses CHA) estão **sem acento** ("Competencia Humana", "Competencia Tecnica"…), divergindo de §8.1.1/§8.8.1 e do bloco de referência acentuado | Divergência de fonte + decisão de normalização (ponto do Recorte 3) | Recorte 1 (`820974d`); reconfirmado no Recorte 3 | `tbox-local.ttl`, linhas 79-80 | Você decidiu "normalizar acentuado" — mas o bloco já está **commitado** desde o Recorte 1; o relabel **não** foi aplicado a conteúdo commitado sem confirmação explícita | Aberto — aguarda seu OK para relabel acentuado das linhas 79-80 (mudança T1, sem impacto em SHACL, que é baseado em URI, não em label) |
| 6 | `ref:applicableIndustry` (§8.2) e `ref:applicableSector` (§8.2.1) têm `rdfs:domain`/`rdfs:range` idênticos (`ref:ReferenceCapability` → `naics:Industry`) | Observação de conteúdo, não decidida | Recorte 4, achado ao extrair §8.2/§8.2.1 | `tbox-local.ttl`: propriedades no bloco `### RECORTE 3 ###` (§8.2/§8.2.1) e nota no bloco `### RECORTE 4 ###`, commit `<COMMIT_R4>` | Decidir na próxima revisão da Arquitetura/curadoria (Frente A): a fonte só diz que `applicableSector` é "mais granular", sem detalhar a distinção — manter as duas, fundir, ou especializar o range de uma delas | Aberto — extraídas exatamente como na fonte, sem fundir, renomear ou inventar diferenciação (mesmo tratamento do item 3) |

Cinco linhas. Três herdadas (1-3); o item 5 (acento de §8.9.1, Recorte 3)
segue aberto; o item 6 (`applicableIndustry` × `applicableSector`) é novo do
Recorte 4. O antigo item 4 (stub de `ReferenceCapability`) foi **resolvido**
pelo Recorte 4 — a definição completa de §8.2 substituiu o stub — e por isso
foi removido da tabela ("cada linha some quando resolvida"). Continua sendo
dívida semântica pequena e rastreável.

---

## 2. Checklist de Extração — Frente A (TBox), o que falta

Cada bloco é um candidato a recorte. Sequência sugerida, não vinculante —
posso agrupar diferente se fizer mais sentido ao chegar lá.

| Bloco | Seção da Arquitetura v1.3 | Status | Recorte alvo (proposto) |
|---|---|---|---|
| SHACL shapes (16) | §9, §8.9.3, §8.10.2 | ✅ Extraído — `shapes.ttl`, commit `6c10576` | Recorte 1 |
| Vocabulário local base (`org:`, `ref:`, `demo:`, `vsm:`) — **inclui §8.9.1 `ref:Competence`** | — (§8.9.1) | ✅ Extraído — `tbox-local.ttl`, commit `820974d`, linhas 77-85 | Recorte 1 |
| `pcf:`, `naics:`, `mgmt:`, `Microactivity`/`FrameworkPhase` | §8.3, §8.4, §8.7, §8.11, parte de §8.12.8 | ✅ Commitado — hash `d5eaa13`, mesclado em `tbox-local.ttl` (429 triplas totais). Conteúdo preservado no bloco `### RECORTE 2 — Mesclado em 2026-07-01 ###`. | Recorte 2 — concluído em 2026-07-01 |
| `MaturityLevel`, `GapType`, `Artifact` | §8.1.1, §8.8.1, §8.5 | ✅ Commitado — hash `52f701749dae12345c4dc0301e0ef0835f1fa460` (`52f7017`), bloco `### RECORTE 3 — Mesclado em 2026-07-08 ###` em `tbox-local.ttl` (429 → 522 triplas). rdflib parse OK; pyshacl `advanced=True` Conforms. **`Competence` (§8.9.1) NÃO fez parte deste recorte — já estava no Recorte 1** (correção da linha anterior deste checklist, que a marcava como não-extraída). | Recorte 3 — concluído em 2026-07-08 |
| `ReferenceCapability` completa + propriedades que apontam para `pcf:`/`naics:` | §8.2, §8.2.1 | ✅ Extraído — commit `<COMMIT_R4>`, substituiu o **stub** do Recorte 3 no próprio bloco `### RECORTE 3 ###`; inclui `applicableIndustry`, `realizedByReferenceProcess`, `org:hasReferenceCapability`, `applicableSector` e as 4 subclasses setoriais (Manufatura Discreta, Serviços Profissionais, Distribuição/Atacado, Varejo). Exemplo `ref:cap_RiscoOperacionalBancario` (naics:522110) **não** migrado — ver Seção 1, item 3. | Recorte 4 — concluído em 2026-07-20 |
| Restante do vocabulário de mudança organizacional (papéis, status, fatores de resistência, readiness) | §8.12 (menos §8.12.8, já feito) | ✅ Extraído — commit `<COMMIT_R4>`. Auditoria de §8.12 concluída: §8.12.2 (papéis Change*), §8.12.3 (`InterventionStatus`), §8.12.5/§8.12.6 (vínculos com `Intervention`) já estavam no Recorte 1 e §8.12.8 no Recorte 2; o Recorte 4 acrescentou §8.12.4 (`ResistanceFactor` + 5 subclasses + 3 propriedades, reusando `ref:ChangeResistor` e `ref:Intervention`) e §8.12.7 (5 subclasses de `ref:Artifact`). **§8.12 completo.** | Recorte 4 — concluído em 2026-07-20 |
| Regras de roteamento semântico (SHACL+SPARQL) | §8.8.2 | ⬜ Escopo a confirmar — não é vocabulário no sentido estrito; decidir se entra como recorte de "regras" separado de TBox | Fora de sequência — decisão pendente sobre se entra na Frente A |

**⚠️ Nota de exatidão do checklist:** o Recorte 3 revelou que este checklist
(e a nota 6 do cabeçalho do Recorte 2) marcava §8.9.1 `ref:Competence` como
"não extraído", quando ele estava presente desde o Recorte 1. Corrigido acima.
Recomenda-se, no checkpoint de reconciliação, uma auditoria linha-a-linha do
que de fato está em `tbox-local.ttl` versus o que o checklist afirma — o
mesmo tipo de descompasso pode existir na linha de §8.12.

**Leitura direta:** com o Recorte 4 mesclado, o vocabulário do TBox da Frente A
está **tecnicamente completo**. A definição completa de `ref:ReferenceCapability`
(§8.2/§8.2.1) e o restante de §8.12 (§8.12.4 fatores de resistência e §8.12.7
artefatos de mudança) foram extraídos e validados (rdflib: 522 → 588 triplas;
pyshacl `advanced=True` Conforms: True). Resta **apenas uma decisão de escopo**,
sobre as regras de roteamento semântico de §8.8.2 (SHACL+SPARQL): se entram como
recorte de "regras" separado ou ficam fora do TBox formal. Essa decisão é do
consultor e **não foi tomada aqui** (está explicitamente fora do escopo do
Recorte 4). Depois de resolvida, a Frente A vai para o checkpoint de
reconciliação da Seção 3 antes de iniciar a Frente C.

---

## 3. Checkpoint de reconciliação (ainda não chegamos lá)

Antes de declarar Frente A madura o suficiente para iniciar a Frente C
(convergência da Metodologia), revisar a Seção 1 inteira com você — decisão
por decisão, nada some sem confirmação explícita. Este documento é o
critério objetivo desse checkpoint, não uma sensação de "acho que já está
bom". Incluir aqui a auditoria linha-a-linha do checklist (Seção 2) mencionada
acima.
