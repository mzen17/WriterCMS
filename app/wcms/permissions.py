from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    Read permissions (GET, HEAD, OPTIONS) are allowed to any authenticated user.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for any safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions (PUT, PATCH, DELETE) are only allowed to the owner.
        # Assuming 'owner' field or 'user_owner' field exists on the model
        # Adjust 'obj.owner' or 'obj.user_owner' based on your model's actual field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user_owner'): # For Bucket model
            return obj.user_owner == request.user
        else:
            return obj == request.user