import firebase_admin
from firebase_admin import credentials, auth
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import logging
import os

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        service_account_path = os.environ.get('FIREBASE_PATH')
        
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase initialized with service account: {service_account_path}")
        else:
            logger.warning("Firebase service account path not found. Set FIREBASE_PATH environment variable.")

# Initialize Firebase on module load
initialize_firebase()

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Simple Firebase authentication for Django REST Framework.
    Extracts Bearer token from Authorization header and validates with Firebase.
    """
    
    def authenticate(self, request):
        """Authenticate request using Firebase ID token"""
        auth_header = authentication.get_authorization_header(request)
        
        if not auth_header:
            return None
        
        # Parse Bearer token
        try:
            auth_parts = auth_header.split()
            if len(auth_parts) != 2 or auth_parts[0].lower() != b'bearer':
                return None
            token = auth_parts[1].decode('utf-8')
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token format')
        
        return self.authenticate_token(token)
    
    def authenticate_token(self, token):
        """Validate Firebase token and get/create Django user"""
        try:
            # Check if Firebase is initialized
            if not firebase_admin._apps:
                logger.error("Firebase not initialized - check FIREBASE_PATH")
                return None
            
            # Verify Firebase ID token
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            
            # Get or create Django user
            User = get_user_model()
            user, created = User.objects.get_or_create(
                firebase_uid=firebase_uid,
                defaults={
                    'username': email or firebase_uid,
                    'email': email,
                    'first_name': name,
                    'is_active': True,
                }
            )
            
            # Update user info if changed (but preserve manual changes)
            if not created:
                updated = False
                if user.email != email and email:
                    user.email = email
                    updated = True
                if not user.first_name and name:
                    user.first_name = name
                    updated = True
                if updated:
                    user.save()
            
            return (user, token)
            
        except auth.InvalidIdTokenError:
            logger.warning("Invalid Firebase ID token")
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except auth.ExpiredIdTokenError:
            logger.warning("Expired Firebase ID token")
            raise exceptions.AuthenticationFailed('Firebase token expired')
        except Exception as e:
            logger.error(f"Firebase authentication error: {e}")
            raise exceptions.AuthenticationFailed('Firebase authentication failed')
    
    def authenticate_header(self, request):
        """Return WWW-Authenticate header value for 401 responses"""
        return 'Bearer'
