"""
Reprend « Dossier projet CDA - HelpMeDraft.docx » et :
  - corrige les NIVEAUX de titre (les formulations ne sont pas touchées) ;
  - insère les 9 planches W-01 à W-09, présentes dans le fichier mais jamais posées ;
  - insère les figures manquantes : MCD, MLD, MPD, architecture, cas d'utilisation, séquence ;
  - insère les captures C-05 et C-07, citées dans le texte mais absentes.
Le résultat garde la mise en forme Word d'origine.
"""
import copy, json, os, sys
import docx
from docx.shared import Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

SRC = "/home/user/HelpMeDraft---projet-fil-rouge/Dossier projet CDA - HelpMeDraft.docx"
OUT = "/home/user/HelpMeDraft---projet-fil-rouge/docs/dossier/dossier-projet-fusionne.docx"
FIG = "/home/user/HelpMeDraft---projet-fil-rouge/docs/dossier/fig"
CAP = "/home/user/HelpMeDraft---projet-fil-rouge/docs/captures"

PAGES = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}

doc = docx.Document(SRC)
STYLES = {st.name: st for st in doc.styles}
P = list(doc.paragraphs)          # figé AVANT toute insertion


def clear(p):
    """Vide un paragraphe de tout son contenu, y compris les runs encapsulés
    dans un w:hyperlink — ce que `paragraph.runs` ne voit pas."""
    for child in list(p._p):
        if child.tag != qn("w:pPr"):
            p._p.remove(child)


def new_after(p, style=None):
    el = OxmlElement("w:p")
    p._p.addnext(el)
    np = Paragraph(el, p._parent)
    if style:
        np.style = STYLES[style]
    return np


def picture(p, path, width_cm):
    clear(p)
    p.style = STYLES["Figure"]
    p.add_run().add_picture(path, width=Cm(width_cm))


def caption_after(p, text):
    c = new_after(p, "Image Caption")
    c.add_run(text)
    return c


def replace_with_figure(idx, path, width_cm, caption=None):
    p = P[idx]
    picture(p, path, width_cm)
    if caption:
        caption_after(p, caption)


def figure_after(idx, path, width_cm, caption=None):
    anchor = P[idx]
    fp = new_after(anchor, "Figure")
    fp.add_run().add_picture(path, width=Cm(width_cm))
    if caption:
        caption_after(fp, caption)


def retitle(idx, style, text=None):
    p = P[idx]
    if text is not None:
        clear(p)
        p.add_run(text)
    p.style = STYLES[style]


def heading_before(idx, text, style="Heading 1"):
    anchor = P[idx]
    el = OxmlElement("w:p")
    anchor._p.addprevious(el)
    np = Paragraph(el, anchor._parent)
    np.style = STYLES[style]
    np.add_run(text)
    return np


# Marges ramenées de 2 cm à 1,8 cm : le dossier doit tenir dans les 60 pages
# de corps qu'impose le référentiel, et une marge de 1,8 cm reste confortable
# à l'impression. C'est le seul réglage de page modifié.
from docx.shared import Cm as _Cm
for sec in doc.sections:
    sec.top_margin = sec.bottom_margin = _Cm(1.8)
    sec.left_margin = sec.right_margin = _Cm(1.8)

W = 16.8      # largeur utile : 21 cm - 2 x 1,8 cm = 17,4 cm

# ---------------------------------------------------------------- figures ---
replace_with_figure(105, f"{FIG}/archi.png", W,
                    "Architecture logicielle — découpage en couches et services périphériques.")
replace_with_figure(139, f"{FIG}/planches/image9.png", W,
                    "Enchaînement des écrans — planche W-09, reprise en annexe § 12.1.")
replace_with_figure(164, f"{FIG}/mcd.png", W,
                    "Modèle conceptuel des données (MCD) — sept entités, huit associations, cardinalités Merise.")
figure_after(171, f"{FIG}/mld.png", W,
             "Modèle logique des données (MLD) — les sept relations après application des règles de passage.")
figure_after(173, f"{FIG}/mpd.png", W,
             "Modèle physique des données (MPD) — types, clés, index et règles de suppression sur MySQL 8.")
replace_with_figure(226, f"{FIG}/usecase.png", W,
                    "Diagramme de cas d'utilisation.")
replace_with_figure(239, f"{FIG}/seq-uc10.png", W,
                    "Diagramme de séquence — générer une assistance IA, scénario nominal.")
figure_after(302, f"{CAP}/C-05-tableau-de-bord.png", 14.5,
             "Capture C-05 — tableau de bord.")
figure_after(308, f"{CAP}/C-07-nouveau-document.png", 14.5,
             "Capture C-07 — éditeur de document, création.")

# ------------------------------------------------- planches W-01 à W-09 ----
# Les paragraphes vides précèdent chacun leur légende W-0n.
for n, idx in enumerate(range(586, 603, 2), start=1):
    picture(P[idx], f"{FIG}/planches/image{n}.png", W)

# -------------------------------------------------- niveaux de titre -------
for idx in (121, 159, 199, 221, 236):     # 5.3 à 5.7 : sous-parties de la partie 5
    retitle(idx, "Heading 2")
for idx in (300, 331, 360, 394):          # 7.1 à 7.4 : sous-parties de la partie 7
    retitle(idx, "Heading 2")
retitle(582, "Heading 2")                 # 12.1

# Titres d'annexe tombés en bloc de code, avec leur préfixe Markdown
for idx, txt in [
    (604, "Les captures d’écrans d’interfaces utilisateurs et le code correspondant"),
    (609, "Le code de composants métier les plus significatifs"),
    (614, "Le code de composants d’accès aux données les plus significatifs"),
    (623, "Le code d’autres composants"),
]:
    retitle(idx, "Heading 2", txt)

retitle(581, "Heading 1", "Les annexes")  # « ANNEXES » en texte courant

# ------------------------------- titres de partie absents du document ------
heading_before(300, "Les réalisations du projet")
heading_before(420, "Les éléments de sécurité de l’application")
heading_before(468, "Le plan de tests")
heading_before(517, "Le jeu d’essai de la fonctionnalité la plus représentative")

# ------------------------------------------------- largeur des tableaux ----
# Les 65 tableaux n'occupent qu'une fraction de la justification : LibreOffice
# les rend sur ~70 % de la largeur utile, ce qui casse les colonnes en colonnes
# d'un mot et gonfle la pagination. On les étire sur toute la largeur.
from docx.enum.table import WD_TABLE_ALIGNMENT
for t in doc.tables:
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    tblPr = t._tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        for el in tblPr.findall(qn(tag)):
            tblPr.remove(el)
    w = OxmlElement("w:tblW"); w.set(qn("w:w"), "5000"); w.set(qn("w:type"), "pct")
    tblPr.append(w)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "autofit")
    tblPr.append(lay)
    for row in t.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            for el in tcPr.findall(qn("w:tcW")):
                tcPr.remove(el)

# ------------------------------------------------------ densité du texte ---
# Le corps est à 12 pt avec 9 pt d'espace AVANT et APRÈS chaque paragraphe :
# le dossier sort à 74 pages de corps, pour une limite de 60. On revient aux
# valeurs par défaut de Word — 11 pt, espace après seulement — sans toucher
# aux polices ni aux couleurs.
from docx.shared import Pt
base = STYLES["Normal"]
base.font.size = Pt(11)
base.paragraph_format.space_after = Pt(6)
base.paragraph_format.space_before = Pt(0)
bt = STYLES["Body Text"]
bt.paragraph_format.space_before = Pt(0)
bt.paragraph_format.space_after = Pt(6)
STYLES["First Paragraph"].paragraph_format.space_before = Pt(0)
STYLES["Compact"].paragraph_format.space_before = Pt(0)
STYLES["Compact"].paragraph_format.space_after = Pt(3)
STYLES["Heading 1"].paragraph_format.space_before = Pt(14)
STYLES["Heading 2"].paragraph_format.space_before = Pt(12)
STYLES["Heading 3"].paragraph_format.space_before = Pt(10)
STYLES["Figure"].paragraph_format.space_before = Pt(8)
STYLES["Figure"].paragraph_format.space_after = Pt(2)
STYLES["Image Caption"].paragraph_format.space_after = Pt(10)

STYLES["Source Code"].paragraph_format.line_spacing = Pt(9)

# ------------------------------------------------------------- sommaire ---
# Le sommaire d'origine est du texte courant, incomplet (ni partie 6 à 12) et
# dont tous les numéros de page valent 0. Il est reconstruit à l'identique de
# forme, avec les intitulés réels du document et les pages mesurées sur le PDF.
TOC = [
 (1, "1. La liste des comp\u00e9tences mises en \u0153uvre dans le cadre du projet"),
 (1, "2. Le cahier des charges ou l\u2019expression des besoins du projet"),
 (1, "3. - la pr\u00e9sentation de l\u2019entreprise et du service"),
 (1, "4. La gestion de projet"),
 (1, "5. Les sp\u00e9cifications fonctionnelles du projet"),
 (2, "5.1. Les contraintes du projet et livrables attendus"),
 (2, "5.2. L\u2019architecture logicielle du projet"),
 (2, "5.3. Les maquettes et encha\u00eenement des maquettes"),
 (2, "5.4. Le mod\u00e8le entit\u00e9s-associations et mod\u00e8le physique de la base de donn\u00e9es"),
 (2, "5.5. Le script de cr\u00e9ation ou de modification de la base de donn\u00e9es"),
 (2, "5.6. Le diagramme du comportement des fonctionnalit\u00e9s de type cas d\u2019utilisations"),
 (2, "5.7. Le diagramme du d\u00e9tail des cas d\u2019utilisations les plus significatifs de type diagramme de s\u00e9quence"),
 (1, "6. Les sp\u00e9cifications techniques du projet"),
 (1, "7. Les r\u00e9alisations du projet"),
 (2, "7.1. Les captures d\u2019\u00e9cran d\u2019interfaces utilisateur et le code correspondant"),
 (2, "7.2. Des extraits de code de composants m\u00e9tier"),
 (2, "7.3. Des extraits de code de composants d\u2019acc\u00e8s aux donn\u00e9es"),
 (2, "7.4. Des extraits de code d\u2019autres composants"),
 (1, "8. Les \u00e9l\u00e9ments de s\u00e9curit\u00e9 de l\u2019application"),
 (1, "9. Le plan de tests"),
 (1, "10. Le jeu d\u2019essai de la fonctionnalit\u00e9 la plus repr\u00e9sentative"),
 (1, "11. - la description de la veille, effectu\u00e9e par le candidat"),
 (1, "12. Les annexes"),
 (2, "12.1. Les maquettes des interfaces utilisateur"),
 (2, "12.2. Les captures d\u2019\u00e9crans d\u2019interfaces utilisateurs et le code correspondant"),
 (2, "12.3. Le code de composants m\u00e9tier les plus significatifs"),
 (2, "12.4. Le code de composants d\u2019acc\u00e8s aux donn\u00e9es les plus significatifs"),
 (2, "12.5. Le code d\u2019autres composants"),
]

from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_BREAK

anchor = P[0]
clear(anchor)
saut = OxmlElement("w:p")
anchor._p.addprevious(saut)
_sp = Paragraph(saut, anchor._parent)
_sp.style = STYLES["Normal"]
_sp.add_run().add_break(WD_BREAK.PAGE)
anchor.style = STYLES["Heading 1"]
anchor.add_run("Table des mati\u00e8res")
anchor.paragraph_format.space_before = Pt(0)
prev = anchor
for lvl, label in TOC:
    line = new_after(prev, "Compact")
    pf = line.paragraph_format
    pf.left_indent = _Cm(0.6 if lvl == 2 else 0)
    pf.tab_stops.add_tab_stop(_Cm(17.4), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    r = line.add_run(label)
    r.bold = (lvl == 1)
    line.add_run("\t" + str(PAGES.get(label.split(" ")[0], "")))
    prev = line
# les 20 lignes de l'ancien sommaire
for i in range(1, 21):
    el = P[i]._p
    el.getparent().remove(el)
# le corps du dossier commence sur une page neuve
prev.add_run().add_break(WD_BREAK.PAGE)

# -------------------------------------------- numérotation des titres ------
# La numérotation automatique des titres de Word numérote les parties mais
# laisse les sous-parties avec un compteur isolé (« 1. », « 4. ») qui entre en
# collision avec les numéros écrits à la main (« 5.4.1. »). On la retire et on
# écrit tous les numéros dans le texte, exactement comme le sommaire les cite.
import re as _re

for sid in ("Heading 1", "Heading 2", "Heading 3"):
    pPr = STYLES[sid].element.get_or_add_pPr()
    for el in pPr.findall(qn("w:numPr")):
        pPr.remove(el)

PROMUS = {
    "Les maquettes et enchaînement des maquettes": "5.3.",
    "Le modèle entités-associations et modèle physique de la base de données": "5.4.",
    "Le script de création ou de modification de la base de données": "5.5.",
    "Le diagramme du comportement des fonctionnalités de type cas d\u2019utilisations": "5.6.",
    "Le diagramme du détail des cas d\u2019utilisations les plus significatifs de type diagramme de séquence.": "5.7.",
    "Les captures d\u2019écran d\u2019interfaces utilisateur et le code correspondant": "7.1.",
    "Des extraits de code de composants métier": "7.2.",
    "Des extraits de code de composants d\u2019accès aux données": "7.3.",
    "Des extraits de code d\u2019autres composants": "7.4.",
    "Les maquettes des interfaces utilisateur": "12.1.",
    "Les captures d\u2019écrans d\u2019interfaces utilisateurs et le code correspondant": "12.2.",
    "Le code de composants métier les plus significatifs": "12.3.",
    "Le code de composants d\u2019accès aux données les plus significatifs": "12.4.",
    "Le code d\u2019autres composants": "12.5.",
}

partie = 0
for par in doc.paragraphs:
    nom = par.style.name or ""
    txt = par.text.strip()
    if nom.startswith("Heading"):
        # certains titres portent la numérotation sur le paragraphe lui-même,
        # et pas seulement via leur style : sans cela, un « 7. » parasite venait
        # s'ajouter devant « 5.7. ».
        _pPr = par._p.get_or_add_pPr()
        for _el in _pPr.findall(qn("w:numPr")):
            _pPr.remove(_el)
    if nom == "Heading 1":
        if txt == "Table des matières":
            continue
        partie += 1
        if not _re.match(r"^\d+\.", txt):
            par.runs[0].text = f"{partie}. " + par.runs[0].text
    elif nom == "Heading 2":
        # les sous-sous-parties de la partie 5 étaient au même niveau que leur
        # parent : elles passent en titre de niveau 3.
        if _re.match(r"^5\.\d\.\d", txt):
            par.style = STYLES["Heading 3"]
        elif txt in PROMUS:
            par.runs[0].text = PROMUS[txt] + " " + par.runs[0].text

doc.save(OUT)
print("écrit :", OUT)
