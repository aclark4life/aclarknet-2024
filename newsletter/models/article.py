import logging


from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


from ..fields import DynamicImageField

logger = logging.getLogger(__name__)

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Article(models.Model):
    """
    An Article within a Message which will be send through a Submission.
    """

    sortorder = models.PositiveIntegerField(
        help_text=_(
            "Sort order determines the order in which articles are "
            "concatenated in a message."
        ),
        verbose_name=_("sort order"),
        blank=True,
    )

    title = models.CharField(max_length=200, verbose_name=_("title"))
    text = models.TextField(verbose_name=_("text"))

    url = models.URLField(verbose_name=_("link"), blank=True, null=True)

    # Make this a foreign key for added elegance
    image = DynamicImageField(
        upload_to="newsletter/images/%Y/%m/%d",
        blank=True,
        null=True,
        verbose_name=_("image"),
    )

    # Message this article is associated with
    message = models.ForeignKey(
        "Message",
        verbose_name=_("message"),
        related_name="articles",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("sortorder",)
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        unique_together = ("message", "sortorder")

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        if self.sortorder is None:
            # If saving a new object get the next available Article ordering
            # as to assure uniqueness.
            self.sortorder = self.message.get_next_article_sortorder()

        super().save()
