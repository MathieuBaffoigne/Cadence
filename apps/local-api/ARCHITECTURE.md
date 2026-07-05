# Architecture de `local-api`

Ce document explique l'architecture hexagonale (ports & adapters) telle qu'appliquée dans `local-api`, avec des exemples tirés du code réel du projet. Objectif : pouvoir s'y référer quand un concept n'est pas clair, plutôt que de le re-expliquer à chaque fois.

## L'idée de base

Le problème que l'architecture hexagonale résout : **empêcher la logique métier de dépendre des détails techniques** (SQLite, FastAPI, HTTP...). Si `CreateEmployeeUseCase` connaissait directement SQLite, on ne pourrait jamais le tester sans une vraie base de données, ni changer de moteur de stockage sans réécrire la logique métier.

La solution : la logique métier ne dépend que d'un **contrat** (le port), jamais d'une implémentation concrète (l'adapter). L'implémentation concrète est injectée de l'extérieur.

```
domain/        ← les règles métier, ne dépend de RIEN d'externe (pas de FastAPI, pas de SQLite)
application/   ← orchestre le domaine (use cases), ne dépend que du domain/
adapters/      ← implémente les contrats du domain/ avec une vraie techno (SQLite)
api/           ← câble tout ensemble et expose en HTTP (FastAPI)
```

La règle de dépendance est à sens unique : `api/` dépend de `adapters/` et `application/`, qui dépendent de `domain/` — jamais l'inverse. `domain/` ne sait même pas que SQLite ou FastAPI existent.

## Les 4 couches, avec les fichiers réels du projet

### 1. `domain/models/` — les modèles de données (entités)

```
domain/models/employee.py → Employee, WeeklyAvailability
```

Des `@dataclass` pures : juste des données + leurs invariants (ex. `WeeklyAvailability.__post_init__` refuse un `day_of_week` hors 0-6). **Aucune méthode d'action, aucune connaissance de SQLite/HTTP.** On peut créer un `Employee` en mémoire dans un test sans jamais toucher une base de données.

### 2. `domain/ports/` — les ports (contrats)

```
domain/ports/health_repository.py    → HealthRepository (ABC)
domain/ports/employee_repository.py  → EmployeeRepository (ABC)
```

Une `ABC` (classe abstraite) = une liste de méthodes **sans implémentation** (`...`). C'est une promesse : "si tu veux persister des employés, voici les opérations que tu dois savoir faire" — sans dire *comment*. On ne peut pas instancier une `ABC` directement.

### 3. `application/` — les use cases

```
application/health.py   → CheckHealthUseCase
application/employee.py → CreateEmployeeUseCase, ListEmployeesUseCase, ...
```

Chaque use case orchestre **une action métier précise**, en ne dépendant que du port (ex. `EmployeeRepository`), jamais d'une implémentation concrète :

```python
@dataclass
class CreateEmployeeUseCase:
    repository: EmployeeRepository   # le contrat, pas SqliteEmployeeRepository

    def execute(self, name: str, role: str | None = None) -> Employee:
        return self.repository.create(Employee(name=name, role=role))
```

C'est ce qui permet de tester `CreateEmployeeUseCase` avec un faux repository en mémoire (`FakeEmployeeRepository` dans les tests), sans SQLite.

### 4. `adapters/` — les adapters

```
adapters/sqlite_health_repository.py   → SqliteHealthRepository(HealthRepository)
adapters/sqlite_employee_repository.py → SqliteEmployeeRepository(EmployeeRepository)
```

L'implémentation *réelle* du contrat — celle qui sait vraiment ouvrir une connexion SQLite et écrire du SQL. Une classe par port, symétrique au fichier de port correspondant dans `domain/ports/`.

### 5. `api/` — le câblage HTTP

```
api/routers/health_routes.py + api/dependencies/health_deps.py     → endpoint GET /health
api/routers/employee_routes.py + api/dependencies/employee_deps.py → endpoints /employees, /employees/{id}/availabilities
```

- `routers/*_routes.py` : la traduction HTTP pure (méthode, URL, requête → appel du use case → réponse). Ne construit jamais rien lui-même.
- `dependencies/*_deps.py` : la construction des objets (repository concret → use case), exposée à FastAPI via `Depends(...)`. C'est le point où on décide *quelle* implémentation concrète utiliser.

`api/` est lui-même un adapter — mais un adapter *driving* (entrant : une requête HTTP pilote l'application), symétrique et opposé aux adapters *driven* (sortants) de `adapters/` (l'application pilote SQLite). C'est pour ça qu'il reste un dossier frère de `application/` et non un sous-dossier : `application/` doit rester agnostique de tout framework, et l'imbrication inverserait visuellement la règle de dépendance à sens unique (`api` → `application` → `domain`, jamais l'inverse).

`app.py` (composition root) assemble les deux routers dans l'app FastAPI.

## Exemple complet : `POST /employees`

Trace d'une requête à travers toutes les couches :

1. **`api/routers/employee_routes.py`** — `create_employee()` reçoit la requête HTTP, la désérialise en `EmployeeRequest` (dataclass), demande un `CreateEmployeeUseCase` via `Depends(get_create_employee_use_case)`.
2. **`api/dependencies/employee_deps.py`** — `get_create_employee_use_case()` construit le use case avec un `SqliteEmployeeRepository(DB_PATH)` (via `get_employee_repository`, mis en cache avec `@lru_cache`).
3. **`application/employee.py`** — `CreateEmployeeUseCase.execute()` crée un `Employee` (le modèle) et appelle `self.repository.create(employee)` — sans savoir que c'est du SQLite derrière.
4. **`adapters/sqlite_employee_repository.py`** — `SqliteEmployeeRepository.create()` exécute le vrai `INSERT INTO employees ...`.
5. Le résultat (`Employee`) remonte jusqu'à la route, qui le retourne — FastAPI le sérialise en JSON.

Ce qui compte : à l'étape 3, le use case ne connaît que le contrat `EmployeeRepository`. Si demain on remplace SQLite par PostgreSQL, seule l'étape 4 change — rien dans `domain/` ni `application/` ne bouge.

## Glossaire

| Terme | Définition | Exemple dans le projet |
|---|---|---|
| **Modèle / Entité** | Structure de données pure représentant un concept métier | `Employee`, `WeeklyAvailability` |
| **Port** | Contrat (interface) définissant des opérations, sans implémentation | `EmployeeRepository` (ABC) |
| **Adapter** | Implémentation concrète d'un port avec une techno réelle | `SqliteEmployeeRepository` |
| **Use case** | Une action métier précise, orchestrant un ou plusieurs ports | `CreateEmployeeUseCase` |
| **DTO** | Structure de données pour transporter de l'info entre couches (ex. requête HTTP) | `EmployeeRequest`, `HealthStatus` |
| **Composition root** | L'endroit où on décide quelle implémentation concrète utiliser | `api/dependencies/employee_deps.py`, `app.py` |
| **Injection de dépendance** | Passer une dépendance (ex. un repository) de l'extérieur plutôt que la construire soi-même | `Depends(get_employee_repository)` |
| **Fake (test double)** | Implémentation en mémoire d'un port, utilisée en test à la place de l'adapter réel | `FakeEmployeeRepository` dans `tests/application/test_employee.py` |

## Règles à suivre pour tout nouveau code

1. **Un concept = son propre fichier**, à chaque couche : un modèle par fichier dans `domain/models/`, un port par fichier dans `domain/ports/`, un adapter par fichier dans `adapters/`, une route par fichier dans `api/routers/`, un provider par fichier dans `api/dependencies/`. Ne jamais mélanger deux concepts métier distincts (ex. Health et Employee) dans un seul fichier.
2. **`domain/` ne dépend jamais de rien d'externe** — pas de `fastapi`, pas de `sqlite3`, pas de `alembic` importés dans `domain/`.
3. **Les use cases ne dépendent que des ports** (`EmployeeRepository`), jamais d'un adapter concret (`SqliteEmployeeRepository`) — sinon on perd la possibilité de tester avec un fake.
4. **TDD** : écrire le test qui échoue en premier (contre un fake pour l'application, contre une vraie DB temporaire pour les adapters), puis le code qui le fait passer.
5. **Dataclasses partout** pour les classes qui ne font que porter un état (modèles, DTOs, use cases, adapters) — pas de `__init__` manuel quand un dataclass suffit.
