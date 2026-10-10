#!/bin/sh
# Remplit la trame officielle puis en produit le PDF, en deux passes :
# la première mesure la pagination, la seconde l'inscrit dans le sommaire.
set -e
cd "$(dirname "$0")"
rendre() {
  soffice --headless -env:UserInstallation=file:///tmp/lo_profile \
          --convert-to pdf --outdir lo2 dossier-projet-rempli.docx >/dev/null 2>&1
}
python3 fill_trame.py >/dev/null; rendre
python3 pages_trame.py
python3 fill_trame.py pages.json >/dev/null; rendre
python3 pages_trame.py --check
cp lo2/dossier-projet-rempli.pdf ../Dossier-projet-HelpMeDraft.pdf
echo "→ docs/Dossier-projet-HelpMeDraft.pdf"
