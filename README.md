# VID-Effects

Utilitaire pour appliquer des effets à une vidéo : on glisse une vidéo, on coche des effets, on lance le rendu, et on récupère la vidéo finale.
Les effets sont de simples fichiers Python, ce qui permet d'en ajouter facilement.

## Installer l'application (Mac)

1. Télécharge **[VID-Effects-mac.zip](https://github.com/Yazog-code/VID-EFFECTS/releases/latest/download/VID-Effects-mac.zip)** (toujours la dernière version).
2. Double-clique sur le zip, puis glisse **VID-Effects** dans le dossier **Applications**.
3. Au premier lancement, macOS bloque l'application parce qu'elle n'est pas signée par Apple (message « est endommagé » ou « impossible de vérifier le développeur »). Ouvre le Terminal et colle :

   ```
   xattr -dr com.apple.quarantine /Applications/VID-Effects.app
   ```

   C'est à faire une seule fois. Rien d'autre n'est à installer : Python et FFmpeg sont inclus.

L'application est construite pour les Mac Apple Silicon (M1 et plus récents).

## Utilisation

- Glisse une vidéo dans la zone « Vidéo source ».
- Coche les effets voulus et ajuste leurs réglages. Ils s'appliquent dans l'ordre de la liste.
- Clique sur **Lancer le rendu**. La vidéo finale est enregistrée dans `~/VID-Effects/rendus`.

## Ajouter un effet

Dépose un fichier `.py` dans `~/VID-Effects/effets`, puis relance l'application. Voir le guide [Créer un effet](docs/creer-un-effet.md).

## Effets inclus

Flou, Fondu au noir, Glitch, Luminosité et contraste, Noir et blanc, Vitesse.

## Développement

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                          # tests
python -m vid_effects           # lancer l'application
python -m vid_effects --navigateur  # ou dans le navigateur
pyinstaller packaging/vid_effects.spec  # construire l'app (sur un Mac)
```

À chaque mise à jour de `main`, GitHub construit l'application et la publie dans la release « dernière version ».
