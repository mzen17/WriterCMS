from django.db import models
from wcms.models.user import WCMSUser
from wcms.models.page import Page

class Comment(models.Model):
    text_content = models.CharField(max_length=1000, help_text="The text content of the comment")

    user = models.ForeignKey(
        WCMSUser,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    def __str__(self):
        return f"Comment {self.pk or 'new'} posted by {self.user}"
    
    class Meta:
        ordering = ['page', 'pk']



    
