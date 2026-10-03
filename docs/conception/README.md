# Dossier de conception — HelpMeDraft

Documents produits en amont du développement, exigés par les compétences **CP 5**, **CP 6** et
**CP 7** du titre CDA et repris tels quels dans le [dossier de projet](../plan-dossier-projet.md).

| # | Document | Compétence | Production attendue à l'examen |
|---|---|---|---|
| 1 | [Expression des besoins](./01-expression-des-besoins.md) | CP 5 | « l'expression des besoins du projet pour définir les objectifs et les limites » |
| 2 | [Cas d'utilisation](./02-cas-utilisation.md) | CP 5 | « le diagramme du comportement des fonctionnalités de type cas d'utilisations » |
| 3 | [Enchaînement des écrans](./03-enchainement-ecrans.md) | CP 5 | « l'enchaînement des maquettes est formalisé par un schéma » |
| 4 | [Modèle de données](./04-modele-donnees.md) | CP 7 | « le modèle entités-associations et modèle physique de la base de données » |
| 5 | [Architecture logicielle](./05-architecture-logicielle.md) | CP 6 | « l'architecture logicielle du projet » |
| 6 | [Diagrammes de séquence](./06-diagrammes-sequence.md) | CP 5 / CP 6 | « le diagramme du détail des cas d'utilisations les plus significatifs » |

## Diagrammes exportés

Les diagrammes sont écrits en Mermaid dans les documents — ils se rendent directement sur GitHub
et restent modifiables avec le code. Ils sont aussi exportés en PNG (×3, fond blanc) dans
[`diagrammes/`](./diagrammes/), prêts à coller dans le dossier imprimé et le diaporama.

| Fichier | Contenu | Source |
|---|---|---|
| `cas-utilisation.png` | 18 cas d'utilisation, 5 acteurs | doc 2 |
| `enchainement-ecrans.png` | 16 écrans, 4 zones d'accès | doc 3 |
| `etats-editeur.png` | états de l'éditeur, dont les chemins d'erreur IA | doc 3 |
| `mcd-entites-associations.png` | modèle conceptuel, 7 entités | doc 4 |
| `mpd-modele-physique.png` | modèle physique, types et contraintes | doc 4 |
| `architecture-couches.png` | vue en couches, client / serveur / services | doc 5 |
| `flux-donnees-personnelles.png` | où vont les données personnelles, et où elles ne vont pas | doc 5 |
| `sequence-generation-ia.png` | UC-10, scénario nominal complet | doc 6 |
| `sequence-generation-ia-erreurs.png` | UC-10, cinq chemins d'erreur | doc 6 |
| `sequence-connexion-refresh.png` | UC-02, connexion puis rotation du refresh token | doc 6 |
| `sequence-reset-mot-de-passe.png` | UC-04, réinitialisation de mot de passe | doc 6 |

### Régénérer les PNG

```bash
# Extraire les blocs Mermaid, puis pour chacun :
npx -p @mermaid-js/mermaid-cli mmdc -i diagramme.mmd -o diagramme.png -b white -s 3
```

## Fonctionnalité la plus représentative

Le dossier de projet et la soutenance demandent de dérouler **une** fonctionnalité de bout en
bout. Celle retenue est **la génération IA sur un document** (UC-10) : elle traverse les quatre
couches, mobilise l'authentification, l'autorisation, la validation des entrées, une règle de
gestion (le quota glissant), un service externe et l'écriture d'une trace. C'est le meilleur
support pour les extraits de code, le jeu d'essai et l'analyse des écarts.

## Avertissement de lecture

Ces documents décrivent l'application **telle qu'elle est**, pas telle qu'elle devrait être.
Les écarts connus y sont signalés explicitement plutôt que passés sous silence : chiffrement au
repos absent, couverture RGAA incomplète, désalignement entre l'ORM et le SQL sur
`ia.id_document`, services écrits en modules de fonctions plutôt qu'en classes. Un jury préfère
un écart identifié et argumenté à un écart découvert pendant l'entretien. Le suivi de ces points
est dans le [TODO](../../TODO.md).
