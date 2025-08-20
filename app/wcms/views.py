from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import routers, serializers, viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

import wcms.models as wm
from wcms.serializers import (
    WCMSUserSerializer,
    BucketSerializer,
    PageSerializer,
    TagSerializer,
    CommentSerializer,
    AssetSerializer
)
from wcms.permissions import IsOwnerOrReadOnly

# max page size = 5
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'  # Allows client to specify page size with ?size=x
    max_page_size = 5             # Maximum page size a client can request
    page_query_param = 'pageno' 

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Get CSRF token for frontend"""
    return Response({'csrfToken': get_token(request)})

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Custom login view that uses session authentication with HTTP-only cookies"""
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            # Use Django's built-in login function to create a session
            login(request, user)
            
            response = Response({
                'success': True,
                'user_id': user.pk,
                'username': user.username
            })
            
            # Set additional security headers for the session cookie
            response.set_cookie(
                'sessionid', 
                request.session.session_key,
                max_age=settings.SESSION_COOKIE_AGE,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=True,
                samesite='Lax'
            )
            
            return response

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout view that clears the session"""
    logout(request)
    response = Response({'success': True, 'message': 'Logged out successfully'})
    response.delete_cookie('sessionid')
    return response

class WCMSUserViewSet(viewsets.ModelViewSet):
    queryset = wm.WCMSUser.objects.all()
    serializer_class = WCMSUserSerializer

    def get_permissions(self):
        """
        Allow user creation (POST) by anyone.
        Allow listing (GET /users/) by anyone.
        Allow retrieval, update, partial update, and deletion of *own* profile by authenticated user.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list':
            # Anyone can list users
            permission_classes = [permissions.AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Authenticated users can retrieve/update/delete their own profile
            # IsOwnerOrReadOnly needs to check obj == request.user for WCMSUser model itself
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            # Default for other actions (e.g., any custom @action not covered)
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create user and generate auth token"""
        user = serializer.save()
        Token.objects.create(user=user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class BucketViewSet(viewsets.ModelViewSet):
    queryset = wm.Bucket.objects.all()
    serializer_class = BucketSerializer
    pagination_class = StandardResultsSetPagination 
    lookup_field="slug"

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def get_permissions(self):
        """
        Authenticated users can create buckets.
        Read access (list, retrieve) based on queryset.
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            # Listing/retrieving handled by get_queryset, just need authentication to see
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only owner can update/delete
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Users can only see their own buckets or buckets that they are a read of using django Q"""
        user = self.request.user
        if user.is_authenticated:
            return wm.Bucket.objects.filter(
                Q(user_owner=user) |
                Q(readers=user) |
                Q(visibility=True)
            ).select_related(
                'user_owner',  # Optimize user_owner lookup
                'bucket_owner'  # Optimize bucket_owner lookup
            ).prefetch_related(
                'tags',  # Optimize tags lookup
                'pages',  # Optimize pages lookup for the bucket
                'bucket_set'  # Optimize children buckets lookup (reverse foreign key)
            ).distinct()
        return wm.Bucket.objects.none()

    def perform_create(self, serializer):
        serializer.save(user_owner=self.request.user)


class PageViewSet(viewsets.ModelViewSet):
    queryset = wm.Page.objects.all()
    serializer_class = PageSerializer
    lookup_field="slug"

    def get_permissions(self):
        """
        Authenticated users can create pages.
        Read access (list, retrieve) based on queryset.
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Users can only see their own pages or pages in buckets they can read"""
        user = self.request.user
        if user.is_authenticated:
            return wm.Page.objects.filter(
                Q(owner=user) |
                Q(readers=user) | # Pages where user is directly a reader
                Q(bucket__readers=user) | # Pages in buckets where user is a reader
                Q(public=True, bucket__visibility=True) # Public pages in public buckets
            ).distinct()
        return wm.Page.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = wm.Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        """
        Authenticated users can create, read, and delete tags.
        Edit/update operations are not allowed.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, ReadOnly]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = wm.Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        """
        Authenticated users can create comments.
        Read access (list, retrieve) based on queryset.
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Users can see comments on:
        1. Their own pages (regardless of privacy)
        2. Pages where they are part of pages.readers (manytomany field) OR are part of the buckets.readers (also m2m field)
        3. Public pages in public buckets
        """
        user = self.request.user
        if user.is_authenticated:
            return wm.Comment.objects.filter(
                Q(page__owner=user) |  # Own pages
                Q(page__readers=user) |  # Pages where user is a reader
                Q(page__bucket__readers=user) |  # Buckets where user is a reader
                Q(page__public=True, page__bucket__visibility=True)  # Public pages in public buckets
            ).distinct()
        return wm.Comment.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) # Assuming 'user' is the FK to WCMSUser on Comment model


class AssetViewSet(viewsets.ModelViewSet):
    queryset = wm.Asset.objects.all()
    serializer_class = AssetSerializer

    def get_permissions(self):
        """
        Authenticated users can create assets.
        Read access (list, retrieve) based on queryset.
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Users can only see assets from pages they can access (owner, reader, or public)"""
        user = self.request.user
        if user.is_authenticated:
            return wm.Asset.objects.filter(
                Q(page__owner=user) |
                Q(page__readers=user) |
                Q(page__bucket__readers=user) | # Assets in pages in buckets where user is a reader
                Q(page__public=True, page__bucket__visibility=True) # Public assets in public pages/buckets
            ).distinct()
        return wm.Asset.objects.none()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user) # Assuming 'uploaded_by' is the FK to WCMSUser on Asset model


router = routers.DefaultRouter()
router.register(r'users', WCMSUserViewSet)
router.register(r'buckets', BucketViewSet)
router.register(r'pages', PageViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'assets', AssetViewSet)