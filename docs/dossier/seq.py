# -*- coding: utf-8 -*-
"""
Diagramme de séquence — générateur.

Trois défauts de la version précédente sont corrigés ici.

1. Les libellés, centrés sur la flèche, débordaient largement des colonnes et
   traversaient les lignes de vie voisines. Le générateur mesure maintenant
   chaque libellé : il réduit le corps, puis coupe sur un mot, jusqu'à ce que
   le texte tienne dans l'écart entre les deux participants.
2. L'ordre était faux. Le code crée l'entrée du journal AVANT d'appeler le
   modèle — pour disposer de son identifiant — et l'annule si l'appel échoue.
   La figure montrait l'écriture après la réponse.
3. Rien ne guidait la lecture : pas de numéro d'étape, pas de barre
   d'activation, aucun regroupement. On a maintenant une gouttière numérotée,
   des barres d'activation et trois phases nommées.
"""
import re

PAL = dict(encre="#111111", parch="#F4F1EA", surf="#FFFFFF", bord="#CFC9BC",
           brique="#C4341C", gris="#5A554C", gris2="#8C867A")

# ── participants : (libellé, sous-titre) ─────────────────────────────────────
PARTS = [
    ("Utilisateur",        "acteur"),
    ("Éditeur",            "navigateur — Vue 3"),
    ("Route IA",           "couche présentation"),
    ("Service IA",         "couche métier"),
    ("Accès aux données",  "couche persistance"),
    ("Ollama",             "service local"),
]
U, E, R, S, D, O_ = range(6)

# ── messages : (de, vers, libellé, nature) ───────────────────────────────────
# nature : "app" appel · "ret" retour · "err" sortie en erreur · "self" interne
MSGS = [
    (U, E,  "sélectionne un passage, choisit une action",            "app"),
    (E, R,  "POST /documents/:id/ia/generer",                        "app"),
    (R, R,  "vérifie le jeton d'accès",                              "self"),
    (R, R,  "valide type_action et scope par liste blanche",          "self"),
    (R, R,  "borne la taille du contenu et des instructions",         "self"),
    (R, D,  "SELECT document WHERE identifiant ET propriétaire",      "app"),
    (D, R,  "le document, ou rien",                                   "ret"),
    (R, E,  "404 si le document n'est pas le sien",                    "err"),
    (R, D,  "COUNT des générations depuis maintenant moins 24 heures", "app"),
    (D, R,  "le compteur, et la limite du compte",                    "ret"),
    (R, E,  "429 si le quota des 24 heures est atteint",               "err"),
    (R, D,  "INSERT ia (contenu avant) puis flush — obtient id_ia",   "app"),
    (R, S,  "compose le prompt depuis le gabarit de l'action",        "app"),
    (S, O_, "POST /api/chat — température propre à l'action",         "app"),
    (O_, S, "texte généré et jetons consommés",                       "ret"),
    (S, R,  "contenu après, jetons",                                  "ret"),
    (R, D,  "ROLLBACK si le modèle n'a pas répondu",                  "err"),
    (R, E,  "502 si le modèle n'a pas répondu — rien n'est conservé",  "err"),
    (R, D,  "UPDATE contenu après, jetons, puis COMMIT",              "app"),
    (R, E,  "201 — id_ia, contenu après, jetons",                     "ret"),
    (E, U,  "affiche la proposition dans une zone distincte",         "ret"),
    (U, E,  "insère, remplace, ou ignore",                            "app"),
]

# ── phases : (premier message, dernier message, nom) ─────────────────────────
PHASES = [(2, 10, "LES CONTRÔLES, DU MOINS AU PLUS COÛTEUX"),
          (11, 15, "LA GÉNÉRATION"),
          (16, 19, "TRAÇABILITÉ ET ÉCHEC")]

# ── géométrie ────────────────────────────────────────────────────────────────
GUT, GNUM = 24, 62          # gouttière : nom de phase, puis numéro d'étape
X0, GAP, BOXW = 190, 230, 190
TOPY, BOXH = 58, 44
Y0, STEP = 126, 28
XS = [X0 + i * GAP for i in range(len(PARTS))]
W = XS[-1] + BOXW // 2 + 24
HT = Y0 + len(MSGS) * STEP + 46

# largeur moyenne d'un caractère Inter, par corps
LARG = {9.0: 4.75, 8.2: 4.33, 7.5: 3.96}


def ajuste(txt, dispo):
    """Rend (lignes, corps) tels que chaque ligne tienne dans `dispo`."""
    for fs in (9.0, 8.2, 7.5):
        if len(txt) * LARG[fs] <= dispo:
            return [txt], fs
    fs = 8.2
    mots, lignes, cur = txt.split(" "), [], ""
    for m in mots:
        essai = (cur + " " + m).strip()
        if len(essai) * LARG[fs] > dispo and cur:
            lignes.append(cur)
            cur = m
        else:
            cur = essai
    lignes.append(cur)
    return lignes, (fs if max(len(l) for l in lignes) * LARG[fs] <= dispo else 7.5)


o = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
     'font-family="Inter, sans-serif">' % (W, HT)]
o.append("<!-- généré par docs/dossier/seq.py — ne pas éditer à la main -->")
o.append("""<defs>
  <marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7.5" markerHeight="7.5"
          orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{encre}"/></marker>
  <marker id="fr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8"
          orient="auto"><path d="M0,1.5 L10,5 L0,8.5" fill="none" stroke="{gris}"
          stroke-width="1.4"/></marker>
  <marker id="fe" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7.5" markerHeight="7.5"
          orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{brique}"/></marker>
</defs>
<style>
  .boite {{ fill:{encre} }}
  .pnom  {{ font-size:9.8px; font-weight:700; fill:#FFFFFF }}
  .psub  {{ font-size:8.2px; fill:#B8B2A6 }}
  .vie   {{ stroke:{bord}; stroke-width:1; stroke-dasharray:4 4 }}
  .actif {{ fill:{parch}; stroke:{gris2}; stroke-width:.9 }}
  .phase {{ fill:{parch}; stroke:none }}
  .ptit  {{ font-size:8px; font-weight:700; fill:{gris}; letter-spacing:.8px }}
  .num   {{ font-size:8.4px; font-weight:700; fill:{gris} }}
  .pastille {{ fill:#FFFFFF; stroke:{bord}; stroke-width:1 }}
  .app   {{ stroke:{encre}; stroke-width:1.3; fill:none }}
  .ret   {{ stroke:{gris}; stroke-width:1.1; stroke-dasharray:5 3; fill:none }}
  .err   {{ stroke:{brique}; stroke-width:1.4; fill:none }}
  .lapp  {{ fill:{encre} }}
  .lret  {{ fill:{gris} }}
  .lerr  {{ fill:{brique}; font-weight:600 }}
</style>""".format(**PAL))

# phases, en fond
for a, b, nom in PHASES:
    y1, y2 = Y0 + a * STEP - 19, Y0 + b * STEP + 9
    o.append('<rect class="phase" x="%d" y="%d" width="%d" height="%d" rx="4"/>'
             % (GUT - 6, y1, W - GUT - 18, y2 - y1))
    o.append('<rect fill="%s" x="%d" y="%d" width="3" height="%d" rx="1.5"/>'
             % (PAL["brique"], GUT - 6, y1, y2 - y1))
    o.append('<text class="ptit" x="%d" y="%d" transform="rotate(-90 %d %d)" '
             'text-anchor="middle">%s</text>'
             % (GUT + 7, (y1 + y2) // 2, GUT + 7, (y1 + y2) // 2, nom))

# lignes de vie, sous les barres d'activation
for i, x in enumerate(XS):
    o.append('<line class="vie" x1="%d" y1="%d" x2="%d" y2="%d"/>'
             % (x, TOPY + BOXH, x, HT - 32))

# barres d'activation : du premier au dernier message qui touche le participant
for i in range(len(PARTS)):
    ys = [Y0 + k * STEP for k, (a, b, _, _) in enumerate(MSGS) if a == i or b == i]
    if len(ys) > 1:
        o.append('<rect class="actif" x="%d" y="%d" width="8" height="%d" rx="2"/>'
                 % (XS[i] - 4, min(ys) - 6, max(ys) - min(ys) + 12))

# en-têtes
for i, (nom, sub) in enumerate(PARTS):
    x = XS[i]
    o.append('<rect class="boite" x="%d" y="%d" width="%d" height="%d" rx="4"/>'
             % (x - BOXW // 2, TOPY, BOXW, BOXH))
    o.append('<text class="pnom" x="%d" y="%d" text-anchor="middle">%s</text>' % (x, TOPY + 19, nom))
    o.append('<text class="psub" x="%d" y="%d" text-anchor="middle">%s</text>' % (x, TOPY + 33, sub))

# messages
for k, (a, b, lab, kind) in enumerate(MSGS):
    y = Y0 + k * STEP
    cl = {"app": "app", "ret": "ret", "err": "err", "self": "app"}[kind]
    tc = {"app": "lapp", "ret": "lret", "err": "lerr", "self": "lapp"}[kind]
    mk = {"app": "fa", "ret": "fr", "err": "fe", "self": "fa"}[kind]

    o.append('<circle class="pastille" cx="%d" cy="%d" r="9"/>' % (GNUM, y))
    o.append('<text class="num" x="%d" y="%d" text-anchor="middle">%d</text>' % (GNUM, y + 3, k + 1))

    if a == b:  # appel interne
        x = XS[a]
        o.append('<path class="%s" d="M%d,%d H%d V%d H%d" marker-end="url(#%s)"/>'
                 % (cl, x, y - 9, x + 30, y + 5, x + 3, mk))
        lignes, fs = ajuste(lab, GAP - 54)
        for j, l in enumerate(lignes):
            o.append('<text class="%s" x="%d" y="%.0f" font-size="%s">%s</text>'
                     % (tc, x + 38, y + 3 - (len(lignes) - 1 - j) * 10 - (0 if len(lignes) == 1 else -4), fs, l))
        continue

    x1, x2 = XS[a], XS[b]
    o.append('<line class="%s" x1="%d" y1="%d" x2="%d" y2="%d" marker-end="url(#%s)"/>'
             % (cl, x1, y, x2, y, mk))
    lignes, fs = ajuste(lab, abs(x2 - x1) - 14)
    for j, l in enumerate(lignes):
        o.append('<text class="%s" x="%d" y="%.0f" font-size="%s" text-anchor="middle">%s</text>'
                 % (tc, (x1 + x2) // 2, y - 8 - (len(lignes) - 1 - j) * 10, fs, l))

o.append('<text x="%d" y="%d" font-size="8.8" fill="%s">Les étapes 12 et 17 vont '
         'ensemble : l\'entrée du journal est créée avant l\'appel, pour que la réponse '
         'porte son identifiant ; si le modèle ne répond pas, elle est annulée. Un échec '
         'ne coûte donc aucun quota.</text>' % (GUT, HT - 14, PAL["gris"]))
o.append("</svg>")

open("/home/user/HelpMeDraft---projet-fil-rouge/docs/dossier/seq-uc10.svg", "w").write("\n".join(o))
print("seq-uc10.svg écrit — %dx%d, ratio %.3f" % (W, HT, W / HT))
