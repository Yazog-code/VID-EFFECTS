import numpy as np

from vid_effects import Effect, Slider


class NoirEtBlanc(Effect):
    name = "Noir et blanc"
    description = "Retire les couleurs, totalement ou en partie."
    params = [Slider("intensite", "Intensité", default=1.0, minimum=0.0, maximum=1.0, step=0.05)]

    def frame(self, image, t, intensite):
        gris = image @ np.array([0.299, 0.587, 0.114])
        gris = np.repeat(gris[..., None], 3, axis=2)
        melange = image * (1 - intensite) + gris * intensite
        return melange.astype(np.uint8)
