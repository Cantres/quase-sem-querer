# ================================================================
# Interpretador de Árvores Normativas
# Projeto: Quase Sem Querer
#
# Responsabilidade:
# - Avaliar modelos normativos declarativos (árvores de expressão)
# - Utilizar exclusivamente valores do Contexto
# - Produzir resultado determinístico e auditável
#
# Não contém lógica jurídica.
# Não valida modelo (pressupõe verificação prévia).
# Não persiste resultados.
# ================================================================

from typing import Dict, Any


class ErroInterpretacao(Exception):
    """Erro ocorrido durante a avaliação da árvore normativa."""
    pass


class InterpretadorArvoreNormativa:
    def __init__(self, modelo_normativo: Dict, contexto: Dict):
        self.modelo = modelo_normativo
        self.contexto = contexto
        self.nos = self._indexar_nos()
        self.memo: Dict[str, float] = {}
        self.trilha: Dict[str, Dict[str, Any]] = {}
        self._nos_avaliados = {}

    # -----------------------------
    # Preparação
    # -----------------------------

    def _indexar_nos(self) -> Dict[str, Dict]:
        index = {}
        for no in self.modelo.get("nos", []):
            index[no["id"]] = no
        return index

    # -----------------------------
    # API pública
    # -----------------------------

    def executar(self, no_raiz: str) -> Dict[str, Any]:
        valor_final = self._avaliar_no(no_raiz)
        return {
            "no_raiz": no_raiz,
            "valor_final": valor_final,
            "trilha_calculo": self.trilha,
            "nos_avaliados": self._nos_avaliados,
        }

    # -----------------------------
    # Avaliação recursiva
    # -----------------------------

    def _avaliar_no(self, no_id: str) -> float:
        if no_id in self.memo:
            return self.memo[no_id]

        if no_id not in self.nos:
            raise ErroInterpretacao(f"Nó inexistente: {no_id}")

        no = self.nos[no_id]
        tipo = no["tipo"]

        if tipo == "constante":
            valor = self._resolver_constante(no_id)

        elif tipo == "referencia":
            valor = self._resolver_referencia(no_id)

        elif tipo == "soma":
            valores = [self._avaliar_no(dep) for dep in no["dependencias"]]
            valor = sum(valores)

        elif tipo == "multiplicacao":
            valores = [self._avaliar_no(dep) for dep in no["dependencias"]]
            valor = 1
            for v in valores:
                valor *= v

        else:
            raise ErroInterpretacao(f"Tipo de nó desconhecido: {tipo}")

        self.memo[no_id] = valor
        self.trilha[no_id] = {
            "tipo": tipo,
            "dependencias": no.get("dependencias", []),
            "valor_calculado": valor,
            "metadados_juridicos": no.get("metadados_juridicos", {})
        }
        self._nos_avaliados[no_id] = {
            "tipo": no["tipo"],
            "dependencias": list(no.get("dependencias", [])),
            "valor_calculado": valor,
            "metadados_juridicos": no.get("metadados_juridicos", {}),
        }
        return valor

    # -----------------------------
    # Resolução de folhas
    # -----------------------------

    def _resolver_constante(self, no_id: str) -> float:
        valor = self._buscar_valor_contexto(no_id)
        if valor is None:
            raise ErroInterpretacao(
                f"Constante '{no_id}' não encontrada no Contexto."
            )
        return valor

    def _resolver_referencia(self, no_id: str) -> float:
        valor = self._buscar_valor_contexto(no_id)
        if valor is None:
            raise ErroInterpretacao(
                f"Referência '{no_id}' não encontrada no Contexto."
            )
        return valor

    # -----------------------------
    # Contexto
    # -----------------------------

    def _buscar_valor_contexto(self, chave: str) -> float | None:
        """
        Procura valor no contexto por chave plana.
        """
        item = self.contexto.get(chave)
        if isinstance(item, dict) and "valor" in item:
            return item["valor"]
        return None
