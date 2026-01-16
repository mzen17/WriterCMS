from django.shortcuts import render
from django.db.models import Q, Case, When, IntegerField, Value, CharField
from django.db.models.functions import Length
from django.conf import settings
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect
from wcms.serializers.asset import get_creds, retrieve_image

from wcms.firebase_auth import FirebaseAuthentication

from rest_framework import routers, serializers, viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

import wcms.models as wm
from wcms.serializers import (
    WCMSUserSerializer,
    BucketSerializer,
    PageSerializer,
    TagSerializer,
    CommentSerializer,
    AssetSerializer,
    RevisionSerializer,
    CreateRevisionSerializer
)
from wcms.permissions import IsOwnerOrReadOnly, IsAuthenticatedOrReadOnlyPublic, RestrictNonGETForGuests, ReadOnlyPermission

# max page size = 5
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'  # Allows client to specify page size with ?size=x
    max_page_size = 5             # Maximum page size a client can request
    page_query_param = 'pageno' 

# Note: CSRF token and login/logout views removed - using Firebase authentication only

class WCMSUserViewSet(viewsets.ModelViewSet):
    queryset = wm.WCMSUser.objects.all()
    serializer_class = WCMSUserSerializer

    def get_permissions(self):
        """
        Firebase handles user creation, so we disable the create action.
        Allow basic user listing (GET /users/) by anyone (but limit data in serializer).
        Allow retrieval, update, partial update of *own* profile by authenticated user only.
        Disable deletion to prevent accidental data loss.
        """
        if self.action == 'create':
            # Disable user creation - Firebase handles this automatically
            permission_classes = [permissions.IsAdminUser]  # Only admin can manually create users
        elif self.action == 'list':
            # Anyone can list users, but restrict to GET only for unauthenticated
            permission_classes = [permissions.AllowAny, RestrictNonGETForGuests]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action == 'destroy':
            # Disable user deletion - Firebase users should be managed through Firebase
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Override create to return helpful message.
        Users are created automatically when they authenticate with Firebase.
        """
        return Response({
            'error': 'User creation is handled automatically through Firebase authentication. '
                    'Users are created when they first authenticate with valid Firebase credentials.'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user's profile"""
        print(request.data)
        serializer = self.get_serializer(request.user)
        print(serializer.data)
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
        Unauthenticated users can only view public buckets (read-only).
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [IsAuthenticatedOrReadOnlyPublic, RestrictNonGETForGuests]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Authenticated users can see their own buckets or buckets that they are a reader of.
        Unauthenticated users can only see public buckets.
        """
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
        else:
            # Unauthenticated users can only see public buckets
            return wm.Bucket.objects.filter(
                visibility=True
            ).select_related(
                'user_owner',
                'bucket_owner'
            ).prefetch_related(
                'tags',
                'pages',
                'bucket_set'
            ).distinct()

    def perform_create(self, serializer):
        serializer.save(user_owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to prevent deletion of buckets with children or pages"""
        bucket = self.get_object()
        
        # Check for child buckets
        child_buckets_count = bucket.bucket_set.count()
        if child_buckets_count > 0:
            return Response(
                {
                    'error': 'Cannot delete bucket with child buckets',
                    'detail': f'This bucket has {child_buckets_count} child bucket(s). Remove or reassign child buckets before deletion.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for pages
        pages_count = bucket.pages.count()
        if pages_count > 0:
            return Response(
                {
                    'error': 'Cannot delete bucket with pages',
                    'detail': f'This bucket has {pages_count} page(s). Remove or reassign pages before deletion.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If no children or pages, proceed with normal deletion
        return super().destroy(request, *args, **kwargs)


class PageViewSet(viewsets.ModelViewSet):

    queryset = wm.Page.objects.all()
    serializer_class = PageSerializer
    lookup_field="slug"

    def get_permissions(self):
        """
        Authenticated users can create pages.
        Unauthenticated users can only view public pages (read-only).
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [IsAuthenticatedOrReadOnlyPublic, RestrictNonGETForGuests]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action in ['create_revision', 'list_revisions']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Authenticated users can see their own pages or pages in buckets they can read.
        Unauthenticated users can only see public pages in public buckets.
        """
        user = self.request.user
        print(str(user))

        if user.id:
            return wm.Page.objects.filter(
                Q(owner=user) |
                Q(readers=user) | # Pages where user is directly a reader
                Q(bucket__readers=user) | # Pages in buckets where user is a reader
                Q(public=True, bucket__visibility=True) # Public pages in public buckets
            ).distinct()
        else:
            # Unauthenticated users can only see public pages in public buckets
            return wm.Page.objects.filter(
                public=True, 
                bucket__visibility=True
            ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """Allow updates to page metadata but prevent content changes"""
        # Remove description from request data if present
        if 'description' in request.data:
            return Response(
                {"error": "Content updates are not allowed. Use the create_revision endpoint to modify content."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Allow partial updates to page metadata but prevent content changes"""
        # Remove description from request data if present
        if 'description' in request.data:
            return Response(
                {"error": "Content updates are not allowed. Use the create_revision endpoint to modify content."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='revisions')
    def create_revision(self, request, slug=None):
        """Create a new revision for the page"""
        page = self.get_object()
        
        # Check if user owns the page
        if request.user != page.owner:
            return Response(
                {"error": "Only the page owner can create revisions."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CreateRevisionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                revision = wm.Revisions.create_revision(
                    page=page,
                    new_content=serializer.validated_data['content'],
                    user=request.user
                )
                
                revision_serializer = RevisionSerializer(
                    revision, 
                    context={'request': request}
                )
                return Response(revision_serializer.data, status=status.HTTP_201_CREATED)
                
            except PermissionError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to create revision: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='revisions/list')
    def list_revisions(self, request, slug=None):
        """List all revisions for the page (only for page owner)"""
        page = self.get_object()
        
        # Check if user owns the page
        if request.user != page.owner:
            return Response(
                {"error": "Only the page owner can view revisions."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        revisions = wm.Revisions.objects.filter(page=page).order_by('-revision_number')
        serializer = RevisionSerializer(
            revisions, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)


class RevisionViewSet(viewsets.ReadOnlyModelViewSet):

    """
    ViewSet for viewing revisions. 
    Revisions are read-only and can only be viewed by page owners.
    """
    queryset = wm.Revisions.objects.all()
    serializer_class = RevisionSerializer
    
    def get_permissions(self):
        """Only authenticated users can view revisions"""
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Only show revisions for pages owned by the current user"""
        user = self.request.user
        if user.is_superuser:
            return wm.Revisions.objects.all()
        return wm.Revisions.objects.filter(page__owner=user)


class TagViewSet(viewsets.ModelViewSet):

    queryset = wm.Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = StandardResultsSetPagination 

    def get_queryset(self):
        """
        Custom queryset with relevancy-based filtering by name.
        Supports 'name' query parameter for smart tag searching.
        
        Search logic:
        1. Exact matches (highest priority)
        2. Starts with query (second priority) 
        3. Contains query (lowest priority)
        4. Within each priority, shorter names come first
        
        Examples:
        - name=b returns: bob, bbob, bobb (starts with 'b', shortest first)
        - name=bo returns: bob, bobb (starts with 'bo', shortest first)  
        - name=bobb returns: bobb (exact match)
        """
        queryset = wm.Tag.objects.all()
        
        # Get the name filter parameter
        name_query = self.request.query_params.get('tag_name', None)
        print(name_query)
        
        if name_query:
            # Create priority-based ordering with Case/When
            queryset = queryset.filter(
                tag_name__icontains=name_query
            ).annotate(
                # Priority scoring: 1=exact, 2=starts_with, 3=contains
                priority=Case(
                    When(tag_name__iexact=name_query, then=Value(1)),
                    When(tag_name__istartswith=name_query, then=Value(2)), 
                    default=Value(3),
                    output_field=IntegerField()
                ),
                # Length for secondary sorting within same priority
                name_length=Length('tag_name')
            ).order_by('priority', 'name_length', 'tag_name')
        print(queryset)
        return queryset

    def get_permissions(self):
        """
        Authenticated users can create, read, and delete tags.
        Unauthenticated users can only view tags (read-only).
        Edit/update operations are not allowed for anyone.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            # Allow both authenticated and unauthenticated users to view tags
            permission_classes = [IsAuthenticatedOrReadOnlyPublic, RestrictNonGETForGuests]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, ReadOnlyPermission]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save()

class CommentViewSet(viewsets.ModelViewSet):

    queryset = wm.Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        """
        Authenticated users can create comments.
        Unauthenticated users can only view public comments (read-only).
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            # Allow both authenticated and unauthenticated users to view
            permission_classes = [IsAuthenticatedOrReadOnlyPublic, RestrictNonGETForGuests]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Authenticated users can see comments on:
        1. Their own pages (regardless of privacy)
        2. Pages where they are part of pages.readers (manytomany field) OR are part of the buckets.readers (also m2m field)
        3. Public pages in public buckets
        
        Unauthenticated users can only see comments on public pages in public buckets.
        """
        user = self.request.user
        if user.is_authenticated:
            return wm.Comment.objects.filter(
                Q(page__owner=user) |  # Own pages
                Q(page__readers=user) |  # Pages where user is a reader
                Q(page__bucket__readers=user) |  # Buckets where user is a reader
                Q(page__public=True, page__bucket__visibility=True)  # Public pages in public buckets
            ).distinct()
        else:
            # Unauthenticated users can only see comments on public pages in public buckets
            return wm.Comment.objects.filter(
                page__public=True, 
                page__bucket__visibility=True
            ).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) # Assuming 'user' is the FK to WCMSUser on Comment model


class AssetViewSet(viewsets.ModelViewSet):

    queryset = wm.Asset.objects.all()
    serializer_class = AssetSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'file_name'
    lookup_value_regex = '[^/]+'  # Allow dots and other characters in file_name

    def get_permissions(self):
        """
        Authenticated users can create assets.
        Unauthenticated users can only view public assets (read-only).
        Update/delete only by owner.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'list']:
            # Allow both authenticated and unauthenticated users to view
            permission_classes = [IsAuthenticatedOrReadOnlyPublic, RestrictNonGETForGuests]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Authenticated users can see assets from pages they can access (owner, reader, or public).
        Unauthenticated users can only see assets from public pages in public buckets.
        Supports ?owner=<user_id> filter to show only assets owned by a specific user.
        """
        user = self.request.user
        owner_filter = self.request.query_params.get('owner', None)
        
        if user.is_authenticated:
            # If owner filter is applied, filter by owner ID
            if owner_filter:
                try:
                    if owner_filter == "me":
                        return wm.Asset.objects.filter(
                        Q(owner=user)
                    ).distinct()

                    owner_id = int(owner_filter)
                    return wm.Asset.objects.filter(
                        Q(owner_id=owner_id, owner=user) |  # Own assets
                        Q(owner_id=owner_id, can_share=True)  # Shared assets from that owner
                    ).distinct()
                except ValueError:
                    pass  # Invalid owner ID, ignore filter
            
            return wm.Asset.objects.filter(
                Q(owner=user) |
                Q(can_share=True) # Public assets in public pages/buckets
            ).distinct()
        else:
            # Unauthenticated users can only see assets from public pages in public buckets
            if owner_filter:
                try:
                    owner_id = int(owner_filter)
                    return wm.Asset.objects.filter(owner_id=owner_id, can_share=True)
                except ValueError:
                    pass
            return wm.Asset.objects.filter(
                can_share=True, 
            ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        """Delete the asset and its S3 file"""
        from wcms.serializers.asset import delete_asset
        delete_asset(instance)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_file_url(request, file_name):
    """
    Custom view to get a presigned URL for a file.
    Checks if file exists and if user has permission to access it.
    Redirects to the presigned S3 URL.
    """    
    # Check if file exists
    try:
        asset = wm.Asset.objects.get(file_name=file_name)
    except wm.Asset.DoesNotExist:
        return Response(
            {'error': 'File not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions: can_share OR owner
    user = request.user
    if not asset.can_share:
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required to access this file'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if asset.owner != user:
            return Response(
                {'error': 'You do not have permission to access this file'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Generate presigned URL and redirect
    s3, bucket = get_creds()
    presigned_url = retrieve_image(s3, bucket, file_name)
    
    return HttpResponseRedirect(presigned_url)


router = routers.DefaultRouter()
router.register(r'users', WCMSUserViewSet)
router.register(r'buckets', BucketViewSet)
router.register(r'pages', PageViewSet)
router.register(r'revisions', RevisionViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'assets', AssetViewSet)