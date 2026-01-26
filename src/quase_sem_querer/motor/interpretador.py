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
import math

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

        # folhas
        if tipo == "constante":
            valor = self._resolver_constante(no_id)

        elif tipo == "referencia":
            valor = self._resolver_referencia(no_id)

        # operações existentes
        elif tipo == "soma":
            valores = [self._avaliar_no(dep) for dep in no["dependencias"]]
            valor = sum(valores)

        elif tipo == "multiplicacao":
            valores = [self._avaliar_no(dep) for dep in no["dependencias"]]
            prod = 1.0
            for v in valores:
                prod *= v
            valor = prod

        elif tipo == "subtracao":
            valores = [self._avaliar_no(dep) for dep in no["dependencias"]]
            # comportamento: a - b - c - ...
            if len(valores) < 2:
                raise ErroInterpretacao(f"Nó '{no_id}' subtracao requer ao menos 2 dependências.")
            valor = valores[0] - sum(valores[1:])

        elif tipo == "divisao":
            valores = [self._avaliar_no(dep) for dep in no["dependencias"]]
            if len(valores) < 2:
                raise ErroInterpretacao(f"Nó '{no_id}' divisao requer ao menos 2 dependências.")
            resultado = valores[0]
            for idx, v in enumerate(valores[1:], start=2):
                if v == 0:
                    raise ErroInterpretacao(
                        f"Divisão por zero ao avaliar nó '{no_id}' (dependência #{idx} resultou em zero)."
                    )
                resultado /= v
            valor = resultado

        elif tipo == "potencia":
            # aridade exatamente 2: base ^ expoente
            deps = no.get("dependencias", [])
            if len(deps) != 2:
                raise ErroInterpretacao(f"Nó '{no_id}' potencia requer exatamente 2 dependências (base, expoente).")
            base = self._avaliar_no(deps[0])
            expo = self._avaliar_no(deps[1])

            # proteger contra base negativa e expoente fracionário que resultaria em número complexo
            if base < 0 and not float(expo).is_integer():
                raise ErroInterpretacao(
                    f"Potência inválida no nó '{no_id}': base negativa ({base}) com expoente fracionário ({expo}) produziria número complexo."
                )
            try:
                valor = base ** expo
            except Exception as e:
                raise ErroInterpretacao(f"Erro ao calcular potencia no nó '{no_id}': {e}")

        elif tipo == "raiz":
            # aridade exatamente 2: radicando, indice
            deps = no.get("dependencias", [])
            if len(deps) != 2:
                raise ErroInterpretacao(f"Nó '{no_id}' raiz requer exatamente 2 dependências (radicando, indice).")
            rad = self._avaliar_no(deps[0])
            indice = self._avaliar_no(deps[1])

            if indice == 0:
                raise ErroInterpretacao(f"Nó '{no_id}' raiz: índice não pode ser zero.")
            # índice deve ser inteiro natural usualmente; aceitar float inteiro (ex.: 2.0)
            if not float(indice).is_integer():
                raise ErroInterpretacao(f"Nó '{no_id}' raiz: índice deve ser número inteiro (recebido {indice}).")
            indice_int = int(indice)

            if rad < 0 and (indice_int % 2 == 0):
                raise ErroInterpretacao(
                    f"Nó '{no_id}' raiz: radicando negativo ({rad}) com índice par ({indice_int}) produziria número complexo."
                )

            try:
                # calcular raiz n-ésima: rad ** (1 / indice)
                valor = rad ** (1.0 / indice_int)
            except Exception as e:
                raise ErroInterpretacao(f"Erro ao calcular raiz no nó '{no_id}': {e}")

        else:
            raise ErroInterpretacao(f"Tipo de nó desconhecido: {tipo}")

        # memo, trilha e nos_avaliados
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
