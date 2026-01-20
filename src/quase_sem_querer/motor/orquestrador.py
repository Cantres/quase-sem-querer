# ================================================================
# Orquestrador da Execução
# Projeto: Quase Sem Querer
#
# Este módulo define o fluxo ÚNICO de execução do sistema:
# 1) carregamento do modelo normativo (atômico / super-modelo)
# 2) carregamento do contexto de valores (atômico / super-contexto)
# 3) verificação estática do modelo
# 4) interpretação da árvore normativa
# 5) persistência opcional da execução
#
# Nenhuma lógica de UI ou CLI reside aqui.
# ================================================================

from __future__ import annotations

from typing import Any, Dict

from quase_sem_querer.carregadores.carregador_modelo import carregar_modelo
from quase_sem_querer.carregadores.carregador_contexto import carregar_contexto
from quase_sem_querer.motor.interpretador import InterpretadorArvoreNormativa
from quase_sem_querer.motor.verificador import VerificadorEstatico
from quase_sem_querer.motor.persistencia_execucao import PersistidorExecucao


# ----------------------------------------------------------------
# API pública
# ----------------------------------------------------------------


def executar_modelo(
    *,
    nome_modelo: str,
    nome_contexto: str | None = None,
    contexto: Dict[str, Any] | None = None,
    no_raiz: str,
    persistir: bool = False,
) -> Dict[str, Any]:
    """
    Executa um modelo normativo de forma canônica.

    Parâmetros:
    - nome_modelo: nome do arquivo JSON do modelo normativo
    - nome_contexto: nome do arquivo JSON do contexto (opcional)
    - contexto: contexto já carregado em memória (opcional)
    - no_raiz: identificador do nó raiz a ser avaliado
    - persistir: se True, persiste a execução

    O `nome_contexto` ou `contexto` é um 'Exclusive OR'. Um ou outro deve ser informado.
    """

    if (nome_contexto is None and contexto is None) or (
        nome_contexto is not None and contexto is not None
    ):
        raise ValueError(
            "Informe exatamente um entre 'nome_contexto' ou 'contexto'."
        )

    # 1) Carregar modelo normativo (atômico ou super-modelo)
    modelo = carregar_modelo(nome_modelo)

    # 2) Carregar contexto (atômico ou super-contexto)
    if nome_contexto is not None:
        contexto_final = carregar_contexto(nome_contexto)
    else:
        contexto_final = contexto

    # 3) Verificação estática do modelo
    VerificadorEstatico.validar_modelo(modelo)

    # 4) Interpretação da árvore normativa
    interpretador = InterpretadorArvoreNormativa(modelo, contexto_final)
    resultado = interpretador.executar(no_raiz)

    # 5) Persistência opcional
    if persistir:
        PersistidorExecucao().salvar_execucao(
            modelo_normativo=modelo,
            contexto=contexto_final,
            resultado=resultado,
            no_raiz=no_raiz,
        )

    return resultado


# ----------------------------------------------------------------
# Testes mínimos (sanity checks)
# ----------------------------------------------------------------


def _test_fluxo_minimo(monkeypatch):
    """Teste estrutural do fluxo sem executar cálculo real."""

    def fake_carregar_modelo(nome):
        return {"nos": [{"id": "x", "tipo": "constante", "dependencias": []}], "raiz": "x"}

    def fake_carregar_contexto(nome):
        return {"x": {"valor": 1}}

    class FakeInterpretador:
        def __init__(self, modelo, contexto):
            pass

        def executar(self, raiz):
            return {"resultado": 1}

    monkeypatch.setattr(
        "quase_sem_querer.carregadores.carregador_modelo.carregar_modelo",
        fake_carregar_modelo,
    )
    monkeypatch.setattr(
        "quase_sem_querer.carregadores.carregador_contexto.carregar_contexto",
        fake_carregar_contexto,
    )
    monkeypatch.setattr(
        "quase_sem_querer.motor.interpretador.InterpretadorArvoreNormativa",
        FakeInterpretador,
    )

    out = executar_modelo(
        nome_modelo="x.json",
        nome_contexto="c.json",
        no_raiz="x",
        persistir=False,
    )

    assert out["resultado"] == 1
