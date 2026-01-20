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


# ----------------------------------------------------------------
# Estado da sessão
# ----------------------------------------------------------------

if "etapa" not in st.session_state:
    st.session_state.etapa = 1

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
    st.markdown("Selecione o **modelo normativo** que define a regra do cálculo.")

    # Drag and drop do modelo (preferencial)
    modelo_file = st.file_uploader(
        "modelo normativo (.json)",
        type=["json"],
        key="modelo_uploader",
    )

    if modelo_file is not None:
        st.session_state.modelo_bytes = modelo_file.read()
        st.session_state.modelo_nome = modelo_file.name
        st.success(f"Modelo carregado: {modelo_file.name}")
        modelo_json = json.loads(st.session_state.modelo_bytes)
        st.session_state.no_raiz_modelo = modelo_json.get("raiz")

    # Botão explícito de avanço (evita salto automático)
    st.button(
        "Próximo →",
        key="btn_etapa1",
        on_click=avancar,
        disabled="modelo_bytes" not in st.session_state,
    )


# ----------------------------------------------------------------
# ETAPA 2 — Decisão normativa (constantes legais)
# ----------------------------------------------------------------

elif st.session_state.etapa == 2:
    st.header("2️⃣ Constantes Legais")
    st.markdown("Escolha os valores **definidos em lei**.")

    # Drag and drop do contexto legal
    ctx_legal_file = st.file_uploader(
        "Contexto de constantes legais (.json)",
        type=["json"],
        key="ctx_legal_uploader",
    )

    if ctx_legal_file is None:
        st.info("Carregue o contexto de constantes legais para continuar.")
        st.button("← Voltar", on_click=voltar)
        st.stop()

    ctx_legal = json.load(ctx_legal_file)

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
        st.button("← Voltar", on_click=voltar, key="voltar2")
    with col2:
        st.button("Próximo →", on_click=avancar, key="avancar2")

# ----------------------------------------------------------------
# ETAPA 3 — Valores operacionais editáveis
# ----------------------------------------------------------------

elif st.session_state.etapa == 3:
    st.header("3️⃣ Valores Operacionais")
    st.markdown("Informe os valores **não definidos por lei**.")

    # ------------------------------------------------------------
    # Geração determinística do contexto operacional
    # ------------------------------------------------------------

    if "ctx_operacional" not in st.session_state:
        st.markdown("### Contexto operacional")
        if st.button("🧠 Gerar contexto automaticamente"):
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

        st.info(
            "O contexto operacional é gerado automaticamente a partir do "
            "modelo normativo e das decisões legais já tomadas."
        )
        st.stop()

    ctx_operacional = st.session_state.ctx_operacional

    # ------------------------------------------------------------
    # Renderização dos campos
    # ------------------------------------------------------------

    valores_livres = {}

    for modulo, campos in ctx_operacional.get("modulos", {}).items():
        with st.expander(modulo.replace("_", " ").title(), expanded=True):
            for chave, meta in campos.items():
                col_valor, col_just = st.columns([1, 2])
                valor_atual = meta.get("valor") or 0.0

                with col_valor:
                    if chave.startswith("percentual_"):
                        valor_pct = st.number_input(
                            chave,
                            value=float(valor_atual * 100),
                            format="%.2f",
                            help="Informe em percentual (ex: 5 = 5%)",
                            key=f"operacional_pct_{chave}",
                        )
                        valor = valor_pct / 100
                    else:
                        valor = st.number_input(
                            chave,
                            value=float(valor_atual),
                            key=f"operacional_val_{chave}",
                        )

                with col_just:
                    justificativa = st.text_input(
                        "Justificativa / referência",
                        value=meta.get("referencia_documental") or "",
                        key=f"just_{chave}",
                        placeholder="Ex.: cláusula contratual, acordo coletivo, despacho…",
                    )

                valores_livres[chave] = {
                    "valor": valor,
                    "origem": "decisao_gestor",
                    "referencia_documental": justificativa or None,
                }

    st.session_state.valores_livres = valores_livres

    col1, col2 = st.columns(2)
    with col1:
        st.button("← Voltar", on_click=voltar, key="voltar3b")
    with col2:
        st.button("Próximo →", on_click=avancar, key="avancar3")


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

    if st.button("Executar cálculo"):
        st.success("Pronto para executar via orquestrador.")

        from quase_sem_querer.motor.orquestrador import executar_modelo

        try:
            resultado = executar_modelo(
                nome_modelo=st.session_state.modelo_nome,
                contexto=contexto_final,
                no_raiz=st.session_state.no_raiz_modelo,
                persistir=True,
            )

            st.success("Cálculo executado com sucesso")

            # -------------------------------------------------------------
            # Árvore de cálculo
            # -------------------------------------------------------------
            st.subheader("🌳 Árvore do cálculo (visualização explicativa)")

            render_no(
                no_id=resultado["no_raiz"],
                nos_avaliados=resultado["nos_avaliados"],
            )
            # -------------------------------------------------------------
            # Resultado
            # -------------------------------------------------------------

            st.subheader("Resultado canônico")
            st.json(resultado)

            # -------------------------------------------------------------
            # Memória de Cálculo
            # -------------------------------------------------------------

            memoria_md = render_memoria_calculo(
                resultado,
                formato="md",
            )

            memoria_txt = render_memoria_calculo(
                resultado,
                formato="txt",
            )

            st.download_button(
                "📄 Baixar memória de cálculo (Markdown)",
                data=memoria_md,
                file_name="memoria_calculo.md",
                mime="text/markdown",
            )

            st.download_button(
                "📄 Baixar memória de cálculo (Texto)",
                data=memoria_txt,
                file_name="memoria_calculo.txt",
                mime="text/plain",
            )

        except Exception as e:
            st.error("Erro durante a execução do cálculo")
            st.exception(e)



    st.button("← Voltar", on_click=voltar, key="voltar4")
