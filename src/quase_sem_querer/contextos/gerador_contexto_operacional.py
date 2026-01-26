from typing import Dict, Set


def extrair_chaves_legais(contexto_legal: Dict) -> Set[str]:
    """
    Extrai todas as chaves já decididas no contexto legal.
    """
    chaves = set()
    for campos in contexto_legal.get("modulos", {}).values():
        chaves.update(campos.keys())
    return chaves


def gerar_super_contexto_operacional(
    modelo_normativo: Dict,
    contexto_legal: Dict
) -> Dict:
    """
    Gera um super-contexto operacional alinhado estruturalmente
    aos módulos do modelo normativo.

    - Preserva os nomes dos módulos
    - Inclui apenas nós do tipo constante ou referencia
    - Exclui nós já decididos no contexto legal
    """

    chaves_legais = extrair_chaves_legais(contexto_legal)

    modulos_operacionais: Dict[str, Dict] = {}

    for nome_modulo, conteudo_modulo in modelo_normativo.get("modulos", {}).items():
        nos = conteudo_modulo.get("nos", [])

        campos_modulo = {}

        for no in nos:
            no_id = no.get("id")
            no_tipo = no.get("tipo")

            # Apenas folhas do modelo exigem valor humano
            if no_tipo not in {"constante", "referencia"}:
                continue

            # Se já foi decidido no contexto legal, não é operacional
            if no_id in chaves_legais:
                continue

            campos_modulo[no_id] = {
                "valor": None,
                "origem": None,
                "referencia_documental": None
            }

        # Só cria o módulo se houver campos operacionais nele
        if campos_modulo:
            modulos_operacionais[nome_modulo] = campos_modulo

    return {
        "tipo": "super_contexto",
        "modulos": modulos_operacionais
    }
