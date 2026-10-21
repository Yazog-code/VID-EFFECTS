import numpy as np
import pytest

from vid_effects import Effect, Slider, discover


@pytest.fixture
def user_dir(tmp_path, monkeypatch):
    path = tmp_path / "effets"
    monkeypatch.setenv("VID_EFFECTS_DIR", str(path))
    return path


def test_builtin_effect_is_found(user_dir):
    registry = discover()
    assert "Noir et blanc" in registry.names()
    assert registry.errors == {}
    assert user_dir.is_dir()


def test_user_effect_is_found(user_dir):
    user_dir.mkdir()
    (user_dir / "inverse.py").write_text(
        "from vid_effects import Effect\n"
        "class Inverse(Effect):\n"
        "    name = 'Inverser'\n"
        "    def frame(self, image, t):\n"
        "        return 255 - image\n"
    )
    registry = discover()
    effect = registry.get("Inverser")()
    image = np.zeros((2, 2, 3), dtype=np.uint8)
    assert (effect.frame(image, 0) == 255).all()


def test_broken_file_does_not_block_others(user_dir):
    user_dir.mkdir()
    (user_dir / "casse.py").write_text("ceci n'est pas du python")
    (user_dir / "sans_nom.py").write_text("from vid_effects import Effect\nclass X(Effect):\n    pass\n")
    registry = discover()
    assert "Noir et blanc" in registry.names()
    assert any("casse.py" in path for path in registry.errors)
    assert any("sans_nom.py" in path for path in registry.errors)


def test_duplicate_name_is_reported(user_dir):
    user_dir.mkdir()
    (user_dir / "doublon.py").write_text(
        "from vid_effects import Effect\nclass Doublon(Effect):\n    name = 'Noir et blanc'\n"
    )
    registry = discover()
    assert "déjà utilisé" in next(iter(registry.errors.values()))


def test_files_starting_with_underscore_are_skipped(user_dir):
    user_dir.mkdir()
    (user_dir / "_brouillon.py").write_text("raise RuntimeError")
    assert discover().errors == {}


def test_params_are_validated():
    class Demo(Effect):
        name = "Demo"
        params = [Slider("force", "Force", default=0.5, minimum=0, maximum=1)]

    assert Demo.resolve_params() == {"force": 0.5}
    assert Demo.resolve_params({"force": 3}) == {"force": 1.0}
    with pytest.raises(ValueError):
        Demo.resolve_params({"inconnu": 1})


def test_noir_et_blanc_frame(user_dir):
    effect = discover().get("Noir et blanc")()
    image = np.zeros((1, 1, 3), dtype=np.uint8)
    image[0, 0] = [255, 0, 0]
    out = effect.frame(image, 0, intensite=1.0)
    assert out.dtype == np.uint8
    assert out[0, 0, 0] == out[0, 0, 1] == out[0, 0, 2]


def test_default_clip_applies_frame_per_image():
    class Plus(Effect):
        name = "Plus"

        def frame(self, image, t):
            return image + 1

    class FakeClip:
        def transform(self, func):
            return func(lambda t: np.zeros(1), 0.0)

    assert Plus().apply(FakeClip())[0] == 1
