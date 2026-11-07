# -*- coding: utf-8 -*-
"""
Diagramme des cas d'utilisation — générateur.

La version précédente tirait un trait de chaque acteur vers chacun des
dix-huit cas : une trentaine de lignes grises qui se croisaient, et aucune
hiérarchie. Ici c'est la BANDE qui porte l'acteur. Un acteur, un trait, une
bande ; l'héritage est dessiné une seule fois sur la gauche. À l'intérieur de
la bande de l'utilisateur, les cas sont regroupés par thème — mes documents,
l'assistance IA, ma session — ce qui donne à l'œil une structure au lieu
d'une grille. Les deux cas inclus sont sortis dans une bande à eux, en
pointillé, avec la liste de ce qui les inclut écrite sous l'ovale : une
phrase remplace huit flèches.
"""

PAL = dict(
    encre="#111111", parch="#F4F1EA", bord="#CFC9BC", surf="#FFFFFF",
    brique="#C4341C", gris="#5A554C", gris2="#8C867A",
)

# ── géométrie ────────────────────────────────────────────────────────────────
W, HT = 1180, 636
BX, BY, BW = 150, 18, 862          # cadre du système
IX, IW = BX + 12, BW - 24          # intérieur utile : 162 → 1000

o = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
     'font-family="Inter, sans-serif">' % (W, HT)]
o.append("<!-- généré par docs/dossier/usecase.py — ne pas éditer à la main -->")
o.append("""<style>
  .cadre {{ fill:none; stroke:{encre}; stroke-width:1.4 }}
  .sys   {{ font-size:10.5px; font-weight:700; fill:{encre}; letter-spacing:1.4px }}
  .bande {{ fill:{parch}; stroke:{bord}; stroke-width:1 }}
  .btit  {{ font-size:9.6px; font-weight:700; fill:{encre}; letter-spacing:.9px }}
  .bsub  {{ font-size:8.6px; fill:{gris} }}
  .grp   {{ fill:{surf}; stroke:{bord}; stroke-width:1 }}
  .gtit  {{ font-size:8.6px; font-weight:700; fill:{gris}; letter-spacing:.7px }}
  .cas   {{ fill:{surf}; stroke:{encre}; stroke-width:1.1 }}
  .cle   {{ fill:#FBEEEA; stroke:{brique}; stroke-width:2 }}
  .cas2  {{ fill:none; stroke:{gris}; stroke-width:1; stroke-dasharray:4 3 }}
  .ucid  {{ font-weight:700; fill:{brique} }}
  .lib   {{ font-size:9.4px; fill:{encre} }}
  .incl  {{ font-size:8.2px; fill:{gris}; font-style:italic }}
  .act   {{ fill:none; stroke:{encre}; stroke-width:1.6 }}
  .anom  {{ font-size:10px; font-weight:700; fill:{encre} }}
  .ext   {{ fill:none; stroke:{gris}; stroke-width:1.5 }}
  .enom  {{ font-size:9.4px; font-weight:700; fill:{gris} }}
  .esub  {{ font-size:8.2px; fill:{gris2} }}
  .lien  {{ stroke:{encre}; stroke-width:1 }}
  .lienx {{ stroke:{gris}; stroke-width:1 }}
  .her   {{ fill:none; stroke:{gris}; stroke-width:1.1; stroke-dasharray:5 3 }}
  .hlab  {{ font-size:8px; fill:{gris}; letter-spacing:.4px }}
  .pied  {{ font-size:8.8px; fill:{gris} }}
</style>""".format(**PAL))

o.append('<rect class="cadre" x="%d" y="%d" width="%d" height="%d" rx="6"/>'
         % (BX, BY, BW, 596 - BY))
o.append('<text class="sys" x="%d" y="%d">SYSTÈME HELPMEDRAFT</text>' % (BX + 12, BY + 20))


def bande(y, h, titre, sous, w=IW, x=IX):
    o.append('<rect class="bande" x="%d" y="%d" width="%d" height="%d" rx="5"/>'
             % (x, y, w, h))
    o.append('<text class="btit" x="%d" y="%d">%s</text>' % (x + 12, y + 17, titre))
    if sous:
        o.append('<text class="bsub" x="%d" y="%d" text-anchor="end">%s</text>'
                 % (x + w - 12, y + 17, sous))


def groupe(x, y, w, h, titre):
    o.append('<rect class="grp" x="%d" y="%d" width="%d" height="%d" rx="4"/>' % (x, y, w, h))
    o.append('<text class="gtit" x="%d" y="%d">%s</text>' % (x + 11, y + 16, titre))


def cas(cx, cy, rx, code, lib, cle=False, pointille=False, fs=9.4):
    cl = "cle" if cle else ("cas2" if pointille else "cas")
    o.append('<ellipse class="%s" cx="%d" cy="%d" rx="%d" ry="18"/>' % (cl, cx, cy, rx))
    o.append('<text class="lib" x="%d" y="%d" font-size="%s" text-anchor="middle">'
             '<tspan class="ucid">%s</tspan>  %s</text>' % (cx, cy + 3, fs, code, lib))


def acteur(cx, ya, nom, ext=False, sous=None):
    c = "ext" if ext else "act"
    o.append('<circle class="%s" cx="%d" cy="%d" r="9"/>' % (c, cx, ya - 18))
    o.append('<path class="%s" d="M%d,%d V%d M%d,%d H%d M%d,%d L%d,%d M%d,%d L%d,%d"/>'
             % (c, cx, ya - 9, ya + 14, cx - 13, ya, cx + 13,
                cx, ya + 14, cx - 11, ya + 30, cx, ya + 14, cx + 11, ya + 30))
    o.append('<text class="%s" x="%d" y="%d" text-anchor="middle">%s</text>'
             % ("enom" if ext else "anom", cx, ya + 46, nom))
    if sous:
        o.append('<text class="esub" x="%d" y="%d" text-anchor="middle">%s</text>'
                 % (cx, ya + 60, sous))


# ── bande 1 : le visiteur ────────────────────────────────────────────────────
bande(48, 102, "SANS COMPTE", "ce qu'un visiteur peut faire")
for i, (code, lib) in enumerate([
        ("UC-01", "S'inscrire"), ("UC-02", "Se connecter"),
        ("UC-14", "Pages vitrine et légales"), ("UC-04", "Mot de passe oublié")]):
    cas(IX + IW * (2 * i + 1) // 8, 114, 100, code, lib, fs=9.0)

# ── bande 2 : l'utilisateur authentifié ──────────────────────────────────────
bande(162, 296, "AVEC UN COMPTE", "hérite de tout ce qui précède")
groupe(IX, 188, 494, 258, "MES DOCUMENTS")
for i, (code, lib) in enumerate([
        ("UC-05", "Créer un document"), ("UC-06", "Rédiger un document"),
        ("UC-07", "Consulter ses documents"), ("UC-13", "Organiser en dossiers"),
        ("UC-08", "Enregistrer automatiquement"), ("UC-09", "Supprimer un document")]):
    cas(IX + 124 + (i % 2) * 247, 252 + (i // 2) * 80, 115, code, lib, fs=8.8)

groupe(IX + 506, 188, 332, 184, "ASSISTANCE IA")
for i, (code, lib, cle) in enumerate([
        ("UC-10", "Demander une suggestion", True),
        ("UC-11", "Appliquer une suggestion", False),
        ("UC-12", "Consulter l'historique", False)]):
    cas(IX + 672, 239 + i * 50, 150, code, lib, cle=cle, fs=9.0)

groupe(IX + 506, 384, 332, 62, "MA SESSION")
cas(IX + 672, 424, 150, "UC-03", "Se déconnecter", fs=9.0)

# ── bas de figure : les deux bandes secondaires, côte à côte ────────────────
DW = (IW - 14) // 2                      # demi-largeur
bande(470, 96, "ADMINISTRATEUR", "hérite de tout", w=DW)
for i, (code, lib) in enumerate([("UC-15", "Gérer les comptes"),
                                 ("UC-16", "Consulter les statistiques")]):
    cas(IX + DW * (2 * i + 1) // 4, 532, 97, code, lib, fs=8.2)

bande(470, 96, "CAS INCLUS", "jamais déclenchés seuls", w=DW, x=IX + DW + 14)
for i, (code, lib, par) in enumerate([
        ("UC-17", "Vérifier le quota", "par UC-10"),
        ("UC-18", "S'authentifier", "par UC-05 à UC-10, UC-13")]):
    cx = IX + DW + 14 + DW * (2 * i + 1) // 4
    cas(cx, 524, 97, code, lib, pointille=True, fs=8.2)
    o.append('<text class="incl" x="%d" y="556" text-anchor="middle">&#171; include &#187; %s</text>'
             % (cx, par))

# ── acteurs, un trait par bande ──────────────────────────────────────────────
for ya, nom in [(114, "Visiteur"), (310, "Utilisateur"), (518, "Administrateur")]:
    acteur(70, ya, nom)
    o.append('<line class="lien" x1="84" y1="%d" x2="%d" y2="%d"/>' % (ya, BX, ya))

# héritage, dessiné une fois
o.append('<path class="her" d="M56,518 H34 V310 H50"/>')
o.append('<polygon points="50,304 62,310 50,316" fill="%s" stroke="%s" stroke-width="1.1"/>'
         % (PAL["parch"], PAL["gris"]))
o.append('<path class="her" d="M56,310 H44 V114 H50"/>')
o.append('<polygon points="50,108 62,114 50,120" fill="%s" stroke="%s" stroke-width="1.1"/>'
         % (PAL["parch"], PAL["gris"]))
o.append('<text class="hlab" x="26" y="420" transform="rotate(-90 26 420)" '
         'text-anchor="middle">hérite</text>')

# ── systèmes externes ────────────────────────────────────────────────────────
acteur(1096, 114, "Messagerie", ext=True, sous="SMTP")
o.append('<line class="lienx" x1="995" y1="114" x2="1083" y2="114"/>')
acteur(1096, 239, "Inférence", ext=True, sous="Ollama, en local")
o.append('<line class="lienx" x1="984" y1="239" x2="1083" y2="239"/>')

# ── notes ────────────────────────────────────────────────────────────────────
o.append('<text class="pied" x="%d" y="620">UC-10, en brique, traverse les trois couches '
         'et sollicite un service externe : c\'est le cas que détaille le diagramme de '
         'séquence. Les systèmes externes ne sont jamais appelés par le navigateur.</text>'
         % BX)
o.append("</svg>")

open("/home/user/HelpMeDraft---projet-fil-rouge/docs/dossier/usecase.svg", "w").write("\n".join(o))
print("usecase.svg écrit — ratio %.3f" % (W / HT))
