import numpy as np
from PIL import Image, ImageFilter

from vid_effects import Effect, Slider


class Flou(Effect):
    name = "Flou"
    description = "Flou gaussien sur toute l'image."
    params = [Slider("rayon", "Rayon (pixels)", default=5.0, minimum=0.0, maximum=40.0, step=0.5)]

    def frame(self, image, t, rayon):
        if rayon <= 0:
            return image
        return np.asarray(Image.fromarray(image).filter(ImageFilter.GaussianBlur(rayon)))
