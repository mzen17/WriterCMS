from django.db.models import Q
from rest_framework import serializers
import wcms.models as wm


class BucketChildSerializer(serializers.ModelSerializer):
    """Simplified serializer for child buckets"""
    class Meta:
        model = wm.Bucket
        fields = ['slug', 'name', 'banner']


class PageSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for pages within a bucket"""
    class Meta:
        model = wm.Page
        fields = ['slug', 'title', 'banner']


class BucketSerializer(serializers.HyperlinkedModelSerializer):
    # Add custom fields for hydrated data
    user_owner_name = serializers.CharField(source='user_owner.email', read_only=True)
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
            'pg_banner',
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
