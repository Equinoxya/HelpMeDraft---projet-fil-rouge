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

from sommaire import SOMMAIRE

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
# Les trois blocs du § 7.4 (397, 403, 406) ont d'abord été retirés avec les
# autres, mais leurs phrases d'introduction les annoncent par deux-points : les
# retirer laissait des annonces sans code. Ils restent.
CODE_DOUBLONS = {334, 341, 347, 352, 363}
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
#
# 5. Quatre intitulés du référentiel laissés tels quels dans le texte source, à
#    la fin de la partie qui précède : « La présentation d'éléments de sécurité
#    de l'application », « La présentation du plan de tests », « La présentation
#    d'un jeu d'essai élaboré par le candidat », « Les réalisations du candidat
#    comportant les extraits de code les plus significatifs ». La trame porte
#    déjà ces titres.
TITRES_EN_DOUBLE = {299, 419, 467, 516}

EXCLUS = (CODE_DOUBLONS | VEILLE_AI_ACT | LANCEMENT_DEV | WIREFRAME_EDITEUR
          | TITRES_EN_DOUBLE)

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

# Les ancres sont résolues sur la trame intacte, AVANT toute insertion. Sinon
# le contenu déjà posé peut contenir un paragraphe commençant par le même
# intitulé, et c'est lui qui est retenu : les parties 8, 9 et 10 se sont ainsi
# retrouvées greffées au milieu de la partie 7, leurs titres restant vides.
ANCRES_RESOLUES = {cle: ancre(debut) for cle, debut in ANCRES.items()}

inseres = []          # tous les éléments venus de la source
for cle in ANCRES:
    titre = ANCRES_RESOLUES[cle]
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

# ─────────────────── 5 quater. conformité au référentiel ──────────────────
# a) Sept parties sur douze portent dans la trame le style « List Paragraph »
#    alors qu'elles appartiennent à la même liste numérotée que les autres.
#    Le sommaire étant construit sur les styles de titre, elles n'y figuraient
#    pas : le dossier annonçait cinq parties sur douze. On leur rend le style
#    de titre en conservant leur numérotation, qui est déjà la bonne.
for par in cible.paragraphs:
    if id(par._p) in ensemble:
        continue
    pPr = par._p.pPr
    if (par.style.name or "") == "List Paragraph" and pPr is not None \
            and pPr.find(qn("w:numPr")) is not None:
        # « Titre1 » est le style de titre de la trame ; le document source en
        # apporte un second, « Heading1 », de même nom mais d'une autre couleur
        # et d'une autre police. Les désigner par leur identifiant évite que
        # sept parties sur douze soient composées différemment des cinq autres.
        pPr.find(qn("w:pStyle")).set(qn("w:val"), "Titre1")
        for rpr in [pPr.find(qn("w:rPr"))] + [r._r.find(qn("w:rPr")) for r in par.runs]:
            if rpr is None:
                continue
            for nom in ("w:rFonts", "w:color"):
                for el in rpr.findall(qn(nom)):
                    rpr.remove(el)

# b) Le référentiel demande, pour le jeu d'essai, « données en entrée, données
#    attendues, données obtenues ET analyse des écarts éventuels ». Les trois
#    colonnes existent, l'analyse des écarts manquait — le mot n'apparaissait
#    nulle part dans la partie 10. Elle est écrite à partir du résultat réel
#    des quinze cas et des réserves déjà posées par l'autrice.
ANALYSE_ECARTS = (
    "Les quinze cas d\u2019essai ont \u00e9t\u00e9 ex\u00e9cut\u00e9s dans les conditions d\u00e9crites ci-dessus : "
    "aucun \u00e9cart n\u2019est constat\u00e9 entre les donn\u00e9es attendues et les donn\u00e9es obtenues. "
    "Deux r\u00e9serves rendent ce r\u00e9sultat lisible. Le jeu d\u2019essai valide la m\u00e9canique autour du "
    "mod\u00e8le \u2014 validation des entr\u00e9es, autorisation, quota, trace, gestion des erreurs \u2014 et "
    "non la qualit\u00e9 linguistique des suggestions, qui n\u2019est pas d\u00e9terministe et ne peut pas "
    "faire l\u2019objet d\u2019une assertion. Et JE-12 est le seul cas ex\u00e9cut\u00e9 sans simulation, "
    "serveur d\u2019inf\u00e9rence r\u00e9ellement arr\u00eat\u00e9 ; les autres s\u2019appuient sur un double de test, ce "
    "qui est la condition de leur reproductibilit\u00e9."
)
for par in cible.paragraphs:
    if id(par._p) in ensemble and par.text.strip().startswith("Cas limites"):
        el = OxmlElement("w:p")
        par._p.addprevious(el)
        intro = Paragraph(el, par._parent)
        intro.style = STYLES["Body Text"]
        intro.add_run("Analyse des \u00e9carts").bold = True
        el2 = OxmlElement("w:p")
        intro._p.addnext(el2)
        corps_ecarts = Paragraph(el2, intro._parent)
        corps_ecarts.style = STYLES["First Paragraph"]
        corps_ecarts.add_run(ANALYSE_ECARTS)
        break

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

# ─────────────────── 5 sexies. retrait des numéros de partie ──────────────
# La liste à deux niveaux de la trame réserve 0,63 cm au numéro de premier
# niveau. À 18 pt, « 2. » dépasse cette réserve : la tabulation qui suit le
# numéro n'avance plus, et le titre venait se coller au point (« 2.Le cahier
# des charges »), sur huit parties des douze. On porte la réserve à 1,27 cm,
# ce qui aligne les douze titres sur une même marge.
_num = cible.part.numbering_part.element
_abs = {n.find(qn("w:abstractNumId")).get(qn("w:val"))
        for n in _num.findall(qn("w:num")) if n.get(qn("w:numId")) == "5"}
for _an in _num.findall(qn("w:abstractNum")):
    if _an.get(qn("w:abstractNumId")) not in _abs:
        continue
    for _lvl in _an.findall(qn("w:lvl")):
        if _lvl.get(qn("w:ilvl")) != "0":
            continue
        _ind = _lvl.find(qn("w:pPr")).find(qn("w:ind"))
        _ind.set(qn("w:left"), "720")
        _ind.set(qn("w:hanging"), "720")

# ─────────────────── 5 quinquies. corrections de relecture ────────────────
# Relecture intégrale du dossier rempli. Trois familles de corrections :
#  - des renvois qui, ramenés au niveau le plus profond que la trame connaisse,
#    finissaient par désigner la section où ils se trouvent ;
#  - des contradictions internes au texte source : audit d'accessibilité donné
#    tantôt fait tantôt à faire, version d'Ollama, origine CORS ;
#  - un paragraphe en double et un renvoi circulaire vers l'annexe.
def remplacer_dans(par, ancien, nouveau):
    """Remplace un fragment en préservant la mise en forme autour de lui."""
    runs = par.runs
    for r in runs:
        if ancien in r.text:
            r.text = r.text.replace(ancien, nouveau, 1)
            return True
    plein = "".join(r.text for r in runs)
    i = plein.find(ancien)
    if i < 0:
        return False
    j, pos = i + len(ancien), 0
    for r in runs:
        d, f = pos, pos + len(r.text)
        pos = f
        if f <= i or d >= j:
            continue
        r.text = (r.text[: max(0, i - d)]
                  + (nouveau if d <= i < f else "")
                  + (r.text[j - d:] if f > j else ""))
    return True

CORRECTIONS = [
    # a) renvois d'une section vers elle-même
    ("séparément (§ 5.3), et le rendu", "séparément, et le rendu"),
    ("de contrôle de déploiement (§ 6).", "de contrôle de déploiement."),
    ("le modèle se télécharge à part (§ 6).", "le modèle se télécharge à part."),
    ("l'image Nginx du frontend (§ 6).", "l'image Nginx du frontend."),
    ("appliqué aux jetons (§ 7.2), où", "appliqué aux jetons, où"),
    ("une exception, documentée en § 8.", "une exception, documentée ci-après."),
    ("restent à définir (§ 8).", "restent à définir."),
    # b) l'origine CORS : le texte et la liste de contrôle se contredisaient
    ("L'origine est aujourd'hui codée en dur pour le développement ; elle devra "
     "passer en variable d'environnement au déploiement (§ 6).",
     "L'origine est lue dans CORS_ORIGINS, dont la valeur par défaut est celle du "
     "développement ; elle doit être renseignée avec le domaine réel au déploiement."),
    # c) audit d'accessibilité : mené le 3 octobre (§ 9), et non restant à faire
    ("L'audit outillé (Lighthouse et WAVE) et son rapport restent à produire (§ 5.1) ; "
     "il sera mené sur la version 4.1.2, en vigueur, la version 5 étant annoncée pour "
     "fin 2026 (§ 11).",
     "L'audit outillé a été mené sur la version 4.1.2, en vigueur, la version 5 étant "
     "annoncée pour fin 2026 (§ 9, § 11)."),
    ("L'audit d'accessibilité restant à réaliser (§ 5.1, § 9) sera donc mené sur le "
     "RGAA 4.1.2",
     "L'audit d'accessibilité a donc été mené sur le RGAA 4.1.2 (§ 9)"),
    # d) version d'Ollama : le tableau porte la version installée, pas un minimum
    ("la version minimale 0.17.1 indiquée ci-dessus découle directement de la veille (§ 11).",
     "la version installée indiquée ci-dessus, 0.35.1, découle directement de la veille (§ 11)."),
    # e) renvoi circulaire : l'annexe 12.5 renvoie au § 6 pour ce même code
    ("Leur code complet figure en annexe § 12.5.",
     "Le code complet de la configuration figure en annexe § 12.5."),
    # f) cookie de refresh : 7 jours est la durée de la session côté serveur,
    #    le cookie portant lui un max_age de 30 jours
    ("path=/auth, durée 7 jours (§ 7.4)",
     "path=/auth, session de 7 jours côté serveur (§ 7.4)"),
    # g) annexe 12.1 : deux introductions se recouvraient, et les planches ne
    #    sont pas « une par page »
    ("Les planches sont reproduites ci-après, une par page, dans l'ordre du parcours "
     "utilisateur. Chacune porte sa référence, l'écran concerné et ses intentions de "
     "conception numérotées — la raison d'être de chaque bloc, et non seulement sa "
     "présence. Le fichier source est docs/maquettes-helpmedraft.html dans le dépôt.",
     "Le fichier source des planches est docs/maquettes-helpmedraft.html dans le dépôt."),
]

def toutes_cellules():
    for tbl in cible.tables:
        for ligne in tbl.rows:
            for cel in ligne.cells:
                for par in cel.paragraphs:
                    yield par

faits = set()
for par in list(cible.paragraphs) + list(toutes_cellules()):
    for n, (ancien, nouveau) in enumerate(CORRECTIONS):
        if n not in faits and remplacer_dans(par, ancien, nouveau):
            faits.add(n)
absentes = [CORRECTIONS[n][0][:45] for n in range(len(CORRECTIONS)) if n not in faits]
print(f"  corrections de relecture : {len(faits)}/{len(CORRECTIONS)}"
      + (" | NON TROUVÉES : " + str(absentes) if absentes else ""))

# Un même renvoi écrit deux fois de suite (« § 8, § 8 ») : séquelle de deux
# renvois distincts ramenés au même niveau.
DOUBLE_RENVOI = re.compile(r"(§\s*\d+(?:\.\d+)*)\s*,\s*§\s*(\d+(?:\.\d+)*)")
for par in list(cible.paragraphs) + list(toutes_cellules()):
    for r in par.runs:
        m = DOUBLE_RENVOI.search(r.text)
        while m:
            if m.group(1).split("§")[-1].strip() != m.group(2):
                break
            r.text = r.text.replace(m.group(0), m.group(1))
            m = DOUBLE_RENVOI.search(r.text)

# Paragraphe en double du § 9 : il répète la phrase qui le précède et annonce
# « quatre contrôles humains » qui ne figurent nulle part.
for par in cible.paragraphs:
    if par.text.strip().startswith("Un outil automatique ne détecte qu'une partie des critères"):
        par._p.getparent().remove(par._p)
        break

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

# captures d'écran du § 7.1 : l'ancre est le repère de lecture de la sous-section,
# qui a perdu son numéro à l'étape 5 ; on la reconnaît donc au code de la capture.
# Les largeurs sont calées sur la hauteur rendue : C-05 est presque carrée.
for repere, fichier, largeur, legende in [
    ("(capture C-05)", f"{CAP}/C-05-tableau-de-bord.png", 10.5,
     "Capture C-05 \u2014 tableau de bord."),
    ("(capture C-07)", f"{CAP}/C-07-nouveau-document.png", 12.0,
     "Capture C-07 \u2014 \u00e9diteur de document, cr\u00e9ation."),
]:
    t = None
    for par in cible.paragraphs:
        if id(par._p) in ensemble and repere in par.text:
            t = par
            break
    if t is None:
        print("  !! ancre de capture introuvable :", repere)
    else:
        image_apres(t, fichier, largeur, legende)

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

# captures C-01 à C-07 : l'annexe 12.2 du référentiel demande les captures
# d'écrans d'interfaces utilisateurs. Le texte source les désignait seulement
# par leur fichier dans le dépôt ; elles sont ici réellement reproduites, dans
# l'ordre du parcours. Les largeurs sont calées sur la hauteur rendue.
CAPTURES_ANNEXE = [
    ("C-01-accueil.png",             8.0,  "Capture C-01 \u2014 accueil (/)."),
    ("C-01b-accueil-mobile.png",     5.0,  "Capture C-01b \u2014 accueil en affichage mobile."),
    ("C-02-connexion.png",          12.5,  "Capture C-02 \u2014 connexion (/login)."),
    ("C-03-inscription.png",        12.0,  "Capture C-03 \u2014 inscription (/register)."),
    ("C-04-mot-de-passe-oublie.png",12.5,  "Capture C-04 \u2014 mot de passe oubli\u00e9 (/forgot-password)."),
    ("C-05-tableau-de-bord.png",    11.0,  "Capture C-05 \u2014 tableau de bord (/dashboard)."),
    ("C-06-liste-documents.png",    12.5,  "Capture C-06 \u2014 liste des documents (/documents)."),
    ("C-07-nouveau-document.png",   12.5,  "Capture C-07 \u2014 nouveau document (/documents/nouveau)."),
]
paras = cible.paragraphs
i122 = next((i for i, p in enumerate(paras)
             if p.text.strip().startswith("Les captures d\u2019\u00e9crans d\u2019interfaces")), None)
if i122 is None:
    print("  !! annexe 12.2 introuvable")
else:
    fin = next((p for p in paras[i122 + 1:]
                if (p.style.name or "").startswith("Heading")), None)
    for fichier, largeur, legende in CAPTURES_ANNEXE:
        el = OxmlElement("w:p")
        if fin is not None:
            fin._p.addprevious(el)
        else:
            cible.element.body.append(el)
        fp = Paragraph(el, paras[i122]._parent)
        fp.style = STYLES["Figure"]
        fp.alignment = 1
        fp.add_run().add_picture(f"{CAP}/{fichier}", width=Cm(largeur))
        el2 = OxmlElement("w:p")
        fp._p.addnext(el2)
        cap = Paragraph(el2, fp._parent)
        cap.style = STYLES["Image Caption"]
        cap.add_run(legende)
    print("  captures en annexe :", len(CAPTURES_ANNEXE))

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
        pf.space_after = Pt(3)
STYLES["Source Code"].paragraph_format.line_spacing = Pt(9)
STYLES["Image Caption"].paragraph_format.space_after = Pt(10)
# Les sept parties passées en titre ont ramené avec elles l'espacement du style
# (18 pt avant) : cinq pages de plus. Ramené à 10 pt, l'allure reste celle de la
# trame.
STYLES["Heading 1"].paragraph_format.space_before = Pt(6)
STYLES["Heading 1"].paragraph_format.space_after = Pt(4)
STYLES["Figure"].paragraph_format.space_before = Pt(8)
STYLES["Figure"].paragraph_format.space_after = Pt(2)

# ─────────────────── 10 bis. mise en forme du texte ───────────────────────
# a) Le gras d'amorce à l'intérieur des paragraphes est retiré : « bcrypt
#    plutôt que SHA-256. Une fonction de hachage… » se lit désormais d'un seul
#    trait. Les paragraphes entièrement en gras sont conservés : ce sont les
#    repères de sous-section, seule structure de lecture entre deux titres.
#    Les tableaux gardent le leur, en-têtes comprises.
amorces = 0
for par in cible.paragraphs:
    if (par.style.name or "").startswith("Heading"):
        continue
    pleins = [r for r in par.runs if r.text.strip()]
    if not pleins:
        continue
    gras = [r for r in pleins if r.bold]
    if gras and len(gras) < len(pleins):
        for r in gras:
            r.bold = None
        amorces += 1
print(f"  amorces en gras retirées : {amorces}")

# b bis) Les fragments de code cités dans une phrase (« Verbatim Char ») étaient
#    composés en 6,5 pt au milieu d'un texte à 11 pt : un corps de différence si
#    marqué qu'il se lisait mal. Ramenés à 8,5 pt, ils restent distincts du texte
#    courant sans être minuscules.
if "Verbatim Char" in STYLES:
    STYLES["Verbatim Char"].font.size = Pt(8.5)

# b) Une seule police pour tout le texte. La trame compose les titres en
#    « Calibri Light » et le corps en « Calibri » : deux graisses de dessin
#    différentes. Les titres passent sur la police du corps.
polices = cible.styles.element.find(qn("w:docDefaults"))
for st in cible.styles.element.findall(qn("w:style")):
    sid = st.get(qn("w:styleId")) or ""
    if not (sid.startswith(("Titre", "Heading", "Title", "Subtitle"))
            or sid in ("TOCHeading", "Sommaire")):
        continue
    rpr = st.find(qn("w:rPr"))
    if rpr is None:
        continue
    for rf in rpr.findall(qn("w:rFonts")):
        for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rf.get(qn(att)) and "major" in rf.get(qn(att)):
                rf.set(qn(att), rf.get(qn(att)).replace("major", "minor"))

# ─────────────────── 10 ter. blocs de code en images ──────────────────────
# Chaque bloc de code est remplacé par son rendu en image, commentaires
# retirés, produit par code_images.py. L'intérêt est une composition
# identique d'un bloc à l'autre, quelle que soit la police d'origine du
# document source. Un bloc trop haut pour une page est rendu en plusieurs
# images, qui se suivent.
import hashlib
from code_nettoyage import nettoyer
IDX = f"{FIG}/code/index.json"
if os.path.exists(IDX):
    manifeste = json.load(open(IDX))
    k = W_FIG / manifeste["largeur_reference_css"]      # cm par pixel CSS
    blocs = manifeste["blocs"]
    poses = introuvables = 0
    for par in list(cible.paragraphs):
        if par.style.name != "Source Code":
            continue
        emp = hashlib.md5(nettoyer(par.text).encode("utf-8")).hexdigest()[:12]
        images = blocs.get(emp)
        if not images:
            introuvables += 1
            continue
        precedent = par._p
        for n, img in enumerate(images):
            largeur = min(W_FIG, img["largeur_css"] * k)
            if n == 0:
                vider(par)
                par.style = STYLES["Figure"]
                par.alignment = 0
                par.paragraph_format.space_before = Pt(4)
                par.paragraph_format.space_after = Pt(2)
                par.add_run().add_picture(f"{FIG}/code/{img['fichier']}",
                                          width=Cm(largeur))
                precedent = par._p
            else:
                el = OxmlElement("w:p")
                precedent.addnext(el)
                suite = Paragraph(el, par._parent)
                suite.style = STYLES["Figure"]
                suite.alignment = 0
                suite.paragraph_format.space_before = Pt(2)
                suite.paragraph_format.space_after = Pt(2)
                suite.add_run().add_picture(f"{FIG}/code/{img['fichier']}",
                                            width=Cm(largeur))
                precedent = el
            poses += 1
    print(f"  blocs de code en images : {poses}"
          + (f" | SANS IMAGE : {introuvables}" if introuvables else ""))
else:
    print("  !! fig/code/index.json absent : lancer code_images.py")

# ─────────────────── 11. mise à jour des champs à l'ouverture ──────────────
# La table des matières de la trame est un champ : sans cette instruction, elle
# reste figée sur les numéros de page de la trame vide (tous à zéro).
reglages = cible.settings.element
if reglages.find(qn("w:updateFields")) is None:
    maj = OxmlElement("w:updateFields")
    maj.set(qn("w:val"), "true")
    reglages.append(maj)

# ─────────────────── 12. sommaire ─────────────────────────────────────────
# Le sommaire de la trame est un champ dont le résultat est mémorisé. Il ne
# listait que les cinq parties portant un style de titre, et ses numéros de
# page étaient ceux de la trame vide. Le résultat mémorisé est reconstruit :
# les douze parties, leurs sous-parties, et la pagination relevée sur le PDF.
# Les délimiteurs du champ sont conservés, pour qu'un rafraîchissement dans
# Word reste possible.

if PAGES:
    for sdt in cible.element.body.iter(qn("w:sdt")):
        if not any("TOC" in (t.text or "") for t in sdt.iter(qn("w:instrText"))):
            continue
        entrees = [e for e in sdt.iter(qn("w:p"))]
        premiere, derniere = entrees[1], entrees[-1]
        style_entree = premiere.pPr.find(qn("w:pStyle")).get(qn("w:val"))

        from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER

        def taquets(par):
            """Un taquet pour le titre, un taquet de droite pointillé pour la
            page. Les taquets hérités du style placent mal les numéros à cinq
            caractères comme « 12.1. »."""
            pf = par.paragraph_format
            pf.left_indent = Cm(1.3)
            pf.first_line_indent = Cm(-1.3)
            for t in list(pf.tab_stops):
                pass
            tabs = par._p.get_or_add_pPr().find(qn("w:tabs"))
            if tabs is not None:
                par._p.pPr.remove(tabs)
            pf.tab_stops.add_tab_stop(Cm(1.3), WD_TAB_ALIGNMENT.LEFT)
            pf.tab_stops.add_tab_stop(Cm(17), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

        def ligne(numero, titre, page, modele):
            el = copy.deepcopy(modele)
            for enfant in list(el):
                if enfant.tag != qn("w:pPr"):
                    el.remove(enfant)
            par = Paragraph(el, None)
            taquets(par)
            par.add_run(f"{numero}\t{titre}\t{page}")
            return el

        # Les entrées intermédiaires sont remplacées ; la première porte
        # l'ouverture du champ, la dernière sa fermeture.
        for e in entrees[2:-1]:
            e.getparent().remove(e)
        for enfant in list(premiere):
            if enfant.tag not in (qn("w:pPr"), qn("w:r")):
                premiere.remove(enfant)

        modele = copy.deepcopy(premiere)
        for enfant in list(modele):
            if enfant.tag != qn("w:pPr"):
                modele.remove(enfant)

        num0, titre0 = SOMMAIRE[0]
        par0 = Paragraph(premiere, None)
        taquets(par0)
        par0.add_run(f"{num0}\t{titre0}\t{PAGES.get(titre0, '')}")
        precedent = premiere
        for numero, titre in SOMMAIRE[1:]:
            el = ligne(numero, titre, PAGES.get(titre, ""), modele)
            precedent.addnext(el)
            precedent = el
        print(f"  sommaire reconstruit : {len(SOMMAIRE)} entr\u00e9es")
        break

# Apostrophes : le texte source emploie l'apostrophe droite d'un bout à l'autre.
# Les quelques paragraphes rédigés pour ce remplissage utilisaient l'apostrophe
# typographique ; on les aligne. Les titres, repris mot pour mot du référentiel,
# gardent la leur.
vu_titre = False
for par in cible.paragraphs:
    if (par.style.name or "").startswith("Heading") and par.text.strip():
        vu_titre = True
        continue
    if not vu_titre or (par.style.name or "").startswith("Heading"):
        continue
    for r in par.runs:
        if "’" in r.text:
            r.text = r.text.replace("’", "'")


# ───────────────────────── marges ─────────────────────────────────────────
# 2 cm au lieu des 2,5 cm de la trame : six pages de corps regagnées sans
# retirer une ligne de texte.
for sec in cible.sections:
    sec.top_margin = sec.bottom_margin = Cm(2)
    sec.left_margin = sec.right_margin = Cm(2)

# ───────────────────────── numérotation des pages ─────────────────────────
# La trame redémarre la numérotation à zéro à chaque section : correct pour un
# document d'une page par section, mais ici la couverture portait « 0 » et le
# corps repartait de « 0 » à la page 3, alors que le sommaire renvoie aux pages
# réelles. Numérotation continue à partir de 1, et aucun numéro sur la
# couverture.
for i, sec in enumerate(cible.sections):
    sp = sec._sectPr
    for pn in sp.findall(qn("w:pgNumType")):
        if i == 0:
            pn.set(qn("w:start"), "1")
        else:
            sp.remove(pn)
pied = cible.sections[0].first_page_footer
for par in pied.paragraphs:
    for child in list(par._p):
        if child.tag != qn("w:pPr"):
            par._p.remove(child)

cible.save(SORTIE)
print("rempli :", SORTIE)
