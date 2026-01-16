from rest_framework import serializers
import wcms.models as wm


class RevisionSerializer(serializers.ModelSerializer):
    """Serializer for page revisions"""
    page = serializers.HyperlinkedRelatedField(
        view_name='page-detail',
        lookup_field='slug',
        read_only=True
    )
    
    class Meta:
        model = wm.Revisions
        fields = [
            'id',
            'page',
            'revision_number',
            'diff',
            'timestamp'
        ]
        read_only_fields = ['id', 'revision_number', 'timestamp', 'page']


class CreateRevisionSerializer(serializers.Serializer):
    """Serializer for creating new revisions"""
    content = serializers.CharField(
        help_text="The new content for the page"
    )
    
    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Content cannot be empty")
        return value
