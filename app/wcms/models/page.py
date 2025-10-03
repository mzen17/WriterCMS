from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from wcms.models.buckets import Bucket
from wcms.models.user import WCMSUser
import difflib

class Page(models.Model):
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, editable=False)  # Now read-only
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

    def calculate_content_from_revisions(self):
        """Calculate the final content from the latest revision"""
        from wcms.models.page import Revisions  # Import here to avoid circular import
        latest_revision = Revisions.objects.filter(page=self).order_by('-revision_number').first()
        
        if latest_revision:
            # For now, we'll store full content in each revision instead of diffs
            return latest_revision.diff
        
        return ""
    
    def update_description_from_revisions(self):
        """Update the page description based on the latest revision"""
        self.description = self.calculate_content_from_revisions()
        # Use update to avoid triggering save() again
        Page.objects.filter(pk=self.pk).update(description=self.description)

    def save(self, *args, **kwargs):
        # Validate that bucket owner matches page owner
        if self.bucket and self.owner and self.bucket.user_owner != self.owner:
            raise ValueError("Page owner must match bucket owner")
        
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


class Revisions(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="revisions",
        help_text="The page this revision belongs to"
    )
    
    revision_number = models.PositiveIntegerField(
        help_text="Sequential revision number for this page"
    )
    
    diff = models.TextField(
        help_text="Full content of the page at this revision"
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When this revision was created"
    )
    
    def save(self, *args, **kwargs):
        # Auto-assign revision number if not set
        if not self.revision_number:
            last_revision = Revisions.objects.filter(page=self.page).order_by('-revision_number').first()
            self.revision_number = (last_revision.revision_number + 1) if last_revision else 1
        
        super().save(*args, **kwargs)
        
        # Update the page's description after saving the revision
        self.page.update_description_from_revisions()
    
    @classmethod
    def create_revision(cls, page, new_content, user=None):
        """
        Create a new revision for a page.
        
        Args:
            page: The Page instance
            new_content: The new content as a string
            user: Optional user creating the revision (for permission checking)
        
        Returns:
            The created or updated Revisions instance
        """
        if user and user != page.owner:
            raise PermissionError("Only the page owner can create revisions")
        
        # Get the latest revision
        last_revision = cls.objects.filter(page=page).order_by('-revision_number').first()
        
        if last_revision:
            # Calculate the character difference between old and new content
            old_content = last_revision.diff
            char_diff = abs(len(new_content) - len(old_content))
            
            # If the difference is less than 1500 characters, update the existing revision
            if char_diff < 1500:
                last_revision.diff = new_content
                last_revision.timestamp = timezone.now()
                last_revision.save()
                return last_revision
        
        # Create a new revision if no previous revision exists or difference is >= 1500 chars
        next_revision_number = (last_revision.revision_number + 1) if last_revision else 1
        
        # Store the full content in each revision for simplicity and reliability
        revision = cls.objects.create(
            page=page,
            revision_number=next_revision_number,
            diff=new_content  # Store full content instead of diff
        )
        
        return revision
    
    def __str__(self):
        return f"{self.page.title} - Revision {self.revision_number}"
    
    class Meta:
        ordering = ['page', 'revision_number']
        unique_together = ['page', 'revision_number']
        verbose_name_plural = "Revisions"