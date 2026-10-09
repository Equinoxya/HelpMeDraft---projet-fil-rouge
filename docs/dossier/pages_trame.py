"""Relève la page de début de chaque partie dans le PDF rendu."""
import json, re, sys, unicodedata
from pypdf import PdfReader

TITRES = [
 ("1.", "La liste des compétences mises en œuvre dans le cadre du projet"),
 ("2.", "Le cahier des charges ou l’expression des besoins du projet"),
 ("3.", "- la présentation de l’entreprise et du service"),
 ("4.", "La gestion de projet"),
 ("5.", "Les spécifications fonctionnelles du projet"),
 ("5.1.", "Les contraintes du projet et livrables attendus"),
 ("5.2.", "L’architecture logicielle du projet"),
 ("5.3.", "Les maquettes et enchaînement des maquettes"),
 ("5.4.", "Le modèle entités-associations et modèle physique de la base de données"),
 ("5.5.", "Le script de création ou de modification de la base de données"),
 ("5.6.", "Le diagramme du comportement des fonctionnalités de type cas d’utilisations"),
 ("5.7.", "Le diagramme du détail des cas d’utilisations les plus significatifs de type diagramme de séquence"),
 ("6.", "Les spécifications techniques du projet"),
 ("7.", "Les réalisations du candidat comportant les extraits de code les plus significatifs"),
 ("7.1.", "Les captures d’écran d’interfaces utilisateur et le code correspondant"),
 ("7.2.", "Des extraits de code de composants métier"),
 ("7.3.", "Des extraits de code de composants d’accès aux données"),
 ("7.4.", "Des extraits de code d’autres composants"),
 ("8.", "La présentation d’éléments de sécurité de l’application"),
 ("9.", "La présentation du plan de tests"),
 ("10.", "La présentation d’un jeu d’essai élaboré par le candidat"),
 ("11.", "- la description de la veille, effectuée par le candidat"),
 ("12.", "ANNEXES"),
 ("12.1.", "Les maquettes des interfaces utilisateur"),
 ("12.2.", "Les captures d’écrans d’interfaces utilisateurs et le code correspondant"),
 ("12.3.", "Le code de composants métier les plus significatifs"),
 ("12.4.", "Le code de composants d’accès aux données les plus significatifs"),
 ("12.5.", "Le code d’autres composants"),
]

def norm(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", t.lower())

reader = PdfReader("lo2/dossier-projet-rempli.pdf")
pages = [norm(p.extract_text() or "") for p in reader.pages]
toc_i = next((i for i, t in enumerate(pages) if norm("Table des matières") in t), 0)
start, res, manquants = toc_i + 1, {}, []
for num, titre in TITRES:
    k = norm(titre)
    pg = next((j + 1 for j in range(start, len(pages)) if k in pages[j]), None)
    if pg is None:
        manquants.append(num)
    else:
        res[titre] = pg
        start = max(pg - 1, toc_i + 1)

if "--check" in sys.argv:
    debut_annexes = res.get("ANNEXES")
    corps = (debut_annexes - toc_i - 2) if debut_annexes else None
    print(f"total {len(pages)} pages | corps {corps} | annexes {len(pages) - debut_annexes + 1 if debut_annexes else '?'}")
    if manquants:
        print("titres non localisés :", manquants)
else:
    json.dump(res, open("pages.json", "w"))
    print("pagination relevée :", len(res), "entrées")
