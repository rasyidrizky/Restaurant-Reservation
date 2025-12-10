from datetime import timedelta
import pytest
from fastapi import HTTPException
from src.core.security import verify_password, get_password_hash, create_access_token, get_current_user

def test_password_hashing():
    password = "secret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_jwt_creation_default():
    token = create_access_token(data={"sub": "testuser"})
    assert isinstance(token, str)

def test_jwt_creation_custom_expire():
    delta = timedelta(minutes=60)
    token = create_access_token(data={"sub": "testuser"}, expires_delta=delta)
    assert isinstance(token, str)

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("invalid.token.here")
    assert excinfo.value.status_code == 401