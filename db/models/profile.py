from db.models.base import BaseModel
from django.db import models
from django.conf import settings
from django.shortcuts import reverse


class Profile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    page_size = models.PositiveIntegerField(blank=True, null=True)
    user_theme_preference = models.CharField(
        max_length=10, choices=settings.THEMES, default="light"
    )
    rate = models.DecimalField(
        "Hourly Rate (United States Dollar - USD)",
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    unit = models.DecimalField(
        "Unit", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    avatar_url = models.URLField("Avatar URL", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=150, blank=True, null=True)
    twitter_username = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=150, blank=True, null=True)
    lounge_password = models.CharField(max_length=150, blank=True, null=True)
    lounge_username = models.CharField(max_length=150, blank=True, null=True)
    mail = models.BooleanField(default=False)
    dark = models.BooleanField("Dark Mode", default=True)
    github_access_token = models.CharField(max_length=150, blank=True, null=True)

    def is_staff(self):
        if self.user:
            if self.user.is_staff:
                return True

    def get_absolute_url(self):
        if self.user:
            return reverse("user_view", args=[str(self.user.id)])

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
