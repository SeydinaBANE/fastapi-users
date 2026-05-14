"""Tests du service utilisateurs."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from schemas.user import UserUpdate
from services.user_service import UserService


async def test_get_me_returns_current_user(mock_session, sample_user):
    result = await UserService(mock_session).get_me(sample_user)
    assert result == sample_user


async def test_update_me_updates_full_name(mock_session, sample_user):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.update = AsyncMock(return_value=sample_user)

        await UserService(mock_session).update_me(sample_user, UserUpdate(full_name="Nouveau Nom"))
        assert sample_user.full_name == "Nouveau Nom"


async def test_update_me_ignores_none_fields(mock_session, sample_user):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.update = AsyncMock(return_value=sample_user)
        original_name = sample_user.full_name

        await UserService(mock_session).update_me(sample_user, UserUpdate())
        assert sample_user.full_name == original_name


async def test_get_all_returns_list(mock_session, sample_user):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_all = AsyncMock(return_value=[sample_user])

        result = await UserService(mock_session).get_all()
        assert result == [sample_user]


async def test_get_by_id_returns_user(mock_session, sample_user):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=sample_user)

        result = await UserService(mock_session).get_by_id(1)
        assert result == sample_user


async def test_get_by_id_not_found_raises(mock_session):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await UserService(mock_session).get_by_id(999)
        assert exc.value.status_code == 404


async def test_update_user_updates_is_active(mock_session, sample_user):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=sample_user)
        MockRepo.return_value.update = AsyncMock(return_value=sample_user)

        await UserService(mock_session).update_user(1, UserUpdate(is_active=False))
        assert sample_user.is_active is False


async def test_update_user_not_found_raises(mock_session):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await UserService(mock_session).update_user(999, UserUpdate())
        assert exc.value.status_code == 404


async def test_delete_user_calls_repo(mock_session, sample_user):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=sample_user)
        MockRepo.return_value.delete = AsyncMock(return_value=None)

        await UserService(mock_session).delete_user(1)
        MockRepo.return_value.delete.assert_called_once_with(sample_user)


async def test_delete_user_not_found_raises(mock_session):
    with patch("services.user_service.UserRepository") as MockRepo:
        MockRepo.return_value.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await UserService(mock_session).delete_user(999)
        assert exc.value.status_code == 404
