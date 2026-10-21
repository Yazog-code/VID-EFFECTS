"""VID-Effects : appliquer des effets Python à une vidéo."""

from .effect import Checkbox, Choice, Effect, Param, Slider
from .registry import Registry, discover, user_effects_dir

__all__ = ["Checkbox", "Choice", "Effect", "Param", "Registry", "Slider", "discover", "user_effects_dir"]
