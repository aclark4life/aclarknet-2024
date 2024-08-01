import logging


from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.template.loader import select_template
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

# from ..fields import DynamicImageField
from ..utils import get_default_sites, ACTIONS

from ..admin.admin_forms import get_address

from .subscription import Subscription

logger = logging.getLogger(__name__)

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Newsletter(models.Model):
    site = models.ManyToManyField(Site, default=get_default_sites)

    title = models.CharField(max_length=200, verbose_name=_("newsletter title"))
    slug = models.SlugField(db_index=True, unique=True)

    email = models.EmailField(verbose_name=_("e-mail"), help_text=_("Sender e-mail"))
    sender = models.CharField(
        max_length=200, verbose_name=_("sender"), help_text=_("Sender name")
    )

    visible = models.BooleanField(
        default=True, verbose_name=_("visible"), db_index=True
    )

    send_html = models.BooleanField(
        default=True,
        verbose_name=_("send html"),
        help_text=_("Whether or not to send HTML versions of e-mails."),
    )

    objects = models.Manager()

    # Automatically filter the current site
    on_site = CurrentSiteManager()

    def get_templates(self, action):
        """
        Return a subject, text, HTML tuple with e-mail templates for
        a particular action. Returns a tuple with subject, text and e-mail
        template.
        """

        assert action in ACTIONS + ("message",), "Unknown action: %s" % action

        # Common substitutions for filenames
        tpl_subst = {"action": action, "newsletter": self.slug}

        # Common root path for all the templates
        tpl_root = "newsletter/message/"

        subject_template = select_template(
            [
                tpl_root + "%(newsletter)s/%(action)s_subject.txt" % tpl_subst,
                tpl_root + "%(action)s_subject.txt" % tpl_subst,
            ]
        )

        text_template = select_template(
            [
                tpl_root + "%(newsletter)s/%(action)s.txt" % tpl_subst,
                tpl_root + "%(action)s.txt" % tpl_subst,
            ]
        )

        if self.send_html:
            html_template = select_template(
                [
                    tpl_root + "%(newsletter)s/%(action)s.html" % tpl_subst,
                    tpl_root + "%(action)s.html" % tpl_subst,
                ]
            )
        else:
            # HTML templates are not required
            html_template = None

        return subject_template, text_template, html_template

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("newsletter")
        verbose_name_plural = _("newsletters")

    def get_absolute_url(self):
        return reverse("newsletter_detail", kwargs={"newsletter_slug": self.slug})

    def subscribe_url(self):
        return reverse(
            "newsletter_subscribe_request", kwargs={"newsletter_slug": self.slug}
        )

    def unsubscribe_url(self):
        return reverse(
            "newsletter_unsubscribe_request", kwargs={"newsletter_slug": self.slug}
        )

    def update_url(self):
        return reverse(
            "newsletter_update_request", kwargs={"newsletter_slug": self.slug}
        )

    def archive_url(self):
        return reverse("newsletter_archive", kwargs={"newsletter_slug": self.slug})

    def get_sender(self):
        return get_address(self.sender, self.email)

    def get_subscriptions(self):
        logger.debug("Looking up subscribers for %s", self)

        return Subscription.objects.filter(newsletter=self, subscribed=True)

    @classmethod
    def get_default(cls):
        try:
            return cls.objects.all()[0].pk
        except IndexError:
            return None
