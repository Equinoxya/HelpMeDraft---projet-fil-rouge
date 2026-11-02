# -*- coding: utf-8 -*-
"""Retrait des commentaires d'un bloc de code.

Partagé par code_images.py, qui rend les images, et par fill_trame.py, qui les
pose : les deux identifient un bloc par l'empreinte de son code nettoyé. Passer
par le code nettoyé plutôt que par le texte brut rend l'empreinte insensible à
la réécriture des renvois, qui touche parfois un commentaire.
"""
# ───────────────────────── retrait des commentaires ────────────────────────
MARQUEURS = {"#": "py", "//": "js", "--": "sql"}

def _hors_chaine(ligne):
    """Position du premier marqueur de commentaire hors d'une chaîne."""
    i, guillemet = 0, None
    while i < len(ligne):
        c = ligne[i]
        if guillemet:
            if c == "\\":
                i += 2
                continue
            if c == guillemet:
                guillemet = None
        elif c in "\"'`":
            guillemet = c
        elif c == "#":
            return i
        elif ligne.startswith("//", i) or ligne.startswith("-- ", i):
            return i
        i += 1
    return -1

def nettoyer(txt):
    lignes, dans_docstring = [], None
    for ligne in txt.split("\n"):
        nu = ligne.strip()
        if dans_docstring:
            if dans_docstring in nu:
                dans_docstring = None
            continue
        if nu.startswith(('"""', "'''")):
            delim = nu[:3]
            if not (len(nu) > 3 and nu.endswith(delim)):
                dans_docstring = delim
            continue
        if nu.startswith(("#", "//", "--", "/*", "*")):
            continue
        pos = _hors_chaine(ligne)
        if pos > 0:
            ligne = ligne[:pos].rstrip()
            if not ligne:
                continue
        lignes.append(ligne.rstrip())
    serre = []
    for l in lignes:
        if not l.strip() and (not serre or not serre[-1].strip()):
            continue
        serre.append(l)
    while serre and not serre[-1].strip():
        serre.pop()
    return "\n".join(serre)

