# Captures d'écran — interfaces implémentées

Ces captures correspondent à l'application réellement développée (haute fidélité,
charte graphique appliquée). Elles alimentent le **§ 7.1** du dossier et l'annexe
**§ 12.2 « Les captures d'écrans d'interfaces utilisateurs et le code correspondant »**.

À ne pas confondre avec les wireframes basse fidélité W-01 à W-09
(`docs/maquettes-helpmedraft.html`), qui relèvent de l'annexe § 12.1.

| Réf | Écran | Route | Fichier | Composant correspondant | Zone d'accès |
|:--|:--|:--|:--|:--|:--|
| C-01 | Accueil | `/` | `C-01-accueil.png` | `HomeView` | publique |
| C-01b | Accueil (mobile) | `/` | `C-01b-accueil-mobile.png` | `HomeView` + `Nav` | publique |
| C-02 | Connexion | `/login` | `C-02-connexion.png` | `LoginView` | `guestOnly` |
| C-03 | Inscription | `/register` | `C-03-inscription.png` | `RegisterView` | `guestOnly` |
| C-04 | Mot de passe oublié | `/forgot-password` | `C-04-mot-de-passe-oublie.png` | `ForgotPasswordView` | `guestOnly` |
| C-05 | Tableau de bord | `/dashboard` | `C-05-tableau-de-bord.png` | `DashboardView` | `requiresAuth` |
| C-06 | Liste des documents | `/documents` | `C-06-liste-documents.png` | `DocumentListView` | `requiresAuth` |
| C-07 | Nouveau document | `/documents/nouveau` | `C-07-nouveau-document.png` | `DocumentEditorView` | `requiresAuth` |
| C-08 | Éditeur, document chargé | `/documents/:id` | `C-08-editeur-document.png` | `DocumentEditorView` + `MarkdownEditor` | `requiresAuth` |
| C-09 | Assistant IA | `/documents/:id` | `C-09-assistant-ia.png` | `DocumentEditorView` (panneau IA) | `requiresAuth` |
| C-10 | Back-office | `/admin` | `C-10-back-office.png` | `AdminView` | `requiresAdmin` |
| C-11 | Réinitialisation | `/reset-password` | `C-11-reinitialisation.png` | `ResetPasswordView` | `guestOnly` |

## Correspondance maquette → réalisation

| Wireframe (§ 12.1) | Capture (§ 12.2) |
|:--|:--|
| W-01 Accueil | C-01, C-01b |
| W-02 Inscription | C-03 |
| W-03 Connexion et récupération | C-02, C-04 |
| W-04 Tableau de bord | C-05 |
| W-05 Liste des documents | C-06 |
| W-06 Éditeur de document | C-07 (création), C-08 (édition) |
| W-07 Assistant IA | C-09 |
| W-08 Back-office | C-10 |

La série est complète : les quatre captures qui manquaient — C-08 à C-11 — sont
produites. C-09 est la plus importante, le REAC demandant explicitement la
capture **et le code correspondant** pour la fonctionnalité la plus
représentative du projet.

### Réserve sur C-09

L'interface n'affiche **pas** le quota d'appels restants : le panneau montre
l'action, la portée, les instructions et l'avertissement sur le contenu généré,
rien de plus. La capture ne peut donc pas le montrer. Le quota n'est visible que
dans le back-office, colonne « QUOTA IA / 24H » de C-10, et il est appliqué côté
serveur. L'afficher dans le panneau serait une évolution de l'interface, pas une
affaire de capture.

## Convention de capture

- Largeur fixe **1654 px**, zoom 100 % — la largeur des captures de la première
  série, conservée pour que les largeurs en centimètres calées dans
  `docs/dossier/fill_trame.py` gardent la même hauteur rendue dans le dossier.
- Pleine page pour C-01, C-03 et C-05 ; hauteur d'écran (1272 px) pour les
  autres, comme la série d'origine.
- Données de démonstration cohérentes d'un écran à l'autre : le **jeu d'essai du
  dépôt** (`backend/database/jeu_essai.py`), chargé dans une base jetable. Les
  écrans connectés montrent le compte de Camille Moreau (5 documents, 15 appels
  IA sur 20), le back-office celui d'Awa Diallo.
- Aucune donnée personnelle réelle : comptes fictifs uniquement (RGPD).
- Format PNG, pas de recadrage après coup.

## Reproduction

Les captures sont produites par un script Playwright contre la pile lancée en
local, et non à la main : une série refaite à la main ne se compare pas d'une
fois sur l'autre, et c'est précisément ce qu'il a fallu faire après la refonte
de l'éditeur. Deux points qui ont demandé correction, et qui valent pour toute
reprise :

- le document de C-08 et C-09 est choisi par son **titre** (« Note de service —
  terminée ») et non « le premier de la liste » : le jeu d'essai contient à
  dessein un « Document vierge » qui donnerait une capture d'éditeur vide ;
- la souris est écartée avant chaque capture, faute de quoi le bouton survolé
  par le clic précédent reste en surbrillance.
