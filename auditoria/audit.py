#!/usr/bin/env python3
# Skill de auditoria de processo -- META-MODELO, pacote S01b (ADR-002 D4).
# Logica deterministica das sete checagens. Criterios normativos em
# Criterios_Skill_Auditoria_v0_1.md -- este arquivo nao os redefine.
#
# Proibicoes de execucao (Criterios Secao 8): esta skill nunca escreve no
# baseline, nunca corrige o que audita, nunca commita. Quando encontra
# divergencia, relata e para.

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import rdflib
import pyshacl
from rdflib import RDF, Namespace
from rdflib.namespace import SH
from rdflib.compare import graph_diff, to_isomorphic

PASSA, AVISO, FALHA, INDETERMINADO = "PASSA", "AVISO", "FALHA", "INDETERMINADO"
_SEVERITY = {PASSA: 0, AVISO: 1, INDETERMINADO: 2, FALHA: 3}

PROV = Namespace("http://www.w3.org/ns/prov#")
ORG = Namespace("https://example.org/ontology/")
MGMT = Namespace("https://example.org/mgmt/")


def worse(a, b):
    return a if _SEVERITY[a] >= _SEVERITY[b] else b


@dataclass
class CheckResult:
    numero: int
    nome: str
    estado: str
    resumo: str
    detalhes: str = ""
    contadores: dict = field(default_factory=dict)


# ---------------------------------------------------------------- git/io ---

def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")


def git(repo, *args):
    r = run(["git", *args], repo)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falhou: {r.stderr.strip()}")
    return r.stdout


def git_show(repo, commit, path):
    r = run(["git", "show", f"{commit}:{path}"], repo)
    if r.returncode != 0:
        return None
    return r.stdout


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def parse_ttl_bytes(data):
    g = rdflib.Graph()
    g.parse(data=data, format="turtle")
    return g


# ------------------------------------------------------ checagem 1 ---

def checagem_1(repo, baseline):
    tbox_path = repo / "tbox-local.ttl"
    if not tbox_path.exists():
        return CheckResult(1, "contagem de triplas", INDETERMINADO,
                            "tbox-local.ttl nao encontrado no clone.")
    raw = tbox_path.read_bytes()
    sha_atual = sha256_bytes(raw)
    try:
        g = parse_ttl_bytes(raw)
    except Exception as e:
        return CheckResult(1, "contagem de triplas", INDETERMINADO,
                            f"parse com rdflib abortou: {e}")

    count_atual = len(g)
    try:
        commit_atual = git(repo, "rev-parse", "HEAD").strip()
    except RuntimeError as e:
        return CheckResult(1, "contagem de triplas", INDETERMINADO, str(e))

    b = baseline["checagem_1"]
    commit_base, count_base, sha_base = b["commit_auditado"], b["triplas"], b["sha256"]

    linhas = [
        f"commit base: {commit_base}",
        f"commit atual: {commit_atual}",
        f"contagem base: {count_base}",
        f"contagem atual: {count_atual}",
        f"delta: {count_atual - count_base:+d}",
        f"sha256 base:   {sha_base}",
        f"sha256 atual:  {sha_atual}",
    ]

    if count_atual < count_base:
        estado = FALHA
        resumo = f"contagem caiu de {count_base} para {count_atual}."
    elif count_atual == count_base and sha_atual != sha_base:
        estado = FALHA
        resumo = "contagem igual, sha256 diverge -- substituicao de conteudo com volume preservado."
    elif count_atual > count_base:
        estado = AVISO
        resumo = f"contagem cresceu de {count_base} para {count_atual} (delta +{count_atual - count_base})."
    else:
        estado = PASSA
        resumo = "delta zero, sha256 identico."

    if estado in (FALHA, AVISO):
        old_content = git_show(repo, commit_base, "tbox-local.ttl")
        if old_content is None:
            linhas.append("nao foi possivel ler tbox-local.ttl no commit base (git show falhou).")
        else:
            try:
                g_old = parse_ttl_bytes(old_content.encode("utf-8"))
                subs_old, subs_new = set(g_old.subjects()), set(g.subjects())
                added, removed = subs_new - subs_old, subs_old - subs_new
                linhas.append(f"sujeitos adicionados ({len(added)}):")
                for s in sorted(added, key=str):
                    n = sum(1 for _ in g.triples((s, None, None)))
                    linhas.append(f"  + {s}  ({n} triplas)")
                linhas.append(f"sujeitos removidos ({len(removed)}):")
                for s in sorted(removed, key=str):
                    n = sum(1 for _ in g_old.triples((s, None, None)))
                    linhas.append(f"  - {s}  ({n} triplas)")
            except Exception as e:
                linhas.append(f"falha ao comparar grafos (commit base vs atual): {e}")

    return CheckResult(1, "contagem de triplas", estado, resumo, "\n".join(linhas))


# ------------------------------------------------------ checagem 2 ---

def checagem_2(repo, baseline, chk1_estado):
    if chk1_estado == INDETERMINADO:
        return CheckResult(2, "validacao SHACL", INDETERMINADO,
                            "nao executada: checagem 1 indeterminada.")

    tbox_path, shapes_path = repo / "tbox-local.ttl", repo / "shapes.ttl"
    if not shapes_path.exists():
        return CheckResult(2, "validacao SHACL", INDETERMINADO, "shapes.ttl nao encontrado.")

    try:
        data = parse_ttl_bytes(tbox_path.read_bytes())
        shapes = parse_ttl_bytes(shapes_path.read_bytes())
    except Exception as e:
        return CheckResult(2, "validacao SHACL", FALHA, f"falha de parse de tbox-local.ttl ou shapes.ttl: {e}")

    node_shape_count = len(set(shapes.subjects(RDF.type, SH.NodeShape)))
    baseline_nodeshapes = baseline["shapes"]["nodeshapes"]

    def major_minor_patch(v):
        parts = (v.split("+")[0].split(".") + ["0", "0", "0"])[:3]
        return tuple(int(p) for p in parts)

    rdflib_installed, pyshacl_installed = rdflib.__version__, pyshacl.__version__
    rdflib_base = baseline["ferramentas"]["rdflib"]
    pyshacl_base = baseline["ferramentas"]["pyshacl"]

    if major_minor_patch(rdflib_installed)[0] != major_minor_patch(rdflib_base)[0] or \
       major_minor_patch(pyshacl_installed)[0] != major_minor_patch(pyshacl_base)[0]:
        return CheckResult(
            2, "validacao SHACL", INDETERMINADO,
            f"versao instalada diverge em major da versao do baseline "
            f"(instalado rdflib {rdflib_installed}/pyshacl {pyshacl_installed}, "
            f"baseline rdflib {rdflib_base}/pyshacl {pyshacl_base}).")

    versao_diverge_menor = (rdflib_installed != rdflib_base) or (pyshacl_installed != pyshacl_base)

    conforms, results_graph, results_text = pyshacl.validate(data, shacl_graph=shapes, advanced=True)

    violacoes, avisos_shacl, infos = [], [], []
    for r in results_graph.subjects(RDF.type, SH.ValidationResult):
        sev = results_graph.value(r, SH.resultSeverity)
        item = {
            "focus_node": str(results_graph.value(r, SH.focusNode) or ""),
            "path": str(results_graph.value(r, SH.resultPath) or ""),
            "message": str(results_graph.value(r, SH.resultMessage) or ""),
        }
        if sev == SH.Violation:
            violacoes.append(item)
        elif sev == SH.Warning:
            avisos_shacl.append(item)
        elif sev == SH.Info:
            infos.append(item)

    estado = PASSA
    motivos = []
    if not conforms or violacoes:
        estado = FALHA
        motivos.append(f"{len(violacoes)} violacao(oes) sh:Violation")
    if node_shape_count != baseline_nodeshapes:
        estado = FALHA
        motivos.append(f"NodeShapes avaliadas = {node_shape_count}, baseline = {baseline_nodeshapes}")
    if versao_diverge_menor:
        estado = worse(estado, AVISO)
        motivos.append(f"versoes divergem em minor/patch (rdflib {rdflib_installed} vs {rdflib_base}, "
                        f"pyshacl {pyshacl_installed} vs {pyshacl_base})")
    if avisos_shacl or infos:
        estado = worse(estado, AVISO)
        motivos.append(f"{len(avisos_shacl)} sh:Warning, {len(infos)} sh:Info (contados)")

    resumo = f"Conforms={conforms}, {node_shape_count} NodeShapes avaliadas." + \
             (f" {'; '.join(motivos)}." if motivos else "")

    linhas = [
        f"Conforms: {conforms}",
        f"NodeShapes avaliadas: {node_shape_count} (baseline: {baseline_nodeshapes})",
        f"rdflib instalado: {rdflib_installed} (baseline: {rdflib_base})",
        f"pyshacl instalado: {pyshacl_installed} (baseline: {pyshacl_base})",
        "", "--- relatorio bruto pyshacl ---", results_text,
    ]
    if violacoes:
        linhas.append("--- violacoes (sh:Violation) ---")
        for v in violacoes:
            linhas.append(f"focus_node={v['focus_node']} path={v['path']} message={v['message']}")
    if avisos_shacl:
        linhas.append("--- avisos (sh:Warning) ---")
        for v in avisos_shacl:
            linhas.append(f"focus_node={v['focus_node']} path={v['path']} message={v['message']}")
    if infos:
        linhas.append("--- info (sh:Info) ---")
        for v in infos:
            linhas.append(f"focus_node={v['focus_node']} path={v['path']} message={v['message']}")

    return CheckResult(2, "validacao SHACL", estado, resumo, "\n".join(linhas))


# ------------------------------------------------------ checagem 3 ---

def checagem_3(repo, baseline, remocao_justificada=None):
    commit_base = baseline["checagem_1"]["commit_auditado"]
    if run(["git", "cat-file", "-e", commit_base], repo).returncode != 0:
        return CheckResult(3, "diff aditivo", INDETERMINADO,
                            f"commit base {commit_base} nao encontrado no clone local (profundidade insuficiente?).")

    diff_text = run(["git", "diff", f"{commit_base}..HEAD", "--", "*.ttl"], repo).stdout

    def load_union(ref):
        g = rdflib.Graph()
        for fname in ("tbox-local.ttl", "shapes.ttl"):
            content = git_show(repo, ref, fname)
            if content:
                g.parse(data=content, format="turtle")
        return g

    try:
        g_base, g_head = load_union(commit_base), load_union("HEAD")
    except Exception as e:
        return CheckResult(3, "diff aditivo", INDETERMINADO, f"falha ao carregar grafos para diff: {e}")

    # graph_diff canonicaliza blank nodes por isomorfismo estrutural; comparar
    # triplas cruas entre dois parses separados falha porque o rdflib atribui
    # identificadores de blank node novos a cada parse, mesmo para conteudo
    # byte-identico (owl:Restriction, owl:oneOf e listas RDF usam blank nodes
    # nas duas ontologias auditadas).
    # graph_diff(g1, g2) -> (in_both, in_g1_only, in_g2_only). O que nos
    # interessa e o que so existe na base (in_g1_only) -- indice 1, nao 2.
    _, base_only, _ = graph_diff(to_isomorphic(g_base), to_isomorphic(g_head))
    removidas = list(base_only.triples((None, None, None)))

    linhas = ["--- diff textual (git diff, *.ttl) ---", diff_text]

    if removidas:
        if remocao_justificada:
            estado = AVISO
            resumo = f"{len(removidas)} tripla(s) removida(s), declaradas com motivo: {remocao_justificada!r}."
        else:
            estado = FALHA
            resumo = f"{len(removidas)} tripla(s) presente(s) na base ausente(s) no HEAD."
        linhas.append(f"--- {len(removidas)} tripla(s) removida(s) (nivel de grafo) ---")
        for s, p, o in sorted(removidas, key=lambda t: tuple(str(x) for x in t)):
            linhas.append(f"  {s} {p} {o}")
            local = str(s).rsplit(("#" if "#" in str(s) else "/"), 1)[-1]
            blame = run(["git", "log", "--oneline", "-S", local, "--", "tbox-local.ttl", "shapes.ttl"], repo).stdout
            first_line = blame.strip().splitlines()[-1] if blame.strip() else "(git log -S sem resultado)"
            linhas.append(f"    introduzida em: {first_line}")
    else:
        removed_lines = [l for l in diff_text.splitlines() if l.startswith("-") and not l.startswith("---")]
        if removed_lines:
            estado = AVISO
            resumo = f"zero triplas removidas em nivel de grafo; {len(removed_lines)} linha(s) textual(is) removida(s) (reformatacao)."
        else:
            estado = PASSA
            resumo = "zero triplas removidas; nenhuma remocao textual."

    return CheckResult(3, "diff aditivo", estado, resumo, "\n".join(linhas))


# ------------------------------------------------------ checagem 4 ---
# Universo = sujeitos no namespace mgmt: (catalogo de frameworks/fases).
# Decisao de escopo tomada em sessao com o consultor (2026-08-01): a
# referencia normativa da checagem ancora isentos e "conteudo curado"
# exclusivamente em sujeitos mgmt:, e mgmt: nao contem classes (so
# individuos nomeados, ver cabecalho do Recorte 2 em tbox-local.ttl).
# Vocabulario ref:/org:/vsm:/demo: (enumeracoes, inclusive as sem
# owl:oneOf como ref:GapType) fica fora do universo por essa decisao.
# LIMITACAO: conteudo curado que venha a existir fora do namespace mgmt:
# (ex.: ref:ReferenceCapability por setor) nao e coberto nesta v0.1.
# Gatilho de revisao: primeira instancia de conteudo curado fora de mgmt:.

REQUIRED_PROV = [PROV.wasGeneratedBy, PROV.generatedAtTime, PROV.wasDerivedFrom, ORG.confidenceLevel]


def checagem_4(repo, baseline):
    tbox_path = repo / "tbox-local.ttl"
    if not tbox_path.exists():
        return CheckResult(4, "cobertura de proveniencia", INDETERMINADO, "tbox-local.ttl nao encontrado.")
    try:
        g = parse_ttl_bytes(tbox_path.read_bytes())
    except Exception as e:
        return CheckResult(4, "cobertura de proveniencia", INDETERMINADO, f"parse falhou: {e}")

    commit_base = baseline["checagem_1"]["commit_auditado"]
    old_content = git_show(repo, commit_base, "tbox-local.ttl")
    g_old = None
    if old_content is not None:
        try:
            g_old = parse_ttl_bytes(old_content.encode("utf-8"))
        except Exception:
            g_old = None
    old_mgmt_subjects = set(s for s in (g_old.subjects() if g_old is not None else []) if str(s).startswith(str(MGMT)))

    mgmt_subjects = sorted(
        {s for s in g.subjects() if isinstance(s, rdflib.URIRef) and str(s).startswith(str(MGMT))},
        key=str)

    def curie(s):
        return "mgmt:" + str(s)[len(str(MGMT)):]

    isentos = set(baseline["proveniencia"]["isentos"].keys()) if isinstance(baseline["proveniencia"]["isentos"], dict) \
        else set(baseline["proveniencia"]["isentos"])

    completos = 0
    isentos_contados, isencoes_novas_suspeitas, faltantes_novos, faltantes_preexistentes = [], [], [], []

    for s in mgmt_subjects:
        missing = [p for p in REQUIRED_PROV if not any(g.triples((s, p, None)))]
        c = curie(s)
        is_new = s not in old_mgmt_subjects
        if not missing:
            completos += 1
            continue
        if c in isentos:
            if is_new:
                isencoes_novas_suspeitas.append((c, missing))
            else:
                isentos_contados.append((c, missing))
        else:
            (faltantes_novos if is_new else faltantes_preexistentes).append((c, missing))

    estado = PASSA
    if faltantes_novos or faltantes_preexistentes or isencoes_novas_suspeitas:
        estado = FALHA
    elif isentos_contados:
        estado = AVISO

    resumo = (f"{completos} completos, {len(isentos_contados)} isentos (dividia contada), "
              f"{len(faltantes_novos) + len(faltantes_preexistentes)} faltante(s) fora da lista, "
              f"{len(isencoes_novas_suspeitas)} isencao(oes) nova(s) suspeita(s).")

    linhas = [
        f"universo avaliado: {len(mgmt_subjects)} sujeitos mgmt:",
        f"completos (4 triplas): {completos}",
        f"isentos nominalmente (baseline): {len(isentos)}",
        f"isentos confirmados nesta execucao: {len(isentos_contados)}",
    ]
    if isentos_contados:
        linhas.append("--- isentos contados (dividia conhecida) ---")
        for c, missing in isentos_contados:
            linhas.append(f"  {c}: faltam {[str(m) for m in missing]}")
    if isencoes_novas_suspeitas:
        linhas.append("--- ISENCOES NOVAS SUSPEITAS (sujeito criado apos baseline e ja marcado isento) ---")
        for c, missing in isencoes_novas_suspeitas:
            linhas.append(f"  {c}: faltam {[str(m) for m in missing]}")
    if faltantes_novos:
        linhas.append("--- faltantes NOVOS (sujeito criado apos o baseline) ---")
        for c, missing in faltantes_novos:
            linhas.append(f"  {c}: faltam {[str(m) for m in missing]}")
    if faltantes_preexistentes:
        linhas.append("--- faltantes preexistentes fora da lista de isentos ---")
        for c, missing in faltantes_preexistentes:
            linhas.append(f"  {c}: faltam {[str(m) for m in missing]}")

    return CheckResult(4, "cobertura de proveniencia", estado, resumo, "\n".join(linhas),
                        contadores={"isentos_proveniencia": len(isentos_contados)})


# ------------------------------------------------------ checagem 7 ---

def checagem_7(repo, baseline, pasta_canonica, anexos):
    itens = baseline["correspondencia"]
    linhas = []
    pior = PASSA
    ok_count = 0

    for item in itens:
        doc = item["documento"]
        hashes, mtimes = {}, {}
        for lado, base_dir in (("repositorio", repo), ("pasta_canonica", pasta_canonica), ("anexo", anexos)):
            relpath = item.get(lado)
            if not relpath or not base_dir:
                hashes[lado] = None
                continue
            p = Path(base_dir) / relpath
            if p.exists():
                data = p.read_bytes()
                hashes[lado] = sha256_bytes(data)
                mtimes[lado] = p.stat().st_mtime
            else:
                hashes[lado] = None

        available = {k: v for k, v in hashes.items() if v is not None}
        if len(available) < 2:
            veredito = INDETERMINADO
        elif len(set(available.values())) == 1:
            veredito = PASSA
            ok_count += 1
        else:
            veredito = FALHA if item.get("fonte_de_verdade") else AVISO

        pior = worse(pior, veredito)
        linhas.append(f"{doc}: repositorio={hashes.get('repositorio')} pasta_canonica={hashes.get('pasta_canonica')} "
                       f"anexo={hashes.get('anexo')} -> {veredito}")
        if veredito not in (PASSA, INDETERMINADO):
            linhas.append(f"    mtimes: {mtimes}")

    resumo = f"{ok_count}/{len(itens)} documento(s) com hashes iguais entre os lados alcancaveis (perfil repositorio, sem anexos)."
    return CheckResult(7, "hash entre anexo, repositorio e pasta canonica", pior, resumo, "\n".join(linhas))


# ---------------------------------------------------- resolucao de arquivo ---
# Um documento pode viver em ate tres lados (Criterios Secao 2.1): anexo do
# Project, repositorio, pasta canonica. Perfil `repositorio` (esta skill via
# Claude Code) nunca alcanca anexo; se nao for passado --anexos, esse lado
# fica sempre None e as asercoes que so vivem la saem INDETERMINADO.

def resolve_file(arquivo_por_lado, repo, pasta_canonica, anexos):
    bases = {"repositorio": repo, "pasta_canonica": pasta_canonica, "anexo": anexos}
    for lado, base in bases.items():
        relpath = (arquivo_por_lado or {}).get(lado)
        if relpath and base:
            p = Path(base) / relpath
            if p.exists():
                return lado, p
    return None, None


DOCX_W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_docx_text(path):
    # .docx real (OOXML/zip): um paragrafo <w:p> por linha, concatenando os
    # nos de texto <w:t> de cada run. Sem biblioteca externa -- so stdlib.
    with zipfile.ZipFile(path) as z:
        with z.open("word/document.xml") as f:
            root = ET.parse(f).getroot()
    linhas = []
    for p in root.iter(f"{DOCX_W_NS}p"):
        texto = "".join(node.text or "" for node in p.iter(f"{DOCX_W_NS}t"))
        linhas.append(texto)
    return "\n".join(linhas)


def read_document_text(path):
    # Alguns documentos do projeto tem extensao .docx mas sao texto piano
    # (ver cabecalho de tbox-local.ttl/shapes.ttl); outros (confirmado para
    # o arquivo real na pasta canonica) sao OOXML binario de verdade.
    # Decide pela assinatura do arquivo (zip = OOXML), nao pela extensao.
    with open(path, "rb") as f:
        assinatura = f.read(4)
    if assinatura[:2] == b"PK":
        return extract_docx_text(path)
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_version(v):
    return tuple(int(x) for x in re.sub(r"[_]", ".", v).split("."))


def versions_match(citada, vigente):
    a, b = normalize_version(citada), normalize_version(vigente)
    n = min(len(a), len(b))
    return a[:n] == b[:n]


# ------------------------------------------------------------ checagem 5 ---

def checagem_5(repo, baseline, pasta_canonica, anexos):
    cfg = baseline.get("checagem_5")
    if not cfg:
        return CheckResult(5, "numeros autorreferentes", INDETERMINADO, "checagem_5 ausente do baseline.")

    versoes_vigentes = {v["documento"]: v for v in cfg["versoes_vigentes"]}
    isencoes = cfg.get("isencoes_citacao_historica", [])

    linhas = []
    pior = PASSA
    faltando_arquivo = set()
    avisos_versao_congelado = 0

    for item in cfg["asercoes_contaveis"]:
        lado, path = resolve_file(item["arquivo"], repo, pasta_canonica, anexos)
        if not path:
            pior = worse(pior, INDETERMINADO)
            faltando_arquivo.add(item["documento"] + " (" + ", ".join(
                v for v in item["arquivo"].values() if v) + ")")
            linhas.append(f"[{INDETERMINADO}] {item['id']}: documento '{item['documento']}' inalcancavel "
                           f"nesta execucao (nem repositorio, nem pasta canonica, nem anexo).")
            continue

        text = read_document_text(path)
        matches = list(re.finditer(item["busca_regex"], text))
        if not matches:
            pior = worse(pior, INDETERMINADO)
            linhas.append(f"[{INDETERMINADO}] {item['id']}: padrao {item['busca_regex']!r} nao encontrado em "
                           f"{path} ({lado}) -- documento pode ter mudado desde a especificacao da assercao.")
            continue

        for m in matches:
            linha_num = text.count("\n", 0, m.start()) + 1
            trecho = text.splitlines()[linha_num - 1].strip()

            if item["tipo"] == "citacao_versao":
                versao_citada = m.group("versao")
                alvo = item.get("documento_citado")
                vv = versoes_vigentes.get(alvo) if alvo else None
                bate = vv is not None and versions_match(versao_citada, vv["versao_vigente"])
                isento = any(re.search(pat, trecho) for pat in isencoes)
                if bate or isento:
                    estado_linha = PASSA
                    detalhe = f"cita v{versao_citada}" + (" (isento por padrao historico)" if isento and not bate else " (vigente)")
                else:
                    estado_linha = FALHA if item["natureza"] == "vivo" else AVISO
                    vigente_str = vv["versao_vigente"] if vv else "(sem alvo conhecido -- referencia orfa)"
                    detalhe = f"cita v{versao_citada}, vigente e v{vigente_str}"
                    if estado_linha == AVISO:
                        avisos_versao_congelado += 1

            elif item["tipo"] in ("contagem_secao", "contagem_vs_shapes"):
                valor_afirmado = int(m.group("n"))
                if item["tipo"] == "contagem_vs_shapes":
                    valor_real = baseline["shapes"]["nodeshapes"]
                    fonte_real = "shapes.ttl (checagem 2)"
                else:
                    # Conta paragrafos nao-vazios dentro da secao, a partir do
                    # primeiro cabecalho de subsecao, excluindo os proprios
                    # cabecalhos de subsecao. Nao conta marcador de lista tipo
                    # '- item': extracao de .docx real (OOXML) nao preserva
                    # glifo de bullet como texto, ele vem da numeracao (numPr),
                    # nao do run de texto -- ver read_document_text.
                    sec_ini = re.search(item["secao_inicio_regex"], text, re.M)
                    if not sec_ini:
                        pior = worse(pior, INDETERMINADO)
                        linhas.append(f"[{INDETERMINADO}] {item['id']}: secao_inicio_regex nao encontrada em {path}.")
                        continue
                    resto = text[sec_ini.end():]
                    sec_fim = re.search(item["secao_fim_regex"], resto, re.M)
                    secao_texto = resto[:sec_fim.start()] if sec_fim else resto
                    sub_re = re.compile(item["subsecao_regex"], re.M)
                    primeira_sub = sub_re.search(secao_texto)
                    if not primeira_sub:
                        pior = worse(pior, INDETERMINADO)
                        linhas.append(f"[{INDETERMINADO}] {item['id']}: subsecao_regex nao encontrada dentro da secao.")
                        continue
                    apos_primeira = secao_texto[primeira_sub.start():]
                    itens_nao_vazios = [l for l in apos_primeira.splitlines() if l.strip()]
                    valor_real = sum(1 for l in itens_nao_vazios if not sub_re.match(l))
                    fonte_real = f"paragrafos nao-vazios apos o primeiro '{item['subsecao_regex']}', excluindo cabecalhos de subsecao"

                if valor_afirmado == valor_real:
                    estado_linha = PASSA
                    detalhe = f"afirma {valor_afirmado}, contagem real ({fonte_real}) = {valor_real}"
                else:
                    estado_linha = FALHA if item["natureza"] == "vivo" else AVISO
                    detalhe = f"afirma {valor_afirmado}, contagem real ({fonte_real}) = {valor_real}"
                    if estado_linha == AVISO:
                        avisos_versao_congelado += 1
            else:
                estado_linha = INDETERMINADO
                detalhe = f"tipo de assercao desconhecido: {item['tipo']}"

            pior = worse(pior, estado_linha)
            linhas.append(f"[{estado_linha}] {item['id']} ({item['documento']}, {lado}, linha {linha_num}, "
                           f"{item['natureza']}): {detalhe}\n    trecho: {trecho!r}")

    resumo = f"{sum(1 for l in linhas if l.startswith('[PASSA]'))} PASSA, " \
             f"{sum(1 for l in linhas if l.startswith('[AVISO]'))} AVISO, " \
             f"{sum(1 for l in linhas if l.startswith('[FALHA]'))} FALHA, " \
             f"{sum(1 for l in linhas if l.startswith('[INDETERMINADO]'))} INDETERMINADO."
    if faltando_arquivo:
        resumo += f" Arquivos necessarios e nao encontrados: {sorted(faltando_arquivo)}."

    detalhes = "\n".join(linhas)
    if avisos_versao_congelado:
        detalhes += f"\n\ncontador -- avisos de ponteiro de versao em documento congelado: {avisos_versao_congelado}"

    return CheckResult(5, "numeros autorreferentes", pior, resumo, detalhes,
                        contadores={"avisos_versao_documento_congelado": avisos_versao_congelado})


# ------------------------------------------------------------ checagem 6 ---

def checagem_6(repo, baseline, pasta_canonica, anexos):
    cfg = baseline.get("checagem_6")
    if not cfg:
        return CheckResult(6, "cobertura da Arquitetura contra o tbox", INDETERMINADO, "checagem_6 ausente do baseline.")

    lado, path = resolve_file(cfg["arquivo_arquitetura"], repo, pasta_canonica, anexos)
    if not path:
        candidatos = ", ".join(v for v in cfg["arquivo_arquitetura"].values() if v)
        return CheckResult(6, "cobertura da Arquitetura contra o tbox", INDETERMINADO,
                            f"Arquitetura vigente inalcancavel nesta execucao (perfil repositorio sem pasta "
                            f"canonica/anexo apontando pra ela). Copie um dos candidatos ({candidatos}) para "
                            f"o repositorio ou aponte --pasta-canonica/--anexos.")

    tbox_path, shapes_path = repo / "tbox-local.ttl", repo / "shapes.ttl"
    if not tbox_path.exists() or not shapes_path.exists():
        return CheckResult(6, "cobertura da Arquitetura contra o tbox", INDETERMINADO, "tbox-local.ttl ou shapes.ttl ausente.")

    try:
        g = rdflib.Graph()
        g.parse(str(tbox_path), format="turtle")
        g.parse(str(shapes_path), format="turtle")
    except Exception as e:
        return CheckResult(6, "cobertura da Arquitetura contra o tbox", INDETERMINADO, f"parse falhou: {e}")

    text = read_document_text(path)

    prefixos_locais = set(cfg["prefixos_escopo_local"])
    prefixos_externos = set(cfg["prefixos_externos"])
    todos_prefixos = prefixos_locais | prefixos_externos
    pattern = re.compile(r"\b(" + "|".join(re.escape(p) for p in todos_prefixos) + r"):([A-Za-z_][A-Za-z0-9_]*)\b")

    ocorrencias = {}
    for m in pattern.finditer(text):
        ident = f"{m.group(1)}:{m.group(2)}"
        linha = text.count("\n", 0, m.start()) + 1
        ocorrencias.setdefault(ident, linha)

    locais = {k: v for k, v in ocorrencias.items() if k.split(":", 1)[0] in prefixos_locais}
    externos = {k: v for k, v in ocorrencias.items() if k.split(":", 1)[0] in prefixos_externos}

    ns_map = dict(g.namespaces())

    def resolve_uri(curie):
        prefix, local = curie.split(":", 1)
        ns = ns_map.get(prefix)
        return rdflib.URIRef(str(ns) + local) if ns is not None else None

    graph_uris = set()
    for s, p, o in g:
        for term in (s, p, o):
            if isinstance(term, rdflib.URIRef):
                graph_uris.add(term)

    ausentes = {}
    for ident, linha in locais.items():
        uri = resolve_uri(ident)
        if uri is None or uri not in graph_uris:
            ausentes[ident] = linha

    triagem = cfg.get("triagem", {})
    nao_triados = {k: v for k, v in ausentes.items() if k not in triagem}
    lacunas_reais = {k: v for k, v in ausentes.items() if triagem.get(k, {}).get("estado") == "lacuna_real"}
    outros_triados = {k: (v, triagem[k]) for k, v in ausentes.items()
                       if k in triagem and triagem[k].get("estado") != "lacuna_real"}

    estado = PASSA
    if nao_triados:
        estado = FALHA
    elif lacunas_reais:
        estado = worse(estado, AVISO)

    resumo = (f"{len(locais)} identificadores locais extraidos ({lado}, {path.name}), "
              f"{len(locais) - len(ausentes)} presentes no grafo, {len(ausentes)} ausentes "
              f"({len(nao_triados)} NAO TRIADOS, {len(lacunas_reais)} lacunas reais abertas, "
              f"{len(outros_triados)} triados como nao-lacuna); {len(externos)} ocorrencia(s) de prefixo externo "
              f"(contadas a parte, sem efeito no veredito).")

    linhas = [
        f"extrator: {cfg.get('extrator_versao', '(nao registrado)')}",
        f"arquivo Arquitetura resolvido via: {lado} -> {path}",
        f"prefixos em escopo local: {sorted(prefixos_locais)}",
        f"prefixos externos (contados a parte): {sorted(prefixos_externos)}",
    ]
    if nao_triados:
        linhas.append(f"--- NAO TRIADOS ({len(nao_triados)}) -- causa FALHA por construcao ---")
        for k in sorted(nao_triados):
            linhas.append(f"  {k}  (primeira ocorrencia: linha {nao_triados[k]})")
    if lacunas_reais:
        linhas.append(f"--- lacunas reais abertas, triadas ({len(lacunas_reais)}) -- AVISO contado ---")
        for k in sorted(lacunas_reais):
            entry = triagem[k]
            linhas.append(f"  {k}  linha {lacunas_reais[k]}  pacote_alvo={entry.get('pacote_alvo')}  "
                           f"fundamento={entry.get('fundamento')}")
    if outros_triados:
        linhas.append(f"--- ausentes triados como nao-lacuna ({len(outros_triados)}) ---")
        for k, (linha, entry) in sorted(outros_triados.items()):
            linhas.append(f"  {k}  linha {linha}  estado={entry.get('estado')}  fundamento={entry.get('fundamento')}")
    if externos:
        linhas.append(f"--- prefixo externo, so contagem ({len(externos)}) ---")
        for k in sorted(externos):
            linhas.append(f"  {k}  linha {externos[k]}")

    return CheckResult(6, "cobertura da Arquitetura contra o tbox", estado, resumo, "\n".join(linhas),
                        contadores={"lacunas_reais_abertas": len(lacunas_reais), "nao_triados": len(nao_triados)})


# --------------------------------------------------------------- report ---

def build_report(perfil, repo, baseline, results):
    lines = []
    commit_atual = git(repo, "rev-parse", "HEAD").strip()
    lines.append("=" * 70)
    lines.append("RELATORIO DE AUDITORIA DE PROCESSO -- META-MODELO")
    lines.append("=" * 70)
    lines.append(f"perfil de execucao: {perfil}")
    import datetime
    lines.append(f"data: {datetime.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"commit avaliado: {commit_atual}")
    lines.append(f"commit do baseline: {baseline['checagem_1']['commit_auditado']}")
    lines.append(f"rdflib: {rdflib.__version__}  pyshacl: {pyshacl.__version__}")
    lines.append("-" * 70)

    global_estado = PASSA
    for r in results:
        global_estado = worse(global_estado, r.estado)
        lines.append(f"[{r.estado:13s}] {r.numero}. {r.nome} -- {r.resumo}")

    lines.append("-" * 70)
    contadores = {}
    for r in results:
        contadores.update(r.contadores)
    lines.append(f"contador: isentos de proveniencia (mgmt:) confirmados = {contadores.get('isentos_proveniencia', 'n/d')}")
    lines.append(f"contador: lacunas reais abertas (checagem 6) = {contadores.get('lacunas_reais_abertas', 'n/d')}")
    lines.append(f"contador: identificadores nao triados (checagem 6) = {contadores.get('nao_triados', 'n/d')}")
    lines.append(f"contador: avisos de ponteiro de versao em documento congelado (checagem 5) = "
                  f"{contadores.get('avisos_versao_documento_congelado', 'n/d')}")
    lines.append("-" * 70)
    lines.append(f"VEREDITO GLOBAL: {global_estado}")
    lines.append("=" * 70)
    lines.append("Esta auditoria e verificacao estrutural. Nao afirma verdade semantica, "
                  "adequacao de classificacao curada, nem que a proveniencia registrada e verdadeira "
                  "(Criterios Secao 6).")
    lines.append("=" * 70)

    for r in results:
        lines.append("")
        lines.append(f"### Checagem {r.numero} -- {r.nome} [{r.estado}]")
        lines.append(r.detalhes)

    exit_code = 1 if global_estado in (FALHA, INDETERMINADO) else 0
    return "\n".join(lines), exit_code


def main():
    ap = argparse.ArgumentParser(description="Skill de auditoria de processo -- META-MODELO S01b")
    ap.add_argument("--repo", default=".", help="raiz do clone git a auditar")
    ap.add_argument("--baseline", default=None, help="caminho para baseline.json (default: auditoria/baseline.json)")
    ap.add_argument("--pasta-canonica", default=None, help="caminho local da pasta canonica (perfil repositorio)")
    ap.add_argument("--anexos", default=None, help="caminho local dos anexos do Project (perfil sessao)")
    ap.add_argument("--perfil", default="repositorio", choices=["repositorio", "sessao"])
    ap.add_argument("--remocao-justificada", default=None,
                     help="motivo declarado para remocao de triplas aceita na checagem 3")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    baseline_path = Path(args.baseline).resolve() if args.baseline else Path(__file__).resolve().parent / "baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    r1 = checagem_1(repo, baseline)
    r2 = checagem_2(repo, baseline, r1.estado)
    r3 = checagem_3(repo, baseline, args.remocao_justificada)
    r4 = checagem_4(repo, baseline)
    r5 = checagem_5(repo, baseline, args.pasta_canonica, args.anexos)
    r6 = checagem_6(repo, baseline, args.pasta_canonica, args.anexos)
    r7 = checagem_7(repo, baseline, args.pasta_canonica, args.anexos)

    report, exit_code = build_report(args.perfil, repo, baseline, [r1, r2, r3, r4, r5, r6, r7])
    print(report)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
