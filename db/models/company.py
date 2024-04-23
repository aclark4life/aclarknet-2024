from django.db import models
from db.models.base import BaseModel


class Company(BaseModel):
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField("Website", blank=True, null=True)
    ein = models.CharField("EIN", max_length=300, blank=True, null=True)

    # https://stackoverflow.com/a/6062320/185820
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def get_absolute_url(self):
        return reverse("company_view", args=[str(self.id)])
