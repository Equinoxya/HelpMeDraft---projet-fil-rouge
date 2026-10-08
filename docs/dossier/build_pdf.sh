#!/bin/sh
# Construit le PDF du dossier à partir du .docx d'origine, en deux passes :
# la première mesure la pagination, la seconde écrit les numéros du sommaire.
set -e
cd "$(dirname "$0")"
render() {
  soffice --headless -env:UserInstallation=file:///tmp/lo_profile \
          --convert-to pdf --outdir lo dossier-projet-fusionne.docx >/dev/null 2>&1
}
python3 build_docx.py >/dev/null; render
python3 toc_pages.py            # écrit toc.json à partir du PDF
python3 build_docx.py toc.json >/dev/null; render
python3 toc_pages.py --check
cp lo/dossier-projet-fusionne.pdf ../Dossier-projet-HelpMeDraft.pdf
echo "→ docs/Dossier-projet-HelpMeDraft.pdf"
