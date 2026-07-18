import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import patch
from fastapi import HTTPException
from jose import jwt

from app.auth.jwt import (
    verify_password,
    get_password_hash,
    create_token,
    decode_token,
)
from app.schemas.token import TokenType
from app.core.config import get_settings

settings = get_settings()


# -----------------------------
# Password hashing tests
# -----------------------------
def test_password_hash_and_verify():
    password = "StrongPass123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPass", hashed) is False


# -----------------------------
# Token creation tests
# -----------------------------
def test_create_access_token():
    token = create_token("123", TokenType.ACCESS)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["sub"] == "123"
    assert decoded["type"] == "access"
    assert "exp" in decoded
    assert "iat" in decoded
    assert "jti" in decoded


def test_create_refresh_token():
    token = create_token("123", TokenType.REFRESH)
    decoded = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["sub"] == "123"
    assert decoded["type"] == "refresh"


def test_create_token_custom_expiration():
    token = create_token("123", TokenType.ACCESS, expires_delta=timedelta(minutes=1))
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["type"] == "access"


def test_create_token_uuid_input():
    user_id = uuid4()
    token = create_token(user_id, TokenType.ACCESS)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == str(user_id)


def test_create_token_exception():
    # Force an exception by breaking the secret key
    with patch("app.auth.jwt.settings.JWT_SECRET_KEY", None):
        with pytest.raises(HTTPException) as exc:
            create_token("123", TokenType.ACCESS)
        assert "Could not create token" in exc.value.detail


# -----------------------------
# Token decoding tests
# -----------------------------
@pytest.mark.asyncio
async def test_decode_valid_access_token():
    token = create_token("123", TokenType.ACCESS)
    payload = await decode_token(token, TokenType.ACCESS)

    assert payload["sub"] == "123"
    assert payload["type"] == "access"


@pytest.mark.asyncio
async def test_decode_invalid_token_type():
    token = create_token("123", TokenType.ACCESS)

    with pytest.raises(HTTPException) as exc:
        await decode_token(token, TokenType.REFRESH)

    assert exc.value.detail == "Invalid token type"


@pytest.mark.asyncio
async def test_decode_blacklisted_token():
    token = create_token("123", TokenType.ACCESS)

    with patch("app.auth.jwt.is_blacklisted", return_value=True):
        with pytest.raises(HTTPException) as exc:
            await decode_token(token, TokenType.ACCESS)

    assert exc.value.detail == "Token has been revoked"


@pytest.mark.asyncio
async def test_decode_expired_token():
    expired_payload = {
        "sub": "123",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        "iat": datetime.now(timezone.utc),
        "jti": "abc123",
    }

    token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(HTTPException) as exc:
        await decode_token(token, TokenType.ACCESS)

    assert exc.value.detail == "Token has expired"


@pytest.mark.asyncio
async def test_decode_invalid_jwt_format():
    invalid_token = "this.is.not.jwt"

    with pytest.raises(HTTPException) as exc:
        await decode_token(invalid_token, TokenType.ACCESS)

    assert exc.value.detail == "Could not validate credentials"

def test_create_token_custom_expiration():
    token = create_token("123", TokenType.ACCESS, expires_delta=timedelta(minutes=1))
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["type"] == "access"

def test_create_token_uuid_input():
    user_id = uuid4()
    token = create_token(user_id, TokenType.ACCESS)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == str(user_id)

def test_create_token_exception():
    with patch("app.auth.jwt.settings.JWT_SECRET_KEY", None):
        with pytest.raises(HTTPException) as exc:
            create_token("123", TokenType.ACCESS)
        assert "Could not create token" in exc.value.detail

@pytest.mark.asyncio
async def test_decode_invalid_jwt_format():
    invalid_token = "this.is.not.jwt"

    with pytest.raises(HTTPException) as exc:
        await decode_token(invalid_token, TokenType.ACCESS)

    assert exc.value.detail == "Could not validate credentials"
