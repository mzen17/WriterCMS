from rest_framework import serializers
import wcms.models as wm


class WCMSUserSerializer(serializers.HyperlinkedModelSerializer):
    # Firebase handles authentication and user identity
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    
    class Meta:
        model = wm.WCMSUser
        fields = ['url', 'email', 'first_name', 'last_name', 'pfp', 'bio', 'dictionary', 'theme', 'username', 'id']
        read_only_fields = ['username', 'email']  # Firebase manages these fields
    
    def create(self, validated_data):
        # Firebase users are created automatically by the authentication backend
        # This method should typically not be called directly
        user = wm.WCMSUser.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Update fields normally (password handling removed)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
