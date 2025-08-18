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
        fields = ['id', 'name', 'banner']

class PageSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for pages within a bucket"""
    class Meta:
        model = wm.Page
        fields = ['id', 'title']

class BucketSerializer(serializers.HyperlinkedModelSerializer):
    # Add custom fields for hydrated data
    user_owner_name = serializers.CharField(source='user_owner.username', read_only=True)
    bucket_owner_name = serializers.CharField(source='bucket_owner.name', read_only=True)
    can_edit = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()
    
    # Add nested serializers for children buckets and pages
    children_buckets = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()

    class Meta:
        model = wm.Bucket
        fields = [
            'url',
            'name',
            'user_owner',  # Keep original URL field
            'user_owner_name',  # Add hydrated username
            'bucket_owner',
            'bucket_owner_name',  # Add hydrated bucket name
            'visibility',
            'tags',
            'tag_names',  # Add hydrated tag names
            'description',
            'banner',
            'can_edit',
            'background',
            'children_buckets',  # Add children buckets
            'pages'  # Add pages
        ]
        read_only_fields = ['user_owner', 'user_owner_name', 'bucket_owner_name', 'tag_names', 'can_edit', 'children_buckets', 'pages'] 

    def get_tag_names(self, obj):
        """Return a list of tag names instead of URLs"""
        return [tag.tag_name for tag in obj.tags.all()]
    
    def get_can_edit(self, obj):
        return self.context['request'].user == obj.user_owner
    
    def get_children_buckets(self, obj):
        """Get all child buckets with their banner, name, and id that the current user can access"""
        user = self.context['request'].user
        children = wm.Bucket.objects.filter(
            bucket_owner=obj
        ).filter(
            Q(user_owner=user) |
            Q(readers=user) |
            Q(visibility=True)
        )
        return BucketChildSerializer(children, many=True).data
    
    def get_pages(self, obj):
        """Get all pages in this bucket with their name and id that the current user can access"""
        user = self.context['request'].user
        pages = obj.pages.filter(
            Q(owner=user) |
            Q(readers=user) |
            Q(public=True, bucket__visibility=True)
        )
        return PageSummarySerializer(pages, many=True).data

    def create(self, validated_data):
        # Set the user_owner here for creation
        validated_data['user_owner'] = self.context['request'].user
        return super().create(validated_data)
class PageSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = wm.Page
        fields = [
            'url',
            'title',
            'description',
            'porder',
            'public',
            'bucket',
            'owner'
        ]
        read_only_fields = ['owner']

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


