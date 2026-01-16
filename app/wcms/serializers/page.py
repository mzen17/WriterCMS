from django.db.models import Q
from rest_framework import serializers
import wcms.models as wm


class PageSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bucket = serializers.HyperlinkedRelatedField(
        view_name='bucket-detail',
        lookup_field='slug',
        queryset=wm.Bucket.objects.all()
    )
    bucket_slug = serializers.CharField(source='bucket.slug', read_only=True)
    bucket_bg = serializers.CharField(source='bucket.background', read_only=True)

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
            'bucket_bg',
            'porder',
            'public',
            'slug',
            'background',
            'banner',
            'bucket',
            'owner'
        ]
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

        read_only_fields = ['owner', 'next', 'before', 'description', 'slug'] 

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
