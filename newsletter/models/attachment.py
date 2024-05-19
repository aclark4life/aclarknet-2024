import logging
import os


from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Attachment(models.Model):
    """Attachment for a Message."""

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    def __str__(self):
        return _("%(file_name)s on %(message)s") % {
            "file_name": self.file_name,
            "message": self.message,
        }

    file = models.FileField(
        # upload_to=attachment_upload_to,
        blank=False,
        null=False,
        verbose_name=_("attachment"),
    )

    message = models.ForeignKey(
        "Message",
        verbose_name=_("message"),
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    @property
    def file_name(self):
        return os.path.split(self.file.name)[1]
