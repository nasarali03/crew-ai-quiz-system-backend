import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Global Firebase client
db: Optional[firestore.Client] = None

def init_db():
    """Initialize Firebase connection"""
    global db
    
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            
            print(f"Looking for Firebase credentials...")
            print(f"FIREBASE_CREDENTIALS_PATH: {cred_path}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Files in current directory: {os.listdir('.')}")
            
            if cred_path and os.path.exists(cred_path):
                # Use service account file
                print(f"✅ Using Firebase credentials from: {cred_path}")
                cred = credentials.Certificate(cred_path)
            elif cred_json:
                # Use JSON credentials from environment variable
                import json
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                print("✅ Using Firebase credentials from environment variable")
            else:
                # Try to find serviceAccountKey.json in current directory
                service_account_path = "serviceAccountKey.json"
                if os.path.exists(service_account_path):
                    print(f"✅ Using Firebase credentials from: {service_account_path}")
                    cred = credentials.Certificate(service_account_path)
                else:
                    # Try alternative names
                    alt_names = ["firebase-service-account.json", "firebase-credentials.json", "service-account.json"]
                    for alt_name in alt_names:
                        if os.path.exists(alt_name):
                            print(f"✅ Using Firebase credentials from: {alt_name}")
                            cred = credentials.Certificate(alt_name)
                            break
                    else:
                        print("❌ No Firebase credentials found!")
                        print("Please either:")
                        print("1. Set FIREBASE_CREDENTIALS_PATH in .env file")
                        print("2. Place serviceAccountKey.json in the backend directory")
                        print("3. Set FIREBASE_CREDENTIALS_JSON in .env file")
                        
                        print("4. Use the project ID directly (less secure)")
                        
                        # Try to use project ID directly (less secure but works for development)
                        project_id = os.getenv("FIREBASE_PROJECT_ID", "crew-ai-de84c")
                        if project_id:
                            print(f"⚠️  Using project ID directly: {project_id}")
                            print("⚠️  This is less secure and may not work for all operations")
                            # For development only - this won't work for production
                            try:
                                # Try to initialize with default credentials
                                firebase_admin.initialize_app()
                                print("✅ Firebase initialized with default credentials")
                            except Exception as default_error:
                                print(f"❌ Default credentials also failed: {default_error}")
                                return None
                        else:
                            return None
            
            if 'cred' in locals():
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized successfully")
        else:
            print("✅ Firebase already initialized")
        
        # Get Firestore client
        db = firestore.client()
        return db
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        print("The server will start without Firebase. Some features may not work.")
        return None

def get_db():
    """Get database connection"""
    global db
    if db is None:
        db = init_db()
    return db

def close_db():
    """Close database connection (Firebase doesn't need explicit closing)"""
    pass
