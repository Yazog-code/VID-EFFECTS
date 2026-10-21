# VID-Effects

Utilitaire pour appliquer des effets à une vidéo : on glisse une vidéo, on choisit des effets, on lance le rendu, et on récupère la vidéo finale.
Les effets sont de simples fichiers Python, ce qui permet d'en ajouter facilement.

## Ajouter un effet

Voir le guide [Créer un effet](docs/creer-un-effet.md).

## Développement

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
