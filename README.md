# FastAPI Users

[![CI](https://github.com/SeydinaBANE/fastapi-users/actions/workflows/ci.yml/badge.svg)](https://github.com/SeydinaBANE/fastapi-users/actions/workflows/ci.yml)

API REST de gestion d'utilisateurs avec architecture modulaire, authentification JWT et rôles admin/user.

## Stack

- **FastAPI** + uvicorn
- **SQLAlchemy async** + asyncpg + **Alembic** (migrations)
- **PostgreSQL** (Docker) 
- **JWT** (access + refresh tokens) + bcrypt
- **pydantic-settings** pour la configuration

## Démarrage rapide — Docker

```bash
git clone https://github.com/SeydinaBANE/fastapi-users.git
cd fastapi-users

cp .env.example .env
make docker-up
make migrate   # ou : docker compose exec app alembic upgrade head
```

API disponible sur [http://localhost:8000](http://localhost:8000)  
Docs Swagger : [http://localhost:8000/docs](http://localhost:8000/docs)

## Installation locale

```bash
cp .env.example .env
pip install -r requirements.txt
# Lancer PostgreSQL, puis :
make migrate
make run
```

## Endpoints

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Créer un compte |
| POST | `/api/v1/auth/login` | — | Connexion → tokens |
| POST | `/api/v1/auth/refresh` | — | Renouveler les tokens |
| GET | `/api/v1/users/me` | user | Profil courant |
| PATCH | `/api/v1/users/me` | user | Modifier son profil |
| GET | `/api/v1/users/` | admin | Lister tous les utilisateurs |
| GET | `/api/v1/users/{id}` | admin | Détail d'un utilisateur |
| PATCH | `/api/v1/users/{id}` | admin | Modifier un utilisateur |
| DELETE | `/api/v1/users/{id}` | admin | Supprimer un utilisateur |

## Tests

```bash
pytest -v                              # 27 tests unitaires
pytest tests/test_auth_service.py -v  # un seul module
```

Tout mocké — aucune base de données requise.

## Makefile

```bash
make run        # uvicorn --reload
make test       # pytest
make check      # ruff + mypy + format
make migrate    # alembic upgrade head
make docker-up  # build + démarre app + db
make docker-down
```

## Structure

```
main.py                  ← composition root + logging
config/settings.py       ← Settings (pydantic-settings), charge .env
core/
  security.py            ← hash_password, JWT encode/decode
  dependencies.py        ← get_current_user, require_admin (FastAPI Depends)
db/
  base.py                ← engine async, AsyncSession, Base
  models/user.py         ← User (id, email, role, is_active)
schemas/                 ← Pydantic : UserCreate, UserRead, Token, LoginRequest
repositories/
  user_repository.py     ← CRUD async (get_by_id, get_by_email, create, update, delete)
services/
  auth_service.py        ← register, login, refresh
  user_service.py        ← get_me, update_me, list/get/update/delete (admin)
api/v1/
  auth.py                ← /auth/register, /login, /refresh
  users.py               ← /users/me, /users/{id}
alembic/                 ← migrations
tests/                   ← 27 tests unitaires (pytest-asyncio)
```

**Flux de dépendances :** `.env → settings → db → repository → service → API`

Les services ne connaissent pas FastAPI. L'API ne connaît pas SQLAlchemy.

## Configuration

| Variable | Défaut | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | URL de connexion PostgreSQL |
| `JWT_SECRET_KEY` | `change-me` | Clé secrète JWT |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Durée de vie du token d'accès |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Durée de vie du token de rafraîchissement |
