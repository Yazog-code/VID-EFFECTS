"""Découverte automatique des effets.

Tout fichier `.py` placé dans un dossier d'effets est chargé, et chaque
classe qui hérite de `Effect` devient disponible. Un fichier qui plante
n'empêche pas les autres de se charger : son erreur est gardée dans
`Registry.errors` pour être affichée dans l'interface.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import os
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

from .effect import Effect

BUILTIN_DIR = Path(__file__).parent / "effets_inclus"


def user_effects_dir() -> Path:
    """Dossier des effets personnels : `~/VID-Effects/effets`, ou la variable `VID_EFFECTS_DIR`."""
    custom = os.environ.get("VID_EFFECTS_DIR")
    return Path(custom).expanduser() if custom else Path.home() / "VID-Effects" / "effets"


@dataclass
class Registry:
    effects: dict[str, type[Effect]] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def names(self) -> list[str]:
        return sorted(self.effects, key=str.casefold)

    def get(self, name: str) -> type[Effect]:
        try:
            return self.effects[name]
        except KeyError:
            raise KeyError(f"Effet inconnu : « {name} »") from None

    def load_dir(self, directory: Path) -> None:
        if not directory.is_dir():
            return
        for path in sorted(directory.glob("*.py")):
            if not path.name.startswith("_"):
                self.load_file(path)

    def load_file(self, path: Path) -> None:
        try:
            module = _import_file(path)
        except Exception:
            self.errors[str(path)] = traceback.format_exc()
            return
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not issubclass(obj, Effect) or obj is Effect or obj.__module__ != module.__name__:
                continue
            if not obj.name:
                self.errors[str(path)] = f"La classe {obj.__qualname__} n'a pas d'attribut `name`."
                continue
            if obj.name in self.effects:
                other = self.effects[obj.name].source
                self.errors[str(path)] = f"Le nom « {obj.name} » est déjà utilisé par {other}."
                continue
            obj.source = str(path)
            self.effects[obj.name] = obj


def _import_file(path: Path):
    # Nom de module unique par chemin, pour que deux fichiers du même nom ne se marchent pas dessus.
    digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:10]
    module_name = f"vid_effects_plugin_{path.stem}_{digest}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        del sys.modules[module_name]
        raise
    return module


def discover(extra_dirs: list[Path] | None = None, create_user_dir: bool = True) -> Registry:
    """Charge les effets inclus, puis ceux du dossier personnel, puis `extra_dirs`."""
    registry = Registry()
    user_dir = user_effects_dir()
    if create_user_dir:
        user_dir.mkdir(parents=True, exist_ok=True)
    for directory in [BUILTIN_DIR, user_dir, *(extra_dirs or [])]:
        registry.load_dir(Path(directory))
    return registry
