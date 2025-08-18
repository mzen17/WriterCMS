from django.db import models

class Tag(models.Model):
    tag_name = models.CharField(max_length=100, unique=True, help_text="Name of the tag (bucket)")
    tag_description = models.CharField(max_length=255, help_text="Description of tag", blank=True, null=True)

    def __str__(self):
        return self.tag_name
