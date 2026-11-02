# Plan du dossier de projet — épreuve CDA

Imposé par le référentiel d'évaluation ([`REV-CDA-V04.pdf`](./REV-CDA-V04.pdf), §3.1).

## Format

| Contrainte | Valeur |
|---|---|
| Volume | **40 à 60 pages maximum**, hors page de garde, sommaire et annexes (schémas et illustrations compris) |
| Annexes | **40 pages maximum** |
| Support | Un **seul** dossier imprimé + un **seul** diaporama |
| Lecture | Le jury lit le dossier **avant** la présentation |

## Déroulé de l'épreuve (2 h 15 pour le candidat)

| Modalité | Durée |
|---|---|
| Questionnaire professionnel (documentation technique en anglais : 2 QCM en français + 2 questions ouvertes en anglais) | 0 h 30 |
| Présentation du projet (diaporama) | 0 h 40 |
| Entretien technique (sur la base du dossier et de la présentation) | 0 h 45 |
| Entretien final (y compris échange sur le dossier professionnel) | 0 h 20 |

## Plan du dossier (projet réalisé pendant la formation)

Le REV prévoit un plan allégé pour un projet de formation :

1. La liste des compétences mises en œuvre dans le cadre du projet
2. L'expression des besoins du projet, pour définir les objectifs et les limites du projet
3. L'environnement technique
4. Les réalisations permettant la mise en œuvre des compétences

> ⚠️ Ce plan court est trompeusement simple : les **critères de performance** des 8 compétences
> obligatoires restent tous évalués. Le point 4 doit donc contenir de quoi les prouver. Le plan
> « entreprise » ci-dessous dit exactement quoi, et c'est aussi ce sur quoi le jury questionne
> pendant l'entretien technique. **Vérifier le plan attendu avec le formateur** — en pratique le
> plan entreprise est souvent demandé.

## Plan du dossier (version entreprise — référence de contenu)

- [ ] Liste des compétences mises en œuvre
- [ ] Cahier des charges ou expression des besoins → **on a le CDC LexiCorp**
- [ ] Présentation de l'entreprise et du service → LexiCorp (contexte fictif)
- [ ] **Gestion de projet** : planning et suivi, environnement humain, objectifs de qualité → *CP4, à produire*
- [ ] **Spécifications fonctionnelles** :
  - [ ] contraintes du projet et livrables attendus
  - [ ] **architecture logicielle** → *CP6, à produire*
  - [ ] **maquettes et enchaînement des maquettes** → maquettes ✅, enchaînement *à produire*
  - [ ] **modèle entités-associations et modèle physique** de la base → *CP7, à produire*
  - [ ] **script de création / modification** de la base → `schema_mysql.sql` ✅
  - [ ] **diagramme de cas d'utilisation** → *à produire*
  - [ ] **diagramme(s) de séquence** des cas les plus significatifs → *à produire*
- [ ] **Spécifications techniques**, y compris pour la sécurité
- [ ] **Réalisations** : extraits de code les plus significatifs + **arguments des choix**, y compris de sécurité
  - [ ] captures d'interfaces utilisateur et code correspondant
  - [ ] extraits de composants métier
  - [ ] extraits de composants d'accès aux données
  - [ ] extraits d'autres composants (contrôleurs, utilitaires)
- [ ] **Éléments de sécurité** de l'application
- [ ] **Plan de tests** → *CP9, à produire*
- [ ] **Jeu d'essai de la fonctionnalité la plus représentative** : données en entrée, données attendues, données obtenues, **analyse des écarts** → *à produire*
- [ ] **Veille sur les vulnérabilités de sécurité** menée pendant le projet : vulnérabilités trouvées, failles corrigées → base existante dans `veille-helpmedraft.html` et `securite-correctifs-2026-09-27.md`

### Annexes (fonctionnalité la plus représentative)

- [ ] maquettes des interfaces
- [ ] captures d'écrans + code correspondant
- [ ] code des composants métier les plus significatifs
- [ ] code des composants d'accès aux données les plus significatifs
- [ ] code des autres composants

> **Choix de la « fonctionnalité la plus représentative »** : la génération IA sur un document.
> Elle traverse toutes les couches — interface (éditeur Markdown) → contrôleur (`ia_route.py`)
> → métier (`ia_service.py`) → accès aux données (ORM, historique `IA`), avec authentification,
> quota, validation des entrées et protection XSS du rendu. C'est le meilleur support pour le
> jeu d'essai et les extraits de code.

## Plan du diaporama

Même ossature que le dossier, resserrée :
1. Expression des besoins, contraintes, livrables
2. Gestion de projet (planning, suivi, qualité)
3. Architecture logicielle
4. Maquettes (une ou deux interfaces) et enchaînement
5. MER + MPD
6. Cas d'utilisation + un ou deux diagrammes de séquence
7. Captures et extraits de code (interface, métier, accès données, autres)
8. Éléments de sécurité
9. Plan de tests
10. Jeu d'essai de la fonctionnalité représentative + analyse des écarts
11. Veille sécurité : vulnérabilités trouvées et corrigées
12. Synthèse et conclusion (satisfactions et difficultés rencontrées)
