"""Point d'entrée de l'application packagée par PyInstaller."""

import multiprocessing
import os
import sys

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # Une app macOS lancée depuis le Finder n'a pas toujours de sortie standard.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    from vid_effects.__main__ import main

    main()
