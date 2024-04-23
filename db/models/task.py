from db.models.base import BaseModel
from django.db import models


class Task(BaseModel):
    rate = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    unit = models.DecimalField(
        "Unit", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )

    # https://stackoverflow.com/a/6062320/185820
    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("task_view", args=[str(self.id)])
