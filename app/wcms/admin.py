from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from wcms.models import WCMSUser, Bucket, Page, Tag, Comment, Asset

# Custom User Admin
class WCMSUserAdmin(UserAdmin):
    # Add custom fields to the user admin interface
    fieldsets = list(UserAdmin.fieldsets) + [
        ('Additional Info', {
            'fields': ('pfp', 'bio', 'dictionary', 'theme')
        }),
    ]
    
    # Fields to display in the list view
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'theme']
    
    # Fields that can be searched
    search_fields = ['username', 'email', 'first_name', 'last_name']

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
    search_fields = ['title', 'description']

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
