import pytest
from gradio_client import Client, handle_file

from vid_effects import ui

from .test_renderer import sample_video  # noqa: F401


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("VID_EFFECTS_DIR", str(tmp_path / "effets"))
    app = ui.build_app()
    url = ui.launch(app, prevent_thread_lock=True, quiet=True, show_error=True)
    yield Client(url, verbose=False), tmp_path
    app.close()


def test_render_from_interface(app, sample_video):  # noqa: F811
    client, tmp_path = app
    endpoint = client.view_api(return_format="dict", print_info=False)["named_endpoints"]["/on_run"]
    labels = [p["label"] for p in endpoint["parameters"]]
    values = [p.get("parameter_default") for p in endpoint["parameters"]]
    values[0] = handle_file(str(sample_video))
    values[labels.index("Noir et blanc")] = True
    _, status = client.predict(*values, api_name="/on_run")
    assert "Rendu terminé" in status
    assert (tmp_path / "rendus" / "source_effets.mp4").is_file()
