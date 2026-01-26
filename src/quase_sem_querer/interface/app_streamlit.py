# ================================================================
# UI Streamlit — WIZARD UNIFICADO (Modelo → Lei → Decisão → Execução)
# Projeto: Quase Sem Querer
# ================================================================
# Este wizard organiza visualmente o fluxo completo de execução
# normativa em etapas sequenciais, forçando compreensão e decisão
# explícita pelo gestor.

import streamlit as st
import json
from quase_sem_querer.relatorios.memoria_calculo import render_memoria_calculo
from quase_sem_querer.contextos.gerador_contexto_operacional import (
    gerar_super_contexto_operacional
)
from quase_sem_querer.interface.arvore_calculo import render_no
from quase_sem_querer.motor.orquestrador import executar_modelo
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DIR_MODELOS = BASE_DIR / "modelos_normativos"
DIR_CONTEXTOS = BASE_DIR / "contextos"

import html
import re

def sanitizar_texto(texto: str) -> str:
    if not texto:
        return ""

    texto = texto.strip()
    texto = texto[:150]
    texto = re.sub(r"[\x00-\x1f\x7f]", "", texto)
    texto = html.escape(texto)
    return texto


def listar_jsons(diretorio: Path) -> list[str]:
    if not diretorio.exists():
        return []
    return sorted(
        [p.name for p in diretorio.glob("*.json") if p.is_file()]
    )


# ----------------------------------------------------------------
# Estado da sessão
# ----------------------------------------------------------------

if "etapa" not in st.session_state:
    st.session_state.etapa = 1

if "ctx_operacional" not in st.session_state:
    st.session_state.ctx_operacional = None


# ----------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------

def avancar():
    st.session_state.etapa += 1


def voltar():
    st.session_state.etapa -= 1

# ----------------------------------------------------------------
# ETAPA 1 — Seleção do modelo normativo
# ----------------------------------------------------------------

st.title("Quase Sem Querer — Sistema de Cálculo de Custos Operacionais")

if st.session_state.etapa == 1:
    st.header("1️⃣ Modelo Normativo")
    st.markdown("Selecione o **modelo normativo** disponível no sistema.")

    modelos_disponiveis = listar_jsons(DIR_MODELOS)

    if not modelos_disponiveis:
        st.error("Nenhum modelo normativo encontrado no sistema.")
        st.stop()

    modelo_escolhido = st.selectbox(
        "Modelo normativo",
        modelos_disponiveis,
        key="modelo_selecionado",
    )

    if modelo_escolhido:
        caminho_modelo = DIR_MODELOS / modelo_escolhido

        with caminho_modelo.open("r", encoding="utf-8") as f:
            st.session_state.modelo_bytes = f.read().encode("utf-8")
            st.session_state.modelo_nome = modelo_escolhido

        modelo_json = json.loads(st.session_state.modelo_bytes)
        st.session_state.no_raiz_modelo = modelo_json.get("raiz")

        st.success(f"Modelo selecionado: {modelo_escolhido}")

    st.button(
        "Próximo →",
        on_click=avancar,
        disabled="modelo_bytes" not in st.session_state,
    )


# ----------------------------------------------------------------
# ETAPA 2 — Decisão normativa (constantes legais)
# ----------------------------------------------------------------

elif st.session_state.etapa == 2:
    st.header("2️⃣ Constantes Legais")
    st.markdown("Selecione o **contexto de constantes legais**.")

    contextos_disponiveis = listar_jsons(DIR_CONTEXTOS)

    if not contextos_disponiveis:
        st.error("Nenhum contexto legal encontrado no sistema.")
        st.stop()

    contexto_escolhido = st.selectbox(
        "Contexto legal",
        contextos_disponiveis,
        key="contexto_legal_selecionado",
    )

    caminho_contexto = DIR_CONTEXTOS / contexto_escolhido

    with caminho_contexto.open("r", encoding="utf-8") as f:
        ctx_legal = json.load(f)

    decisoes_legais = {}

    for modulo, campos in ctx_legal.get("modulos", {}).items():
        with st.expander(modulo.replace("_", " ").title(), expanded=True):
            for nome, meta in campos.items():
                valores = meta["valor"]

                if isinstance(valores, list):
                    escolha = st.selectbox(
                        nome,
                        valores,
                        format_func=lambda v: f"{v*100:.2f}%",
                        key=f"legal.{nome}",
                    )
                    decisoes_legais[nome] = {
                        "valor": escolha,
                        "origem": "decisao_gestor",
                        "referencia_documental": meta.get("referencia_documental"),
                    }
                else:
                    st.text_input(nome, value=str(valores), disabled=True)
                    decisoes_legais[nome] = {
                        "valor": valores,
                        "origem": "norma",
                        "referencia_documental": meta.get("referencia_documental"),
                    }

    st.session_state.decisoes_legais = decisoes_legais

    col1, col2 = st.columns(2)
    with col1:
        st.button("← Voltar", on_click=voltar)
    with col2:
        st.button("Próximo →", on_click=avancar)

# ----------------------------------------------------------------
# ETAPA 3 — Valores Operacionais Editáveis
# ----------------------------------------------------------------


elif st.session_state.etapa == 3:
    st.header("3️⃣ Valores Operacionais")
    st.markdown("Informe os valores **não definidos por lei**.")

    # ============================================================
    # ESTADO 1 — Antes da geração do contexto operacional
    # ============================================================

    if st.session_state["ctx_operacional"] is None:
        st.markdown("### Contexto operacional")

        if st.button("🧠 Gerar contexto automaticamente", key="gerar_ctx_operacional"):
            modelo = json.loads(st.session_state.modelo_bytes)

            contexto_legal = {
                "tipo": "super_contexto",
                "modulos": {
                    "legal": dict(st.session_state.decisoes_legais)
                }
            }

            st.session_state.ctx_operacional = gerar_super_contexto_operacional(
                modelo_normativo=modelo,
                contexto_legal=contexto_legal
            )

            st.success("Contexto operacional gerado.")
            st.rerun()

        st.info(
            "O contexto operacional é gerado automaticamente a partir do "
            "modelo normativo e das decisões legais já tomadas."
        )

    # ============================================================
    # ESTADO 2 — Contexto já gerado → renderização ORDENADA
    # ============================================================

    else:
        ctx_operacional = st.session_state["ctx_operacional"]
        valores_livres = {}

        modelo = json.loads(st.session_state.modelo_bytes)
        modulos_modelo = modelo.get("modulos") or {}
        modulos_ctx = ctx_operacional.get("modulos", {})

        for nome_modulo, conteudo_modulo in modulos_modelo.items():
            nos = conteudo_modulo.get("nos", [])
            campos_ctx = modulos_ctx.get(nome_modulo, {})

            if not campos_ctx:
                continue

            with st.expander(nome_modulo.replace("_", " ").title(), expanded=True):
                for no in nos:
                    no_id = no.get("id")
                    if no_id not in campos_ctx:
                        continue

                    meta = campos_ctx[no_id]
                    valor_atual = meta.get("valor") or 0.0
                    key_base = f"ctx_{nome_modulo}_{no_id}"

                    col_valor, col_just = st.columns([1, 2])

                    with col_valor:
                        if "percentual" in no_id:
                            valor_pct = st.number_input(
                                no_id,
                                value=float(valor_atual * 100),
                                format="%.2f",
                                key=f"{key_base}_pct",
                            )
                            valor = valor_pct / 100
                        else:
                            valor = st.number_input(
                                no_id,
                                value=float(valor_atual),
                                key=f"{key_base}_val",
                            )

                    with col_just:
                        justificativa = sanitizar_texto(
                            st.text_input(
                                "Justificativa / referência",
                                value=meta.get("referencia_documental") or "",
                                key=f"just_{key_base}",
                                max_chars=150,
                            )
                        )

                    valores_livres[no_id] = {
                        "valor": valor,
                        "origem": "decisao_gestor",
                        "referencia_documental": justificativa or None,
                    }

        st.session_state.valores_livres = valores_livres

        col1, col2 = st.columns(2)
        with col1:
            st.button("← Voltar", on_click=voltar)
        with col2:
            st.button("Próximo →", on_click=avancar)



# ----------------------------------------------------------------
# ETAPA 4 — Consolidação e execução
# ----------------------------------------------------------------

elif st.session_state.etapa == 4:
    st.header("4️⃣ Consolidação e Execução")

    contexto_final = {}

    contexto_final.update(st.session_state.decisoes_legais)
    contexto_final.update(st.session_state.valores_livres)

    st.subheader("Contexto aplicado")
    st.json(contexto_final)

    # -------------------------------------------------------------
    # Download do contexto consolidado
    # -------------------------------------------------------------

    contexto_json_str = json.dumps(
        contexto_final,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        label="📥 Baixar contexto consolidado (JSON)",
        data=contexto_json_str,
        file_name="contexto_consolidado.json",
        mime="application/json",
    )

    st.markdown("---")

    st.info(f"Nó raiz do modelo: {st.session_state.no_raiz_modelo}")

    # --------------------------------------------
    # Execução (ação)
    # --------------------------------------------

    if st.button("Executar cálculo", key="executar_calculo"):
        try:
            st.session_state.resultado_execucao = executar_modelo(
                nome_modelo=st.session_state.modelo_nome,
                contexto=contexto_final,
                no_raiz=st.session_state.no_raiz_modelo,
                persistir=True,
            )


        except Exception as e:
            st.error("Erro durante a execução do cálculo")
            st.exception(e)

    # --------------------------------------------
    # Exibição (estado)
    # --------------------------------------------

    if "resultado_execucao" in st.session_state:
        resultado = st.session_state.resultado_execucao

        # 🌳 Árvore
        st.subheader("🌳 Árvore do cálculo (visualização explicativa)")
        render_no(
            no_id=resultado["no_raiz"],
            nos_avaliados=resultado["nos_avaliados"],
        )

        # 📦 Resultado canônico
        st.subheader("Resultado canônico")
        st.json(resultado)

        # 📄 Memória de cálculo
        memoria_md = render_memoria_calculo(resultado, formato="md")
        memoria_txt = render_memoria_calculo(resultado, formato="txt")

        st.download_button(
            "📄 Baixar memória de cálculo (Markdown)",
            data=memoria_md,
            file_name="memoria_calculo.md",
            mime="text/markdown",
            key="download_md",
        )

        st.download_button(
            "📄 Baixar memória de cálculo (Texto)",
            data=memoria_txt,
            file_name="memoria_calculo.txt",
            mime="text/plain",
            key="download_txt",
        )



    st.button("← Voltar", on_click=voltar, key="voltar4")
