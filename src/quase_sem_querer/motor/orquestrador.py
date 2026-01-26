# ================================================================
# Orquestração canônica da execução normativa
# Projeto: Quase Sem Querer
# ================================================================

from __future__ import annotations
from typing import Any, Dict

from quase_sem_querer.carregadores.carregador_modelo import carregar_modelo
from quase_sem_querer.carregadores.carregador_contexto import carregar_contexto
from quase_sem_querer.motor.interpretador import InterpretadorArvoreNormativa
from quase_sem_querer.motor.verificador import VerificadorEstatico
from quase_sem_querer.motor.persistencia_execucao import PersistidorExecucao


def executar_modelo(
    *,
    nome_modelo: str,
    nome_contexto: str | None = None,
    contexto: Dict[str, Any] | None = None,
    no_raiz: str,
    persistir: bool = False,
) -> Dict[str, Any]:

    if (nome_contexto is None and contexto is None) or (
        nome_contexto is not None and contexto is not None
    ):
        raise ValueError(
            "Informe exatamente um entre 'nome_contexto' ou 'contexto'."
        )

    modelo = carregar_modelo(nome_modelo)

    if nome_contexto is not None:
        contexto_final = carregar_contexto(nome_contexto)
    else:
        contexto_final = contexto

    VerificadorEstatico.validar_modelo(modelo)

    interpretador = InterpretadorArvoreNormativa(modelo, contexto_final)
    resultado = interpretador.executar(no_raiz)

    if persistir:
        PersistidorExecucao().salvar_execucao(
            modelo_normativo=modelo,
            contexto=contexto_final,
            resultado=resultado,
            no_raiz=no_raiz,
        )

    return resultado
