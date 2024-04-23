from db.models.base import BaseModel
from django.db import models
from django.utils import timezone


class Testimonial(BaseModel):
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, null=True, default=timezone.now
    )

    def get_absolute_url(self):
        return reverse("testimonial_view", args=[str(self.id)])
