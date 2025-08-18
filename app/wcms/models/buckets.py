from django.db import models
from django.core.exceptions import ValidationError
from wcms.models.user import WCMSUser
from wcms.models.tags import Tag

class Bucket(models.Model):
    name = models.CharField(max_length=255)
    user_owner = models.ForeignKey(
        WCMSUser,
        on_delete=models.CASCADE,
        related_name="buckets"
    )
    
    bucket_owner = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    readers = models.ManyToManyField(
        WCMSUser,
        related_name = "bucket_readers"
    )


    visibility = models.BooleanField(default=True, null=False)

    tags = models.ManyToManyField(
        Tag,
        related_name='buckets',
    )

    # Custom bucket entries
    description = models.CharField(max_length=500)
    banner = models.CharField(max_length=255)
    background = models.CharField(max_length=255)

    def clean(self):
        """Validate that there are no circular parent relationships"""
        if self.bucket_owner:
            # Check for direct self-reference
            if self.bucket_owner == self:
                raise ValidationError("A bucket cannot be its own parent.")
            
            # Only check for circular references if this bucket has been saved (has an ID)
            if self.pk:
                # Check for circular references by traversing up the parent chain
                current = self.bucket_owner
                visited = set()
                
                while current:
                    if current.pk == self.pk:
                        raise ValidationError("Circular parent relationship detected.")
                    
                    if current.pk in visited:
                        # This shouldn't happen with proper data, but prevents infinite loops
                        break
                        
                    visited.add(current.pk)
                    current = current.bucket_owner

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name