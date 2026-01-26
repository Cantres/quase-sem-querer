# ================================================================
# Verificador Estático do Modelo Normativo
# Projeto: Quase Sem Querer

# Responsabilidade:
# - Validar estruturalmente modelos normativos declarativos (JSON)
# - Impedir execução de árvores inválidas
# - Produzir diagnóstico auditável de inconsistências

# Nenhum cálculo é executado.
# Nenhum valor é avaliado.
# ================================================================

from typing import Dict, List, Set

TIPOS_VALIDOS = {
    "constante",
    "referencia",
    "soma",
    "multiplicacao",
    "subtracao",
    "divisao",
    "potencia",
    "raiz",
}

class ErroModeloInvalido(Exception):
    """Erro bloqueante contendo múltiplas inconsistências estruturais."""

    def __init__(self, erros: List[str]):
        self.erros = erros
        super().__init__("\n".join(erros))


class VerificadorEstatico:
    def __init__(self, modelo: Dict):
        self.modelo = modelo
        self.erros: List[str] = []
        self.nos = self._indexar_nos()
        self.grafo = self._construir_grafo_dependencias()

        # -----------------------------
        # Indexação e estrutura básica
        # -----------------------------

    def _indexar_nos(self) -> Dict[str, Dict]:
        if "nos" not in self.modelo:
            self.erros.append("Modelo inválido: chave 'nos' ausente.")
            return {}

        index = {}
        for no in self.modelo["nos"]:
            no_id = no.get("id")
            if not no_id:
                self.erros.append("Nó sem 'id' definido.")
                continue
            if no_id in index:
                self.erros.append(f"ID de nó duplicado: {no_id}")
                continue
            index[no_id] = no
        return index

    def _construir_grafo_dependencias(self) -> Dict[str, List[str]]:
        grafo = {}
        for no_id, no in self.nos.items():
            deps = no.get("dependencias", [])
            if not isinstance(deps, list):
                self.erros.append(
                    f"Nó '{no_id}': 'dependencias' deve ser lista."
                )
                grafo[no_id] = []
            else:
                grafo[no_id] = deps
        return grafo

    # -----------------------------
    # Verificação principal
    # -----------------------------

    def verificar(self):
        self._verificar_tipos()
        self._verificar_referencias_existentes()
        self._verificar_aridade_operacoes()
        self._verificar_ciclos()
        self._verificar_alcancabilidade()

        if self.erros:
            raise ErroModeloInvalido(self.erros)

    # -----------------------------
    # Verificações específicas
    # -----------------------------

    def _verificar_tipos(self):
        for no_id, no in self.nos.items():
            tipo = no.get("tipo")
            if tipo not in TIPOS_VALIDOS:
                self.erros.append(
                    f"Nó '{no_id}': tipo inválido '{tipo}'."
                )

    def _verificar_referencias_existentes(self):
        for no_id, dependencias in self.grafo.items():
            for dep in dependencias:
                if dep not in self.nos:
                    self.erros.append(
                        f"Nó '{no_id}' referencia nó inexistente '{dep}'."
                    )

    def _verificar_aridade_operacoes(self):
        for no_id, no in self.nos.items():
            tipo = no.get("tipo")
            deps = no.get("dependencias", [])

            # operações que exigem ao menos 2 operandos (vararg)
            if tipo in ("soma", "multiplicacao", "subtracao", "divisao") and len(deps) < 2:
                self.erros.append(
                    f"Nó '{no_id}' do tipo '{tipo}' deve possuir ao menos 2 dependências."
                )

            # operações que exigem exatamente 2 operandos
            if tipo in ("potencia", "raiz") and len(deps) != 2:
                self.erros.append(
                    f"Nó '{no_id}' do tipo '{tipo}' deve possuir exatamente 2 dependências."
                )

            # folhas não devem possuir dependências
            if tipo in ("constante", "referencia") and deps:
                self.erros.append(
                    f"Nó '{no_id}' do tipo '{tipo}' não deve possuir dependências."
                )

    def _verificar_ciclos(self):
        visitados: Set[str] = set()
        pilha: Set[str] = set()

        def dfs(no_id: str):
            if no_id in pilha:
                self.erros.append(
                    f"Ciclo detectado envolvendo o nó '{no_id}'."
                )
                return
            if no_id in visitados:
                return

            pilha.add(no_id)
            for dep in self.grafo.get(no_id, []):
                dfs(dep)
            pilha.remove(no_id)
            visitados.add(no_id)

        for no_id in self.nos:
            dfs(no_id)

    def _verificar_alcancabilidade(self):
        referenciados = set()
        for deps in self.grafo.values():
            referenciados.update(deps)

        nos_raiz = set(self.nos.keys()) - referenciados
        if not nos_raiz:
            self.erros.append(
                "Nenhum nó raiz identificado (ausência de ponto de consolidação)."
            )
            return

        alcançados = set()

        def marcar(no_id: str):
            if no_id in alcançados:
                return
            alcançados.add(no_id)
            for dep in self.grafo.get(no_id, []):
                marcar(dep)

        for raiz in nos_raiz:
            marcar(raiz)

        nos_orfaos = set(self.nos.keys()) - alcançados
        if nos_orfaos:
            self.erros.append(
                f"Nós inalcançáveis (órfãos): {sorted(nos_orfaos)}"
            )

    # -----------------------------
    # API pública
    # -----------------------------

    @staticmethod
    def validar_modelo(modelo: Dict):
        verificador = VerificadorEstatico(modelo)
        verificador.verificar()
        return True
