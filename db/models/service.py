from django.db import models
from db.models.base import BaseModel


class Service(BaseModel):
    description = models.TextField(blank=True, null=True)

    class Meta:  # https://stackoverflow.com/a/6062320/185820
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("service_view", args=[str(self.id)])
