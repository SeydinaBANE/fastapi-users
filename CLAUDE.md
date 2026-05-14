# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Prérequis

Docker ou Python 3.11+ avec PostgreSQL en local.

## Lancer l'application

**Via Docker (recommandé) :**

```bash
cp .env.example .env
make docker-up
make migrate   # ou : docker compose exec app alembic upgrade head
```

**En local :**

```bash
cp .env.example .env
pip install -r requirements.txt
make migrate
make run   # uvicorn main:app --reload
```

## Tests

```bash
pytest -v                              # tous les tests (27)
pytest tests/test_auth_service.py -v  # un seul module
```

Tout mocké — aucune base de données requise pour les tests.

## Qualité du code

```bash
pre-commit install   # activer les hooks (une fois)
make check           # ruff lint + mypy + ruff format --check
make lint            # ruff check . uniquement
make format          # ruff format .
```

La config ruff, mypy et pytest est dans `pyproject.toml`. Le CI exécute le job `lint` avant `tests`.

## Migrations

```bash
make migrate                                        # appliquer toutes les migrations
alembic revision --autogenerate -m "description"   # générer une migration depuis les modèles
alembic downgrade -1                                # revenir en arrière d'une migration
```

## Configuration

Tous les paramètres sont dans `.env` (copié depuis `.env.example`), chargés via `pydantic-settings` dans `config/settings.py`. Aucune valeur n'est hardcodée.

## Architecture modulaire

```
main.py                  ← composition root : monte le routeur + configure logging
pyproject.toml           ← config ruff, mypy, pytest (asyncio_mode = "auto")
alembic/                 ← migrations async (env.py configuré pour SQLAlchemy async)
config/settings.py       ← Settings (pydantic-settings), charge .env
core/
  security.py            ← hash_password, verify_password, create/decode JWT
  dependencies.py        ← get_current_user, require_admin (FastAPI Depends)
db/
  base.py                ← engine async, AsyncSessionLocal, Base déclarative, get_db()
  models/user.py         ← User (id, email, hashed_password, full_name, role, is_active)
schemas/
  user.py                ← UserCreate, UserRead, UserUpdate (Pydantic)
  auth.py                ← LoginRequest, RefreshRequest, Token
repositories/
  user_repository.py     ← CRUD async : get_by_id, get_by_email, get_all, create, update, delete
services/
  auth_service.py        ← register(), login(), refresh() — logging + erreurs HTTP
  user_service.py        ← get_me(), update_me(), get_all(), get_by_id(), update_user(), delete_user()
api/v1/
  auth.py                ← POST /auth/register, /login, /refresh
  users.py               ← GET/PATCH /users/me + CRUD admin /users/{id}
tests/                   ← 27 tests unitaires (pytest-asyncio, tout mocké)
```

**Flux de dépendances :** `.env → settings → db → repository → service → API`

Les services ne connaissent pas FastAPI (pas d'import de `Request`, `Depends`, etc.).  
L'API ne connaît pas SQLAlchemy (pas de `select`, `session.execute` dans les routers).

## Chaîne de dépendances FastAPI

- `get_db()` — générateur async qui yield une `AsyncSession`
- `get_current_user` — décode le Bearer token, charge l'utilisateur via `UserRepository`
- `require_admin` — dépend de `get_current_user`, vérifie `role == Role.admin`

Les endpoints admin utilisent `dependencies=[Depends(require_admin)]` — la vérification est transparente sans polluer la signature.

## Gestion d'erreurs et logging

- Logging configuré dans `main.py` (`logging.basicConfig`, format ISO, level INFO)
- `AuthService` et `UserService` : `logger = logging.getLogger(__name__)`, erreurs loggées avant re-raise
- Les erreurs métier lèvent des `HTTPException` directement dans les services (409 conflit, 401 non autorisé, 404 introuvable)

## Auth JWT

- **Access token** : durée courte (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`), payload `{"sub": user_id, "type": "access"}`
- **Refresh token** : durée longue (`JWT_REFRESH_TOKEN_EXPIRE_DAYS`), payload `{"sub": user_id, "type": "refresh"}`
- `core/security.py` valide le champ `type` pour éviter d'utiliser un refresh token comme access token

## Tests async

`asyncio_mode = "auto"` dans `pyproject.toml` : toutes les fonctions `async def test_*` s'exécutent automatiquement avec asyncio, sans `@pytest.mark.asyncio`.  
Les repositories sont mockés via `patch("services.xxx.UserRepository")` — le patch cible le nom dans le module consommateur, pas la définition.
