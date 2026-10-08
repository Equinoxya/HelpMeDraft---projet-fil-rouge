#!/bin/sh
# Régénère le PDF du dossier de projet depuis dossier-projet.html
set -e
cd "$(dirname "$0")"
node render.mjs
python3 - <<'PY'
from pypdf import PdfWriter, PdfReader
D = "."
OUT = "../Dossier-projet-HelpMeDraft.pdf"
body = PdfReader(f"{D}/.body.pdf"); cover = PdfReader(f"{D}/.cover.pdf")
w = PdfWriter()
w.add_page(cover.pages[0])            # couverture sans pied de page
for p in body.pages[1:]:
    w.add_page(p)
w.add_metadata({
    "/Title": "Dossier de projet — HelpMeDraft",
    "/Author": "Ophélie Bellissens",
    "/Subject": "Titre professionnel Concepteur développeur d'applications (TP-01281) — session 2026",
    "/Keywords": "CDA, HelpMeDraft, LexiCorp, dossier de projet",
})
with open(OUT, "wb") as f:
    w.write(f)
print("pages", len(w.pages))
PY
rm -f .body.pdf .cover.pdf
