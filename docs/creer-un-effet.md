# Créer un effet

Un effet est un fichier `.py` déposé dans le dossier **`~/VID-Effects/effets`** (dans ton dossier personnel, créé automatiquement au premier lancement). Au prochain lancement de l'application, l'effet apparaît dans la liste. Pas besoin de reconstruire l'application.

## L'exemple le plus simple

```python
from vid_effects import Effect


class Inverser(Effect):
    name = "Inverser les couleurs"
    description = "Effet négatif photo."

    def frame(self, image, t):
        return 255 - image
```

`frame()` est appelée pour chaque image de la vidéo :

- `image` est un tableau NumPy de taille hauteur x largeur x 3 (rouge, vert, bleu), avec des valeurs de 0 à 255 ;
- `t` est le moment de l'image, en secondes ;
- elle doit renvoyer une image de la même taille.

## Ajouter des réglages

Les réglages déclarés dans `params` s'affichent dans l'interface et sont passés à `frame()` par leur nom.

```python
import numpy as np
from vid_effects import Effect, Slider, Choice, Checkbox


class Teinte(Effect):
    name = "Teinte"
    params = [
        Slider("force", "Force", default=0.5, minimum=0.0, maximum=1.0, step=0.05),
        Choice("couleur", "Couleur", default="bleu", options=("rouge", "vert", "bleu")),
        Checkbox("inverser", "Inverser ensuite", default=False),
    ]

    def frame(self, image, t, force, couleur, inverser):
        canal = {"rouge": 0, "vert": 1, "bleu": 2}[couleur]
        out = image.astype(np.float32)
        out[..., canal] = out[..., canal] * (1 - force) + 255 * force
        if inverser:
            out = 255 - out
        return out.astype(np.uint8)
```

## Effets qui touchent au temps ou au son

Pour accélérer, ralentir, couper ou modifier le son, redéfinis `clip()` au lieu de `frame()`. Elle reçoit la vidéo entière (un clip [MoviePy](https://zulko.github.io/moviepy/)) et doit renvoyer le nouveau clip.

```python
from vid_effects import Effect, Slider
from moviepy import vfx


class Vitesse(Effect):
    name = "Vitesse"
    params = [Slider("facteur", "Facteur", default=2.0, minimum=0.25, maximum=4.0)]

    def clip(self, clip, facteur):
        return clip.with_effects([vfx.MultiplySpeed(facteur)])
```

## Bon à savoir

- Un fichier qui contient une erreur n'empêche pas les autres effets de marcher : l'erreur est affichée dans l'application.
- Les fichiers dont le nom commence par `_` sont ignorés, pratique pour un brouillon.
- Deux effets ne peuvent pas avoir le même `name`.
- L'application inclut NumPy et MoviePy. Un effet qui a besoin d'une autre bibliothèque ne marchera pas dans l'application `.app`.
