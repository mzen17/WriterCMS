from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from wcms.models import WCMSUser, Bucket, Page, Tag, Comment, Asset, Revisions

# Custom User Admin
class WCMSUserAdmin(UserAdmin):
    # Add custom fields to the user admin interface
    fieldsets = list(UserAdmin.fieldsets) + [
        ('Additional Info', {
            'fields': ('pfp', 'bio', 'dictionary', 'theme')
        }),
    ]
    
    # Fields to display in the list view
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'theme']
    
    # Fields that can be searched
    search_fields = ['email', 'first_name', 'last_name']

# Register the custom user model
admin.site.register(WCMSUser, WCMSUserAdmin)

# Register other models with basic admin interfaces
@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_owner', 'visibility']
    list_filter = ['visibility']
    search_fields = ['name', 'description']
    filter_horizontal = ['tags']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'bucket', 'public', 'porder']
    list_filter = ['public', 'bucket']
    search_fields = ['title']
    readonly_fields = ['description', 'slug']  # Make description read-only since it's calculated from revisions
    
    def get_readonly_fields(self, request, obj=None):
        # Always make description read-only since it's calculated from revisions
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if 'description' not in readonly_fields:
            readonly_fields.append('description')
        return readonly_fields

@admin.register(Revisions)
class RevisionsAdmin(admin.ModelAdmin):
    list_display = ['page', 'revision_number', 'timestamp']
    list_filter = ['timestamp', 'page__owner']
    search_fields = ['page__title']
    readonly_fields = ['revision_number', 'timestamp']  # Revisions cannot be edited or deleted
    
    def has_delete_permission(self, request, obj=None):
        # Revisions cannot be deleted
        return False
    
    def has_change_permission(self, request, obj=None):
        # Revisions cannot be edited
        return False
    
    def get_queryset(self, request):
        # Only show revisions for pages owned by the current user (if not superuser)
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(page__owner=request.user)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_name', 'tag_description']
    search_fields = ['tag_name']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['text_content', 'user', 'page']
    list_filter = ['page']
    search_fields = ['text_content']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'size', 'page']
    list_filter = ['page']
    search_fields = ['file_name']
