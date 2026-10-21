# Recette PyInstaller : `pyinstaller packaging/vid_effects.spec` depuis la racine du dépôt.
# Sur Mac, produit dist/VID-Effects.app ; ailleurs, le dossier dist/VID-Effects.

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).parent

datas, binaries, hiddenimports = [], [], []
# Gradio et ses dépendances lisent leurs propres fichiers (front-end, modèles) à l'exécution.
for package in ["gradio", "gradio_client", "safehttpx", "groovy", "imageio_ffmpeg", "moviepy", "proglog"]:
    d, b, h = collect_all(package)
    datas += d
    binaries += b
    hiddenimports += h
if sys.platform == "darwin":
    d, b, h = collect_all("webview")
    datas += d
    binaries += b
    hiddenimports += h

# Les effets inclus sont chargés comme fichiers .py, ils doivent donc être copiés tels quels.
datas.append((str(ROOT / "vid_effects" / "effets_inclus"), "vid_effects/effets_inclus"))
# Les effets personnels peuvent importer ces bibliothèques : on les embarque en entier.
hiddenimports += collect_submodules("vid_effects") + collect_submodules("PIL") + collect_submodules("numpy")

a = Analysis(
    [str(ROOT / "packaging" / "launcher.py")],
    pathex=[str(ROOT)],
    datas=datas,
    binaries=binaries,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "pytest"],
    # Gradio inspecte le code source de ses modules : il faut les garder en .py.
    module_collection_mode={"gradio": "py", "gradio_client": "py"},
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VID-Effects",
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="VID-Effects")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="VID-Effects.app",
        bundle_identifier="io.github.yazog-code.vid-effects",
        info_plist={
            "CFBundleDisplayName": "VID-Effects",
            "CFBundleShortVersionString": "0.1.0",
            "NSHighResolutionCapable": True,
        },
    )
