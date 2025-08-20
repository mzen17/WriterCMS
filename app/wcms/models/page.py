from django.db import models
from django.utils.text import slugify
from wcms.models.buckets import Bucket
from wcms.models.user import WCMSUser

class Page(models.Model):
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    porder = models.IntegerField(default=-1)
    public = models.BooleanField(default=False)

    bucket = models.ForeignKey(
        Bucket,
        on_delete=models.CASCADE,
        related_name="pages",
    )

    owner = models.ForeignKey(
        WCMSUser,
        on_delete=models.CASCADE,
        related_name="pages",
    )

    readers = models.ManyToManyField(
        WCMSUser,
        related_name = "readers"
    )

    def generate_slug(self):
        """Generate a unique slug based on the title"""
        base_slug = slugify(self.title)
        if not base_slug:
            base_slug = 'page'
        
        slug = base_slug
        counter = 1
        
        # Keep trying until we find a unique slug
        while Page.objects.filter(slug=slug).exclude(slug=self.slug if hasattr(self, 'slug') and self.slug else None).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug

    def save(self, *args, **kwargs):
        title_changed = False
        if self.slug:
            try:
                original = Page.objects.get(slug=self.slug)
                if original.title != self.title:
                    title_changed = True
            except Page.DoesNotExist:
                pass
        
        if not self.slug or title_changed:
            self.slug = self.generate_slug()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['bucket', 'porder', 'pk']
