# ================================================================
# cli.py — Entrada única para a UI
# Projeto: Quase Sem Querer
# ================================================================

from __future__ import annotations
import subprocess
import sys
from pathlib import Path


def main() -> None:
    app = Path(__file__).parent / "app_streamlit.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app)],
        check=True,
    )


if __name__ == "__main__":
    main()
