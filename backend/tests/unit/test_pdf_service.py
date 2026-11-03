"""
Tests unitaires du rendu PDF — app/services/pdf_service.py.

Le module ne connaît ni Flask ni la base : il reçoit un titre et du Markdown,
il rend des octets. Ces tests l'exercent donc directement, sans application ni
écriture en base.

CE QUI EST VÉRIFIÉ ICI, ET CE QUI NE L'EST PAS. On vérifie qu'un PDF valide
sort, que le Markdown a bien été interprété, et que le titre de l'utilisateur ne
peut pas casser le document. On ne vérifie PAS la mise en page : la position
d'un filet ou la graisse d'un titre relèvent de la relecture visuelle, et un
test qui les figerait casserait au premier ajustement de la feuille de style
sans rien signaler d'utile.
"""

from datetime import datetime

import pytest

from app.services.pdf_service import (
    EXTENSIONS,
    construire_html,
    nom_de_fichier,
    rendre_document,
)

LE_3_NOVEMBRE = datetime(2026, 11, 3)


# ── Production du fichier ────────────────────────────────────────────────────


def test_rendre_document_produit_un_pdf_valide():
    pdf = rendre_document("Note de service", "# Titre\n\nUn paragraphe.")

    assert pdf.startswith(b"%PDF-"), "l'en-tête d'un PDF est %PDF-"
    assert pdf.rstrip().endswith(b"%%EOF"), "un PDF se termine par %%EOF"
    assert len(pdf) > 1000, "un PDF d'une page fait plus d'un kilo-octet"


def test_le_titre_devient_celui_du_document():
    """Le titre renseigne le <title>, que la visionneuse affiche dans son
    onglet — et non le nom du fichier."""
    html = construire_html("Attestation de situation", "Corps.")
    assert "<title>Attestation de situation</title>" in html


def test_un_document_sans_corps_reste_exportable():
    """
    Un document terminé mais vide doit sortir, avec son en-tête seul.

    Échouer obligerait l'interface à traiter un cas incompréhensible pour
    l'utilisateur : son document existe, il est marqué terminé, et l'export
    refuserait de produire quoi que ce soit.
    """
    for vide in (None, "", "   "):
        pdf = rendre_document("Document vierge", vide)
        assert pdf.startswith(b"%PDF-")


def test_la_date_d_export_est_en_francais_sans_dependre_de_la_locale():
    """
    `strftime("%B")` rendrait « November » sur python:3.11-slim, dont la locale
    française n'est pas installée. Le mois est donc écrit à la main.
    """
    html = construire_html("Note", "Corps.", LE_3_NOVEMBRE)
    assert "Exporté le 3 novembre 2026" in html


# ── Interprétation du Markdown ───────────────────────────────────────────────


def test_les_extensions_markdown_couvrent_ce_que_l_editeur_produit():
    """
    Aucune des quatre n'est interchangeable :

    - sans `tables`, « | Champ | Valeur | » sort tel quel, barres comprises ;
    - sans `fenced_code`, un bloc délimité par trois accents graves — ce
      qu'insère le bouton « Code » — sort en texte courant ;
    - sans `nl2br`, un saut de ligne simple est avalé, alors que l'aperçu de
      l'éditeur le rend (marked est configuré avec breaks: true) ;
    - sans `sane_lists`, une liste collée au paragraphe précédent n'est pas
      reconnue.
    """
    assert set(EXTENSIONS) == {"tables", "fenced_code", "nl2br", "sane_lists"}


@pytest.mark.parametrize(
    ("markdown_source", "balise_attendue"),
    [
        ("# Titre de niveau 1", "<h1>"),
        ("| Champ | Valeur |\n|---|---|\n| Nom | Dupont |", "<table>"),
        ("- premier\n- deuxième", "<ul>"),
        ("1. premier\n2. deuxième", "<ol>"),
        ("> Une citation.", "<blockquote>"),
        ("**gras**", "<strong>"),
        ("*italique*", "<em>"),
        ("[un lien](https://exemple.test)", 'href="https://exemple.test"'),
        ("```\nbloc de code\n```", "<pre>"),
    ],
)
def test_le_markdown_de_l_editeur_est_bien_interprete(markdown_source, balise_attendue):
    """
    Chaque forme que la barre d'outils de l'éditeur sait produire doit arriver
    en HTML structuré. Vérifier seulement qu'un PDF sort ne prouverait rien :
    du Markdown non interprété produit lui aussi un PDF valide, où « | Champ | »
    s'affiche avec ses barres verticales.
    """
    html = construire_html("Essai", markdown_source)
    assert balise_attendue in html


def test_un_saut_de_ligne_simple_est_conserve():
    """
    Comportement repris de l'aperçu, où marked est configuré avec breaks: true.
    Un PDF qui recollerait les lignes ne montrerait pas ce que l'utilisateur a
    relu avant de cliquer.
    """
    assert "<br" in construire_html("Essai", "première ligne\nseconde ligne")


# ── Robustesse face au titre, qui n'est pas du Markdown ──────────────────────


@pytest.mark.parametrize(
    "titre",
    [
        "R&D — bilan",
        "<script>alert(1)</script>",
        "Contrat <terminé>",
        'Devis "ferme"',
    ],
)
def test_un_titre_a_caracteres_speciaux_est_echappe(titre):
    """
    Le titre est inséré dans le gabarit HTML sans passer par la bibliothèque
    Markdown, qui n'échappe que le corps. Sans échappement explicite, un « & »
    ou un chevron produirait un HTML invalide — au mieux.
    """
    html = construire_html(titre, "Corps.")

    # Ni chevron ni esperluette bruts ne subsistent dans ce que l'utilisateur a
    # saisi : on vérifie l'absence de la forme non échappée.
    for brut in ("<script>", "<terminé>", "&nbsp", "R&D "):
        assert brut not in html.split("<body>")[0] or brut not in titre, (
            f"« {brut} » doit être échappé dans le gabarit"
        )
    assert rendre_document(titre, "Corps.").startswith(b"%PDF-")


# ── Nom du fichier proposé au téléchargement ─────────────────────────────────


def test_nom_de_fichier_derive_du_titre_et_porte_la_date():
    assert nom_de_fichier("Note de service", LE_3_NOVEMBRE) == "Note-de-service-2026-11-03.pdf"


@pytest.mark.parametrize(
    "titre",
    [
        "../../etc/passwd",
        "dossier/sous-dossier",
        "fichier:avec:deux-points",
        'guillemets"et\\barres',
        "retour\nligne",
    ],
)
def test_nom_de_fichier_ne_laisse_passer_aucun_separateur(titre):
    """
    Le titre est saisi librement et finit dans un en-tête HTTP. Une barre
    oblique y désignerait un chemin, et un retour à la ligne permettrait
    d'injecter un en-tête supplémentaire.
    """
    nom = nom_de_fichier(titre, LE_3_NOVEMBRE)

    for interdit in ("/", "\\", ":", '"', "\n", "\r", ".."):
        assert interdit not in nom, f"« {interdit} » ne doit pas subsister dans « {nom} »"
    assert nom.endswith(".pdf")


def test_nom_de_fichier_tient_sur_un_titre_vide_ou_sans_caractere_utile():
    """Un titre que le filtrage vide entièrement ne doit pas produire « -.pdf »."""
    for titre in ("", "   ", "///", "???"):
        assert nom_de_fichier(titre, LE_3_NOVEMBRE) == "document-2026-11-03.pdf"


def test_nom_de_fichier_borne_la_longueur():
    nom = nom_de_fichier("Titre interminable " * 20, LE_3_NOVEMBRE)
    assert len(nom) <= 60 + len("-2026-11-03.pdf")
