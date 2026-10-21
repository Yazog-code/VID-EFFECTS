"""Interface Gradio : glisser une vidéo, cocher des effets, lancer le rendu."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr

from .effect import Checkbox, Choice, Effect, Param, Slider
from .registry import Registry, discover, user_effects_dir
from .renderer import Step, default_output_path, render


def renders_dir() -> Path:
    return user_effects_dir().parent / "rendus"


def _component(param: Param):
    if isinstance(param, Slider):
        return gr.Slider(param.minimum, param.maximum, value=param.default, step=param.step, label=param.label)
    if isinstance(param, Choice):
        return gr.Dropdown(list(param.options), value=param.default, label=param.label)
    if isinstance(param, Checkbox):
        return gr.Checkbox(value=param.default, label=param.label)
    return gr.Textbox(value=str(param.default), label=param.label)


def _open_in_finder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    opener = {"darwin": "open", "win32": "explorer"}.get(sys.platform, "xdg-open")
    subprocess.Popen([opener, str(path)])


def _errors_markdown(registry: Registry) -> str:
    if not registry.errors:
        return ""
    lines = ["### ⚠️ Effets non chargés"]
    for path, error in registry.errors.items():
        lines.append(f"**{Path(path).name}**\n```\n{error.strip()}\n```")
    return "\n\n".join(lines)


def build_app(registry: Registry | None = None) -> gr.Blocks:
    registry = registry or discover()
    effects: list[type[Effect]] = [registry.get(name) for name in registry.names()]
    # Pour chaque effet : la case "activer" puis un composant par réglage, dans un seul tableau à plat.
    layout: list[tuple[type[Effect], int]] = []
    inputs: list[gr.components.Component] = []

    with gr.Blocks(title="VID-Effects") as app:
        gr.Markdown("# VID-Effects\nGlisse une vidéo, coche les effets voulus, puis lance le rendu.")
        with gr.Row():
            with gr.Column(scale=1):
                video_in = gr.Video(label="Vidéo source", sources=["upload"])
                gr.Markdown("**Effets** (appliqués dans l'ordre de la liste)")
                for effect in effects:
                    with gr.Group():
                        enabled = gr.Checkbox(label=effect.name, info=effect.description or None, value=False)
                        inputs.append(enabled)
                        with gr.Accordion("Réglages", open=False, visible=bool(effect.params)):
                            for param in effect.params:
                                inputs.append(_component(param))
                    layout.append((effect, len(effect.params)))
                run = gr.Button("Lancer le rendu", variant="primary")
            with gr.Column(scale=1):
                video_out = gr.Video(label="Résultat", interactive=False)
                status = gr.Markdown()
                with gr.Row():
                    open_renders = gr.Button("Ouvrir le dossier des rendus")
                    open_effects = gr.Button("Ouvrir le dossier des effets")
                gr.Markdown(
                    f"Les vidéos rendues sont enregistrées dans `{renders_dir()}`.  \n"
                    f"Pour ajouter un effet, dépose un fichier `.py` dans `{user_effects_dir()}` "
                    "puis relance l'application."
                )
                gr.Markdown(_errors_markdown(registry))

        def on_run(video_path, *values, progress=gr.Progress()):
            if not video_path:
                raise gr.Error("Ajoute d'abord une vidéo.")
            steps, i = [], 0
            for effect, n_params in layout:
                enabled, params = values[i], values[i + 1 : i + 1 + n_params]
                i += 1 + n_params
                if enabled:
                    steps.append(Step(effect.name, {p.name: v for p, v in zip(effect.params, params)}))
            if not steps:
                raise gr.Error("Coche au moins un effet.")
            output = default_output_path(Path(video_path), renders_dir())
            try:
                render(video_path, output, steps, registry, lambda f, msg: progress(f, desc=msg))
            except Exception as exc:
                raise gr.Error(f"Le rendu a échoué : {exc}") from exc
            names = ", ".join(s.effect for s in steps)
            return str(output), f"✅ Rendu terminé ({names}) : `{output}`"

        run.click(on_run, inputs=[video_in, *inputs], outputs=[video_out, status])
        open_renders.click(lambda: _open_in_finder(renders_dir()))
        open_effects.click(lambda: _open_in_finder(user_effects_dir()))

    return app


def launch(app: gr.Blocks, **kwargs):
    """Démarre le serveur local ; renvoie l'URL de la page."""
    renders_dir().mkdir(parents=True, exist_ok=True)
    app.queue(default_concurrency_limit=1)
    app.launch(
        server_name="127.0.0.1",
        ssr_mode=False,
        allowed_paths=[str(renders_dir())],
        **kwargs,
    )
    return app.local_url
