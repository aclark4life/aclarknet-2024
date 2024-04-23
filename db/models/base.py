from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    archived = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    published = models.BooleanField(default=False)
    notes = models.ManyToManyField("Note", blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated = timezone.now()
        super(BaseModel, self).save(*args, **kwargs)

    def get_model_name(self):
        return self._meta.verbose_name

    def __str__(self):
        if self.name:
            return f"{self.name}"
        elif self.title:
            return f"{self.title}"
        else:
            try:
                if self.subject:
                    return f"{self.subject}"
            except AttributeError:
                try:
                    if self.description:
                        return f"{self.description}"
                except AttributeError:
                    pass
        return f"{self.__class__.__name__.lower()}-{self.pk}"

    def get_absolute_url(self):
        raise NotImplementedError(
            "Subclass of ModelWithUrl must define get_absolute_url()"
        )
