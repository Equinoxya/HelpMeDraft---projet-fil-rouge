"""
Rendu d'un document en PDF, pour l'export des documents terminés.

CHAÎNE DE RENDU : Markdown -> HTML -> PDF.

Le détour par HTML n'est pas une complication gratuite. Le document est écrit
en Markdown et l'éditeur en montre déjà un rendu HTML ; produire le PDF depuis
la même représentation est le seul moyen d'obtenir un fichier qui ressemble à
ce que l'utilisateur a relu avant de cliquer. Composer le PDF primitive par
primitive, comme le ferait une bibliothèque de dessin, obligerait à
réimplémenter la mise en forme des titres, des listes et des tableaux — et à la
maintenir en parallèle de celle de l'aperçu, avec la dérive que cela promet.

CE MODULE NE CONNAÎT NI FLASK NI LA BASE. Il reçoit un titre et du Markdown,
il rend des octets. C'est ce qui permet de le tester sans monter l'application
ni écrire en base.
"""

from datetime import datetime

import markdown
from weasyprint import HTML

# Extensions Markdown activées, et uniquement celles qui servent au rendu des
# documents que l'application produit :
#
#   tables      — les tableaux de l'éditeur ; sans elle, « | Champ | Valeur | »
#                 sort tel quel, en texte brut avec ses barres verticales ;
#   fenced_code — les blocs délimités par trois accents graves, que le bouton
#                 « Code » de la barre d'outils insère. Python-Markdown ne
#                 reconnaît sans elle que les blocs INDENTÉS de quatre espaces :
#                 un bloc de code de l'éditeur sortait donc en texte courant,
#                 accents graves compris. Un test l'a révélé ;
#   nl2br       — un saut de ligne simple devient <br>, comme dans l'aperçu
#                 (marked est configuré avec breaks: true, voir MarkdownEditor) ;
#   sane_lists  — une liste qui suit un paragraphe sans ligne vide est reconnue,
#                 ce que le Markdown d'origine refuse et que personne n'attend.
EXTENSIONS = ["tables", "fenced_code", "nl2br", "sane_lists"]

# Feuille de style du document exporté.
#
# Reprend la charte de l'application — Georgia pour les titres, le rouge de
# l'interface pour les filets — sans dépendre d'une police à télécharger : la
# génération se fait côté serveur, sans accès réseau, et une @font-face
# injoignable ferait retomber tout le document sur une police de secours.
#
# @page porte la marge et le pied de page. Le numéro de page vient de
# `counter(page)`, que WeasyPrint sait résoudre et qu'aucun traitement de texte
# n'aurait donné sans intervention manuelle.
FEUILLE_DE_STYLE = """
@page {
    size: A4;
    margin: 2.5cm 2cm 2cm 2cm;

    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-family: "DejaVu Serif", Georgia, "Times New Roman", serif;
        font-size: 9pt;
        color: #666666;
    }
}

body {
    /* DejaVu Serif EN TÊTE, et non Georgia. Georgia n'est pas libre et n'est
       installée sur aucune image Debian : la nommer en premier laissait
       WeasyPrint retomber sur la police de secours du système, qui diffère
       d'une machine à l'autre — le PDF n'était donc pas reproductible. DejaVu
       est celle qu'installe backend/Dockerfile. Les suivantes ne servent qu'à
       un poste de développement qui ne l'aurait pas. */
    font-family: "DejaVu Serif", Georgia, "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #111111;
}

/* En-tête du document : titre et date d'export, séparés du corps par un filet,
   pour qu'un PDF sorti de l'application se reconnaisse d'un coup d'œil. */
.entete {
    border-bottom: 2px solid #111111;
    padding-bottom: 0.6cm;
    margin-bottom: 1cm;
}
.entete h1 {
    font-family: "DejaVu Serif", Georgia, "Times New Roman", serif;
    font-size: 20pt;
    margin: 0 0 0.2cm 0;
    page-break-after: avoid;
}
.entete .date {
    font-size: 9pt;
    color: #666666;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: bold;
    margin: 0.8em 0 0.4em 0;
    /* Un titre seul en bas de page, son texte à la page suivante, est le
       défaut le plus visible d'un PDF généré. */
    page-break-after: avoid;
}
h1 { font-size: 17pt; }
h2 { font-size: 14pt; }
h3 { font-size: 12pt; }

p { margin: 0.4em 0; }

/* Trois lignes orphelines ou veuves suffisent à rendre un document bancal. */
p, li { orphans: 2; widows: 2; }

ul, ol { margin: 0.4em 0; padding-left: 1.2cm; }
li { margin: 0.15em 0; }

a { color: #c4341c; }

blockquote {
    border-left: 3px solid #c4341c;
    padding-left: 0.5cm;
    margin: 0.5em 0 0.5em 0;
    color: #444444;
    font-style: italic;
}

code {
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 9.5pt;
    background: #f0f0f0;
    padding: 0 2px;
}
pre {
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 9pt;
    background: #f5f5f5;
    padding: 0.3cm;
    /* Le bloc de code ne se coupe pas au milieu si la place le permet. */
    page-break-inside: avoid;
    white-space: pre-wrap;
}
pre code { background: none; padding: 0; }

table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.5em 0;
    font-size: 10pt;
}
th, td {
    border: 1px solid #999999;
    padding: 0.15cm 0.25cm;
    text-align: left;
    vertical-align: top;
}
th { background: #f0f0f0; font-weight: bold; }
/* Une ligne de tableau coupée entre deux pages est illisible. */
tr { page-break-inside: avoid; }

hr { border: none; border-top: 1px solid #111111; margin: 0.8em 0; }

img { max-width: 100%; }
"""

MOIS = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


def _date_en_toutes_lettres(moment: datetime) -> str:
    """« 3 novembre 2026 », sans dépendre de la locale du système.

    `strftime("%d %B %Y")` rendrait « November » sur un conteneur dont la locale
    n'est pas installée — et elle ne l'est pas sur python:3.11-slim.
    """
    return f"{moment.day} {MOIS[moment.month - 1]} {moment.year}"


def _echapper(texte: str) -> str:
    """Échappement HTML du titre, qui n'est PAS du Markdown.

    Le titre est saisi librement par l'utilisateur et inséré dans le gabarit.
    Sans échappement, un titre contenant « <script> » ou simplement « R&D »
    casserait le document — au mieux. La bibliothèque Markdown échappe déjà le
    corps ; le titre, lui, ne passe pas par elle.
    """
    return (
        texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def construire_html(titre: str, contenu: str | None, exporte_le: datetime | None = None) -> str:
    """
    Compose le HTML intermédiaire, avant passage au moteur de rendu.

    SÉPARÉE DU RENDU POUR ÊTRE VÉRIFIABLE. Le texte d'un PDF est compressé : y
    chercher une chaîne ne prouve rien, et les premiers tests écrits ainsi
    échouaient sans que le rendu soit en cause. L'échappement du titre, la date
    en français et l'interprétation du Markdown se vérifient ici, sur du texte
    lisible ; le rendu, lui, se vérifie à ce qu'il produise un PDF valide.
    """
    moment = exporte_le or datetime.now()

    corps = markdown.markdown(contenu or "", extensions=EXTENSIONS)

    return f"""<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>{_echapper(titre)}</title>
<style>{FEUILLE_DE_STYLE}</style></head>
<body>
<header class="entete">
    <h1>{_echapper(titre)}</h1>
    <p class="date">Exporté le {_date_en_toutes_lettres(moment)}</p>
</header>
{corps}
</body>
</html>"""


def rendre_document(titre: str, contenu: str | None, exporte_le: datetime | None = None) -> bytes:
    """
    Rend un document en PDF et renvoie ses octets.

    `contenu` peut être vide : un document terminé sans corps reste exportable,
    et le PDF porte alors son en-tête seul. Renvoyer une erreur obligerait
    l'interface à traiter un cas que l'utilisateur ne comprendrait pas — son
    document existe, il est marqué terminé, et l'export échouerait.
    """
    # base_url laissé à None, et c'est délibéré : sans lui, WeasyPrint ne
    # résout aucune URL relative, donc aucune lecture de fichier local. Le
    # contenu vient de l'utilisateur ; lui donner une racine permettrait à une
    # balise <img src="/etc/passwd"> de faire lire ce fichier au serveur pour
    # l'embarquer dans le PDF.
    return HTML(string=construire_html(titre, contenu, exporte_le)).write_pdf()


def nom_de_fichier(titre: str, exporte_le: datetime | None = None) -> str:
    """
    Nom du fichier proposé au téléchargement, dérivé du titre.

    Le titre est saisi librement : il peut contenir des barres obliques, des
    deux-points ou des caractères que Windows refuse, et il finirait dans un
    en-tête HTTP. On n'en garde que des caractères sûrs, et la date suffit à
    distinguer deux exports du même document.
    """
    moment = exporte_le or datetime.now()

    base = "".join(c if c.isalnum() or c in " -_" else "-" for c in (titre or "").strip())
    # Les séparatifs consécutifs produits par le remplacement sont réduits, et
    # les espaces deviennent des tirets : un nom de fichier sans espace se
    # manipule sans guillemets en ligne de commande.
    base = "-".join(morceau for morceau in base.replace(" ", "-").split("-") if morceau)
    base = base[:60] or "document"

    return f"{base}-{moment:%Y-%m-%d}.pdf"
