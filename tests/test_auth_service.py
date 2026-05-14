"""Tests du service d'authentification."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from core.security import create_refresh_token
from schemas.user import UserCreate
from services.auth_service import AuthService


async def test_register_creates_user(mock_session, sample_user):
    with patch("services.auth_service.UserRepository") as MockRepo:
        repo = MockRepo.return_value
        repo.get_by_email = AsyncMock(return_value=None)
        repo.create = AsyncMock(return_value=sample_user)

        result = await AuthService(mock_session).register(
            UserCreate(email="new@example.com", password="pass123")
        )
        repo.create.assert_called_once()
        assert result == sample_user


async def test_register_duplicate_email_raises(mock_session, sample_user):
    with patch("services.auth_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_email = AsyncMock(return_value=sample_user)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).register(
                UserCreate(email="test@example.com", password="pass123")
            )
        assert exc.value.status_code == 409


async def test_login_returns_tokens(mock_session, sample_user):
    with patch("services.auth_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_email = AsyncMock(return_value=sample_user)

        token = await AuthService(mock_session).login("test@example.com", "password123")
        assert token.access_token
        assert token.refresh_token
        assert token.token_type == "bearer"


async def test_login_wrong_password_raises(mock_session, sample_user):
    with patch("services.auth_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_email = AsyncMock(return_value=sample_user)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).login("test@example.com", "wrong")
        assert exc.value.status_code == 401


async def test_login_unknown_email_raises(mock_session):
    with patch("services.auth_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_email = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).login("unknown@example.com", "pass")
        assert exc.value.status_code == 401


async def test_login_inactive_user_raises(mock_session, sample_user):
    sample_user.is_active = False
    with patch("services.auth_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_email = AsyncMock(return_value=sample_user)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).login("test@example.com", "password123")
        assert exc.value.status_code == 401


async def test_refresh_returns_new_tokens(mock_session, sample_user):
    token = create_refresh_token(sample_user.id)
    with patch("services.auth_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=sample_user)

        result = await AuthService(mock_session).refresh(token)
        assert result.access_token
        assert result.refresh_token


async def test_refresh_invalid_token_raises(mock_session):
    with pytest.raises(HTTPException) as exc:
        await AuthService(mock_session).refresh("invalid.token")
    assert exc.value.status_code == 401


async def test_refresh_with_access_token_raises(mock_session, sample_user):
    from core.security import create_access_token

    access_token = create_access_token(sample_user.id)
    with pytest.raises(HTTPException) as exc:
        await AuthService(mock_session).refresh(access_token)
    assert exc.value.status_code == 401
