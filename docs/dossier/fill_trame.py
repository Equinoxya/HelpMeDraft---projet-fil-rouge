# -*- coding: utf-8 -*-
"""
Remplit la trame officielle du dossier de projet CDA avec le contenu rédigé
dans « Dossier projet CDA - HelpMeDraft.docx ».

La trame donne la structure : page de garde, numérotation automatique sur deux
niveaux, en-têtes et pieds de page, douze parties et leurs sous-parties, avec
les intitulés officiels. Le contenu vient du dossier déjà rédigé. Les figures
sont posées depuis fig/, jamais recopiées depuis un .docx, pour que les images
soient réellement intégrées au nouveau fichier.
"""
import copy, json, os, re, sys
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

RACINE = "/home/user/HelpMeDraft---projet-fil-rouge"
TRAME = f"{RACINE}/docs/dossier/trame-dossier-projet-cda.docx"
SOURCE = f"{RACINE}/Dossier projet CDA - HelpMeDraft.docx"
SORTIE = f"{RACINE}/docs/dossier/dossier-projet-rempli.docx"
FIG = f"{RACINE}/docs/dossier/fig"
CAP = f"{RACINE}/docs/captures"
PAGES = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}

W_FIG = 15.8          # largeur des figures, inchangée : la rendre plus large coûtait une page
DECALAGE_NUM = 1000   # pour que les listes de la source n'écrasent pas celles de la trame

cible = docx.Document(TRAME)
src = docx.Document(SOURCE)

# ───────────────────────── 1. styles manquants ─────────────────────────────
# Le contenu source s'appuie sur des styles (corps de texte, blocs de code,
# tableaux) que la trame ne connaît pas : sans eux, les blocs de code
# retomberaient en texte courant.
ids_cible = {s.element.get(qn("w:styleId")) for s in cible.styles}
styles_cible = cible.styles.element
for st in src.styles.element:
    if st.tag == qn("w:style") and st.get(qn("w:styleId")) not in ids_cible:
        styles_cible.append(copy.deepcopy(st))

# ───────────────────────── 2. numérotations de la source ───────────────────
num_src = src.part.numbering_part.element
num_cible = cible.part.numbering_part.element
for an in num_src.findall(qn("w:abstractNum")):
    c = copy.deepcopy(an)
    c.set(qn("w:abstractNumId"), str(int(an.get(qn("w:abstractNumId"))) + DECALAGE_NUM))
    num_cible.append(c)
for n in num_src.findall(qn("w:num")):
    c = copy.deepcopy(n)
    c.set(qn("w:numId"), str(int(n.get(qn("w:numId"))) + DECALAGE_NUM))
    ref = c.find(qn("w:abstractNumId"))
    ref.set(qn("w:val"), str(int(ref.get(qn("w:val"))) + DECALAGE_NUM))
    num_cible.append(c)

# ───────────────────────── 3. découpage de la source ───────────────────────
# Bornes relevées sur le dossier rédigé : première et dernière ligne de contenu
# de chaque partie, en indices de paragraphe.
BORNES = {
    "1":    (22, 27),   "2":    (28, 51),   "3":    (52, 60),   "4":    (61, 82),
    "5":    (83, 86),   "5.1":  (87, 102),  "5.2":  (103, 121), "5.3":  (122, 159),
    "5.4":  (160, 199), "5.5":  (200, 221), "5.6":  (222, 236), "5.7":  (237, 256),
    "6":    (257, 300), "7.1":  (301, 331), "7.2":  (332, 360), "7.3":  (361, 394),
    "7.4":  (395, 420), "8":    (420, 468), "9":    (468, 517), "10":   (517, 539),
    "11":   (540, 581), "12.1": (583, 604), "12.2": (605, 609), "12.3": (610, 614),
    "12.4": (615, 623), "12.5": (624, None),
}

corps_src = list(src.element.body)
pos_par = {}            # indice de paragraphe -> indice dans le corps
k = 0
for j, el in enumerate(corps_src):
    if el.tag == qn("w:p"):
        pos_par[k] = j
        k += 1
fin_corps = len(corps_src) - 1      # le dernier enfant est le sectPr


# ───────────────────────── coupes de volume ───────────────────────────────
# Le corps doit tenir dans les 60 pages du référentiel ; il en faisait 70.
# Indices de paragraphe du document source écartés du remplissage.
#
# 1. Huit blocs de code de la partie 7 reproduits à l'identique dans les
#    annexes. Sur les 268 lignes significatives de la partie 7, 124 figurent
#    déjà en annexe ; ces huit blocs le sont de 77 % à 100 %. Le référentiel
#    attend en partie 7 des extraits commentés, et en annexe le code complet :
#    rien n'est perdu. Les blocs du front (7.1) ne sont pas dupliqués, ils
#    restent.
CODE_DOUBLONS = {334, 341, 347, 352, 363, 397, 403, 406}
#
# 2. La veille AI Act : veille réglementaire, là où le référentiel demande la
#    veille sur les vulnérabilités de sécurité ; et la traçabilité AI Act sort
#    du cahier des charges.
VEILLE_AI_ACT = set(range(562, 573))
#
# 3. « Lancement en développement » : des instructions d'installation, qui
#    relèvent du README plutôt que du dossier.
LANCEMENT_DEV = set(range(282, 287))
#
# 4. Le wireframe ASCII de l'éditeur : le texte qui l'introduit renvoie déjà à
#    la planche W-06, reproduite en annexe 12.1 dans une version bien plus
#    lisible. Le dessin faisait doublon avec elle.
WIREFRAME_EDITEUR = {147}

EXCLUS = CODE_DOUBLONS | VEILLE_AI_ACT | LANCEMENT_DEV | WIREFRAME_EDITEUR

def blocs(cle):
    deb, fin = BORNES[cle]
    j0 = pos_par[deb]
    j1 = pos_par[fin] if fin is not None else fin_corps
    ecartes = {pos_par[i] for i in EXCLUS if i in pos_par}
    return [el for j, el in enumerate(corps_src[j0:j1], start=j0) if j not in ecartes]

# ───────────────────────── 4. remplissage ──────────────────────────────────
titres = {}
for p in cible.paragraphs:
    t = p.text.strip().rstrip(".").lower()
    if t:
        titres[t] = p

def ancre(debut):
    for p in cible.paragraphs:
        if p.text.strip().lower().startswith(debut.lower()):
            return p
    raise KeyError(debut)

ANCRES = {
    "1":   "La liste des compétences",
    "2":   "Le cahier des charges",
    "3":   "- la présentation de l’entreprise",
    "4":   "La gestion de projet",
    "5":   "Les spécifications fonctionnelles",
    "5.1": "Les contraintes du projet",
    "5.2": "L’architecture logicielle",
    "5.3": "Les maquettes et enchaînement",
    "5.4": "Le modèle entités-associations",
    "5.5": "Le script de création",
    "5.6": "Le diagramme du comportement",
    "5.7": "Le diagramme du détail",
    "6":   "Les spécifications techniques",
    "7.1": "Les captures d’écran d’interfaces",
    "7.2": "Des extraits de code de composants métier",
    "7.3": "Des extraits de code de composants d’accès",
    "7.4": "Des extraits de code d’autres composants",
    "8":   "La présentation d’éléments de sécurité",
    "9":   "La présentation du plan de tests",
    "10":  "La présentation d’un jeu d’essai",
    "11":  "- la description de la veille",
    "12.1":"Les maquettes des interfaces utilisateur",
    "12.2":"Les captures d’écrans d’interfaces",
    "12.3":"Le code de composants métier",
    "12.4":"Le code de composants d’accès",
    "12.5":"Le code d’autres composants",
}

inseres = []          # tous les éléments venus de la source
for cle, debut in ANCRES.items():
    titre = ancre(debut)
    courant = titre._p
    for el in blocs(cle):
        c = copy.deepcopy(el)
        for npr in c.iter(qn("w:numId")):
            npr.set(qn("w:val"), str(int(npr.get(qn("w:val"))) + DECALAGE_NUM))
        courant.addnext(c)
        courant = c
        inseres.append(c)

STYLES = {st.name: st for st in cible.styles}
ensemble = set(id(e) for e in inseres)

# ─────────────────── 5. sous-titres venus de la source ────────────────────
# La trame ne prévoit de sous-parties qu'en 5, 7 et 12. Les sous-sections du
# document source ne doivent donc pas devenir des titres : elles créeraient des
# rubriques absentes de la trame, qui remonteraient dans le sommaire et dans la
# numérotation. Elles redeviennent du texte courant en gras, sans leur numéro,
# ce qui conserve les repères de lecture sans ajouter de niveau.
for par in cible.paragraphs:
    if id(par._p) not in ensemble:
        continue
    if not (par.style.name or "").startswith("Heading"):
        continue
    texte = re.sub(r"^\s*(\d+(\.\d+)*\.?|[a-z]\.)\s*", "", par.text.strip())
    pPr = par._p.get_or_add_pPr()
    for el in pPr.findall(qn("w:numPr")):
        pPr.remove(el)
    for child in list(par._p):
        if child.tag != qn("w:pPr"):
            par._p.remove(child)
    par.style = STYLES["Body Text"]
    run = par.add_run(texte)
    run.bold = True

# ─────────────────── 5 ter. veille AI Act, version courte ─────────────────
# La section AI Act d'origine faisait 1,7 page et a été retirée pour tenir dans
# les 60 pages. Mais le dossier la cite encore à dix endroits, et la troisième
# conclusion de la veille — « le cadre réglementaire bouge pendant le projet »
# — n'avait plus d'exemple. On remet une version condensée, écrite à partir du
# texte d'origine : le constat, ce qui est déjà couvert, les trois compléments
# tels que l'autrice les avait listés, et ce que l'entrée prouve sur la veille.
INTRO_AI_ACT = (
    "Depuis le 2 ao\u00fbt 2026, les obligations de transparence du r\u00e8glement europ\u00e9en sur "
    "l\u2019intelligence artificielle sont applicables. Deux concernent HelpMeDraft : informer "
    "clairement l\u2019utilisateur qu\u2019il interagit avec une intelligence artificielle, et marquer "
    "les contenus g\u00e9n\u00e9r\u00e9s. Le projet en couvre d\u00e9j\u00e0 une partie \u2014 le panneau est intitul\u00e9 "
    "\u00ab\u00a0Assistant IA \u2014 Ollama\u00a0\u00bb, l\u2019action demand\u00e9e est explicite, et aucune proposition "
    "n\u2019est appliqu\u00e9e sans d\u00e9cision de l\u2019utilisateur. Trois compl\u00e9ments restent \u00e0 produire :"
)
PUCES_AI_ACT = [
    "une mention d\u2019information non ambigu\u00eb au premier usage de l\u2019assistant, et non seulement "
    "un titre de panneau\u00a0;",
    "une trace des passages issus d\u2019une g\u00e9n\u00e9ration dans le document \u2014 la table ia conserve "
    "d\u00e9j\u00e0 l\u2019information c\u00f4t\u00e9 base (\u00a7\u00a05.4), il reste \u00e0 l\u2019exposer c\u00f4t\u00e9 interface\u00a0;",
    "une clause d\u00e9di\u00e9e dans les CGU et la politique de confidentialit\u00e9, distincte du "
    "consentement au traitement des donn\u00e9es.",
]
FIN_AI_ACT = (
    "Cette entr\u00e9e justifie la veille comme livrable : le cahier des charges, r\u00e9dig\u00e9 avant "
    "l\u2019entr\u00e9e en application du r\u00e8glement, ne mentionne que le RGPD. Sans ce suivi, "
    "l\u2019application aurait \u00e9t\u00e9 livr\u00e9e non conforme \u00e0 une obligation entr\u00e9e en vigueur trois "
    "semaines avant la fin du d\u00e9veloppement."
)

rgaa = None
for par in cible.paragraphs:
    if id(par._p) in ensemble and par.text.strip().startswith("RGAA \u2014 la version 5"):
        rgaa = par
        break
if rgaa is None:
    print("  !! point d\u2019insertion AI Act introuvable")
else:
    # Modèle de puce : on reprend la mise en forme d'une liste déjà présente,
    # pour que les trois points ne détonnent pas dans la partie.
    modele_puce = None
    for par in cible.paragraphs:
        if (id(par._p) in ensemble and (par.style.name or "") == "Compact"
                and par._p.pPr is not None and par._p.pPr.find(qn("w:numPr")) is not None):
            modele_puce = copy.deepcopy(par._p.pPr)
            break

    def inserer_avant(voisin, texte, style="Body Text", gras=False, puce=False):
        el = OxmlElement("w:p")
        voisin._p.addprevious(el)
        nouveau = Paragraph(el, voisin._parent)
        nouveau.style = STYLES["Compact" if puce else style]
        if puce and modele_puce is not None:
            nouveau._p.insert(0, copy.deepcopy(modele_puce))
        run = nouveau.add_run(texte)
        run.bold = gras
        return nouveau

    inserer_avant(rgaa, "AI Act \u2014 une exigence apparue en cours de projet", gras=True)
    inserer_avant(rgaa, INTRO_AI_ACT)
    for point in PUCES_AI_ACT:
        inserer_avant(rgaa, point, puce=True)
    inserer_avant(rgaa, FIN_AI_ACT)

# ─────────────────── 5 bis. renvois internes ──────────────────────────────
# Le texte source renvoyait à ses propres sous-sections (« § 8.2 », « § 5.4.5 »).
# Ces niveaux n'existent plus : la trame ne numérote que les douze parties et
# les sous-parties de 5, 7 et 12. Chaque renvoi est ramené au niveau le plus
# profond qui existe réellement — § 5.4.5 devient § 5.4, § 8.2 devient § 8.
CIBLES_VALIDES = (
    {str(i) for i in range(1, 13)}
    | {f"5.{i}" for i in range(1, 8)}
    | {f"7.{i}" for i in range(1, 5)}
    | {f"12.{i}" for i in range(1, 6)}
)

def cible_valide(numero):
    morceaux = numero.split(".")
    for n in range(len(morceaux), 0, -1):
        candidat = ".".join(morceaux[:n])
        if candidat in CIBLES_VALIDES:
            return candidat
    return None

def tous_paragraphes(document):
    for par in document.paragraphs:
        yield par
    for tbl in document.tables:
        for ligne in tbl.rows:
            for cellule in ligne.cells:
                for par in cellule.paragraphs:
                    yield par

RENVOI = re.compile(r"§\s*(\d+(?:\.\d+)*)")
tronques = supprimes = 0
for par in tous_paragraphes(cible):
    if "§" not in par.text:
        continue
    # Les renvois vers la veille AI Act visent une section retirée : les
    # ramener à « § 11 » enverrait le lecteur vers un texte qui n'en parle
    # plus. Le renvoi est retiré, la phrase est conservée.
    ai_act = "AI Act" in par.text
    for run in par.runs:
        if "§" not in run.text:
            continue
        if ai_act and "11.4" in run.text:
            avant = run.text
            run.text = re.sub(r"\s*\(§\s*11\.4\)", "", run.text)
            run.text = re.sub(r"\s+en\s*§\s*11\.4", "", run.text)
            run.text = re.sub(r"\s*§\s*11\.4", "", run.text)
            if run.text != avant:
                supprimes += 1
                continue
        def remplacer(m):
            global tronques
            but = cible_valide(m.group(1))
            if but is None or but == m.group(1):
                return m.group(0)
            tronques += 1
            return "\u00a7 " + but
        run.text = RENVOI.sub(remplacer, run.text)
print(f"  renvois ramen\u00e9s \u00e0 un niveau existant : {tronques} | renvois retir\u00e9s : {supprimes}")

# ─────────────────── 6. figures ────────────────────────────────────────────
def para_contenant(fragment, style=None):
    for par in cible.paragraphs:
        if id(par._p) not in ensemble:
            continue
        if style and (par.style.name or "") != style:
            continue
        if fragment in par.text:
            return par
    return None

def vider(par):
    for child in list(par._p):
        if child.tag != qn("w:pPr"):
            par._p.remove(child)

def poser_image(par, chemin, largeur, legende=None):
    vider(par)
    par.style = STYLES["Figure"]
    par.alignment = 1
    par.add_run().add_picture(chemin, width=Cm(largeur))
    if legende:
        el = OxmlElement("w:p")
        par._p.addnext(el)
        cap = Paragraph(el, par._parent)
        cap.style = STYLES["Image Caption"]
        cap.add_run(legende)
        return cap
    return par

def image_apres(par, chemin, largeur, legende=None):
    el = OxmlElement("w:p")
    par._p.addnext(el)
    fp = Paragraph(el, par._parent)
    fp.style = STYLES["Figure"]
    fp.alignment = 1
    fp.add_run().add_picture(chemin, width=Cm(largeur))
    if legende:
        el2 = OxmlElement("w:p")
        fp._p.addnext(el2)
        cap = Paragraph(el2, fp._parent)
        cap.style = STYLES["Image Caption"]
        cap.add_run(legende)
    return fp

REMPLACEMENTS = [
    ("Navigateur", f"{FIG}/archi.png",
     "Architecture logicielle \u2014 d\u00e9coupage en couches et services p\u00e9riph\u00e9riques."),
    ("ZONE PUBLIQUE", f"{FIG}/planches/image9.png",
     "Encha\u00eenement des \u00e9crans \u2014 planche W-09, reprise en annexe \u00a7 12.1."),
    ("USER", f"{FIG}/mcd.png",
     "Mod\u00e8le conceptuel des donn\u00e9es (MCD) \u2014 sept entit\u00e9s, huit associations, cardinalit\u00e9s Merise."),
    ("HelpMeDra", f"{FIG}/usecase.png", "Diagramme de cas d\u2019utilisation."),
    ("DocumentEditor", f"{FIG}/seq-uc10.png",
     "Diagramme de s\u00e9quence \u2014 g\u00e9n\u00e9rer une assistance IA, sc\u00e9nario nominal."),
]
for fragment, chemin, legende in REMPLACEMENTS:
    cible_par = para_contenant(fragment, style="Source Code")
    if cible_par is None:
        print("  !! ancre introuvable :", fragment)
    else:
        poser_image(cible_par, chemin, W_FIG, legende)

# MLD : juste avant la sous-section « Le modèle physique des données »
mpd_titre = para_contenant("Le mod\u00e8le physique des donn\u00e9es")
if mpd_titre is not None:
    el = OxmlElement("w:p")
    mpd_titre._p.addprevious(el)
    fp = Paragraph(el, mpd_titre._parent)
    fp.style = STYLES["Figure"]
    fp.alignment = 1
    fp.add_run().add_picture(f"{FIG}/mld.png", width=Cm(W_FIG))
    el2 = OxmlElement("w:p")
    fp._p.addnext(el2)
    cap = Paragraph(el2, fp._parent)
    cap.style = STYLES["Image Caption"]
    cap.add_run("Mod\u00e8le logique des donn\u00e9es (MLD) \u2014 les sept relations apr\u00e8s application des r\u00e8gles de passage.")

# MPD : après la phrase d'introduction des sept tables
sept = para_contenant("Sept tables.")
if sept is not None:
    image_apres(sept, f"{FIG}/mpd.png", W_FIG,
                "Mod\u00e8le physique des donn\u00e9es (MPD) \u2014 types, cl\u00e9s, index et r\u00e8gles de suppression sur MySQL 8.")

# captures d'écran
for debut, fichier, legende in [
    ("7.1.1.", f"{CAP}/C-05-tableau-de-bord.png", "Capture C-05 \u2014 tableau de bord."),
    ("7.1.2.", f"{CAP}/C-07-nouveau-document.png", "Capture C-07 \u2014 \u00e9diteur de document, cr\u00e9ation."),
]:
    t = None
    for par in cible.paragraphs:
        if id(par._p) in ensemble and par.text.strip().startswith(debut):
            t = par
            break
    if t is not None:
        image_apres(t, fichier, 13.5, legende)

# planches W-01 à W-09 : les paragraphes vides qui précèdent chaque légende
vides = []
paras = cible.paragraphs
for i, par in enumerate(paras):
    if id(par._p) in ensemble and re.match(r"^W-0\d\s+\u2014", par.text.strip()):
        prec = paras[i - 1]
        if not prec.text.strip():
            vides.append(prec)
for n, par in enumerate(vides, start=1):
    poser_image(par, f"{FIG}/planches/image{n}.png", W_FIG)
print("  planches pos\u00e9es :", len(vides))

# ─────────────────── 7. page de garde ──────────────────────────────────────
# Les cinq champs de la page de garde sont des contrôles de contenu Word.
COUVERTURE = {
    "Société": "LexiCorp",
    "Titre": "Dossier projet",
    "Sous-titre": "HelpMeDraft \u2014 assistant de r\u00e9daction assist\u00e9e par IA",
    "Auteur": "Oph\u00e9lie Bellissens  /  CDA  /  Metz Numeric School",
    "Date": "Octobre 2026",
}
a_degrouper = []
for sdt in cible.element.body.iter(qn("w:sdt")):
    alias = sdt.find(".//" + qn("w:alias"))
    if alias is None:
        continue
    valeur = COUVERTURE.get(alias.get(qn("w:val")))
    if valeur is None:
        continue
    textes = sdt.findall(".//" + qn("w:t"))
    if not textes:
        continue
    textes[0].text = valeur
    for t in textes[1:]:
        t.text = ""
    a_degrouper.append(sdt)

# Les champs de la page de garde sont ensuite dégroupés : tant qu'ils restent
# des contrôles de contenu, les outils de rendu affichent leur texte de
# remplacement à la place de la valeur saisie.
for sdt in a_degrouper:
    contenu = sdt.find(qn("w:sdtContent"))
    if contenu is None:
        continue
    parent = sdt.getparent()
    i = list(parent).index(sdt)
    for enfant in list(contenu):
        parent.insert(i, enfant)
        i += 1
    parent.remove(sdt)

# ─────────────────── 8. lignes vides de la trame ───────────────────────────
# La page de garde est composée de cadres ancrés à des paragraphes vides :
# les supprimer ferait remonter le sommaire sur la couverture. On ne nettoie
# donc qu'à partir de la fin de la première section.
paras = cible.paragraphs
debut_nettoyage = 0
for i, par in enumerate(paras):
    pPr = par._p.pPr
    if pPr is not None and pPr.find(qn("w:sectPr")) is not None:
        debut_nettoyage = i + 1
        break
for par in paras[debut_nettoyage:]:
    if id(par._p) in ensemble or par.text.strip():
        continue
    pPr = par._p.pPr
    if pPr is not None and pPr.find(qn("w:sectPr")) is not None:
        continue
    if len(par._p) <= 1:
        par._p.getparent().remove(par._p)

# ─────────────────── 9. largeur des tableaux ───────────────────────────────
from docx.enum.table import WD_TABLE_ALIGNMENT
for t in cible.tables:
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
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

# ─────────────────── 10. densité ───────────────────────────────────────────
# Le dossier doit tenir dans les 60 pages de corps du référentiel.
normal = STYLES["Normal"].paragraph_format
normal.space_after = Pt(6)
normal.space_before = Pt(0)
normal.line_spacing = 1.0
for nom in ("Body Text", "First Paragraph", "Compact"):
    if nom in STYLES:
        pf = STYLES[nom].paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(4)
STYLES["Source Code"].paragraph_format.line_spacing = Pt(9)
STYLES["Image Caption"].paragraph_format.space_after = Pt(10)
STYLES["Figure"].paragraph_format.space_before = Pt(8)
STYLES["Figure"].paragraph_format.space_after = Pt(2)

# ─────────────────── 11. mise à jour des champs à l'ouverture ──────────────
# La table des matières de la trame est un champ : sans cette instruction, elle
# reste figée sur les numéros de page de la trame vide (tous à zéro).
reglages = cible.settings.element
if reglages.find(qn("w:updateFields")) is None:
    maj = OxmlElement("w:updateFields")
    maj.set(qn("w:val"), "true")
    reglages.append(maj)

# ─────────────────── 12. numéros de page du sommaire ───────────────────────
# Le sommaire de la trame est un champ dont le résultat est mémorisé ; tant que
# Word ne l'a pas rafraîchi, il affiche les numéros de la trame vide. On réécrit
# le résultat mémorisé avec la pagination relevée sur le PDF, en laissant le
# champ en place pour qu'un rafraîchissement reste possible.
if PAGES:
    import unicodedata
    def cle(t):
        t = unicodedata.normalize("NFKD", t)
        t = "".join(c for c in t if not unicodedata.combining(c))
        return re.sub(r"[^a-z0-9]+", "", t.lower())
    table = {cle(k): v for k, v in PAGES.items()}
    for sdt in cible.element.body.iter(qn("w:sdt")):
        if not any("TOC" in (t.text or "") for t in sdt.iter(qn("w:instrText"))):
            continue
        for par in sdt.iter(qn("w:p")):
            textes = par.findall(".//" + qn("w:t"))
            if len(textes) < 2:
                continue
            libelle = "".join(t.text or "" for t in textes[:-1])
            libelle = re.sub(r"^\s*\d+(\.\d+)*\.?\s*", "", libelle)
            num = table.get(cle(libelle))
            if num:
                textes[-1].text = str(num)
        break

# ───────────────────────── marges ─────────────────────────────────────────
# 2 cm au lieu des 2,5 cm de la trame : six pages de corps regagnées sans
# retirer une ligne de texte.
for sec in cible.sections:
    sec.top_margin = sec.bottom_margin = Cm(2)
    sec.left_margin = sec.right_margin = Cm(2)

cible.save(SORTIE)
print("rempli :", SORTIE)
