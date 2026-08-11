---
name: auditoria-processo
description: Roda as sete checagens deterministicas de auditoria de processo do META-MODELO (ADR-002 D4) sobre o estado atual do repositorio -- contagem de triplas, validacao SHACL, diff aditivo, cobertura de proveniencia, numeros autorreferentes, cobertura da Arquitetura contra o tbox, e hash entre anexo/repositorio/pasta canonica. Use quando o consultor pedir para auditar, verificar ou validar o estado do tbox-local.ttl, do shapes.ttl, do Registro ou da consistencia da documentacao antes de um commit, apos um recorte de curadoria, ou antes de fechar um pacote do backlog de M1.
---

# Skill de auditoria de processo

Invólucro fino sobre `auditoria/audit.py`. A lógica das sete checagens é
código determinístico ali; os critérios que ela verifica (o que conta como
PASSA, AVISO, FALHA, INDETERMINADO, e o que cada checagem não cobre) estão
em `auditoria/Criterios_Skill_Auditoria_v0_2.md`. Esta skill não repete
nem reinterpreta nenhum critério — se um resultado parecer errado, o
problema está no script ou no `baseline.json`, nunca em reler o critério
com outro julgamento.

## Quando invocar

Quando o consultor pedir para auditar, verificar ou validar o estado do
repositório, do `tbox-local.ttl`, do `shapes.ttl`, do Registro, ou a
consistência de números/versões na documentação — inclusive antes de um
commit, ao final de um recorte de curadoria, ou antes de fechar um pacote
do backlog.

## Como chamar

```bash
python auditoria/audit.py --repo . [--pasta-canonica CAMINHO] [--anexos CAMINHO] [--remocao-justificada "motivo"]
```

- `--pasta-canonica`: caminho local da pasta canônica, necessário para as
  checagens 5, 6 e parte da 7 alcançarem ADR-002, Instruções do Project,
  Arquitetura e Calibração. Sem ele, essas linhas saem INDETERMINADO.
- `--anexos`: caminho local com cópia dos anexos do Project, se disponível
  nesta sessão (perfil `sessao`).
- `--remocao-justificada`: só se o consultor autorizou explicitamente uma
  remoção de tripla nesta sessão (Checagem 3).
- Dependências: `pip install -r auditoria/requirements.txt`.

Código de saída diferente de zero em qualquer FALHA ou INDETERMINADO.

## Saída

A saída do script volta **bruta, sem editar e sem resumir em prosa**. Cole
o relatório completo na resposta ao consultor. Relatar e parar em qualquer
divergência é o comportamento correto — a skill não corrige o que audita,
não escreve no `baseline.json` e não commita. Mover o baseline para um
novo estado auditado é ato do consultor, feito fora desta skill.
