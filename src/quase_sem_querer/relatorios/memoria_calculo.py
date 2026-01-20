# ================================================================
# Geração de memória de cálculo amigável
# Projeto: Quase Sem Querer
#
# Este módulo gera representações em linguagem natural (TXT e MD)
# a partir do resultado da execução.
#
# Princípios:
# - Nenhuma lógica de cálculo
# - Nenhuma leitura de modelo ou contexto
# - Fonte única da verdade: resultado canônico
# - Ordem inferida automaticamente pela árvore (topológica)
# ================================================================

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List


def _titulo(formato: str, texto: str) -> str:
    if formato == "md":
        return f"# {texto}\n"
    return f"{texto}\n{'=' * len(texto)}\n"


def _subtitulo(formato: str, texto: str) -> str:
    if formato == "md":
        return f"## {texto}\n"
    return f"\n{texto.upper()}\n{'-' * len(texto)}\n"


def _fmt_valor(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_percentual(v: float) -> str:
    return f"{v * 100:.2f}%".replace(".", ",")


def _fmt_valor_contextual(no_id: str, v: float) -> str:
    if no_id.startswith("percentual_"):
        return _fmt_percentual(v)
    return _fmt_valor(v)


def render_memoria_calculo(
    resultado: Dict[str, Any],
    *,
    formato: str = "md",
    numeracao_hierarquica: bool = False,
) -> str:
    if formato not in {"md", "txt"}:
        raise ValueError("Formato inválido. Use 'md' ou 'txt'.")

    linhas: List[str] = []

    # ------------------------------------------------------------
    # Cabeçalho
    # ------------------------------------------------------------

    titulo = "MEMÓRIA DE CÁLCULO — IN nº 05/2017"
    linhas.append(_titulo(formato, titulo))

    meta = resultado.get("meta_execucao", {})
    data_exec = meta.get("data_execucao") or datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    linhas.append(f"Data da execução: {data_exec}")
    linhas.append(f"Nó raiz avaliado: {resultado.get('no_raiz', '—')}")
    linhas.append("")

    # ------------------------------------------------------------
    # Trilha de cálculo
    # ------------------------------------------------------------

    trilha = resultado.get("trilha_calculo", [])
    decisoes = resultado.get("decisoes_humanas", {})

    linhas.append(_subtitulo(formato, "Detalhamento do cálculo"))

    indice_por_no: Dict[str, str] = {}
    filhos_por_pai: Dict[str, int] = {}

    nos = resultado.get("nos_avaliados", {})

    for idx, no_id in enumerate(trilha, start=1):
        no = nos.get(no_id)
        if not isinstance(no, dict):
            continue

        tipo = no.get("tipo")
        valor = no.get("valor_calculado")
        deps = no.get("dependencias", [])
        meta_jur = no.get("metadados_juridicos", {})

        descricao = (
            meta_jur.get("descricao")
            or no_id.replace("_", " ").title()
        )



        # -----------------------------
        # Numeração
        # -----------------------------
        if numeracao_hierarquica and deps:
            pai = next((d for d in deps if d in indice_por_no), None)
            if pai:
                filhos_por_pai[pai] = filhos_por_pai.get(pai, 0) + 1
                indice = f"{indice_por_no[pai]}.{filhos_por_pai[pai]}"
            else:
                indice = str(idx)
        else:
            indice = str(idx)

        indice_por_no[no_id] = indice

        if formato == "md":
            linhas.append(f"### {indice}. {descricao}")
        else:
            linhas.append(f"\n{indice}. {descricao.upper()}")

        if deps:
            deps_fmt = []
            for d in deps:
                v = nos.get(d, {}).get("valor_calculado")
                if isinstance(v, (int, float)):
                    deps_fmt.append(f"{d} ({_fmt_valor_contextual(d, v)})")
                else:
                    deps_fmt.append(d)
            linhas.append(f"- Dependências consideradas: {', '.join(deps_fmt)}")


        if no_id in decisoes:
            dec = decisoes[no_id]
            linhas.append(f"- Origem: {dec.get('origem', '—')}")
            if dec.get("referencia_documental"):
                linhas.append(
                    f"- Referência documental: {dec['referencia_documental']}"
                )

        if isinstance(valor, (int, float)):
            rotulo = "Valor calculado" if deps else "Valor adotado"
            linhas.append(
                f"- {rotulo}: {_fmt_valor_contextual(no_id, valor)}"
            )


        if meta_jur.get("fundamento_legal"):
            linhas.append(f"- Fundamento legal: {meta_jur['fundamento_legal']}")

        if meta_jur.get("observacoes"):
            linhas.append(f"- Observações: {meta_jur['observacoes']}")

        linhas.append("")

    # ------------------------------------------------------------
    # Resultado final
    # ------------------------------------------------------------

    valor_final = resultado.get("valor_final")
    if valor_final is not None:
        linhas.append(_subtitulo(formato, "Resultado final"))
        linhas.append(f"Valor total apurado: {_fmt_valor(valor_final)}")

    return "\n".join(linhas)
