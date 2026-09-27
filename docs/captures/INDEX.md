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

## Correspondance maquette → réalisation

| Wireframe (§ 12.1) | Capture (§ 12.2) |
|:--|:--|
| W-01 Accueil | C-01, C-01b |
| W-02 Inscription | C-03 |
| W-03 Connexion et récupération | C-02, C-04 |
| W-04 Tableau de bord | C-05 |
| W-05 Liste des documents | C-06 |
| W-06 Éditeur de document | C-07 (création) — **édition manquante** |
| W-07 Assistant IA | **manquante** |
| W-08 Back-office | **manquante** |

## Captures restant à produire

- `C-08-editeur-document.png` — `/documents/:id`, document existant chargé (W-06)
- `C-09-assistant-ia.png` — modale IA ouverte sur `/documents/:id`, avec quota affiché (W-07)
- `C-10-back-office.png` — `/admin` (W-08)
- `C-11-reinitialisation.png` — `/reset-password` avec jeton valide

C-09 est la plus importante : c'est la fonctionnalité la plus représentative du
projet, et le REAC demande explicitement la capture **et le code correspondant**
pour cette fonctionnalité.

## Convention de capture

- Chrome DevTools → largeur fixe **1440 px**, zoom 100 %
- Données de démonstration cohérentes d'un écran à l'autre (même compte, mêmes documents)
- Aucune donnée personnelle réelle : comptes fictifs uniquement (RGPD)
- Format PNG, pas de recadrage après coup
