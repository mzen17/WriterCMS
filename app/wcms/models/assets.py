from django.db import models
from wcms.models.user import WCMSUser

class Asset(models.Model):
    file_name = models.CharField(max_length=255, unique=True, help_text="Image stored on the S3")
    size = models.IntegerField(help_text="Size of asset (file) in bytes")
    can_share = models.BooleanField(default=False)

    owner = models.ForeignKey(
        WCMSUser,
        on_delete=models.CASCADE,
        related_name='assets',
    )

    def __str__(self):
        return f"Asset of: {self.owner}. Hash: {self.file_name}. Size: {self.size}"
    
    class Meta:
        ordering = ['owner', 'file_name', 'size']


