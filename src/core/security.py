from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
# Hapus import passlib dan CryptContext
import bcrypt # Gunakan bcrypt langsung
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Konfigurasi Rahasia
SECRET_KEY = "Tubes TST"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup Skema Auth FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def verify_password(plain_password: str, hashed_password: str):
    # Logika verifikasi menggunakan bcrypt langsung
    # Encode string ke bytes karena bcrypt butuh bytes
    password_byte = plain_password.encode('utf-8')
    # hashed_password dari database mungkin str, ubah ke bytes
    hashed_password_byte = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_byte, hashed_password_byte)

def get_password_hash(password: str):
    # Logika hashing menggunakan bcrypt langsung
    password_byte = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_byte, salt)
    # Kembalikan sebagai string agar mudah disimpan di JSON/Dict
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username