"""Lance VID-Effects : dans sa propre fenêtre si pywebview est disponible, sinon dans le navigateur.

    python -m vid_effects               # fenêtre d'application
    python -m vid_effects --navigateur  # page dans le navigateur
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    from .ui import build_app, launch

    app = build_app()
    try:
        if "--navigateur" in argv:
            raise ImportError
        import webview
    except ImportError:
        launch(app, inbrowser=True)  # bloque jusqu'à Ctrl+C
        return

    url = launch(app, prevent_thread_lock=True, quiet=True)
    webview.settings["ALLOW_DOWNLOADS"] = True
    webview.create_window("VID-Effects", url, width=1200, height=850, min_size=(800, 600))
    webview.start()  # bloque jusqu'à la fermeture de la fenêtre
    app.close()


if __name__ == "__main__":
    main()
