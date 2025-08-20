from django.db import models
from wcms.models.page import Page

class Asset(models.Model):
    file_name = models.CharField(max_length=255, help_text="Image stored on the S3")
    size = models.IntegerField(help_text="Size of asset (file) in bytes")
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='assets',
    )

    def __str__(self):
        return f"Asset for page: {self.page}. Hash: {self.file_name}"
    
    class Meta:
        ordering = ['page', 'file_name']


