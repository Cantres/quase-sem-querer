# ================================================================
# Persistidor de Execução
# Projeto: Quase Sem Querer
# ================================================================

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

    # ------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------

    def salvar_execucao(
        self,
        *,
        modelo_normativo: Dict,
        contexto: Dict,
        resultado: Dict[str, Any],
        no_raiz: str
    ) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        uid = uuid.uuid4().hex[:8]
        execucao_id = f"execucao_{timestamp}_{uid}"

        payload = {
            "meta_execucao": {
                "id_execucao": execucao_id,
                "formato_persistencia_version": FORMATO_PERSISTENCIA_VERSION,
                "data_execucao_utc": datetime.utcnow().isoformat() + "Z",
                "no_raiz": no_raiz,
                "hash_modelo_normativo": self._hash_json(modelo_normativo),
                "hash_contexto": self._hash_json(contexto),
            },
            "resultado": resultado,
        }

        caminho = self.diretorio / f"{execucao_id}.json"

        with caminho.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return caminho

    # ------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------

    @staticmethod
    def _hash_json(objeto: Dict) -> str:
        serializado = json.dumps(objeto, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serializado.encode("utf-8")).hexdigest()
