from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.database import get_db
from app.models.schemas import AdminCreate, AdminLogin, AdminResponse, Token, TokenData
from app.services.auth_service import AuthService

load_dotenv()

router = APIRouter()

# Security
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
        token_data = TokenData(admin_id=admin_id)
    except JWTError:
        raise credentials_exception
    
    from app.services.firebase_service import FirebaseService
    firebase_service = FirebaseService(db)
    admin = await firebase_service.get_admin_by_id(token_data.admin_id)
    if admin is None:
        raise credentials_exception
    return admin

@router.post("/register", response_model=AdminResponse)
async def register_admin(admin_data: AdminCreate, db = Depends(get_db)):
    """Register a new admin"""
    auth_service = AuthService(db)
    return await auth_service.create_admin(admin_data)

@router.post("/login", response_model=Token)
async def login_admin(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    """Login admin and return access token"""
    auth_service = AuthService(db)
    admin = await auth_service.authenticate_admin(form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
async def read_admin_me(current_admin = Depends(get_current_admin)):
    """Get current admin information"""
    return current_admin
