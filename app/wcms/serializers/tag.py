from rest_framework import serializers
import wcms.models as wm


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = wm.Tag
        fields = [
            'url',
            'id',
            'tag_name',
            'tag_description',
        ]
        read_only_fields = ['url']
