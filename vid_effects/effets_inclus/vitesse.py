from moviepy import afx, vfx

from vid_effects import Effect, Slider


class Vitesse(Effect):
    name = "Vitesse"
    description = "Accélère (plus de 1) ou ralentit (moins de 1) la vidéo et le son."
    params = [Slider("facteur", "Facteur de vitesse", default=2.0, minimum=0.25, maximum=4.0, step=0.05)]

    def clip(self, clip, facteur):
        # MultiplySpeed s'applique aussi au son, qui reste synchronisé.
        return clip.with_effects([vfx.MultiplySpeed(facteur)])


class Fondu(Effect):
    name = "Fondu au noir"
    description = "Fondu depuis le noir au début et vers le noir à la fin, son compris."
    params = [Slider("duree", "Durée (secondes)", default=1.0, minimum=0.1, maximum=5.0, step=0.1)]

    def clip(self, clip, duree):
        duree = min(duree, clip.duration / 2)
        clip = clip.with_effects([vfx.FadeIn(duree), vfx.FadeOut(duree)])
        if clip.audio is not None:
            clip = clip.with_audio(clip.audio.with_effects([afx.AudioFadeIn(duree), afx.AudioFadeOut(duree)]))
        return clip
