# ================================================================
# Carregador unificado de contextos de valores
# Projeto: Quase Sem Querer
#
# Este carregador aceita:
# 1) contexto atômico (formato atual, chaves planas ou agrupadas)
# 2) super-contexto (formato: {"tipo": "super_contexto", "modulos": {...}})
# 3) FUTURO: contexto composto/importado
#
# A responsabilidade deste módulo é:
# - carregar JSON
# - normalizar para um único contexto de valores
# - entregar um contexto pronto para o interpretador
#
# Nenhuma inferência, cálculo ou validação normativa ocorre aqui.
# ================================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


# ----------------------------------------------------------------
# Exceções
# ----------------------------------------------------------------

class ErroContextoInvalido(Exception):
    """Erro estrutural bloqueante no carregamento do contexto."""
    pass


# ----------------------------------------------------------------
# API pública
# ----------------------------------------------------------------

Contexto = Dict[str, Any]


def carregar_contexto(nome_contexto: str, *, base_dir: Path | None = None) -> Contexto:
    """
    Ponto único de entrada para carregamento de contextos de valores.

    Aceita:
    - contexto atômico (legado)
    - super-contexto (achatado por módulos)
    - FUTURO: contexto composto/importado
    """

    base_dir = base_dir or Path(__file__).resolve().parent.parent / "contextos"
    caminho = base_dir / nome_contexto

    if not caminho.exists():
        raise FileNotFoundError(f"Contexto não encontrado: {caminho}")

    with caminho.open("r", encoding="utf-8") as f:
        contexto_raw = json.load(f)

    # 1) Super-contexto (prioridade explícita)
    if contexto_raw.get("tipo") == "super_contexto":
        return _carregar_super_contexto(contexto_raw)

    # 2) Contexto atômico (legado)
    return _normalizar_contexto_atomico(contexto_raw)


# ----------------------------------------------------------------
# Implementações internas
# ----------------------------------------------------------------


def _normalizar_contexto_atomico(contexto: Contexto) -> Contexto:
    if not isinstance(contexto, dict):
        raise ErroContextoInvalido("Contexto deve ser um objeto JSON.")

    return contexto



def _carregar_super_contexto(contexto: Contexto) -> Contexto:
    """
    Achata um super-contexto em um único contexto de valores.

    Estrutura esperada:
    {
      "tipo": "super_contexto",
      "modulos": {
        "remuneracao": { ... },
        "insumos": { ... }
      }
    }
    """

    modulos = contexto.get("modulos")
    if not isinstance(modulos, dict) or not modulos:
        raise ErroContextoInvalido(
            "Super-contexto deve conter a chave 'modulos' com ao menos um módulo."
        )

    contexto_flat: Dict[str, Any] = {}

    for nome_modulo, valores in modulos.items():
        if not isinstance(valores, dict):
            raise ErroContextoInvalido(
                f"Módulo de contexto '{nome_modulo}' deve ser um objeto JSON."
            )

        for chave, definicao in valores.items():
            if chave in contexto_flat:
                raise ErroContextoInvalido(
                    f"Chave de contexto duplicada '{chave}' entre módulos."
                )

            contexto_flat[chave] = definicao

    return contexto_flat


# ----------------------------------------------------------------
# Testes mínimos (sanity checks)
# ----------------------------------------------------------------


def _test_contexto_atomico():
    ctx = {"x": {"valor": 1}}
    out = _normalizar_contexto_atomico(ctx)
    assert out["x"]["valor"] == 1


def _test_super_contexto():
    ctx = {
        "tipo": "super_contexto",
        "modulos": {
            "a": {"x": {"valor": 1}},
            "b": {"y": {"valor": 2}},
        },
    }
    out = _carregar_super_contexto(ctx)
    assert out["x"]["valor"] == 1
    assert out["y"]["valor"] == 2
