from django.db import models
from db.models.base import BaseModel
from django.conf import settings
from django.shortcuts import reverse


class Note(BaseModel):
    html = models.BooleanField("HTML", default=False)
    text = models.TextField(blank=True, null=True)
    contacts = models.ManyToManyField("Contact", blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse("note_view", args=[str(self.id)])
