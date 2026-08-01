# CLAUDE.md — regras de sessão para este repositório

- Não editar `tbox-local.ttl` nem `shapes.ttl` sem instrução explícita na sessão em curso.
- Não commitar sem instrução explícita.
- Resultado de verificação (skill de auditoria, pyshacl, testes) volta como saída de comando não editada, nunca como resumo narrado.
- A lógica da auditoria de processo vive em `auditoria/audit.py`; os critérios que ela verifica vivem em `auditoria/Criterios_Skill_Auditoria_v0_1.md` e não são redefinidos fora daquele documento.
