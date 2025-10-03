from passlib.context import CryptContext
from app.models.schemas import AdminCreate, AdminResponse
from app.services.firebase_service import FirebaseService
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db):
        self.db = db
        self.firebase_service = FirebaseService(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_admin(self, admin_data: AdminCreate) -> AdminResponse:
        """Create a new admin user"""
        # Check if admin already exists
        existing_admin = self.firebase_service.get_admin_by_email(admin_data.email)
        if existing_admin:
            raise ValueError("Admin with this email already exists")
        
        # Hash password
        hashed_password = self.get_password_hash(admin_data.password)
        
        # Create admin
        admin_dict = {
            "email": admin_data.email,
            "password": hashed_password,
            "name": admin_data.name
        }
        
        admin = self.firebase_service.create_admin(admin_dict)
        
        return AdminResponse(
            id=admin['id'],
            email=admin['email'],
            name=admin['name'],
            created_at=admin['created_at']
        )

    def authenticate_admin(self, email: str, password: str) -> Optional[AdminResponse]:
        """Authenticate admin with email and password"""
        admin = self.firebase_service.get_admin_by_email(email)
        if not admin:
            return None
        
        if not self.verify_password(password, admin['password']):
            return None
        
        return AdminResponse(
            id=admin['id'],
            email=admin['email'],
            name=admin['name'],
            created_at=admin['created_at']
        )
