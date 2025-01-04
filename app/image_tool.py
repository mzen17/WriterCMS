"""Module for managing images through an S3-compatible API."""
import os
import hashlib
import re

from dotenv import load_dotenv
import boto3

class ImageManager:
    """Singleton"""
    def __init__(self):
        load_dotenv()

        s3 = boto3.client(
            service_name ="s3",
            endpoint_url = os.environ["AWS_ENDPOINT"],
            region_name=os.environ["AWS_DEFAULT_REGION"]
        )

        self.s3 = s3
        self.bucket = os.environ["AWS_BUCKET_NAME"]
    
    def retreve_image(self, image_name):
        presigned_url = self.s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.bucket, 'Key': image_name},
            ExpiresIn=3600  # URL expires in 1hr
        )
        return presigned_url

    def check_file_exists(self, file_key):
        try:
            self.s3.head_object(Bucket=self.bucket, Key=file_key)
            return True  # File exists
        except Exception as e:
            return False  # File does not exist

    def upload_image(self, filepath):
        """Yeet an image into S3
        returns a custom filename"""
        # Read the image
        with open(filepath, 'rb') as img_file:
            img_data = img_file.read()
        extension_match = re.search(r'\.(\w+)$', filepath)

        image_hash = hashlib.sha256(img_data).hexdigest()[:8]
        s3_key = f'{image_hash}{extension_match.group(0)}'  # You can change the extension based on the image format

        self.s3.put_object(Bucket=self.bucket, Key=s3_key, Body=img_data, ContentType='image/jpeg')

        return s3_key

    def delete_image(self, image_name):
        """Kills an image out of bucket if it exists"""
