"""Relève la page de début de chaque partie dans le PDF rendu."""
import json, re, sys, unicodedata
from pypdf import PdfReader

from sommaire import SOMMAIRE as TITRES


def norm(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", t.lower())

reader = PdfReader("lo2/dossier-projet-rempli.pdf")
pages = [norm(p.extract_text() or "") for p in reader.pages]
toc_i = next((i for i, t in enumerate(pages) if norm("Table des matières") in t), 0)
start, res, manquants = toc_i + 1, {}, []
for num, titre in TITRES:
    k = norm(titre)
    pg = next((j + 1 for j in range(start, len(pages)) if k in pages[j]), None)
    if pg is None:
        manquants.append(num)
    else:
        res[titre] = pg
        start = max(pg - 1, toc_i + 1)

if "--check" in sys.argv:
    debut_annexes = res.get("ANNEXES")
    corps = (debut_annexes - toc_i - 2) if debut_annexes else None
    print(f"total {len(pages)} pages | corps {corps} | annexes {len(pages) - debut_annexes + 1 if debut_annexes else '?'}")
    if manquants:
        print("titres non localisés :", manquants)
else:
    json.dump(res, open("pages.json", "w"))
    print("pagination relevée :", len(res), "entrées")
