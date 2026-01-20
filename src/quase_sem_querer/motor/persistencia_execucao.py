# ================================================================
# Persistidor de Execução
# Projeto: Quase Sem Querer
#
# Responsabilidade:
# - Persistir o resultado final de uma execução
# - Utilizar exclusivamente valores do contexto e do modelo normativo
# - Produzir resultado determinístico e auditável
#
# Não contém lógica jurídica.
# Não valida modelo (pressupõe verificação prévia).
# Não realiza cálculos.
# ================================================================
#
import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


FORMATO_PERSISTENCIA_VERSION = "1.0.0"


class PersistidorExecucao:
    def __init__(self, diretorio_resultados: Path | None = None):
         if diretorio_resultados is None:
             diretorio_resultados = (
                 Path(__file__)
                 .resolve()
                 .parent.parent
                 / "resultados"
                 / "execucoes"
             )

         self.diretorio = diretorio_resultados
         self.diretorio.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # API pública
    # -----------------------------

    def salvar_execucao(
        self,
        modelo_normativo: Dict,
        contexto: Dict,
        resultado: Dict[str, Any],
        no_raiz: str
    ) -> Path:
        # id único da execução: timestamp UTC + uuid4
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        uid = uuid.uuid4().hex[:8]
        execucao_id = f"execucao_{timestamp}_{uid}"

        # hashes estáveis dos artefatos de entrada
        hash_modelo = self._hash_json(modelo_normativo)
        hash_contexto = self._hash_json(contexto)

        # extrair recorte decisório do contexto: para nós folha avaliados
        decisoes = self._extrair_decisoes_humanas(contexto, resultado.get("trilha_calculo", {}))

        payload = {
            "meta_execucao": {
                "id_execucao": execucao_id,
                "formato_persistencia_version": FORMATO_PERSISTENCIA_VERSION,
                "data_execucao_utc": datetime.utcnow().isoformat() + "Z",
                "no_raiz": no_raiz,
                "hash_modelo_normativo": hash_modelo,
                "hash_contexto": hash_contexto
            },
            # resultado fornecido pelo interpretador (valor + trilha)
            "resultado": resultado,
            # recorte decisório (valores + origem + referencia_documental) usado na execução
            "decisoes_humanas": decisoes
        }

        caminho = self.diretorio / f"{execucao_id}.json"

        # gravação com indent para facilitar auditoria manual
        with caminho.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return caminho

    # -----------------------------
    # Utilidades internas
    # -----------------------------

    @staticmethod
    def _hash_json(objeto: Dict) -> str:
        """
        Gera hash SHA-256 estável do conteúdo JSON.
        """
        serializado = json.dumps(objeto, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serializado.encode("utf-8")).hexdigest()

    def _extrair_decisoes_humanas(self, contexto: Dict, trilha_calculo: Dict) -> Dict[str, Any]:
        """
        Gera um recorte do contexto contendo apenas as entradas
        correspondentes a nós folha (constante/referencia) efetivamente avaliados.

        Estratégia:
        - percorre a trilha_calculo;
        - identifica nós cujo tipo é 'constante' ou 'referencia' OR nós com dependencias vazias;
        - para cada nó folha, procura por uma entrada no contexto (procura por chave em cada bloco do contexto);
        - quando encontrada, inclui o objeto inteiro (valor, origem, referencia_documental);
        - quando não encontrada, inclui um marcador para auditoria.
        """

        decisoes: Dict[str, Any] = {}

        for no_id, meta in trilha_calculo.items():
            tipo = meta.get("tipo", "")
            deps = meta.get("dependencias", [])

            is_folha = (tipo in ("constante", "referencia")) or (not deps)
            if not is_folha:
                continue

            encontrado = False
            # procura dentro dos blocos do contexto (ex.: "remuneracao": {...})
            for bloco_nome, bloco in contexto.items():
                if isinstance(bloco, dict) and no_id in bloco:
                    # copia inteira do item do contexto (preserva origem e referencia_documental)
                    decisoes[no_id] = {
                        "bloco_contexto": bloco_nome,
                        "presente_no_contexto": True,
                        "conteudo": bloco[no_id]
                    }
                    encontrado = True
                    break

            if not encontrado:
                # registro explícito de ausência para auditoria posterior
                decisoes[no_id] = {
                    "bloco_contexto": None,
                    "presente_no_contexto": False,
                    "conteudo": None
                }

        return decisoes
