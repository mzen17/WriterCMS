"""Module for managing images through an S3-compatible API."""
import os
import hashlib
import re
from sqlalchemy.orm import Session

from app import fmodels
import app.database.models as models

from dotenv import load_dotenv
import boto3

class ImageManager:
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

    def upload_image_via_uniq_id(self, filepath: str, id: int):
        """Hashless image upload; uses unique id instead"""
        with open(filepath, 'rb') as img_file:
            img_data = img_file.read()
        extension_match = re.search(r'\.(\w+)$', filepath)
        
        s3_key = f'{id}{extension_match.group(0)}'  # You can change the extension based on the image format
        self.s3.put_object(Bucket=self.bucket, Key=s3_key, Body=img_data, ContentType='image/jpeg')

        return s3_key

    def image_crud(self, session: Session, filepath: str, pg_id: int):
        """
        This function is complex. It creates an object, saves it, then uploads it using the unique db ID. 
        """
        image = models.Images(size=10, file_name="", page_id=pg_id)
        session.add(image)
        session.commit()
        session.refresh(image)

        idx = self.upload_image_via_uniq_id(filepath, image.id)
        image.file_name = idx
        session.commit()
        return idx

    def get_image_crud(self, session: Session, filepath: str):
        if session:
            image = session.query(models.Images).filter_by(file_name=filepath).first()
            if image:
                # check if its page is public
                pages = session.query(models.Page).filter_by(id=image.page_id).first()
                if not pages or not pages.public:
                    return "F"
                
                return self.retreve_image(filepath)
                
            else:
                return "F"

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
