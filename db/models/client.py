from django.db import models
from taggit.managers import TaggableManager

from db.models.base import BaseModel
from django.shortcuts import reverse


class Client(BaseModel):
    tags = TaggableManager(blank=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField("Website", blank=True, null=True)
    publish = models.BooleanField(default=False)
    link = models.BooleanField(default=False)

    # https://stackoverflow.com/a/6062320/185820
    class Meta:
        ordering = ["name"]

    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse("client_view", args=[str(self.id)])
