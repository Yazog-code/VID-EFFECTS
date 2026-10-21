import numpy as np

from vid_effects import Effect, Slider


class LuminositeContraste(Effect):
    name = "Luminosité et contraste"
    description = "Éclaircit ou assombrit, et renforce ou adoucit le contraste."
    params = [
        Slider("luminosite", "Luminosité", default=0.0, minimum=-100.0, maximum=100.0, step=1),
        Slider("contraste", "Contraste", default=1.0, minimum=0.0, maximum=3.0, step=0.05),
    ]

    def frame(self, image, t, luminosite, contraste):
        out = (image.astype(np.float32) - 128) * contraste + 128 + luminosite
        return np.clip(out, 0, 255).astype(np.uint8)
