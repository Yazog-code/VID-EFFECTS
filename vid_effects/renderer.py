"""Moteur de rendu : lit une vidéo, enchaîne les effets choisis et réencode le résultat."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import proglog

from .registry import Registry

ProgressCallback = Callable[[float, str], None]


@dataclass
class Step:
    """Un effet à appliquer, avec ses réglages (les manquants prennent leur valeur par défaut)."""

    effect: str
    params: dict[str, Any] = field(default_factory=dict)


class _ProgressLogger(proglog.ProgressBarLogger):
    """Traduit la progression de MoviePy en une fraction 0-1 pour l'interface."""

    def __init__(self, callback: ProgressCallback):
        super().__init__()
        self._callback = callback

    def bars_callback(self, bar, attr, value, old_value=None):
        if bar != "frame_index" or attr != "index":
            return
        total = self.bars[bar].get("total") or 0
        if total:
            self._callback(min(value / total, 1.0), f"Image {value} / {total}")


def default_output_path(input_path: Path, output_dir: Path) -> Path:
    """`video.mp4` → `video_effets.mp4`, puis `video_effets_2.mp4`, etc. sans écraser."""
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate = output_dir / f"{input_path.stem}_effets.mp4"
    n = 2
    while candidate.exists():
        candidate = output_dir / f"{input_path.stem}_effets_{n}.mp4"
        n += 1
    return candidate


def render(
    input_path: str | Path,
    output_path: str | Path,
    steps: list[Step],
    registry: Registry,
    progress: ProgressCallback | None = None,
) -> Path:
    """Applique `steps` dans l'ordre à `input_path` et écrit une vidéo MP4 (H.264 + AAC)."""
    from moviepy import VideoFileClip

    input_path, output_path = Path(input_path), Path(output_path)
    # Résoudre les effets et réglages avant d'ouvrir la vidéo, pour échouer vite.
    prepared = [(registry.get(s.effect)(), registry.get(s.effect).resolve_params(s.params)) for s in steps]

    report = progress or (lambda fraction, message: None)
    report(0.0, "Ouverture de la vidéo")
    source = VideoFileClip(str(input_path))
    try:
        clip = source
        for effect, params in prepared:
            clip = effect.clip(clip, **params)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            # yuv420p pour que la vidéo se lise partout (QuickTime, iPhone...).
            ffmpeg_params=["-pix_fmt", "yuv420p"],
            # Par défaut MoviePy écrit le son temporaire dans le dossier courant,
            # qui est « / » (lecture seule) pour une app lancée depuis le Finder.
            temp_audiofile_path=tempfile.gettempdir(),
            logger=_ProgressLogger(report) if progress else None,
        )
    finally:
        source.close()
    report(1.0, "Terminé")
    return output_path
