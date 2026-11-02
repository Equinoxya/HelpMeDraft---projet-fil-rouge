# Tests backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # .venv\Scripts\activate sous Windows
pip install -r requirements.txt -r requirements-dev.txt

pytest                                   # toute la suite
pytest -m securite                       # la seule campagne de sécurité (bloquante)
pytest tests/unit                        # unitaires seuls
pytest --cov=app --cov=database --cov-report=term-missing
```

## Organisation

| Dossier | Niveau | Contenu |
|---|---|---|
| `unit/` | unitaire | primitives d'authentification, cycle des sessions, service IA |
| `integration/` | intégration | routes complètes, du HTTP à la base |
| `security/` | sécurité | non-régression des parades, marqueur `securite` |

## Environnement

Les fixtures de `conftest.py` posent un environnement **hermétique** :

- base **SQLite en mémoire**, recréée avant chaque test — rien n'est écrit sur le disque ;
- **aucun appel réseau** : le service d'inférence et l'envoi de courriel sont remplacés par des doubles ;
- **limitation de débit désactivée**, sans quoi le sixième test de connexion échouerait en `429` ;
- clé de signature de test injectée, `app/config.py` refusant de démarrer sans.

L'ordre des instructions de `conftest.py` est contraint : les variables d'environnement sont
posées **avant** tout import applicatif, parce que `config.py` lève à l'import et que `db.py`
lie le moteur à l'import. Ne pas réordonner ces lignes.

## Conventions

- Un test nomme ce qu'il vérifie, en français, et porte son identifiant du
  [plan de tests](../../docs/plan-de-tests.md) quand il en a un (`test_ti40_...`).
- Chaque règle de gestion `RG-01` à `RG-10` a au moins un test qui échoue si on la retire.
- Les tests de cloisonnement passent toujours par deux comptes : le propriétaire et un tiers.
