from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

def open_path(path: Path) -> None:
    p = Path(path)
    if not p.exists():
        return

    try:
        if sys.platform.startswith("win"):
            os.startfile(str(p))  # noqa: S606 (Windows shell open)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
    except Exception:
        # Do not crash the run if opening fails
        return
