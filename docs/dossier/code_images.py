# -*- coding: utf-8 -*-
"""Rend chaque bloc de code du dossier en image, commentaires retirés.

Les blocs restent dans le document source ; ce script en produit une image par
bloc (ou plusieurs si le bloc dépasse une hauteur de page), que fill_trame.py
vient poser à la place du texte. L'image est rendue par Chromium dans une seule
police monospace, ce qui donne une composition identique d'un bloc à l'autre.

Sortie : fig/code/<empreinte>-<n>.png et fig/code/index.json
"""
import hashlib, html, json, os, shutil
import docx
from PIL import Image
from playwright.sync_api import sync_playwright

RACINE = "/home/user/HelpMeDraft---projet-fil-rouge"
SOURCE = f"{RACINE}/Dossier projet CDA - HelpMeDraft.docx"
SORTIE = f"{RACINE}/docs/dossier/fig/code"

PX = 20          # corps du texte dans le rendu, en pixels CSS
INTERLIGNE = 1.18
MARGE = 7        # marge intérieure du cadre, en pixels CSS
LARGEUR_MAX = 116        # la plus longue ligne du dossier, après nettoyage
LIGNES_MAX = 68          # au-delà, le bloc ne tiendrait pas dans une page
ECHELLE = 2              # facteur de rendu, pour que l'image reste nette

from code_nettoyage import nettoyer

def tronconner(code):
    lignes = code.split("\n")
    if len(lignes) <= LIGNES_MAX:
        return [code]
    morceaux, n = [], len(lignes)
    parts = (n + LIGNES_MAX - 1) // LIGNES_MAX
    taille = (n + parts - 1) // parts        # morceaux de hauteur comparable
    for d in range(0, n, taille):
        morceaux.append("\n".join(lignes[d:d + taille]))
    return morceaux

# ───────────────────────────── rendu ───────────────────────────────────────
GABARIT = """<!doctype html><html><head><meta charset="utf-8"><style>
  body {{ margin:0; background:#fff; }}
  pre  {{ font-family:'DejaVu Sans Mono', monospace;
          font-size:{px}px; line-height:{li};
          color:#1A1A1A; background:#FAFAF8;
          border:1px solid #D8D6D0; border-radius:2px;
          padding:{m}px; margin:0 0 24px 0;
          display:inline-block; white-space:pre; }}
</style></head><body>{corps}</body></html>"""

def rendre(morceaux):
    corps = "".join(f'<pre id="b{i}">{html.escape(m)}</pre>'
                    for i, m in enumerate(morceaux))
    page_html = GABARIT.format(px=PX, li=INTERLIGNE, m=MARGE, corps=corps)
    chemin = "/tmp/code_blocs.html"
    open(chemin, "w", encoding="utf-8").write(page_html)
    tailles = []
    with sync_playwright() as pw:
        # Chromium est préinstallé dans l'image ; on le désigne explicitement
        # plutôt que de laisser Playwright en télécharger un autre.
        nav = pw.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        page = nav.new_page(device_scale_factor=ECHELLE,
                            viewport={"width": 1800, "height": 1000})
        page.goto("file://" + chemin)
        for i, _ in enumerate(morceaux):
            el = page.locator(f"#b{i}")
            boite = el.bounding_box()
            el.screenshot(path=f"{SORTIE}/tmp-{i}.png")
            tailles.append((boite["width"], boite["height"]))
        nav.close()
    return tailles

def main():
    shutil.rmtree(SORTIE, ignore_errors=True)
    os.makedirs(SORTIE, exist_ok=True)
    src = docx.Document(SOURCE)
    blocs = [p.text for p in src.paragraphs if p.style.name == "Source Code"]

    # Un même extrait peut figurer à deux endroits du dossier — en partie 7 et
    # en annexe, par exemple. Il partage alors son empreinte, donc son image :
    # on ne le rend qu'une fois, sans quoi la liste des morceaux de cette
    # empreinte doublerait et le bloc serait posé deux fois de suite.
    morceaux, reperes, vus = [], [], set()
    for brut in blocs:
        net = nettoyer(brut)
        if not net.strip():
            continue
        emp = hashlib.md5(net.encode("utf-8")).hexdigest()[:12]
        if emp in vus:
            continue
        vus.add(emp)
        for n, m in enumerate(tronconner(net)):
            reperes.append((emp, n))
            morceaux.append(m)
    print(f"  blocs : {len(blocs)} | images à produire : {len(morceaux)}")

    tailles = rendre(morceaux)

    index = {}
    for i, ((emp, n), (lcss, hcss)) in enumerate(zip(reperes, tailles)):
        nom = f"{emp}-{n}.png"
        im = Image.open(f"{SORTIE}/tmp-{i}.png").convert("RGB")
        im.quantize(colors=16, method=Image.MEDIANCUT).save(
            f"{SORTIE}/{nom}", optimize=True)
        os.remove(f"{SORTIE}/tmp-{i}.png")
        index.setdefault(emp, []).append({"fichier": nom, "largeur_css": lcss})
    # largeur de référence : le bloc le plus large occupe toute la colonne
    ref = LARGEUR_MAX * 0.60238 * PX + 2 * MARGE + 2
    json.dump({"largeur_reference_css": ref, "blocs": index},
              open(f"{SORTIE}/index.json", "w"), indent=1)
    poids = sum(os.path.getsize(f"{SORTIE}/{f}") for f in os.listdir(SORTIE)
                if f.endswith(".png"))
    print(f"  images écrites : {len(morceaux)} | {poids/1e6:.1f} Mo")

if __name__ == "__main__":
    main()
