from django.db import models
from wcms.models.buckets import Bucket
from wcms.models.user import WCMSUser

class Page(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    porder = models.IntegerField()
    public = models.BooleanField()

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

    def __str__(self):
        return self.title
