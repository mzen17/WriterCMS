"""
This serializer is diff from wcms because this is for the system wide data.
"""
from django.urls import path, include
from django.contrib.auth.models import User
from django.db.models import Q

import wcms.models as wm

from rest_framework import serializers
from django.contrib.auth import get_user_model

class WCMSUserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = wm.WCMSUser
        fields = ['url', 'username', 'email', 'first_name', 'last_name', 'pfp', 'bio', 'dictionary', 'theme', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = wm.WCMSUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update fields normally
        for attr, value in validated_data.items():
            if attr == 'password':
                # Only set password if it's provided in the update data
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class BucketChildSerializer(serializers.ModelSerializer):
    """Simplified serializer for child buckets"""
    class Meta:
        model = wm.Bucket
        fields = ['slug', 'name', 'banner']

class PageSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for pages within a bucket"""
    class Meta:
        model = wm.Page
        fields = ['slug', 'title']

class BucketSerializer(serializers.HyperlinkedModelSerializer):
    # Add custom fields for hydrated data
    user_owner_name = serializers.CharField(source='user_owner.username', read_only=True)
    bucket_owner_name = serializers.CharField(source='bucket_owner.name', read_only=True)
    bucket_owner_slug = serializers.CharField(source='bucket_owner.slug', read_only=True)
    can_edit = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()
    
    # Add nested serializers for children buckets and pages
    children_buckets = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()
    
    # Configure the bucket_owner hyperlinked field to use slug
    bucket_owner = serializers.HyperlinkedRelatedField(
        view_name='bucket-detail',
        lookup_field='slug',
        queryset=wm.Bucket.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        lookup_field="slug"
        model = wm.Bucket
        fields = [
            'url',
            'name',
            'user_owner',  # Keep original URL field
            'user_owner_name',  # Add hydrated username
            'bucket_owner',
            'bucket_owner_slug',
            'bucket_owner_name',  # Add hydrated bucket name
            'visibility',
            'tags',
            'tag_names',  # Add hydrated tag names
            'description',
            'banner',
            'can_edit',
            'slug',
            'background',
            'children_buckets',  # Add children buckets
            'pages'  # Add pages
        ]
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

        read_only_fields = ['user_owner', 'user_owner_name', 'bucket_owner_name', 'tag_names', 'can_edit', 'children_buckets', 'pages'] 

    def get_tag_names(self, obj):
        """Return a list of tag names instead of URLs"""
        return [tag.tag_name for tag in obj.tags.all()]
    
    def get_can_edit(self, obj):
        return self.context['request'].user == obj.user_owner
    
    def get_children_buckets(self, obj):
        """Get all child buckets with their banner, name, and id that the current user can access"""
        user = self.context['request'].user

        if user.is_authenticated:
            children = wm.Bucket.objects.filter(
                bucket_owner=obj
            ).filter(
                Q(user_owner=user) |
                Q(readers=user) |
                Q(visibility=True)
            )
        else:
            children = wm.Bucket.objects.filter(
                bucket_owner=obj
            ).filter(
                Q(visibility=True)
            )
        return BucketChildSerializer(children, many=True).data
    
    def get_pages(self, obj):
        """Get all pages in this bucket with their name and id that the current user can access"""
        user = self.context['request'].user
        if user.is_authenticated:
            pages = obj.pages.filter(
                Q(owner=user) |
                Q(readers=user) |
                Q(public=True, bucket__visibility=True)
            )
        else:
            pages = obj.pages.filter(
                Q(public=True, bucket__visibility=True)
            )
        return PageSummarySerializer(pages, many=True).data

    def create(self, validated_data):
        # Set the user_owner here for creation
        validated_data['user_owner'] = self.context['request'].user
        return super().create(validated_data)
class PageSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bucket = serializers.HyperlinkedRelatedField(
        view_name='bucket-detail',
        lookup_field='slug',
        queryset=wm.Bucket.objects.all()
    )
    bucket_slug = serializers.CharField(source='bucket.slug', read_only=True)
    next = serializers.SerializerMethodField()
    before = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()


    lookup_field='slug'
    
    class Meta:
        model = wm.Page
        fields = [
            'url',
            'title',
            'description',
            'bucket_slug',
            'next',
            'before',
            'can_edit',
            'porder',
            'public',
            'slug',
            'bucket',
            'owner'
        ]
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

        read_only_fields = ['owner', 'next', 'before']

    def get_next(self, obj):
        """Find the page with the closest higher porder in the same bucket that the user can access"""
        try:
            user = self.context['request'].user
            if user.is_authenticated:
                next_page = wm.Page.objects.filter(
                    bucket=obj.bucket,
                    porder__gt=obj.porder
                ).filter(
                    Q(owner=user) |
                    Q(readers=user) |
                    Q(public=True, bucket__visibility=True)
                ).order_by('porder').first()
            else:
                next_page = wm.Page.objects.filter(
                    bucket=obj.bucket,
                    porder__gt=obj.porder
                ).filter(
                    Q(public=True, bucket__visibility=True)
                ).order_by('porder').first()
            
            if next_page:
                return {
                    'slug': next_page.slug,
                    'title': next_page.title,
                    'porder': next_page.porder
                }
            return None
        except Exception:
            return None

    def get_before(self, obj):
        """Find the page with the closest lower porder in the same bucket that the user can access"""
        try:
            user = self.context['request'].user
            if user.is_authenticated:
                previous_page = wm.Page.objects.filter(
                    bucket=obj.bucket,
                    porder__lt=obj.porder
                ).filter(
                    Q(owner=user) |
                    Q(readers=user) |
                    Q(public=True, bucket__visibility=True)
                ).order_by('-porder').first()
            else:
                previous_page = wm.Page.objects.filter(
                bucket=obj.bucket,
                porder__lt=obj.porder
            ).filter(
                Q(public=True, bucket__visibility=True)
            ).order_by('-porder').first()
            
            if previous_page:
                return {
                    'slug': previous_page.slug,
                    'title': previous_page.title,
                    'porder': previous_page.porder
                }
            return None
        except Exception:
            return None

    def get_can_edit(self, obj):
        return self.context['request'].user == obj.owner

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = wm.Tag
        fields = [
            'url',
            'tag_name',
            'tag_description'
        ]

class CommentSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = wm.Comment
        fields = [
            'url',
            'text_content',
            'user',
            'page'
        ]
        read_only_fields = ['user']

class AssetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = wm.Asset
        fields = [
            'url',
            'file_name',
            'size',
            'page'
        ]


