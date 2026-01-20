# ================================================================
# Carregador unificado de modelos normativos
# Projeto: Quase Sem Querer
#
# Este carregador aceita:
# 1) modelos atômicos (formato atual: {"nos": [...]})
# 2) super-modelos (formato: {"tipo": "super_modelo", "modulos": {...}})
# 3) FUTURO: modelos compostos com imports explícitos
#
# A responsabilidade deste módulo é:
# - carregar JSON
# - normalizar para um único grafo normativo
# - entregar um modelo pronto para o VerificadorEstatico
#
# Nenhuma validação semântica ou cálculo ocorre aqui.
# ================================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


# ----------------------------------------------------------------
# Exceções
# ----------------------------------------------------------------

class ErroModeloNormativoInvalido(Exception):
    """Erro estrutural bloqueante no carregamento do modelo normativo."""
    pass


# ----------------------------------------------------------------
# API pública
# ----------------------------------------------------------------

Modelo = Dict[str, Any]


def carregar_modelo(nome_modelo: str, *, base_dir: Path | None = None) -> Modelo:
    """
    Ponto único de entrada para carregamento de modelos normativos.

    Aceita:
    - modelo atômico (formato legado)
    - super-modelo (achatado por módulos)
    - FUTURO: modelo composto com imports
    """

    base_dir = base_dir or Path(__file__).resolve().parent.parent / "modelos_normativos"
    caminho = base_dir / nome_modelo

    if not caminho.exists():
        raise FileNotFoundError(f"Modelo normativo não encontrado: {caminho}")

    with caminho.open("r", encoding="utf-8") as f:
        modelo_raw = json.load(f)

    # 1) Super-modelo (prioridade explícita)
    if modelo_raw.get("tipo") == "super_modelo":
        return _carregar_super_modelo(modelo_raw)

    # 2) Modelo composto (placeholder para evolução futura)
    if modelo_raw.get("tipo") == "composto":
        raise NotImplementedError(
            "Modelo composto com imports ainda não implementado."
        )

    # 3) Modelo atômico (legado)
    return _normalizar_modelo_atomico(modelo_raw)


# ----------------------------------------------------------------
# Implementações internas
# ----------------------------------------------------------------


def _normalizar_modelo_atomico(modelo: Modelo) -> Modelo:
    if "nos" not in modelo:
        raise ErroModeloNormativoInvalido(
            "Modelo atômico inválido: chave 'nos' ausente."
        )

    return {
        "nos": modelo["nos"],
        "raiz": modelo.get("raiz"),
    }



def _carregar_super_modelo(modelo: Modelo) -> Modelo:
    """
    Achata um super-modelo em um único grafo normativo.
    """

    modulos = modelo.get("modulos")
    if not isinstance(modulos, dict) or not modulos:
        raise ErroModeloNormativoInvalido(
            "Super-modelo deve conter a chave 'modulos' com ao menos um módulo."
        )

    raiz = modelo.get("raiz")
    if not raiz:
        raise ErroModeloNormativoInvalido(
            "Super-modelo deve declarar explicitamente o nó raiz."
        )

    nos_flat: Dict[str, Dict[str, Any]] = {}

    for nome_modulo, conteudo in modulos.items():
        nos = conteudo.get("nos")
        if not isinstance(nos, list):
            raise ErroModeloNormativoInvalido(
                f"Módulo '{nome_modulo}' deve conter lista 'nos'."
            )

        for no in nos:
            no_id = no.get("id")
            if not no_id:
                raise ErroModeloNormativoInvalido(
                    f"Módulo '{nome_modulo}' contém nó sem 'id'."
                )

            if no_id in nos_flat:
                raise ErroModeloNormativoInvalido(
                    f"ID de nó duplicado '{no_id}' entre módulos."
                )

            nos_flat[no_id] = no

    return {
        "nos": list(nos_flat.values()),
        "raiz": raiz,
    }


# ----------------------------------------------------------------
# Testes mínimos (sanity checks)
# ----------------------------------------------------------------


def _test_modelo_atomico():
    modelo = {"nos": [{"id": "x", "tipo": "constante", "dependencias": []}]}
    out = _normalizar_modelo_atomico(modelo)
    assert "nos" in out


def _test_super_modelo():
    modelo = {
        "tipo": "super_modelo",
        "modulos": {
            "a": {"nos": [{"id": "x", "tipo": "constante", "dependencias": []}]},
            "b": {"nos": [{"id": "y", "tipo": "soma", "dependencias": ["x", "x"]}]},
        },
        "raiz": "y",
    }
    out = _carregar_super_modelo(modelo)
    assert len(out["nos"]) == 2
    assert out["raiz"] == "y"
