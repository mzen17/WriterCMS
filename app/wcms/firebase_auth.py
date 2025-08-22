import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.utils.deprecation import MiddlewareMixin
from rest_framework import authentication, exceptions
import logging
import os

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        # Check for service account key path from environment
        service_account_path = os.environ.get('FIREBASE_PATH')
        
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            logger.info(f"Firebase initialized with service account: {service_account_path}")
        else:
            logger.warning("Firebase service account path not found. Set FIREBASE_PATH environment variable.")

# Initialize Firebase on module load
initialize_firebase()

class FirebaseAuthenticationBackend(BaseBackend):
    """
    Django authentication backend for Firebase ID tokens.
    This allows Firebase authentication to work with Django's auth system.
    """
    
    def authenticate(self, request, username=None, password=None, firebase_token=None, **kwargs):
        """
        Authenticate using Firebase ID token.
        """
        if not firebase_token:
            return None
        
        return self._authenticate_token(firebase_token)
    
    def get_user(self, user_id):
        """
        Get user by ID for Django's auth system.
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def _authenticate_token(self, token):
        """
        Authenticate the Firebase ID token and return Django user.
        """
        try:
            # Check if Firebase is initialized
            if not firebase_admin._apps:
                logger.error("Firebase Admin SDK not initialized")
                return None
                
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            
            # Get or create Django user based on Firebase UID
            User = get_user_model()
            
            try:
                # Try to get existing user by Firebase UID
                user = User.objects.get(firebase_uid=uid)
                
                # Update user info if it has changed, but be careful not to override manual changes
                updated = False
                
                # Always sync email from Firebase
                if user.email != email and email:
                    user.email = email
                    updated = True
                
                if not user.first_name and name:
                    user.first_name = name
                    updated = True
                    
                if updated:
                    user.save()
                    logger.info(f"Updated user info for: {user.username}")
                    
            except User.DoesNotExist:
                logger.info(f"Creating new user for Firebase UID: {uid}")
                username = email or uid  # Use email as username, fallback to uid
                
                # Ensure username is unique (only for new user creation)
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                user = User.objects.create(
                    firebase_uid=uid,
                    email=email,
                    username=username,
                    first_name=name,
                    is_active=True,
                    # Don't set password - Firebase handles authentication
                )
                
                logger.info(f"Created new user: {user.username} (Firebase UID: {uid})")
            
            return user
            
        except auth.InvalidIdTokenError as e:
            logger.warning(f"Invalid Firebase ID token: {e}")
            return None
        except auth.ExpiredIdTokenError as e:
            logger.warning(f"Expired Firebase ID token: {e}")
            return None
        except Exception as e:
            logger.error(f"Firebase authentication error: {e}")
            return None

class FirebaseAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate users via Firebase ID tokens for regular Django views.
    """
    
    def process_request(self, request):
        """
        Extract Firebase token from Authorization header and authenticate user.
        """
        # Skip if user is already authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return
        
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return
        
        # Parse Bearer token
        try:
            auth_parts = auth_header.split()
            if len(auth_parts) == 2 and auth_parts[0].lower() == 'bearer':
                token = auth_parts[1]
                
                # Use the Firebase backend to authenticate
                backend = FirebaseAuthenticationBackend()
                user = backend._authenticate_token(token)
                
                if user:
                    # Set the user on the request
                    request.user = user
                    # Set the backend used for authentication
                    user.backend = 'wcms.firebase_auth.FirebaseAuthenticationBackend'
                    
        except Exception as e:
            logger.error(f"Firebase authentication middleware error: {e}")
            
        return

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for Firebase ID tokens in Django REST Framework.
    This replaces Django's built-in authentication system for API endpoints.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Firebase ID token from Authorization header.
        """
        auth_header = authentication.get_authorization_header(request)
        
        if not auth_header:
            return None
            
        try:
            # Split the header to get the token
            auth_parts = auth_header.split()
            
            if len(auth_parts) != 2 or auth_parts[0].lower() != b'bearer':
                return None
                
            token = auth_parts[1].decode('utf-8')
            
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain invalid characters.')
        
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, token):
        """
        Authenticate the token using Firebase Admin SDK and get/create Django user.
        """
        try:
            # Use the shared backend logic
            backend = FirebaseAuthenticationBackend()
            user = backend._authenticate_token(token)
            
            if not user:
                raise exceptions.AuthenticationFailed('Invalid or expired Firebase ID token.')
                
            return (user, token)
            
        except auth.InvalidIdTokenError as e:
            logger.warning(f"Invalid Firebase ID token: {e}")
            raise exceptions.AuthenticationFailed('Invalid Firebase ID token.')
        except auth.ExpiredIdTokenError as e:
            logger.warning(f"Expired Firebase ID token: {e}")
            raise exceptions.AuthenticationFailed('Firebase ID token has expired.')
        except Exception as e:
            logger.error(f"Firebase authentication error: {e}")
            raise exceptions.AuthenticationFailed('Firebase authentication failed.')
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'
