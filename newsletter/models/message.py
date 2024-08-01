import logging


from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .newsletter import Newsletter


logger = logging.getLogger(__name__)

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Message(models.Model):
    """Message as sent through a Submission."""

    title = models.CharField(max_length=200, verbose_name=_("title"))
    slug = models.SlugField(verbose_name=_("slug"))

    newsletter = models.ForeignKey(
        "Newsletter",
        verbose_name=_("newsletter"),
        on_delete=models.CASCADE,
        # default=get_default_newsletter,
    )

    date_create = models.DateTimeField(
        verbose_name=_("created"), auto_now_add=True, editable=False
    )
    date_modify = models.DateTimeField(
        verbose_name=_("modified"), auto_now=True, editable=False
    )

    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        unique_together = ("slug", "newsletter")

    def __str__(self):
        try:
            return _("%(title)s in %(newsletter)s") % {
                "title": self.title,
                "newsletter": self.newsletter,
            }
        except Newsletter.DoesNotExist:
            logger.warning("No newsletter has been set for this message yet.")
            return self.title

    def get_next_article_sortorder(self):
        """Get next available sortorder for Article."""

        next_order = self.articles.aggregate(models.Max("sortorder"))["sortorder__max"]

        if next_order:
            return next_order + 10
        else:
            return 10

    @cached_property
    def _templates(self):
        """Return a (subject_template, text_template, html_template) tuple."""
        return self.newsletter.get_templates("message")

    @property
    def subject_template(self):
        return self._templates[0]

    @property
    def text_template(self):
        return self._templates[1]

    @property
    def html_template(self):
        return self._templates[2]

    @classmethod
    def get_default(cls):
        try:
            return cls.objects.order_by("-date_create").all()[0]
        except IndexError:
            return None
