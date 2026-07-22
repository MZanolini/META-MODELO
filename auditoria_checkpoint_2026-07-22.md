# Auditoria de reconciliação — checkpoint 2026-07-22

**Escopo:** verificação (não extração, não decisão, não correção) dos arquivos
`tbox-local.ttl` e `shapes.ttl` no HEAD do repositório
`camada25-ontologia`, contra o `Registro_Pendencias_Camada25.md`.

**Estado do repositório na auditoria:**

- HEAD: `7f47734` (Checkpoint de reconciliação da Frente A concluído (2026-07-20))
- Working tree: limpo (`git status --short` sem saída).
- `tbox-local.ttl`: 718 linhas, 39.277 bytes (`ls -la`).
- `shapes.ttl`: 142 linhas, 10.799 bytes (`ls -la`).

**Ferramenta:** `rdflib` (parse), `pyshacl advanced=True` (validação),
`grep -n` (localização por linha), `git log --oneline`, `git show --stat`.

**Não modifica** `tbox-local.ttl`, `shapes.ttl` nem
`Registro_Pendencias_Camada25.md`. **Não commita.** Divergências ficam
reportadas para decisão do consultor.

---

## 0. Verificações-base

### 0.1 Existência dos seis commits citados pelo checklist

Saída bruta de `git log --oneline` (recortada para os hashes citados na
tarefa):

```
7f47734 Checkpoint de reconciliação da Frente A concluído (2026-07-20)...
aad74e4 Registro: decisão de escopo §8.8.2 (adiado para Frente C, DMAIC/VSM)...
bc73532 Recorte 4 (backfill): preenche o hash f09dc6a...
f09dc6a Recorte 4: definição completa de ReferenceCapability (§8.2/8.2.1)...
52f7017 Recorte 3: adiciona MaturityLevel, GapType, Artifact ao TBox...
d5eaa13 recorte 2 do TBox (vocabulário pcf:, naics:, mgmt:, Microactivity/FrameworkPhase)...
820974d Adiciona tbox-local.ttl: vocabulário local usado pelos 16 shapes já validados...
6c10576 Extração inicial: 16 SHACL shapes da Arquitetura v1.3...
```

Todos os seis commits (`6c10576`, `820974d`, `d5eaa13`, `52f7017`,
`f09dc6a`, e a linhagem completa até o HEAD) estão presentes. Confere.

### 0.2 rdflib parse — contagem exata de triplas

```python
from rdflib import Graph
g = Graph(); g.parse("tbox-local.ttl", format="turtle")
print(len(g))   # 588
s = Graph(); s.parse("shapes.ttl", format="turtle")
print(len(s))   # 143
```

Saída bruta:
```
TBOX_TRIPLES=588
SHAPES_TRIPLES=143
```

**Observação de divergência com o Registro §2:** o Registro afirma que
`tbox-local.ttl` tinha 522 triplas ao fim do Recorte 3 (Recorte 2 = 429 →
Recorte 3 = 522). Não há afirmação numérica sobre o total pós-Recorte 4 no
Registro. O total atual é 588; o delta 522 → 588 (66 triplas) é
compatível com o `git show --stat f09dc6a` (+91 linhas em `tbox-local.ttl`,
das quais uma parte é comentário/estrutura). Não é divergência, é
informação nova.

### 0.3 pyshacl advanced=True

```python
from pyshacl import validate
conforms, _, results_text = validate(
    data_graph=data, shacl_graph=shapes,
    advanced=True, inference='none'
)
```

Saída bruta:
```
CONFORMS=True
---RESULTS_TEXT_START---
Validation Report
Conforms: True

---RESULTS_TEXT_END---
```

Conforms. Zero violações e zero warnings sobre o próprio TBox como
data-graph.

---

## Parte 1 — Auditoria do checklist (Seção 2 do Registro)

**Convenções:** "explicit" = URI é objeto de `rdf:type owl:Class /
ObjectProperty / DatatypeProperty`. "implicit via subClassOf" = URI aparece
como sujeito ou objeto de `rdfs:subClassOf` mas sem `rdf:type owl:Class`
explícito (semanticamente equivalente em OWL, mas menos rigoroso na
declaração). "individual (a X)" = URI declarada como `a ref:X` /
`a demo:X`, sendo instância de uma classe do próprio arquivo.

### Bloco 1 — SHACL shapes (16) | commit `6c10576` | §9, §8.9.3, §8.10.2

Contagem via rdflib (`sh:NodeShape`):

```
COUNT_SHAPES=16
https://example.org/ontology/AlgedonicTargetsS5
https://example.org/ontology/BusinessProcessHasRole
https://example.org/ontology/CapabilityHasDimensionShape
https://example.org/ontology/CapabilityIsRealized
https://example.org/ontology/ConstraintInfluencesBehavior
https://example.org/ontology/CriticalRoleHasOwner
https://example.org/ontology/GoalHasDriver
https://example.org/ontology/MultiActorProcessRealizesTransaction
https://example.org/ontology/OrganizationHasGoverningAgreement
https://example.org/ontology/ProcessHasDimensionShape
https://example.org/ontology/SingleDimensionShape
https://example.org/ontology/TransactionPhaseCardinality
https://example.org/ref/CapabilityTripodShape
https://example.org/ref/CompetenceWeightSumShape
https://example.org/ref/InterventionReadinessShape
https://example.org/ref/InterventionSponsorShape
```

**16 shapes confere.** Grep de posicionamento (uma linha por shape, exceto
a linha 13 do cabeçalho que é o comentário de documentação da técnica de
extração):

```
39:org:BusinessProcessHasRole a sh:NodeShape
41:org:CapabilityIsRealized a sh:NodeShape
43:org:GoalHasDriver a sh:NodeShape
46:org:SingleDimensionShape a sh:NodeShape
48:org:ProcessHasDimensionShape a sh:NodeShape
50:org:CapabilityHasDimensionShape a sh:NodeShape
54:org:MultiActorProcessRealizesTransaction a sh:NodeShape
56:org:TransactionPhaseCardinality a sh:NodeShape
60:org:OrganizationHasGoverningAgreement a sh:NodeShape
62:org:CriticalRoleHasOwner a sh:NodeShape
64:org:AlgedonicTargetsS5 a sh:NodeShape
66:org:ConstraintInfluencesBehavior a sh:NodeShape
71:ref:CompetenceWeightSumShape a sh:NodeShape
80:ref:CapabilityTripodShape a sh:NodeShape
100:ref:InterventionSponsorShape a sh:NodeShape
114:ref:InterventionReadinessShape a sh:NodeShape
```

**Status: confere.**

### Bloco 2 — Vocabulário local base (`org:`, `ref:`, `demo:`, `vsm:`), inclui §8.9.1 `ref:Competence` | commit `820974d`

| Item esperado | Encontrado (linha) | Status |
|---|---|---|
| `demo:realizesCoordinationPattern` (ObjectProperty) | L38 explicit | confere |
| `demo:Transaction` (Class) | L40 explicit | confere |
| `demo:hasPhase` (ObjectProperty) | L41 explicit | confere |
| `demo:TransactionPhase` (Class) | L42 explicit | confere |
| `vsm:VSMFunction` (Class) | L49 explicit | confere |
| `vsm:targetFunction` (ObjectProperty) | L51 explicit | confere |
| `vsm:vsmFunction` (ObjectProperty) | L53 explicit | confere |
| `org:AlgedonicAlert` (Class) | L57 explicit | confere (**ver §Bloco 2 — Achado A**) |
| `ref:KPI` (Class) | L62 explicit | confere |
| `ref:BSCPerspective` (Class) | L63 explicit | confere |
| `ref:measuresCapability` (ObjectProperty) | L64 explicit | confere |
| `ref:hasBSCPerspective` (ObjectProperty) | L65 explicit | confere |
| `ref:hasThreshold` (ObjectProperty) | L66 explicit | confere |
| `ref:Threshold` (Class) | L67 explicit | confere |
| `ref:greenUpperBound` (DatatypeProperty) | L68 explicit | confere |
| `ref:yellowUpperBound` (DatatypeProperty) | L69 explicit | confere |
| `ref:Intervention` (Class) | L71 explicit | confere |
| `ref:appliesFramework` (ObjectProperty) | L72 explicit | confere |
| `ref:targetsCapability` (ObjectProperty) | L73 explicit | confere |
| `ref:investmentCost` (DatatypeProperty) | L74 explicit | confere |
| `ref:realizedReturn` (DatatypeProperty) | L75 explicit | confere |
| `ref:Competence` (Class, §8.9.1) | L79 explicit | confere |
| `ref:TechnicalCompetence` (subclasse CHA) | **ausente do grafo** | **DIVERGE** — ver **Bloco 2 — Achado B** |
| `ref:BehavioralCompetence` (subclasse CHA) | **ausente do grafo** | **DIVERGE** — ver **Bloco 2 — Achado B** |
| `ref:ManagerialCompetence` (subclasse CHA) | **ausente do grafo** | **DIVERGE** — ver **Bloco 2 — Achado B** |
| `ref:anchoredInDimension` (ObjectProperty, §8.9.1) | L82 explicit | confere |
| `org:capabilityRequiresCompetence` (ObjectProperty, §8.9.1) | L84 explicit | confere |
| `org:competenceWeight` (DatatypeProperty, §8.9.1) | L85 explicit | confere |
| `ref:ChangeSponsor` (Class, §8.12.2) | L89 explicit | confere |
| `ref:ChangeAgent` (Class, §8.12.2) | L93 explicit | confere |
| `ref:ChangeEndUser` (Class, §8.12.2) | L97 explicit | confere |
| `ref:ChangeResistor` (Class, §8.12.2) | L101 explicit | confere |
| `ref:InterventionStatus` (Class, §8.12.3) | L108 explicit | confere |
| `ref:interventionStatus` (ObjectProperty, §8.12.3) | L119 explicit | confere |
| `ref:ChangeReadinessAssessment` (Class, §8.12.5) | L125 explicit | confere |
| `ref:hasSponsor` (ObjectProperty, §8.12.6) | L161 explicit | confere |
| `ref:hasChangeAgent` (ObjectProperty, §8.12.6) | L165 explicit | confere |
| `org:ManagementDimension` (Class, provisório) | L188 explicit | confere |

**Bloco 2 — Achado A (`org:AlgedonicAlert`): restrição de fecho universal a `vsm:S5` está SILENCIOSAMENTE PERDIDA no grafo parseado.**

`grep -n "org:AlgedonicAlert" tbox-local.ttl`:

```
57:org:AlgedonicAlert a owl:Class ; rdfs:subClassOf gist:Event ; rdfs:label "Alerta algedônico"@pt ; rdfs:comment "Sinal de urgência que contorna canais regulares de coordenação"@pt . 
58: # Todo AlgedonicAlert tem como destino canônico S5 (Identidade) . org:AlgedonicAlert rdfs:subClassOf [ a owl:Restriction ; owl:onProperty vsm:targetFunction ; owl:hasValue vsm:S5 ] .
```

A linha 58 abre com `# Todo AlgedonicAlert tem como destino canônico S5 (Identidade) .` e, na mesma linha, ainda dentro do comentário `#` que se estende até fim-de-linha em Turtle, aparece o statement `org:AlgedonicAlert rdfs:subClassOf [ a owl:Restriction ; owl:onProperty vsm:targetFunction ; owl:hasValue vsm:S5 ] .`. Esse statement **não entra no grafo**. Verificação por rdflib:

```
--- org:AlgedonicAlert subclass-of triples ---
  https://example.org/ontology/AlgedonicAlert rdfs:subClassOf https://ontologies.semanticarts.com/gist/Event
```

Só o `rdfs:subClassOf gist:Event` foi parseado. O `owl:hasValue vsm:S5` está fora do grafo. Consequência funcional: nada é violado hoje porque a SHACL Shape 11 (`org:AlgedonicTargetsS5`, `shapes.ttl` L64) impõe a mesma condição via `sh:property [sh:path vsm:targetFunction ; sh:hasValue vsm:S5]` sobre as instâncias, e a validação atual só usa o próprio TBox como data-graph (sem instâncias). Mas a intenção declarada no comentário (fecho ontológico do AlgedonicAlert → S5) não está no grafo. É o mesmo mecanismo de corrupção mecânica que o Registro §2 já cita na nota do Recorte 3 sobre "possível descompasso em §8.12" — só que este é em §7.3, Recorte 1.

**Bloco 2 — Achado B (§8.9.1, subclasses CHA): as três subclasses `ref:TechnicalCompetence`, `ref:BehavioralCompetence`, `ref:ManagerialCompetence` estão SILENCIOSAMENTE COMENTADAS OUT.**

`grep -n "ref:TechnicalCompetence\|ref:BehavioralCompetence\|ref:ManagerialCompetence" tbox-local.ttl`:

```
80: # Tres subclasses CHA ref:TechnicalCompetence rdfs:subClassOf ref:Competence ; rdfs:label "Competencia Tecnica (Conhecimento aplicado)"@pt . ref:BehavioralCompetence rdfs:subClassOf ref:Competence ; rdfs:label "Competencia Comportamental (Atitude)"@pt . ref:ManagerialCompetence rdfs:subClassOf ref:Competence ; rdfs:label "Competencia Gerencial (Habilidade integradora)"@pt . 
```

A linha 80 inteira começa com `# Tres subclasses CHA ...` e, embora contenha três statements `subClassOf` válidos, todos estão dentro do comentário. Verificação por rdflib (zero triplas para os três URIs):

```
--- https://example.org/ref/TechnicalCompetence ---   triples as subject: 0
--- https://example.org/ref/BehavioralCompetence ---  triples as subject: 0
--- https://example.org/ref/ManagerialCompetence ---  triples as subject: 0
---subjects rdfs:subClassOf ref:Competence---
(vazio)
```

Isso é uma divergência de dois níveis:

1. **Com o próprio checklist e com o Registro §1 item 5.** O Registro §1 item 5 afirma "Labels de §8.9.1 (`ref:Competence` + 3 subclasses CHA) estão **sem acento**", pressupondo que as três subclasses existem no grafo e só o label precisaria mudar. Na verdade, as três não existem no grafo do jeito nenhum. O item 5 do Registro trata como problema de normalização de label o que é, mecanicamente, ausência de declaração.

2. **Com a §8.12 (Recorte 4) que declara `ref:ResistanceFactor`.** Os subtipos de ResistanceFactor (linhas 689-701, Recorte 4) declaram cada subclasse em linhas separadas, iniciando com URI no início da linha. Padrão correto. Já as subclasses CHA (linha 80, Recorte 1) foram colapsadas numa única linha comentada. Divergência entre padrão do Recorte 1 e padrão do Recorte 4.

Ambos os achados (A e B) são do mesmo tipo mecânico de corrupção descrito no cabeçalho do próprio `shapes.ttl` (linhas 11-13): "Quebras de linha entre comentario '# ... --' e a declaracao Turtle seguinte foram perdidas na fonte (paragrafo colapsado) — restauradas via deteccao do padrao '<texto> <prefixo:Entidade> a sh:NodeShape' colado numa unica linha." A restauração foi aplicada em `shapes.ttl` mas **não** foi aplicada aos dois trechos análogos do `tbox-local.ttl` (L58 e L80).

**Status do Bloco 2: 35 de 38 itens conferem; 3 divergem (subclasses CHA); 1 achado adicional (restrição AlgedonicAlert → S5 perdida) fora da lista original do checklist mas relevante.**

### Bloco 3 — `pcf:`, `naics:`, `mgmt:`, `Microactivity`/`FrameworkPhase` | commit `d5eaa13`

| Item esperado | Encontrado (linha) | Status |
|---|---|---|
| `ref:ManagementFramework` (Class, §8.3) | L306 explicit | confere |
| `ref:ManagementSystem` | L310 implicit via subClassOf | confere |
| `ref:Methodology` | L311 implicit via subClassOf | confere |
| `ref:Technique` | L312 implicit via subClassOf | confere |
| `ref:Standard` | L313 implicit via subClassOf | confere |
| `ref:ConceptualModel` | L314 implicit via subClassOf | confere |
| `ref:AnalyticalFramework` | L315 implicit via subClassOf | confere |
| `ref:applicableDomain` (ObjectProperty) | L317 explicit | confere |
| `pcf:PCFNode` (Class, §8.4) | L353 explicit | confere |
| `pcf:ProcessCategory` | L356 implicit via subClassOf | confere |
| `pcf:ProcessGroup` | L359 implicit via subClassOf | confere |
| `pcf:Process` | L362 implicit via subClassOf | confere |
| `pcf:Activity` | L365 implicit via subClassOf | confere |
| `pcf:Task` | L368 implicit via subClassOf | confere |
| `pcf:identifier` (DatatypeProperty) | L371 explicit | confere |
| `pcf:apqcCode` (DatatypeProperty) | L376 explicit | confere |
| `pcf:parentNode` (ObjectProperty) | L381 explicit | confere |
| `org:realizesPCFNode` (ObjectProperty, §8.4) | L386 explicit | confere |
| `naics:Industry` (Class, §8.7) | L394 explicit | confere |
| `naics:naicsCode` (DatatypeProperty, §8.7) | L398 explicit | confere |
| `org:industryCode` (ObjectProperty, §8.7) | L402 explicit | confere |
| `ref:Microactivity` (Class, §8.11.1) | L410 explicit | confere |
| `ref:FrameworkPhase` (Class, §8.11.1) | L415 explicit | confere |
| `ref:phaseOfFramework` (ObjectProperty) | L419 explicit | confere |
| `ref:partOfFrameworkPhase` (ObjectProperty) | L423 explicit | confere |
| `mgmt:DMAIC` (individual, `a ref:Methodology`) | L457 | confere |
| `mgmt:ISO9001` (individual, `a ref:Standard, ref:ManagementSystem`) | L464 | confere |
| `mgmt:ADKAR` (individual, `a ref:Methodology`, §8.12.8) | L486 | confere |
| `mgmt:DMAIC_F1_Define` (individual, `a ref:FrameworkPhase`) | L504 | confere |
| `mgmt:ADKAR_Awareness/Desire/Knowledge/Ability/Reinforcement` (individuals) | L511-527 | confere |
| `mgmt:LeanSixSigma` (individual, provisório) | L535 | confere |
| `mgmt:OKR` (individual, provisório) | L538 | confere |

**Observações do Bloco 3, não divergências:**

- As 6 subclasses de `ref:ManagementFramework` (L310-315) e as 5 subclasses de `pcf:PCFNode` (L356-368) usam apenas `rdfs:subClassOf` sem declaração explícita `a owl:Class`. Em OWL isso é semanticamente válido (o resource é implicitamente uma classe via inferência RDFS), mas se o critério for "explicit owl:Class", elas não passam. Comparar com o padrão do Recorte 4 (§8.12.4, L689-701) que declara `a owl:Class ; rdfs:subClassOf ...` no mesmo enunciado, e do Recorte 1 (L89-101, papéis Change*) que também declara `a owl:Class`. Não é divergência com o checklist (que não especifica "explicit"), é observação para o consultor decidir se quer padronizar.
- A propriedade `ref:involvesEntity` (L431) e `ref:producesAnalyticalObject` (L434) estão declaradas como `owl:ObjectProperty` sem `rdfs:range`. O texto-fonte da Arquitetura pode ou não requerer range; não verifiquei contra a fonte. Registrado como observação, não decidido aqui.

**Status do Bloco 3: 100% dos itens declarados no checklist conferem.**

### Bloco 4 — `MaturityLevel`, `GapType`, `Artifact` | commit `52f7017`

| Item esperado | Encontrado (linha) | Status |
|---|---|---|
| `ref:MaturityLevel` (Class, §8.1.1) | L575 explicit | confere |
| `ref:Initial/Repeatable/Defined/Managed/Optimized` (individuals) | L578-582 | confere |
| `ref:levelOrder` (DatatypeProperty) | L583 explicit | confere |
| `org:hasMaturityLevel` (ObjectProperty) | L585 explicit | confere |
| `ref:GapType` (Class, §8.8.1) | L627 explicit | confere |
| 7 individuals de GapType (HighVariability, LongLeadTime, LowAdaptability, StrategyExecutionGap, ControlFailure, SupplyDemandMismatch, KnowledgeAttrition) | L628-634 | confere |
| `org:gapType` (ObjectProperty, §8.8.1) | L635 explicit | confere |
| `ref:Artifact` (Class, §8.5) | L643 explicit | confere |
| 10 subclasses de Artifact (FMEAWorksheet, CTQTree, SIPOCDiagram, ValueStreamMap, RACIMatrix, OKRSheet, BSCDashboard, CanvasBMC, DMAICTemplate, RiskHeatmap) | L646-655 (todas via `rdfs:subClassOf ref:Artifact`, implicit class) | confere |
| `ref:instrumentsTask` (ObjectProperty, §8.5) | L656 explicit | confere |
| `ref:templateURL` (DatatypeProperty, §8.5) | L657 explicit | confere |
| `ref:partOfFramework` (ObjectProperty, §8.5) | L658 explicit | confere |

**Status do Bloco 4: 100% confere.**

### Bloco 5 — `ReferenceCapability` completa | commit `f09dc6a`, §8.2, §8.2.1

| Item esperado | Encontrado (linha) | Status |
|---|---|---|
| `ref:ReferenceCapability` (Class, `rdfs:subClassOf archimate:Capability`, §8.2) | L592 explicit | confere |
| `ref:applicableIndustry` (ObjectProperty → naics:Industry) | L596 explicit | confere |
| `ref:realizedByReferenceProcess` (ObjectProperty → pcf:Process) | L599 explicit | confere |
| `org:hasReferenceCapability` (ObjectProperty → ref:ReferenceCapability) | L603 explicit | confere |
| `ref:DiscreteManufacturingCapability` (subclasse setorial) | L607 implicit via subClassOf | confere |
| `ref:ProfessionalServicesCapability` (subclasse setorial) | L610 implicit | confere |
| `ref:DistributionWholesaleCapability` (subclasse setorial) | L612 implicit | confere |
| `ref:RetailCapability` (subclasse setorial) | L614 implicit | confere |
| `ref:applicableSector` (ObjectProperty, §8.2.1) | L616 explicit | confere |

**4 subclasses setoriais confere.** O item 6 do Registro (`applicableIndustry` × `applicableSector` com domain/range idênticos) é observação semântica em aberto, não divergência mecânica com o checklist.

**Item extra encontrado (não citado na tarefa mas presente no bloco `§8.2`):** `org:targetMaturityLevel` (L619, ObjectProperty, domain `ref:ReferenceCapability`, range `ref:MaturityLevel`). Não é divergência, é conteúdo do Recorte 3 (era stub) preservado dentro do bloco §8.2. Registrado para transparência.

**Status do Bloco 5: 100% confere.**

### Bloco 6 — Vocabulário de mudança organizacional completo | §8.12 | commit `f09dc6a`

O checklist da tarefa enumera: "papéis Change*, InterventionStatus, ResistanceFactor + 5 subclasses + 3 propriedades, 5 subclasses de Artifact de §8.12.7". Note-se que os papéis Change* (§8.12.2) e InterventionStatus (§8.12.3) já foram extraídos no Recorte 1 (commit `820974d`) e reaparecem aqui apenas para conferência de completude. §8.12.4 e §8.12.7 são os itens novos do Recorte 4.

| Item esperado | Seção | Encontrado (linha) | Status |
|---|---|---|---|
| `ref:ChangeSponsor` (BusinessRole) | §8.12.2 | L89 explicit | confere |
| `ref:ChangeAgent` (BusinessRole) | §8.12.2 | L93 explicit | confere |
| `ref:ChangeEndUser` (BusinessRole) | §8.12.2 | L97 explicit | confere |
| `ref:ChangeResistor` (BusinessRole) | §8.12.2 | L101 explicit | confere |
| `ref:InterventionStatus` (Class + 5 individuals: Proposed/Approved/InProgress/Concluded/Cancelled) | §8.12.3 | L108-118 | confere |
| `ref:ResistanceFactor` (Class) | §8.12.4 | L687 explicit | confere |
| `ref:CulturalResistance` (subclasse) | §8.12.4 | L689 explicit + subClassOf | confere |
| `ref:PoliticalResistance` (subclasse) | §8.12.4 | L692 explicit + subClassOf | confere |
| `ref:CognitiveResistance` (subclasse) | §8.12.4 | L695 explicit + subClassOf | confere |
| `ref:EmotionalResistance` (subclasse) | §8.12.4 | L698 explicit + subClassOf | confere |
| `ref:CapacityResistance` (subclasse) | §8.12.4 | L701 explicit + subClassOf | confere |
| `ref:exhibitsResistance` (ObjectProperty) | §8.12.4 | L704 explicit | confere |
| `ref:affectsIntervention` (ObjectProperty) | §8.12.4 | L705 explicit | confere |
| `ref:resistanceSeverity` (DatatypeProperty) | §8.12.4 | L706 explicit | confere |
| `ref:CommunicationPlan` (subclasse de Artifact) | §8.12.7 | L712 implicit via subClassOf | confere |
| `ref:StakeholderMap` (subclasse) | §8.12.7 | L713 implicit | confere |
| `ref:SponsorshipChecklist` (subclasse) | §8.12.7 | L714 implicit | confere |
| `ref:ResistanceLog` (subclasse) | §8.12.7 | L715 implicit | confere |
| `ref:ChangeTrainingPlan` (subclasse) | §8.12.7 | L716 implicit | confere |

**Contagens: papéis Change* = 4 ✓; ResistanceFactor + 5 subclasses = 6 ✓; 3 propriedades (exhibits/affects/severity) = 3 ✓; 5 subclasses de Artifact §8.12.7 = 5 ✓.**

A atenção especial pedida pela tarefa ("o Registro já registra precedente de descompasso entre checklist e conteúdo real") não achou divergência em §8.12: o Recorte 4 (commit `f09dc6a`) foi feito com o padrão de uma linha por declaração e URI no início da linha, portanto imune à corrupção que afetou §7.3 (Bloco 2 Achado A) e §8.9.1 (Bloco 2 Achado B).

**Status do Bloco 6: 100% confere.**

### Resumo consolidado da Parte 1

| Bloco | Itens verificados | Confere | Diverge | Achados adicionais |
|---|---:|---:|---:|---:|
| 1 — SHACL shapes | 16 | 16 | 0 | 0 |
| 2 — Vocabulário base + §8.9.1 | 38 | 35 | 3 | 1 (AlgedonicAlert restriction perdida) |
| 3 — pcf/naics/mgmt/Microactivity | 32 | 32 | 0 | 0 (2 observações sem gravidade) |
| 4 — MaturityLevel/GapType/Artifact | 27 | 27 | 0 | 0 |
| 5 — ReferenceCapability | 9 | 9 | 0 | 1 (org:targetMaturityLevel presente, esperado) |
| 6 — Mudança organizacional §8.12 | 19 | 19 | 0 | 0 |
| **Total** | **141** | **138** | **3** | **2** |

Todas as divergências e o achado adicional relevante (Bloco 2 A) são do mesmo tipo mecânico: statement Turtle colado a comentário `#` na mesma linha física, perdido silenciosamente pelo parser sem erro nem warning. É a mesma classe de corrupção que o cabeçalho de `shapes.ttl` (linhas 5-13) descreve como corrigida em Recorte 1, mas a mesma correção não foi aplicada em duas ocorrências dentro do próprio `tbox-local.ttl` (linhas 58 e 80).

---

## Parte 2 — Auditoria de alinhamento gist/ArchiMate (item 8 do Registro)

**Método:** enumerar toda URI nos namespaces `ref:`, `mgmt:`, `pcf:` de `tbox-local.ttl` que qualifique como classe (declaração explícita `owl:Class` OU aparição como sujeito/objeto de `rdfs:subClassOf`), percorrer `rdfs:subClassOf` até profundidade 2 (direto e um salto adicional), reportar se termina em `gist:` ou `archimate:`.

**Nota de escopo:** o namespace `mgmt:` no arquivo contém apenas indivíduos (instâncias) — nenhuma classe é declarada em `mgmt:`. Portanto a lista mgmt: aparece vazia em ambas as categorias. Isso não é ausência de dado, é a arquitetura definida no cabeçalho do Recorte 2 (linhas 452-455): "mgmt: não contém classes — só indivíduos nomeados das classes ref: declaradas acima".

Total de candidatos: **56 classes** (`ref:` = 45, `pcf:` = 6, `mgmt:` = 0, mais 5 subclasses setoriais e outras herdadas).

### 2.1 Alinhadas (35 classes com ancestral `gist:` ou `archimate:` em ≤ 2 saltos)

| Classe | Caminho |
|---|---|
| `ref:AnalyticalFramework` | `ref:AnalyticalFramework → ref:ManagementFramework → gist:Specification` |
| `ref:Artifact` | `ref:Artifact → gist:Specification` |
| `ref:BSCDashboard` | `ref:BSCDashboard → ref:Artifact → gist:Specification` |
| `ref:CTQTree` | `ref:CTQTree → ref:Artifact → gist:Specification` |
| `ref:CanvasBMC` | `ref:CanvasBMC → ref:Artifact → gist:Specification` |
| `ref:ChangeAgent` | `ref:ChangeAgent → archimate:BusinessRole` |
| `ref:ChangeEndUser` | `ref:ChangeEndUser → archimate:BusinessRole` |
| `ref:ChangeResistor` | `ref:ChangeResistor → archimate:BusinessRole` |
| `ref:ChangeSponsor` | `ref:ChangeSponsor → archimate:BusinessRole` |
| `ref:ChangeTrainingPlan` | `ref:ChangeTrainingPlan → ref:Artifact → gist:Specification` |
| `ref:CommunicationPlan` | `ref:CommunicationPlan → ref:Artifact → gist:Specification` |
| `ref:ConceptualModel` | `ref:ConceptualModel → ref:ManagementFramework → gist:Specification` |
| `ref:DMAICTemplate` | `ref:DMAICTemplate → ref:Artifact → gist:Specification` |
| `ref:DiscreteManufacturingCapability` | `ref:DiscreteManufacturingCapability → ref:ReferenceCapability → archimate:Capability` |
| `ref:DistributionWholesaleCapability` | `ref:DistributionWholesaleCapability → ref:ReferenceCapability → archimate:Capability` |
| `ref:FMEAWorksheet` | `ref:FMEAWorksheet → ref:Artifact → gist:Specification` |
| `ref:Intervention` | `ref:Intervention → gist:Project` |
| `ref:KPI` | `ref:KPI → gist:Magnitude` |
| `ref:ManagementFramework` | `ref:ManagementFramework → gist:Specification` |
| `ref:ManagementSystem` | `ref:ManagementSystem → ref:ManagementFramework → gist:Specification` |
| `ref:Methodology` | `ref:Methodology → ref:ManagementFramework → gist:Specification` |
| `ref:Microactivity` | `ref:Microactivity → gist:Specification` |
| `ref:OKRSheet` | `ref:OKRSheet → ref:Artifact → gist:Specification` |
| `ref:ProfessionalServicesCapability` | `ref:ProfessionalServicesCapability → ref:ReferenceCapability → archimate:Capability` |
| `ref:RACIMatrix` | `ref:RACIMatrix → ref:Artifact → gist:Specification` |
| `ref:ReferenceCapability` | `ref:ReferenceCapability → archimate:Capability` |
| `ref:ResistanceLog` | `ref:ResistanceLog → ref:Artifact → gist:Specification` |
| `ref:RetailCapability` | `ref:RetailCapability → ref:ReferenceCapability → archimate:Capability` |
| `ref:RiskHeatmap` | `ref:RiskHeatmap → ref:Artifact → gist:Specification` |
| `ref:SIPOCDiagram` | `ref:SIPOCDiagram → ref:Artifact → gist:Specification` |
| `ref:SponsorshipChecklist` | `ref:SponsorshipChecklist → ref:Artifact → gist:Specification` |
| `ref:StakeholderMap` | `ref:StakeholderMap → ref:Artifact → gist:Specification` |
| `ref:Standard` | `ref:Standard → ref:ManagementFramework → gist:Specification` |
| `ref:Technique` | `ref:Technique → ref:ManagementFramework → gist:Specification` |
| `ref:ValueStreamMap` | `ref:ValueStreamMap → ref:Artifact → gist:Specification` |

**Notas sobre a lista alinhada:**

- Todas as âncoras `gist:` usadas: `gist:Specification` (majoritária, via ManagementFramework e Artifact), `gist:Project` (Intervention), `gist:Magnitude` (KPI). Nenhuma âncora em `gist:Category` ou `gist:Agreement` ou `gist:Event`.
- `gist:Event` é usado por `org:AlgedonicAlert` (fora deste conjunto porque está no namespace `org:`, não em ref/mgmt/pcf) e como `rdfs:domain` de `vsm:targetFunction`.
- Todas as âncoras `archimate:` usadas: `archimate:Capability` e `archimate:BusinessRole`. Nenhuma âncora em `archimate:BusinessProcess`, `archimate:BusinessFunction`, `archimate:BusinessActor`, `archimate:Stakeholder`, `archimate:Goal`, `archimate:Driver`, `archimate:Constraint`, apesar de estas serem referenciadas como domain/range de propriedades e como target de SHACL shapes.

### 2.2 Não alinhadas (21 classes sem ancestral `gist:` ou `archimate:` em ≤ 2 saltos)

| Classe | Pais diretos (`rdfs:subClassOf`) |
|---|---|
| `pcf:PCFNode` | (nenhum) — âncora local |
| `pcf:ProcessCategory` | `pcf:PCFNode` (não alinhado) |
| `pcf:ProcessGroup` | `pcf:PCFNode` |
| `pcf:Process` | `pcf:PCFNode` |
| `pcf:Activity` | `pcf:PCFNode` |
| `pcf:Task` | `pcf:PCFNode` |
| `ref:BSCPerspective` | (nenhum) — enumerada, `owl:oneOf` |
| `ref:CapacityResistance` | `ref:ResistanceFactor` (não alinhado) |
| `ref:ChangeReadinessAssessment` | (nenhum) |
| `ref:CognitiveResistance` | `ref:ResistanceFactor` |
| `ref:Competence` | (nenhum) |
| `ref:CulturalResistance` | `ref:ResistanceFactor` |
| `ref:EmotionalResistance` | `ref:ResistanceFactor` |
| `ref:FrameworkPhase` | (nenhum) |
| `ref:GapType` | (nenhum) — enumerada por instâncias |
| `ref:InterventionStatus` | (nenhum) — enumerada, `owl:oneOf` |
| `ref:MaturityLevel` | (nenhum) — enumerada, `owl:oneOf` |
| `ref:PhaseScore` | (nenhum) — reificação |
| `ref:PoliticalResistance` | `ref:ResistanceFactor` |
| `ref:ResistanceFactor` | (nenhum) |
| `ref:Threshold` | (nenhum) |

**Padrões observáveis (não decisões):**

1. **Classes enumeradas / de classificação** — `ref:MaturityLevel`, `ref:GapType`, `ref:InterventionStatus`, `ref:BSCPerspective` — todas sem ancestral. Seguem o mesmo padrão sintático de `org:ManagementDimension` (que é explicitamente marcada como "provisória" no cabeçalho e no Registro §1 item 1). Se o item 1 do Registro sobre `org:ManagementDimension` é decisão em aberto, então por analogia estas quatro estão implicitamente na mesma situação. Nenhuma delas está no Registro §1 hoje.
2. **Reificação** — `ref:PhaseScore` é reificação de score de fase, sem ancestral. Comportamento esperado para uma reificação; alinhamento a gist/ArchiMate teria que ser explícito (ex: `gist:Content` ou uma classe de "assessment result").
3. **Estruturais sem ancestral** — `ref:Competence`, `ref:FrameworkPhase`, `ref:Threshold`, `ref:ChangeReadinessAssessment`, `ref:ResistanceFactor` — cinco classes de natureza estrutural (§8.9, §8.11, §8.12) que não herdam de nada gist/archimate. As cinco subclasses de `ref:ResistanceFactor` herdam apenas dela, herdando o não-alinhamento (mesmo padrão).
4. **`pcf:` inteira** — `pcf:PCFNode` é âncora local do namespace; suas 5 subclasses herdam apenas dela. Não há ancoragem gist/archimate na taxonomia PCF, o que é uma decisão pragmática (PCF é catálogo externo com sua própria semântica), mas não há registro explícito dessa decisão no Registro §1.

**Nota metodológica:** a auditoria percorreu apenas `rdfs:subClassOf`. Não percorreu:
- `owl:equivalentClass` — várias classes usam `owl:equivalentClass [ owl:oneOf ... ]` para enumeração fechada; isso não é ancoragem em gist/archimate.
- Propriedades de anotação como `skos:broader` ou `dc:conformsTo` — nenhuma classe em ref/mgmt/pcf usa essas para vincular a gist/archimate no arquivo atual.
- Ancoragem via propriedades `owl:` (ex: `owl:Restriction`) — a única restrição do arquivo (AlgedonicAlert → S5) está comentada out (Bloco 2 Achado A).

O item 8 do Registro pergunta se cada classe carrega "alinhamento explícito (`rdfs:subClassOf`) a `gist:`/`archimate:`". A resposta desta auditoria é: **35 sim, 21 não**. Isso é o insumo mecânico. A decisão do item 8 (entre "auditoria SPARQL de cobertura" ou "propriedade de anotação SKOS de natureza") permanece com o consultor.

---

## Ambiguidades reportadas, não resolvidas

Nada de URI parecida-mas-não-idêntica foi encontrado nesta auditoria (nenhum caso de `ref:Xxxx` vs `Ref:Xxxx` ou similar). As três divergências reportadas no Bloco 2 são de conteúdo ausente, não de URI ambígua.

## Convite explícito para decisão

Esta auditoria não corrige nada. Os pontos que aguardam decisão do consultor:

1. **Bloco 2 Achado A (linha 58, restrição AlgedonicAlert → S5 dentro de comentário):** aplicar a mesma correção mecânica do Recorte 1 (quebrar a linha entre `# ... .` e o statement), ou aceitar que Shape 11 já garante o comportamento e remover o statement comentado por completo?
2. **Bloco 2 Achado B (linha 80, três subclasses CHA dentro de comentário):** aplicar quebra mecânica de linha? Se sim, aproveitar para aplicar o relabel acentuado (item 5 do Registro §1) na mesma passada?
3. **Registro §1 item 5:** a redação hoje pressupõe que as três subclasses CHA existem no grafo — precisa atualizar para refletir que estão ausentes.
4. **Parte 2:** decidir entre (a) tratar cada uma das 21 classes não-alinhadas como pendência individual, (b) adotar propriedade de anotação SKOS de "natureza" como proposto no item 8, ou (c) declarar 21 exceções documentadas e seguir. Nenhuma opção precisa ser tomada agora; a auditoria só produziu o insumo.

---

**Fim do relatório.**
