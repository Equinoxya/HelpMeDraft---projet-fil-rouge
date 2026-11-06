# -*- coding: utf-8 -*-
"""
Renomme les médias d'un .pptx selon la convention de PowerPoint.

POURQUOI. pptxgenjs nomme ses images « image-16-1.png » : le numéro de
diapositive, puis un rang. PowerPoint, lui, écrit « image1.png ». Le fichier
reste valide dans les deux cas — le lien est porté par les relations, pas par
le nom — mais certains lecteurs simplifiés, dont l'aperçu d'iOS, semblent
réconcilier les médias sur leur nom plutôt que sur la relation, et affichent
alors la même image sur plusieurs diapositives.

Ce script ne touche qu'aux noms : chaque fichier de ppt/media/ est renuméroté
et toutes les relations qui le désignent sont réécrites. Aucun contenu de
diapositive n'est modifié.

    python3 docs/soutenance/normaliser-pptx.py fichier.pptx
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path


def normaliser(chemin: Path) -> None:
    src = zipfile.ZipFile(chemin)
    entrees = src.infolist()

    medias = sorted(e.filename for e in entrees if e.filename.startswith("ppt/media/"))
    rang = {}
    compte = {}
    for ancien in medias:
        ext = ancien.rsplit(".", 1)[-1].lower()
        base = "media" if ext in ("mp4", "m4v", "mov", "wmv", "avi") else "image"
        compte[base] = compte.get(base, 0) + 1
        rang[ancien] = f"ppt/media/{base}{compte[base]}.{ext}"

    # Un nom ne doit pas en écraser un autre : on vérifie la bijection.
    assert len(set(rang.values())) == len(rang), "collision de noms"

    par_base = {Path(a).name: Path(n).name for a, n in rang.items()}
    # Du plus long au plus court : « image-21-1 » ne doit pas être remplacé
    # par la règle de « image-21-10 » tronquée, ni l'inverse.
    motif = re.compile("|".join(re.escape(k) for k in sorted(par_base, key=len, reverse=True)))

    sortie = chemin.with_suffix(".pptx.tmp")
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as dst:
        for e in entrees:
            data = src.read(e.filename)
            nom = rang.get(e.filename, e.filename)
            if e.filename.endswith(".rels") or e.filename.endswith(".xml"):
                texte = data.decode("utf-8")
                remplace = motif.sub(lambda m: par_base[m.group(0)], texte)
                data = remplace.encode("utf-8")
            dst.writestr(nom, data)
    src.close()
    shutil.move(sortie, chemin)
    print(f"{chemin.name} : {len(medias)} médias renommés")


if __name__ == "__main__":
    normaliser(Path(sys.argv[1]))
