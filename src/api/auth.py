from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.core.security import verify_password, create_access_token, get_password_hash

router = APIRouter()

# Simulasi Database User (Username: admin, Password: password123)
# Hash di bawah adalah hasil dari bcrypt("password123")
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("password123")
    }
}

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Jika sukses, buat token
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}