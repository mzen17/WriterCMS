from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from wcms.models.user import WCMSUser
from wcms.models.tags import Tag

class Bucket(models.Model):
    slug = models.SlugField(max_length=255, unique=True, editable=False)
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
        blank=True,
    )

    readers = models.ManyToManyField(
        WCMSUser,
        related_name = "bucket_readers"
    )


    visibility = models.BooleanField(default=True, null=False)

    tags = models.ManyToManyField(
        Tag,
        related_name='buckets',
        blank=True
    )

    # Custom bucket entries
    description = models.CharField(max_length=500, blank=True)
    banner = models.CharField(max_length=255, blank=True)
    background = models.CharField(max_length=255, blank=True)

    def generate_slug(self):
        """Generate a unique slug based on the name"""
        base_slug = slugify(self.name)
        if not base_slug:
            base_slug = 'bucket'
        
        slug = base_slug
        counter = 1
        
        # Keep trying until we find a unique slug
        while Bucket.objects.filter(slug=slug).exclude(slug=self.slug if hasattr(self, 'slug') and self.slug else None).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug

    def clean(self):
        """Validate that there are no circular parent relationships"""
        if self.bucket_owner and self.bucket_owner.user_owner != self.user_owner:
            raise ValueError("Bucket owner must match bucket user owner")

        
        if self.bucket_owner:
            # Check for direct self-reference
            if self.bucket_owner == self:
                raise ValidationError("A bucket cannot be its own parent.")
            
            if self.slug:
                current = self.bucket_owner
                visited = set()
                
                while current:
                    if current.slug == self.slug:
                        raise ValidationError("Circular parent relationship detected.")
                    
                    if current.slug in visited:
                        # This shouldn't happen with proper data, but prevents infinite loops
                        break
                        
                    visited.add(current.slug)
                    current = current.bucket_owner

    def save(self, *args, **kwargs):
        name_changed = False
        if self.slug:
            try:
                original = Bucket.objects.get(slug=self.slug)
                if original.name != self.name:
                    name_changed = True
            except Bucket.DoesNotExist:
                pass
        
        if not self.slug or name_changed:
            self.slug = self.generate_slug()
            
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['pk', 'name']