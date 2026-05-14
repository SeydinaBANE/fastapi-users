"""Tests des utilitaires de sécurité (hash, JWT)."""

import pytest
from jose import JWTError

from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_returns_hashed():
    assert hash_password("secret") != "secret"


def test_hash_password_same_input_different_hash():
    assert hash_password("secret") != hash_password("secret")


def test_verify_password_correct():
    hashed = hash_password("secret")
    assert verify_password("secret", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("secret")
    assert verify_password("wrong", hashed) is False


def test_create_access_token_type():
    payload = decode_token(create_access_token(42))
    assert payload["type"] == "access"
    assert payload["sub"] == "42"


def test_create_refresh_token_type():
    payload = decode_token(create_refresh_token(42))
    assert payload["type"] == "refresh"
    assert payload["sub"] == "42"


def test_decode_token_invalid_raises():
    with pytest.raises(JWTError):
        decode_token("invalid.token.here")


def test_access_and_refresh_tokens_differ():
    assert create_access_token(1) != create_refresh_token(1)
