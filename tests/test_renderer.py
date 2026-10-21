import subprocess

import imageio_ffmpeg
import numpy as np
import pytest

from vid_effects import discover
from vid_effects.renderer import Step, default_output_path, render


@pytest.fixture(scope="module")
def sample_video(tmp_path_factory):
    path = tmp_path_factory.mktemp("videos") / "source.mp4"
    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(), "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "testsrc=size=160x120:rate=10:duration=2",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path),
        ],
        check=True,
    )
    return path


@pytest.fixture
def registry(tmp_path, monkeypatch):
    monkeypatch.setenv("VID_EFFECTS_DIR", str(tmp_path / "effets"))
    reg = discover()
    assert reg.errors == {}
    return reg


def test_all_builtin_effects_render(sample_video, registry, tmp_path):
    from moviepy import VideoFileClip

    steps = [Step(name) for name in registry.names()]
    seen = []
    out = render(sample_video, tmp_path / "out.mp4", steps, registry, lambda f, m: seen.append(f))
    with VideoFileClip(str(out)) as clip:
        # Vitesse x2 par défaut : 2 s deviennent 1 s.
        assert clip.duration == pytest.approx(1.0, abs=0.25)
        assert clip.audio is not None
        frame = clip.get_frame(0.5)
        # Noir et blanc appliqué : les trois canaux sont presque égaux.
        assert np.abs(frame[..., 0].astype(int) - frame[..., 2]).mean() < 10
    assert seen[0] == 0.0 and seen[-1] == 1.0


def test_unknown_effect_fails_before_opening(registry, tmp_path):
    with pytest.raises(KeyError):
        render(tmp_path / "absent.mp4", tmp_path / "out.mp4", [Step("Inexistant")], registry)


def test_default_output_path_does_not_overwrite(tmp_path):
    first = default_output_path(tmp_path / "video.mov", tmp_path / "rendus")
    assert first.name == "video_effets.mp4"
    first.touch()
    assert default_output_path(tmp_path / "video.mov", tmp_path / "rendus").name == "video_effets_2.mp4"


def test_temp_audio_is_not_written_to_current_dir(sample_video, registry, tmp_path, monkeypatch):
    # Une app lancée depuis le Finder a « / » (lecture seule) comme dossier courant.
    from moviepy.video.VideoClip import VideoClip

    calls = []
    original = VideoClip.write_videofile

    def spy(self, *args, **kwargs):
        calls.append(kwargs)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(VideoClip, "write_videofile", spy)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    render(sample_video, tmp_path / "out.mp4", [Step("Noir et blanc")], registry)
    assert calls[0]["temp_audiofile_path"] not in ("", ".", str(cwd))
