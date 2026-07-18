# tests/integration/test_user_auth.py

import pytest
from uuid import UUID
import pydantic_core
from sqlalchemy.exc import IntegrityError
from app.models.user import User

def test_password_hashing(db_session, fake_user_data):
    """Test password hashing and verification functionality"""
    original_password = "TestPass123"  # Use known password for test
    hashed = User.hash_password(original_password)
    
    user = User(
        first_name=fake_user_data['first_name'],
        last_name=fake_user_data['last_name'],
        email=fake_user_data['email'],
        username=fake_user_data['username'],
        password=hashed
    )
    
    assert user.verify_password(original_password) is True
    assert user.verify_password("WrongPass123") is False
    assert hashed != original_password

def test_user_registration(db_session, fake_user_data):
    """Test user registration process"""
    fake_user_data['password'] = "TestPass123"
    
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    
    assert user.first_name == fake_user_data['first_name']
    assert user.last_name == fake_user_data['last_name']
    assert user.email == fake_user_data['email']
    assert user.username == fake_user_data['username']
    assert user.is_active is True
    assert user.is_verified is False
    assert user.verify_password("TestPass123") is True

def test_duplicate_user_registration(db_session):
    """Test registration with duplicate email/username"""
    # First user data
    user1_data = {
        "first_name": "Test",
        "last_name": "User1",
        "email": "unique.test@example.com",
        "username": "uniqueuser1",
        "password": "TestPass123"
    }
    
    # Second user data with same email
    user2_data = {
        "first_name": "Test",
        "last_name": "User2",
        "email": "unique.test@example.com",  # Same email
        "username": "uniqueuser2",
        "password": "TestPass123"
    }
    
    # Register first user
    first_user = User.register(db_session, user1_data)
    db_session.commit()
    db_session.refresh(first_user)
    
    # Try to register second user with same email
    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)

def test_user_authentication(db_session, fake_user_data):
    """Test user authentication and token generation"""
    # Use fake_user_data from fixture
    fake_user_data['password'] = "TestPass123"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    
    # Test successful authentication
    auth_result = User.authenticate(
        db_session,
        fake_user_data['username'],
        "TestPass123"
    )
    
    assert auth_result is not None
    assert "access_token" in auth_result
    assert "token_type" in auth_result
    assert auth_result["token_type"] == "bearer"
    assert "user" in auth_result

def test_user_last_login_update(db_session, fake_user_data):
    """Test that last_login is updated on authentication"""
    fake_user_data['password'] = "TestPass123"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    
    # Authenticate and check last_login
    assert user.last_login is None
    auth_result = User.authenticate(db_session, fake_user_data['username'], "TestPass123")
    db_session.refresh(user)
    assert user.last_login is not None

def test_unique_email_username(db_session):
    """Test uniqueness constraints for email and username"""
    # Create first user with specific test data
    user1_data = {
        "first_name": "Test",
        "last_name": "User1",
        "email": "unique_test@example.com",
        "username": "uniqueuser",
        "password": "TestPass123"
    }
    
    # Register and commit first user
    User.register(db_session, user1_data)
    db_session.commit()
    
    # Try to create user with same email
    user2_data = {
        "first_name": "Test",
        "last_name": "User2",
        "email": "unique_test@example.com",  # Same email
        "username": "differentuser",
        "password": "TestPass123"
    }
    
    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)

def test_short_password_registration(db_session):
    """Test that registration fails with a short password"""
    # Prepare test data with a 5-character password
    test_data = {
        "first_name": "Password",
        "last_name": "Test",
        "email": "short.pass@example.com",
        "username": "shortpass",
        "password": "Shor1"  # 5 characters, should fail
    }
    
    # Attempt registration with short password
    with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
        User.register(db_session, test_data)

def test_invalid_token():
    """Test that invalid tokens are rejected"""
    invalid_token = "invalid.token.string"
    result = User.verify_token(invalid_token)
    assert result is None

def test_token_creation_and_verification(db_session, fake_user_data):
    """Test token creation and verification"""
    fake_user_data['password'] = "TestPass123"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    
    # Create token
    token = User.create_access_token({"sub": str(user.id)})
    
    # Verify token
    decoded_user_id = User.verify_token(token)
    assert decoded_user_id == user.id

def test_authenticate_with_email(db_session, fake_user_data):
    """Test authentication using email instead of username"""
    fake_user_data['password'] = "TestPass123"
    user = User.register(db_session, fake_user_data)
    db_session.commit()
    
    # Test authentication with email
    auth_result = User.authenticate(
        db_session,
        fake_user_data['email'],  # Using email instead of username
        "TestPass123"
    )
    
    assert auth_result is not None
    assert "access_token" in auth_result

def test_user_model_representation(test_user):
    """Test the string representation of User model"""
    expected = f"<User(name={test_user.first_name} {test_user.last_name}, email={test_user.email})>"
    assert str(test_user) == expected

def test_missing_password_registration(db_session):
    """Test that registration fails when no password is provided."""
    test_data = {
        "first_name": "NoPassword",
        "last_name": "Test",
        "email": "no.password@example.com",
        "username": "nopassworduser",
        # Password is missing
    }
    
    # Adjust the expected error message
    with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
        User.register(db_session, test_data)

# Lines 37
def test_get_current_user_minimal_payload():
    """
    Ensure get_current_user returns a default UserResponse when the JWT
    contains only a 'sub' claim.
    """
    from app.auth.dependencies import get_current_user
    from app.models.user import User
    from fastapi import Depends
    from fastapi.testclient import TestClient
    from app.main import app

    # Create a token with ONLY a 'sub' claim
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = User.create_access_token({"sub": user_id})

    # Temporary test route using the dependency
    @app.get("/test-current-user")
    def test_route(current_user=Depends(get_current_user)):
        return current_user

    client = TestClient(app)

    response = client.get(
        "/test-current-user",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == user_id
    assert data["username"] == "unknown"
    assert data["email"] == "unknown@example.com"
    assert data["first_name"] == "Unknown"
    assert data["last_name"] == "User"
    assert data["is_active"] is True
    assert data["is_verified"] is False

# Line 37, 65
# def test_get_current_user_invalid_payload():
#     """
#     Force get_current_user to hit the fallback exception block (line 65)
#     by providing a decoded payload missing both 'username' and 'sub'.
#     """
#     from app.auth.dependencies import get_current_user
#     from app.models.user import User
#     from fastapi import Depends
#     from fastapi.testclient import TestClient
#     from app.main import app

#     # Create a token with an invalid payload (no 'username', no 'sub')
#     token = User.create_access_token({"foo": "bar"})

#     @app.get("/test-invalid-payload")
#     def test_route(current_user=Depends(get_current_user)):
#         return current_user

#     client = TestClient(app)

#     response = client.get(
#         "/test-invalid-payload",
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     # Should hit the fallback exception → 401
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Could not validate credentials"


# Lines 76-77
import pytest
from fastapi import HTTPException
from app.auth.jwt import decode_token
from app.schemas.token import TokenType

@pytest.mark.asyncio
async def test_decode_invalid_jwt_format():
    invalid_token = "this.is.not.jwt"

    with pytest.raises(HTTPException) as exc:
        await decode_token(invalid_token, TokenType.ACCESS)

    assert exc.value.detail == "Could not validate credentials"

# Lines 90-127
from app.auth.jwt import create_token
from app.schemas.token import TokenType
from datetime import timedelta
from jose import jwt
from app.core.config import get_settings

settings = get_settings()

def test_create_token_custom_expiration():
    token = create_token("123", TokenType.ACCESS, expires_delta=timedelta(minutes=1))
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["sub"] == "123"
    assert decoded["type"] == "access"

from uuid import uuid4
from app.auth.jwt import create_token
from app.schemas.token import TokenType
from jose import jwt
from app.core.config import get_settings

settings = get_settings()

def test_create_token_uuid_input():
    user_id = uuid4()
    token = create_token(user_id, TokenType.ACCESS)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert decoded["sub"] == str(user_id)

from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.auth.jwt import create_token
from app.schemas.token import TokenType

def test_create_token_exception():
    with patch("app.auth.jwt.settings.JWT_SECRET_KEY", None):
        with pytest.raises(HTTPException) as exc:
            create_token("123", TokenType.ACCESS)

        assert "Could not create token" in exc.value.detail

# Lines 141-161
import pytest
from fastapi import HTTPException
from app.auth.jwt import get_current_user, create_token
from app.schemas.token import TokenType

@pytest.mark.asyncio
async def test_get_current_user_not_found(db_session):
    token = create_token("non-existent-id", TokenType.ACCESS)

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db=db_session)

    assert exc.value.detail == "User not found"

import pytest
from fastapi import HTTPException
from app.auth.jwt import get_current_user, create_token
from app.schemas.token import TokenType

@pytest.mark.asyncio
async def test_get_current_user_inactive(db_session, test_user):
    test_user.is_active = False
    db_session.commit()

    token = create_token(str(test_user.id), TokenType.ACCESS)

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db=db_session)

    assert exc.value.detail == "Inactive user"