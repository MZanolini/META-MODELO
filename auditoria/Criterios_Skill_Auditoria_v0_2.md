# Critérios da Skill de Auditoria de Processo, v0.2

**Status**: proposto (v0.1), emendado (v0.2)
**Data**: 2026-07-31; emenda 2026-08-11
**Pacote**: S01a do backlog de M1 (ADR-002 §4); emenda na sessão S01b-fix
**Decisor**: consultor (Marcelo Zanolini), em sessão de chat de 2026-07-31; emenda decidida em sessão de 2026-08-11
**Escopo**: processo de construção do programa. Não é escopo de Camada 2.5 e não vai no Registro.
**Entrada para**: S01b, implementação em Claude Code com Sonnet 5 contra esta especificação.
**Estado de partida assumido**: repositório `https://github.com/MZanolini/META-MODELO.git`, branch `main`, HEAD `7111e03`; `tbox-local.ttl` com 833 triplas; `shapes.ttl` com 16 NodeShapes; `pyshacl advanced=True` conformando sem violação; Registro com 162 linhas.
**Emenda v0.2 (2026-08-11)**: sessão S01b-fix corrige dois defeitos de implementação da checagem 1 (o `sha256` do baseline não vinha de medição; o diff de sujeitos não canonicalizava blank node) e emenda o critério da checagem 7 para comparar conteúdo normalizado quanto a fim de linha — ver nota ao final da seção da checagem 7. Registrado como item 21 do Registro de Pendências.

---

## 1. Propósito e fronteira

Este documento fixa os critérios das sete checagens que o ADR-002 D4 enumera, para que a implementação não os defina. A restrição de D4 é literal: a skill não define os critérios que ela mesma verifica. O que a implementação decide é como executar; o que este documento decide é o que conta como aprovação, o que conta como reprovação e o que a aprovação não autoriza concluir.

A skill de auditoria de processo é distinta do agente de Auditoria do produto (ADR-002 D3). Aquele emite veredito sobre asserção alheia dentro da cadeia diagnóstica e tem uma camada de julgamento semântico confiada a LLM. Esta é integralmente determinística e verifica o estado dos artefatos do próprio programa. A fronteira segue a diretriz da §7 do documento de calibração: automatizar agora a camada determinística, que é reaproveitável, e não recriar informalmente a camada adversarial de julgamento fora do pipeline formal.

O modo de falha que a skill existe para atacar está documentado no ADR-002 §5.3, com quatro instâncias independentes: o projeto produz desenho mais rápido do que reconcilia desenho no artefato único verificável por máquina, e peças corretas permanecem fora da ontologia por meses sem que nada sinalize a ausência. As checagens 5 e 6 são as que atacam diretamente esse modo. As demais protegem contra regressão.

---

## 2. Decisões transversais

Três decisões fechadas em 2026-07-31, cada uma com fundamento e gatilho de revisão, porque governam campos de todas as sete checagens.

### 2.1 Perfil de execução

A skill tem um núcleo único e dois perfis de invocação, porque nenhum ambiente alcança as três origens de insumo. O Cowork alcança a pasta canônica e o clone nativo, e não alcança os anexos do Project. A sessão de chat com ambiente de código alcança os anexos e consegue clonar o repositório, e não alcança a pasta canônica.

| Perfil | Alcança | Checagens completas | Checagens parciais ou indeterminadas |
|---|---|---|---|
| `repositorio` (Cowork ou Claude Code) | clone nativo, pasta canônica | 1, 2, 3, 4, 6 | 5 sem os documentos que só existem como anexo; 7 sem o lado do anexo |
| `sessao` (chat do Project com ambiente de código) | anexos do Project, clone nativo | 1, 2, 3, 4, 5, 6, 7 | 5 sem os documentos que só existem na pasta canônica |

Toda execução declara no cabeçalho do relatório qual perfil rodou e quais checagens ficaram parciais. *Fundamento*: um relatório verde produzido por um perfil que não enxergava metade das entradas é pior que nenhum relatório, porque cria confiança sem lastro. *Gatilho de revisão*: se a pasta canônica passar a ser alcançável da mesma sessão que alcança os anexos, os dois perfis colapsam em um.

### 2.2 Referência durável

Toda referência entre execuções vive em `auditoria/baseline.json`, versionado no repositório. A alternativa considerada foi guardar na pasta canônica, sem versionamento, o que dispensa commit e perde durabilidade entre ambientes, reproduzindo em miniatura o problema que a skill existe para resolver.

A skill nunca escreve no baseline. Mover o baseline é ato explícito do consultor, feito depois de uma execução aprovada, e é ele que constitui o registro de que aquele estado foi auditado. *Fundamento*: se a skill movesse o baseline sozinha, uma remoção silenciosa passaria a ser silenciosamente aceita na execução seguinte, e a checagem 3 perderia o sentido. *Gatilho*: se o custo fixo de clonar e commitar (calibração §8) tornar a atualização do baseline tão cara que ela deixe de ser feita, avaliar migrar a atualização para CI no GitHub Actions.

### 2.3 Estados, severidade e o princípio dos limiares

Quatro estados por checagem. **PASSA** é conformidade verificada. **AVISO** é dívida conhecida, registrada e contada, que não bloqueia. **FALHA** é regressão ou entrada nova fora de conformidade, que bloqueia. **INDETERMINADO** é entrada ausente ou ambiente insuficiente, e nunca é aprovação.

O código de saída é diferente de zero em qualquer FALHA ou INDETERMINADO. O veredito global é o pior estado entre as sete.

O princípio que governa todos os limiares é que **a skill barra o novo e conta o conhecido**. Falha dura sinaliza regressão introduzida desde o último marco auditado; dívida herdada e declarada vira aviso contável, com o número impresso a cada execução. O motivo é operacional: se lacuna conhecida for falha dura, a skill reprova em toda execução até S06 fechar, e uma checagem que sempre reprova deixa de ser lida.

A severidade por sensibilidade do alvo segue a §6.2 do documento de calibração. Desvio em `tbox-local.ttl`, `shapes.ttl` ou no Registro escala sempre. Desvio em documento auxiliar registra.

---

## 3. Estrutura do baseline

O esquema abaixo é normativo quanto aos campos, não quanto ao formato de serialização.

| Chave | Conteúdo | Alimenta |
|---|---|---|
| `commit_auditado` | hash do commit aprovado na última execução | 1, 3 |
| `tbox.triplas`, `tbox.sha256` | contagem e hash do arquivo naquele commit | 1 |
| `shapes.nodeshapes` | contagem de NodeShapes naquele commit | 2 |
| `ferramentas` | versões de rdflib, pyshacl e do extrator de `.docx` | 2, 6 |
| `proveniencia.isentos` | URIs isentos, nominalmente, com motivo | 4 |
| `asercoes_contaveis` | documento, âncora, regra de contagem | 5 |
| `versoes_vigentes` | documento, versão vigente, natureza (congelado ou vivo) | 5 |
| `isencoes_citacao_historica` | padrões textuais que isentam citação a versão antiga | 5 |
| `cobertura.triagem` | identificador, estado de triagem, fundamento, pacote alvo | 6 |
| `correspondencia` | documento, caminho no anexo, no repositório e na pasta canônica, e se é fonte de verdade de sessão | 7 |

---

## 4. As sete checagens

### Checagem 1: contagem de triplas

**Mede** a variação de volume do `tbox-local.ttl` desde o commit auditado, e se essa variação é explicável.

**Entradas**: `tbox-local.ttl` do clone nativo no HEAD, nunca do caminho FUSE; `commit_auditado`, `tbox.triplas` e `tbox.sha256` do baseline. Se o clone falhar, o arquivo não existir ou o parse com rdflib abortar, o resultado é INDETERMINADO com o motivo impresso, e a checagem 2 não roda.

**Referência**: 833 triplas no commit `7111e03`, guardadas no baseline, movidas apenas por ato explícito do consultor.

**Saída ao passar**: commit base, commit atual, contagem base, contagem atual, delta e sha256 do arquivo. **Ao falhar**: os mesmos campos, mais a diferença de conjuntos de sujeitos entre os dois grafos, com os sujeitos adicionados e os removidos nomeados por URI e a contagem de triplas por sujeito, para que o delta seja reconciliável aritmeticamente sem reabrir o arquivo, como foi feito à mão na auditoria do Recorte 7.

**Limiar**: contagem menor que a do baseline é FALHA. Contagem igual com sha256 diferente é FALHA, porque significa substituição de conteúdo com volume preservado, que é o caso que passaria despercebido. Contagem maior é AVISO, com o delta e os sujeitos novos impressos para justificativa humana no fecho do pacote. Delta zero com hash igual é PASSA.

**Não cobre**: se as triplas novas estão corretas; se o que deveria existir existe, que é a checagem 6; e alterações em `shapes.ttl`, cuja integridade é medida pela checagem 2.

**Emenda de 2026-08-11 (v0.2).** A checagem 1 compara o conteúdo do `tbox-local.ttl` na cópia de trabalho, normalizado quanto a fim de linha (`\r\n` e `\r` convertidos em `\n`) antes do cálculo do sha256, e não os bytes crus do arquivo nem o blob armazenado pelo Git. Fundamento: a cópia de trabalho em Windows carrega CRLF por `core.autocrlf=true` enquanto o blob guarda LF, de modo que hashear bytes crus reprova por forma de transporte, e hashear o blob perde a sensibilidade a edição ainda não commitada, que é justamente o que esta checagem existe para detectar. O delta de sujeitos é apurado por `graph_diff` sobre grafos canonicalizados, em três categorias: sujeito nomeado por URI adicionado, sujeito nomeado por URI removido, e sujeito nomeado por URI que permanece mas teve triplas alteradas; estruturas anônimas entram apenas em agregado, por isomorfismo. O que esta checagem deixa de cobrir a partir daqui: divergência de fim de linha no próprio `tbox-local.ttl`. Gatilho de revisão: o mesmo do item 21 do Registro.

### Checagem 2: validação SHACL

**Mede** a conformidade estrutural do tbox contra as shapes, com o conjunto de shapes verificadamente intacto.

**Entradas**: `tbox-local.ttl` e `shapes.ttl` do clone; versões de rdflib e pyshacl declaradas no baseline. A execução é obrigatoriamente com `advanced=True`, por causa das constraints `sh:sparql`. Se a versão instalada divergir da do baseline em patch ou minor, o resultado vale e sai com AVISO trazendo as duas versões; se divergir em major, é INDETERMINADO, porque a comparação com a execução anterior deixa de ser legítima.

**Referência**: `Conforms: True`, zero violações e 16 NodeShapes efetivamente avaliadas.

**Saída ao passar**: a linha de conformidade, o número de NodeShapes avaliadas, as versões das bibliotecas. **Ao falhar**: o relatório bruto do pyshacl, não editado nem resumido, mais focus node, path e mensagem por violação. A regra de saída bruta é a mesma do ajuste 3 da §6 da calibração e existe porque relay narrado introduz alegação não verificável.

**Limiar**: qualquer resultado de severidade `sh:Violation` é FALHA. Falha de parse de qualquer dos dois arquivos é FALHA. Contagem de NodeShapes diferente de 16 é FALHA mesmo com `Conforms: True`, porque conformidade obtida com menos shapes é verde trivial e é exatamente como uma shape apagada passaria. Resultados `sh:Warning` e `sh:Info` são AVISO contado, o que prepara a proposta de shapes informativos do item 19 do Registro.

**Não cobre**: verdade semântica, já que um grafo pode conformar e ainda assim afirmar coisa errada; e a lacuna que não viola shape alguma, que é justamente a classe de problema registrada no item 19 e endereçada pela checagem 6.

### Checagem 3: diff aditivo

**Mede** se alguma tripla preexistente foi removida ou alterada entre o commit auditado e o HEAD.

**Entradas**: `git diff` entre o commit do baseline e o HEAD, restrito aos arquivos `.ttl`; e os dois grafos carregados em rdflib para comparação de conjuntos de triplas. Se o commit base não estiver no clone por profundidade insuficiente, refazer o clone com profundidade suficiente; persistindo a ausência, INDETERMINADO.

**Referência**: o invariante de que o conjunto de triplas do commit base é subconjunto do conjunto do HEAD.

**Saída ao passar**: inserções, remoções e hunks do diff textual, mais a afirmação explícita de zero triplas removidas em nível de grafo. **Ao falhar**: cada tripla presente na base e ausente no HEAD, serializada, mais as linhas textuais correspondentes com o commit que as introduziu, obtido por `git blame`.

**Limiar**: qualquer tripla removida é FALHA, salvo remoção declarada na invocação com motivo, que vira AVISO e entra no relatório com o motivo transcrito. Remoção textual sem perda de tripla, como reordenação ou reformatação, é AVISO. O diff textual é o sensor barato e o diff de grafo é a autoridade: divergência entre os dois é reportada, não arbitrada.

**Não cobre**: remoção ocorrida em commit intermediário caso o baseline tenha andado sem auditoria, motivo pelo qual o baseline só se move por ato explícito; e alteração em documentos, já que o escopo é o grafo.

### Checagem 4: cobertura de proveniência

**Mede** quantos indivíduos de conteúdo curado carregam as quatro triplas de proveniência: `prov:wasGeneratedBy`, `prov:generatedAtTime`, `prov:wasDerivedFrom` e `org:confidenceLevel`.

**Entradas**: `tbox-local.ttl` do clone e a lista nominal de isentos no baseline. O universo avaliado precisa ser explícito, senão a checagem mede outra coisa: são sujeitos que têm `rdf:type` apontando para classe do vocabulário local e que não são eles próprios `owl:Class`, `owl:ObjectProperty`, `owl:DatatypeProperty` nem `sh:NodeShape`. Vocabulário não leva proveniência de instância; conteúdo curado leva.

**Referência**: zero faltantes fora da lista de isentos, e lista de isentos com exatamente os 14 sujeitos `mgmt:` registrados no item 14 do Registro, na correção factual de 2026-07-25.

**Saída ao passar**: quantos com as quatro triplas completas, quantos isentos nominalmente, e a afirmação de zero faltantes fora da lista. **Ao falhar**: URI de cada sujeito faltante e quais das quatro triplas faltam nele.

**Limiar**: sujeito criado após o baseline sem as quatro triplas é FALHA. Crescimento da lista de isentos é FALHA, porque isenção nova é dívida nova disfarçada de exceção. Os 14 isentos são AVISO contado a cada execução, para a dívida permanecer visível até o gatilho do item 14 disparar.

**Não cobre**: se a proveniência é verdadeira, isto é, se `prov:wasDerivedFrom` aponta para a fonte que de fato sustenta a instância, que é julgamento semântico e pertence à camada de LLM do agente de Auditoria em D3; nem se o `org:confidenceLevel` atribuído é o adequado, que é o item 18 do Registro e está deliberadamente adiado.

### Checagem 5: números autorreferentes

**Mede** se cada número que um documento afirma sobre si mesmo bate com o que o documento contém, e se cada citação a documento versionado aponta para a versão vigente.

**Entradas**: dois conjuntos. O primeiro são as asserções contáveis registradas no baseline, cada uma com documento, âncora do número e regra de contagem. O segundo é o índice de versões vigentes, derivado dos cabeçalhos dos documentos. A origem varia por perfil: o perfil `sessao` lê os anexos, o perfil `repositorio` lê a pasta canônica e o clone. Documento não alcançável pelo perfil corrente produz INDETERMINADO naquela linha, nunca PASSA.

**Referência**: o baseline, nas chaves `asercoes_contaveis`, `versoes_vigentes` e `isencoes_citacao_historica`, mais a classificação de natureza por documento. Documento **congelado** é registro datado de uma decisão ou de uma verificação, como ADR aceita e relatório de auditoria. Documento **vivo** orienta trabalho futuro e é reescrito, como as instruções do Project, a calibração, o Registro e a Arquitetura.

**Saída ao passar**: por linha, documento, âncora, valor afirmado, valor contado e veredito. **Ao falhar**: os mesmos campos mais o trecho literal em que o número aparece, com número de linha, para o reparo ser feito sem reabrir o arquivo.

**Limiar**: em documento vivo, divergência de contagem é FALHA e ponteiro de versão desatualizado é FALHA, porque uma sessão futura sem contexto vai buscar a versão errada e agir sobre ela. Em documento congelado, ambos são AVISO, com recomendação de nota de errata ao fim do documento e nunca de edição do corpo, porque corrigir o corpo de uma ADR aceita destrói o registro do que foi decidido e quando. Citação a versão antiga isenta por padrão textual reconhecido, como "vX e anteriores" ou marcação explícita de historicidade, é PASSA, e a lista de padrões vive no baseline e é ampliável.

**Casos de teste obrigatórios da v0.1**. Dois defeitos foram deixados no lugar de propósito em 2026-07-28 e servem de caso real que ninguém plantou. A citação do ADR-002 §4 ao "documento de calibração v0.2" está em documento congelado e deve sair como AVISO. As citações à v0.3 nas linhas 126 e 169 do arquivo de instruções estão em documento vivo e devem sair como FALHA. A distinção não é sobre gravidade do erro, é sobre qual reparo é legítimo. Somam-se os defeitos já confirmados da Arquitetura v1.3, todos em documento vivo e portanto FALHA: "20 Competency Questions" nas linhas 36 e 923 contra 49 efetivamente listadas, "12 NodeShapes" na linha 1395 contra 16, e a referência órfã a "v3.1" na linha 1403. A execução que não reproduzir esses cinco vereditos não está implementada corretamente.

**Não cobre**: número que se refere a coisa fora do corpus, como a velocidade medida ou as datas de marco; coerência entre dois documentos sobre um mesmo fato que não seja contagem nem ponteiro de versão; e se o número é o certo em substância, já que a checagem só afere consistência interna.

### Checagem 6: cobertura da Arquitetura contra o tbox

**Mede** quais identificadores de vocabulário local citados na Arquitetura não existem no grafo, e se algum deles ainda não foi triado.

**Entradas**: o texto da Arquitetura vigente, extraído por um extrator único fixado no baseline junto com sua versão, porque o perfil `sessao` lê a renderização em texto que o Project expõe e o perfil `repositorio` leria o `.docx` da pasta canônica, e dois extratores diferentes produzem listas diferentes; `tbox-local.ttl` e `shapes.ttl` do clone; e o registro de triagem no baseline. Prefixos em escopo: `ref:`, `org:`, `mgmt:`, `pcf:`, `demo:` e `vsm:`. Prefixos externos, contados à parte e sem efeito no veredito, porque sua ausência é esperada e tem gatilho próprio no item 1 do Registro: `gist:`, `archimate:`, `prov:`, `owl:`, `sh:`, `skos:` e `naics:`.

**Referência**: o registro de triagem, com quatro estados possíveis por identificador, cada um com fundamento em uma linha, e com o pacote alvo quando o estado for lacuna real.

| Estado | Significado | Exemplo medido em 2026-07-31 |
|---|---|---|
| `lacuna_real` | especificado e ausente, deve ser extraído | `ref:MaturityCriterion`, `ref:precedesFramework` |
| `exemplo_abox` | instância ilustrativa, não pertence ao TBox | `ref:tpl_FMEA_v2` |
| `mencao_rejeitada_ou_candidata` | citado como alternativa recusada ou candidato futuro | `ref:ChangeRole`, `ref:BodyOfKnowledge` |
| `fora_de_escopo_por_decisao` | especificado e deliberadamente não extraído | `ref:Tenant`, cortado por D9 |

**Saída ao passar**: total extraído, total presente no grafo, total ausente, decomposição dos ausentes por estado de triagem, e a lista nominal das lacunas reais ainda abertas com o pacote alvo de cada uma. **Ao falhar**: os identificadores ausentes e não triados, cada um com o trecho da Arquitetura em que aparece, para a triagem ser decidida sem reabrir o documento.

**Limiar**: identificador ausente e não triado é FALHA, e este é o invariante central da checagem, porque é ele que impede uma peça nova de entrar em silêncio. Crescimento da contagem de lacunas reais abertas sem entrada correspondente no registro de triagem é FALHA. Lacunas reais já triadas e ainda abertas são AVISO contado, com a lista impressa a cada execução até o pacote alvo fechar.

**Medição de referência**. Em 2026-07-31 a heurística foi rodada à mão sobre a v1.3 e o HEAD `7111e03`: 337 identificadores distintos extraídos, 305 presentes no grafo, 59 ausentes, dos quais 47 de prefixo local e 12 de vocabulário externo. Uma amostra de oito foi triada manualmente e resultou em quatro lacunas reais, três falsos positivos de três naturezas diferentes e um caso fora de escopo por decisão. A amostra é pequena e não sustenta extrapolação confiável da proporção, mas sustenta duas conclusões: o índice manual não é opção, porque o Checklist da Seção 2 do Registro é um índice manual e lista três peças não extraídas onde a heurística aponta dezenas de candidatos; e a heurística pura também não serve, porque reapresentar o ruído a cada execução treina o leitor a ignorar a saída.

**Correção de medição, 2026-08-19.** A medição de referência de 2026-07-31 acima fica registrada como está, e não fecha aritmeticamente: 305 presentes mais 59 ausentes somam 364 contra 337 extraídos, o que indica que pelo menos um dos três números foi apurado sobre base diferente, provavelmente ocorrências contra identificadores distintos. Medição por execução do instrumento, sobre a v1.3 e o HEAD `a443631`, depois do conserto da resolução de prefixo: 266 identificadores locais distintos extraídos, 212 presentes no grafo, 54 ausentes, mais 71 ocorrências de prefixo externo contadas à parte. Os 54 ausentes se distribuem em 13 de `org:`, 38 de `ref:` e 3 de `pcf:`. Fundamento do registro: a resolução de CURIE usava o mapa de namespaces do rdflib, que pré-vincula `org` ao vocabulário do W3C e sobrepõe a declaração do arquivo, o que produzia 31 ausências falsas. Gatilho de revisão: qualquer mudança nos prefixos declarados nos `.ttl`, ou a conclusão da triagem, o que vier primeiro.

**Consequência operacional a resolver antes da primeira execução**: enquanto os 47 identificadores locais não forem triados, a checagem 6 reprova por construção. A triagem é decisão curatorial e portanto não pertence ao S01b, que é implementação. As opções são triar em bloco numa sessão de chat própria, ou fazer o bootstrap com estado provisório presumido e converter em triagem definitiva ao longo dos pacotes. Decisão pendente do consultor.

**Não cobre**: peça especificada em prosa sem identificador em notação de prefixo; peça desenhada fora da Arquitetura, sendo o `EvidenceItem` do Manual de Diagnóstico §1.6 o caso conhecido e justamente a instância 3 da fragmentação, que esta checagem na v0.1 não pega; e se o identificador presente no grafo está definido corretamente ou apenas mencionado de passagem.

### Checagem 7: hash entre anexo, repositório e pasta canônica

**Mede** se a cópia do documento que orienta a sessão é a mesma que o repositório e a pasta canônica têm.

**Entradas**: o mapa de correspondência do baseline, com três caminhos por documento e a marcação de quais são fonte de verdade de sessão. Lado ausente produz INDETERMINADO para aquela linha, não PASSA.

**Referência**: igualdade de sha256 entre os lados existentes.

**Saída ao passar**: tabela com documento, hash por lado e veredito por linha. **Ao falhar**: a mesma tabela, mais data de modificação por lado e, para documento de texto, o número de linhas divergentes, o que dimensiona a divergência sem arbitrar qual lado está certo.

**Limiar**: divergência em documento marcado como fonte de verdade de sessão, hoje o Registro, o ADR-002 e a Arquitetura, é FALHA, porque a sessão inteira parte de premissa errada. Divergência em documento informativo é AVISO.

**Observação de escopo medida em 2026-07-31**: dos dez anexos do Project, apenas o `Registro_Pendencias_Camada25.md` tem contraparte no repositório, e os dois estavam idênticos nesta data. A checagem 7 como enunciada em D4, restrita a anexo contra HEAD, cobre portanto uma única linha. Por isso a especificação a estende ao par anexo contra pasta canônica quando não houver lado no repositório, sem o que a checagem seria quase inerte justamente para os documentos que mais orientam sessão, como o ADR-002 e a calibração.

**Não cobre**: qual lado está certo, apenas que divergem; e sincronia do espelho FUSE `camada25-ontologia/`, que é cópia manual conhecidamente defasada e não deve entrar no mapa de correspondência.

**Emenda de 2026-08-11 (v0.2).** A comparação entre cópias é feita sobre o conteúdo normalizado quanto a fim de linha: `\r\n` e `\r` são convertidos em `\n` antes do cálculo do sha256. Fundamento: as três cópias vivem em ambientes distintos (repositório em LF, pasta canônica em Windows, anexo do Project reprocessado no upload), e uma checagem que reprova por forma de transporte em vez de por conteúdo deixa de discriminar e ensina o operador a ignorar o próprio vermelho. O que esta checagem deixa de cobrir a partir daqui: divergência de fim de linha entre as cópias, que passa a sair como nota informativa sem alterar o veredito, e divergência de codificação, que nunca esteve coberta. Gatilho de revisão: aparecer divergência real de conteúdo mascarada pela normalização, ou passar a existir cópia em codificação distinta de UTF-8; reavaliar também na redação da Arquitetura v1.4, no pacote S07.

---

## 5. Relatório consolidado

O relatório abre com perfil de execução, data, commit avaliado, commit do baseline e versões das ferramentas. Segue com uma linha por checagem, no formato número, nome, estado e uma frase de resultado. Fecha com três contadores de dívida (isentos de proveniência, lacunas reais abertas, avisos de ponteiro de versão em documento congelado), o veredito global e o código de saída.

O relatório sai bruto. Quem executa a skill não resume a saída dela em prosa antes de devolver, pela mesma razão que a calibração já registra para o handoff com o Cowork: relay narrado introduz alegação não verificável no ponto exato em que a verificação era o objetivo.

---

## 6. O que a passagem das sete não autoriza concluir

A skill inteira é verificação estrutural. Uma execução integralmente verde afirma que o grafo não regrediu, que conforma às shapes existentes, que o conteúdo curado carrega proveniência, que os documentos são internamente consistentes nos números que declaram e que nenhuma peça citada na Arquitetura entrou em silêncio. Não afirma que o vocabulário está certo, que as classificações curadas são adequadas, que a proveniência registrada é verdadeira nem que a ontologia responde às Competency Questions. Essa é a distinção entre garantia estrutural, assegurável por máquina, e garantia semântica, assegurável por humano, e ela precisa aparecer no rodapé de todo relatório, senão a existência da skill produz exatamente a falsa confiança que ela deveria dissolver.

---

## 7. Limitações da v0.1 e gatilhos de revisão

| Limitação | Gatilho de revisão |
|---|---|
| Origem restrita à Arquitetura na checagem 6, deixando de fora o desenho que vive em manuais | promoção do `EvidenceItem` em S03, quando a lacuna passa a ter consequência direta |
| Extrator de `.docx` único a fixar, com risco de divergência entre perfis | primeira divergência observada entre execuções de perfis diferentes |
| Triagem inicial dos 47 identificadores locais não feita | primeira execução real da checagem 6 |
| Sobreposição com CI: as checagens 1 a 3 são candidatas a GitHub Actions, conforme §9 da calibração | se a skill passar a ser executada menos de uma vez por pacote que toca o repositório |
| Versões de rdflib e pyshacl pinadas no baseline | mudança de major em qualquer das duas |
| Checagem 4 poderia ser expressa como shape informativa, medida a cada validação | implementação da proposta de `sh:severity sh:Info` do item 19 do Registro, em S06 ou depois |

---

## 8. Entrada para o S01b

A implementação recebe esta especificação e não redefine nenhum critério dela. Três proibições explícitas valem para a skill em execução: ela não escreve no baseline, não corrige nenhum artefato que audita e não commita. Quando encontra divergência, ela relata e para. Alterar o estado auditado é ato do consultor, e é esse ato que constitui o registro de que o estado foi aceito.
