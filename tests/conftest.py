"""Fixtures partagées entre tous les tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.security import hash_password
from db.models.user import Role, User


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def sample_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.hashed_password = hash_password("password123")
    user.full_name = "Test User"
    user.role = Role.user
    user.is_active = True
    return user


@pytest.fixture
def admin_user(sample_user):
    sample_user.role = Role.admin
    return sample_user
