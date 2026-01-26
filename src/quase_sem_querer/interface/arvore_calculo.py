# ================================================================
# arvore_calculo.py — Visualização semântica derivada (árvore)
# Projeto: Quase Sem Querer
#
# Fonte única: resultado canônico da execução
# Não calcula, não valida, não persiste
# ================================================================

from typing import Dict, Any
import streamlit as st


def _fmt_valor(no_id: str, v: float | None) -> str:
    if v is None:
        return "—"

    if no_id.startswith("percentual_"):
        return f"{v * 100:.2f}%"

    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")



def render_no(
    *,
    no_id: str,
    nos_avaliados: Dict[str, Dict[str, Any]],
    nivel: int = 0,
):
    """
    Renderiza um nó da árvore de cálculo de forma recursiva.
    """

    no = nos_avaliados.get(no_id)
    if not no:
        st.error(f"Nó '{no_id}' não encontrado no resultado.")
        return

    valor = no.get("valor_calculado")
    deps = no.get("dependencias", [])
    meta = no.get("metadados_juridicos", {})

    titulo = f"{no_id} — {_fmt_valor(no_id, valor)}"

    # Indentação visual leve por nível (opcional)
    margem = nivel * 0.5

    with st.container():
        st.markdown(f"<div style='margin-left: {margem}rem;'>", unsafe_allow_html=True)

        with st.expander(titulo, expanded=(nivel == 0)):
            st.markdown(f"**Tipo de nó:** `{no.get('tipo')}`")

            if meta.get("fundamento_legal"):
                st.markdown(
                    f"**Fundamento legal:** {meta['fundamento_legal']}"
                )

            if meta.get("observacoes"):
                st.markdown(
                    f"**Observações:** {meta['observacoes']}"
                )

            if deps:
                st.markdown("**Dependências:**")
                for dep in deps:
                    render_no(
                        no_id=dep,
                        nos_avaliados=nos_avaliados,
                        nivel=nivel + 1,
                    )
            else:
                st.markdown("_Nó folha (valor proveniente do Contexto)._")

        st.markdown("</div>", unsafe_allow_html=True)
