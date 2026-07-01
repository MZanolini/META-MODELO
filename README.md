# camada25-ontologia

Repositório de ontologia da Camada 2.5 (Camada de Conhecimento de Referência).

## shapes.ttl

16 SHACL NodeShapes extraídas de `Arquitetura_Ontologica_Empresarial_v1_3.docx`, §9 (Shapes 01–12,
15–16), §8.9.3 (Shape 13) e §8.10.2 (Shape 14).

- **Origem**: Arquitetura Ontológica Empresarial v1.3
- **Data de extração**: 2026-07-01
- **Método**: extração determinística (correção de link markdown `[url](url)` → `<url>` e restauração
  de quebras de linha entre comentário e statement Turtle — ambas mecânicas, sem alteração de
  conteúdo semântico) + uma resolução explícita de ambiguidade de formatação na Shape 14
  (documentada no cabeçalho do próprio `shapes.ttl`).
- **Validação**: `pyshacl` (modo `advanced=True`, necessário pelas SPARQL constraints das Shapes
  07, 10, 13, 16) — parse e carga bem-sucedidos, 16/16 NodeShapes reconhecidas. Validado apenas
  contra grafo de dados vazio; não validado contra dados reais (isso depende do triplestore/TBox,
  ainda pendentes — ver Mapa de Gap).
- **Status**: rascunho de extração, não validado pelo consultor quanto à correção semântica do
  conteúdo original (só a fidelidade da transcrição foi verificada).

## Próximo passo

Extração do TBox (classes e propriedades fora das shapes) — não incluído neste commit.
