# ================================================================
# Persistidor de Contexto
# Projeto: Quase Sem Querer
#
# Responsabilidade:
# - Persistir o resultado final de um contexto editado pelo usuário
#
# Não contém lógica jurídica.
# Não valida modelo (pressupõe verificação prévia).
# Não realiza cálculos.
# Não persiste execuções.
# ================================================================
#
import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


FORMATO_CONTEXTO_VERSION = "1.0.0"


class ErroContextoInvalido(Exception):
    """Erro estrutural bloqueante no contexto de valores."""
    pass


class PersistidorContexto:
    def __init__(self, diretorio_contextos: str = "quase_sem_querer/contexto"):
        self.diretorio = Path(diretorio_contextos)
        self.diretorio.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # API pública
    # -----------------------------

    def salvar_contexto(
        self,
        blocos_contexto: Dict[str, Dict[str, Dict[str, Any]]],
        *,
        autor: str,
        descricao: str,
        fonte_evidencia: list[str]
    ) -> Path:
        """
        Persiste um Contexto de Valores versionado e auditável.

        blocos_contexto:
            {
              "remuneracao": {
                 "salario_base": {
                     "valor": 1412.0,
                     "origem": "norma",
                     "referencia_documental": "Salário mínimo nacional"
                 }
              },
              "citl": { ... }
            }
        """

        self._validar_blocos(blocos_contexto)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        uid = uuid.uuid4().hex[:6]
        id_contexto = f"contexto_{timestamp}_{uid}"

        contexto = {
            "meta": {
                "id_contexto": id_contexto,
                "formato_contexto_version": FORMATO_CONTEXTO_VERSION,
                "autor": autor,
                "data_criacao_utc": datetime.utcnow().isoformat() + "Z",
                "descricao": descricao,
                "fonte_evidencia": fonte_evidencia
            }
        }

        # anexar blocos
        for nome_bloco, conteudo in blocos_contexto.items():
            contexto[nome_bloco] = conteudo

        # hash do contexto completo
        contexto["meta"]["hash_contexto"] = self._hash_json(contexto)

        caminho = self.diretorio / f"{id_contexto}.json"

        with caminho.open("w", encoding="utf-8") as f:
            json.dump(contexto, f, indent=2, ensure_ascii=False)

        return caminho

    # -----------------------------
    # Validação estrutural mínima
    # -----------------------------

    def _validar_blocos(self, blocos: Dict[str, Dict[str, Any]]) -> None:
        if not isinstance(blocos, dict) or not blocos:
            raise ErroContextoInvalido("Contexto vazio ou inválido.")

        for nome_bloco, bloco in blocos.items():
            if not isinstance(bloco, dict):
                raise ErroContextoInvalido(
                    f"Bloco '{nome_bloco}' deve ser um dicionário."
                )

            for chave, item in bloco.items():
                if not isinstance(item, dict):
                    raise ErroContextoInvalido(
                        f"Entrada '{chave}' no bloco '{nome_bloco}' deve ser um objeto."
                    )

                for campo in ("valor", "origem", "referencia_documental"):
                    if campo not in item:
                        raise ErroContextoInvalido(
                            f"Entrada '{chave}' no bloco '{nome_bloco}' "
                            f"não contém o campo obrigatório '{campo}'."
                        )

    # -----------------------------
    # Utilidades
    # -----------------------------

    @staticmethod
    def _hash_json(objeto: Dict) -> str:
        serializado = json.dumps(objeto, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serializado.encode("utf-8")).hexdigest()
