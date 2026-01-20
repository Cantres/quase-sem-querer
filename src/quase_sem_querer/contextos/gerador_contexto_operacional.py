from typing import Dict, Set


def extrair_chaves_modelo(modelo: Dict) -> Set[str]:
    chaves = set()
    for modulo in modelo.get("modulos", {}).values():
        for no in modulo.get("nos", []):
            if no.get("tipo") in {"constante", "referencia"}:
                chaves.add(no["id"])
    return chaves


def extrair_chaves_contexto(contexto_legal: Dict) -> Set[str]:
    chaves = set()
    for campos in contexto_legal.get("modulos", {}).values():
        chaves.update(campos.keys())
    return chaves


def gerar_super_contexto_operacional(
    modelo_normativo: Dict,
    contexto_legal: Dict
) -> Dict:
    chaves_modelo = extrair_chaves_modelo(modelo_normativo)
    chaves_legais = extrair_chaves_contexto(contexto_legal)

    chaves_operacionais = sorted(chaves_modelo - chaves_legais)

    return {
        "tipo": "super_contexto",
        "modulos": {
            "operacional": {
                chave: {
                    "valor": None,
                    "origem": None,
                    "referencia_documental": None
                }
                for chave in chaves_operacionais
            }
        }
    }
