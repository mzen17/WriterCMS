from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class WCMSUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='wcmsuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='wcmsuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    pfp = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    dictionary = models.CharField(max_length=255, blank=True, null=True)
    theme = models.BooleanField(default=False)