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
| 2 | `mgmt:LeanSixSigma` + `mgmt:OKR` declarados `ref:Methodology` | Decisão provisória | Recorte 2, decidido por você em 2026-07-01 | `tbox-local.ttl`, commit `d5eaa13` (bloco `### RECORTE 2 ###`) | Reconciliar quando a Metodologia consultiva formalizar o catálogo real de frameworks (Frente C) | Aberto — **este é o ponto de abertura natural da agenda da Frente C**, o gatilho é literalmente o início dela |
| 6 | `ref:applicableIndustry` (§8.2) e `ref:applicableSector` (§8.2.1) têm `rdfs:domain`/`rdfs:range` idênticos (`ref:ReferenceCapability` → `naics:Industry`) | Decisão provisória | Recorte 4, achado ao extrair §8.2/§8.2.1; decidido no checkpoint de reconciliação em 2026-07-20 | `tbox-local.ttl`, bloco `### RECORTE 3 ###` (propriedades) | Revisitar quando um setor além de Manufatura Discreta for curado e o uso real mostrar se a distinção de granularidade é necessária | Aberto — decisão: manter as duas por ora, sem fundir ou especializar range |
| 7 | Escopo de §8.8.2 (regras de roteamento semântico, SHACL+SPARQL) | Decisão provisória | Decidida por você em 2026-07-20, fora de sessão de extração | Não extraída — conteúdo permanece só na Arquitetura v1.3 §8.8.2, não migrado para shapes.ttl | Revisitar quando a Frente C convergir DMAIC/VSM (primeiro piloto planejado); o mapeamento gap→framework deve nascer validado contra metodologia real, não contra os 3 exemplos ilustrativos do documento | Aberto — decisão de adiar tomada; extração condicionada à convergência da Frente C |

Quatro linhas (1, 2, 6, 7). Os itens 3 e 5 foram decididos no checkpoint de
reconciliação de 2026-07-20 e saem desta seção: a ambiguidade em si está
resolvida, o que resta é só executar um texto/edição sem julgamento
pendente, por isso migraram para a Seção 2 (Checklist) como trabalho
sem ambiguidade. O item 4 (stub de `ReferenceCapability`) segue removido
desde o Recorte 4. Continua sendo dívida semântica pequena e rastreável.

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
| Revisão ortográfica única de todos os `rdfs:label` do TBox (não só §8.9.1, que motivou o achado) — normalizar acentuação onde divergente | Todo o `tbox-local.ttl` | ⬜ Não implementado — decisão tomada no checkpoint de 2026-07-20: não aplicar patch pontual, fazer como passada única e deliberada (ver histórico da Seção 1, ex-item 5) | Passada de revisão ortográfica dedicada, sem data definida |

**⚠️ Nota de exatidão do checklist:** o Recorte 3 revelou que este checklist
(e a nota 6 do cabeçalho do Recorte 2) marcava §8.9.1 `ref:Competence` como
"não extraído", quando ele estava presente desde o Recorte 1. Corrigido. A
auditoria linha-a-linha do checkpoint de 2026-07-20 não encontrou nenhum
outro descompasso do mesmo tipo.

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
