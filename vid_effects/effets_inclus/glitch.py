import numpy as np

from vid_effects import Effect, Slider


class Glitch(Effect):
    name = "Glitch"
    description = "Décalage des couleurs et bandes horizontales qui sautent, façon signal abîmé."
    params = [
        Slider("force", "Force", default=0.5, minimum=0.0, maximum=1.0, step=0.05),
        Slider("frequence", "Fréquence des sauts", default=0.3, minimum=0.0, maximum=1.0, step=0.05),
    ]

    def frame(self, image, t, force, frequence):
        hauteur, largeur, _ = image.shape
        # Graine liée au temps : le rendu est identique d'une fois sur l'autre.
        rng = np.random.default_rng(int(t * 1000))
        decalage = int(force * largeur * 0.02)
        out = image.copy()
        if decalage:
            out[..., 0] = np.roll(image[..., 0], decalage, axis=1)
            out[..., 2] = np.roll(image[..., 2], -decalage, axis=1)
        if rng.random() < frequence:
            for _ in range(rng.integers(1, 6)):
                y = rng.integers(0, hauteur)
                h = rng.integers(2, max(3, hauteur // 12))
                dx = int(rng.integers(-1, 2) * force * largeur * 0.1)
                out[y : y + h] = np.roll(out[y : y + h], dx, axis=1)
        return out
