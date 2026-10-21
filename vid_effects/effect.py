"""Base commune à tous les effets.

Un effet est une classe qui hérite de `Effect`. Le plus simple est de
redéfinir `frame()`, appelée pour chaque image de la vidéo. Pour les effets
qui touchent au temps ou au son (accéléré, ralenti...), on redéfinit
plutôt `clip()`, qui reçoit la vidéo entière.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass(frozen=True)
class Param:
    """Un réglage d'effet affiché dans l'interface."""

    name: str
    label: str
    default: Any

    def validate(self, value: Any) -> Any:
        return value


@dataclass(frozen=True)
class Slider(Param):
    """Curseur numérique entre `minimum` et `maximum`."""

    minimum: float = 0.0
    maximum: float = 1.0
    step: float | None = None

    def validate(self, value: Any) -> float:
        value = float(value)
        return min(max(value, self.minimum), self.maximum)


@dataclass(frozen=True)
class Choice(Param):
    """Liste déroulante parmi `options`."""

    options: tuple[str, ...] = field(default_factory=tuple)

    def validate(self, value: Any) -> str:
        if value not in self.options:
            raise ValueError(f"« {value} » n'est pas une option de « {self.label} » : {self.options}")
        return value


@dataclass(frozen=True)
class Checkbox(Param):
    """Case à cocher (vrai / faux)."""

    def validate(self, value: Any) -> bool:
        return bool(value)


class Effect:
    """Classe à hériter pour créer un effet.

    Attributs à définir dans la classe fille :
      - `name` : nom affiché dans l'interface (obligatoire)
      - `description` : phrase courte affichée sous le nom
      - `params` : liste de réglages (`Slider`, `Choice`, `Checkbox`)
    """

    name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    params: ClassVar[list[Param]] = []

    # Rempli par le registre : fichier d'où vient l'effet.
    source: ClassVar[str] = ""

    def frame(self, image, t: float, **params):
        """Transforme une image (tableau NumPy hauteur x largeur x 3, valeurs 0-255).

        `t` est le temps de l'image en secondes. Doit renvoyer une image de même forme.
        """
        raise NotImplementedError

    def clip(self, clip, **params):
        """Transforme la vidéo entière (un clip MoviePy) et renvoie le nouveau clip.

        Par défaut, applique `frame()` à chaque image sans toucher au son.
        """
        return clip.transform(lambda get_frame, t: self.frame(get_frame(t), t, **params))

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return {p.name: p.default for p in cls.params}

    @classmethod
    def resolve_params(cls, values: dict[str, Any] | None = None) -> dict[str, Any]:
        """Complète les valeurs manquantes par défaut et valide chaque réglage."""
        values = values or {}
        known = {p.name for p in cls.params}
        unknown = set(values) - known
        if unknown:
            raise ValueError(f"Réglages inconnus pour « {cls.name} » : {sorted(unknown)}")
        return {p.name: p.validate(values.get(p.name, p.default)) for p in cls.params}

    def apply(self, clip, values: dict[str, Any] | None = None):
        """Point d'entrée utilisé par le moteur de rendu."""
        return self.clip(clip, **self.resolve_params(values))
