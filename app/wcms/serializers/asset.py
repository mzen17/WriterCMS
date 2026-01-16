from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
import wcms.models as wm

"""Module for managing images through an S3-compatible API."""
import os
import hashlib
import re
import mimetypes

import boto3

# 500MB limit in bytes
MAX_STORAGE_BYTES = 500 * 1024 * 1024  # 500MB = 524288000 bytes

# S3 management functions

def get_creds():
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=os.environ["AWS_ENDPOINT"],
        region_name=os.environ["AWS_DEFAULT_REGION"]
    )
    return s3, os.environ["AWS_BUCKET_NAME"]


def retrieve_image(s3, bucket, image_name):
    """Generate a presigned URL for retrieving an image"""
    presigned_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket, 'Key': image_name},
        ExpiresIn=3600  # URL expires in 1hr
    )
    return presigned_url


def upload_image(s3, bucket, file_data, filename):
    """Upload an image to S3 from buffer data, returns a custom filename"""
    # Get file extension from original filename
    extension_match = re.search(r'\.(\w+)$', filename)
    extension = extension_match.group(0) if extension_match else '.bin'
    
    # Generate hash-based filename
    image_hash = hashlib.sha256(file_data).hexdigest()[:8]
    s3_key = f'{image_hash}{extension}'
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'
    
    s3.put_object(Bucket=bucket, Key=s3_key, Body=file_data, ContentType=content_type)
    
    return s3_key

def delete_image(s3, bucket, image_name):
    """Delete an image from S3 bucket"""
    s3.delete_object(Bucket=bucket, Key=image_name)


def get_user_total_storage(user):
    """Calculate total storage used by a user in bytes"""
    total = wm.Asset.objects.filter(owner=user).aggregate(total_size=Sum('size'))
    return total['total_size'] or 0


class AssetSerializer(serializers.HyperlinkedModelSerializer):
    # Accept file upload - write only, not returned in response
    file = serializers.FileField(write_only=True, required=False)
    
    # Explicitly define the url field with correct lookup
    url = serializers.HyperlinkedIdentityField(
        view_name='asset-detail',
        lookup_field='file_name',
    )
    
    class Meta:
        model = wm.Asset
        fields = [
            'url',
            'file_name',
            'size',
            'owner',
            'can_share',
            'file'
        ]
        read_only_fields = ['owner', 'size', 'file_name']

    def create(self, validated_data):
        # Extract file from validated data
        uploaded_file = validated_data.pop('file', None)
        
        if not uploaded_file:
            raise ValidationError({'file': 'A file must be uploaded'})
        
        # Get the user from context (set by perform_create in viewset)
        user = validated_data.get('owner')
        if not user:
            raise ValidationError({'owner': 'Owner is required'})
        
        # Calculate file size
        file_size = uploaded_file.size
        
        # Check storage limit
        current_usage = get_user_total_storage(user)
        if current_usage + file_size > MAX_STORAGE_BYTES:
            available = MAX_STORAGE_BYTES - current_usage
            raise ValidationError({
                'file': f'Storage limit exceeded. You have {available / (1024*1024):.2f}MB available, '
                        f'but the file is {file_size / (1024*1024):.2f}MB.'
            })
        
        # Read file data
        file_data = uploaded_file.read()
        original_filename = uploaded_file.name
        
        # Upload to S3
        s3, bucket = get_creds()
        s3_filename = upload_image(s3, bucket, file_data, original_filename)
        
        # Set the computed fields
        validated_data['file_name'] = s3_filename
        validated_data['size'] = file_size
        
        return super().create(validated_data)


def delete_asset(asset):
    """Delete an asset and its S3 file"""
    s3, bucket = get_creds()
    delete_image(s3, bucket, asset.file_name)
    asset.delete()
