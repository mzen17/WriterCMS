from rest_framework import serializers
import wcms.models as wm


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
