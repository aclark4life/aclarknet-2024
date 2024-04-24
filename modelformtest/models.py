from django.db import models
from django.shortcuts import reverse

# import hashlib
# import secrets
import uuid
from django.utils import timezone


class TestModel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=True)
    unsubscribe_token = models.CharField(max_length=64, blank=True)
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name or f"test-model-{self.pk}"

    def get_absolute_url(self):
        return reverse("testmodel_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name or f"test-model-{self.pk}"

    #     def save(self, *args, **kwargs):
    #         if not self.unsubscribe_token:
    #             token = secrets.token_hex(32)
    #             self.unsubscribe_token = hashlib.sha256(token.encode()).hexdigest()
    #         super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            self.unsubscribe_token = uuid.uuid4()
        super().save(*args, **kwargs)


class MarketingEmailMessage(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return self.subject
