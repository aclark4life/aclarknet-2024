import logging
import time


from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.utils.timezone import now
from django.urls import reverse


from .attachment import Attachment


logger = logging.getLogger(__name__)

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Submission(models.Model):
    """
    Submission represents a particular Message as it is being submitted
    to a list of Subscribers. This is where actual queueing and submission
    happen.
    """

    class Meta:
        verbose_name = _("submission")
        verbose_name_plural = _("submissions")

    def __str__(self):
        return _("%(newsletter)s on %(publish_date)s") % {
            "newsletter": self.message,
            "publish_date": self.publish_date,
        }

    @cached_property
    def extra_headers(self):
        return {
            "List-Unsubscribe": "http://{}{}".format(
                Site.objects.get_current().domain,
                reverse(
                    "newsletter_unsubscribe_request",
                    args=[self.message.newsletter.slug],
                ),
            ),
        }

    def submit(self):
        subscriptions = self.subscriptions.filter(subscribed=True)

        logger.info(
            gettext("Submitting %(submission)s to %(count)d people"),
            {"submission": self, "count": subscriptions.count()},
        )

        assert (
            self.publish_date < now()
        ), "Something smells fishy; submission time in future."

        self.sending = True
        self.save()

        try:
            for idx, subscription in enumerate(subscriptions, start=1):
                if hasattr(settings, "NEWSLETTER_EMAIL_DELAY"):
                    time.sleep(settings.NEWSLETTER_EMAIL_DELAY)
                if (
                    hasattr(settings, "NEWSLETTER_BATCH_SIZE")
                    and settings.NEWSLETTER_BATCH_SIZE > 0
                ):
                    if idx % settings.NEWSLETTER_BATCH_SIZE == 0:
                        time.sleep(settings.NEWSLETTER_BATCH_DELAY)
                self.send_message(subscription)
            self.sent = True

        finally:
            self.sending = False
            self.save()

    def send_message(self, subscription):
        variable_dict = {
            "subscription": subscription,
            "site": Site.objects.get_current(),
            "submission": self,
            "message": self.message,
            "newsletter": self.newsletter,
            "date": self.publish_date,
            "STATIC_URL": settings.STATIC_URL,
            "MEDIA_URL": settings.MEDIA_URL,
        }

        subject = self.message.subject_template.render(variable_dict).strip()
        text = self.message.text_template.render(variable_dict)

        message = EmailMultiAlternatives(
            subject,
            text,
            from_email=self.newsletter.get_sender(),
            to=[subscription.get_recipient()],
            headers=self.extra_headers,
        )

        attachments = Attachment.objects.filter(message_id=self.message.id)

        for attachment in attachments:
            message.attach_file(attachment.file.path)

        if self.message.html_template:
            message.attach_alternative(
                self.message.html_template.render(variable_dict), "text/html"
            )

        try:
            logger.debug(gettext("Submitting message to: %s."), subscription)

            message.send()

        except Exception as e:
            # TODO: Test coverage for this branch.
            logger.error(
                gettext("Message %(subscription)s failed " "with error: %(error)s"),
                {"subscription": subscription, "error": e},
            )

    @classmethod
    def submit_queue(cls):
        todo = cls.objects.filter(
            prepared=True, sent=False, sending=False, publish_date__lt=now()
        )

        for submission in todo:
            submission.submit()

    @classmethod
    def from_message(cls, message):
        logger.debug(gettext("Submission of message %s"), message)
        submission = cls()
        submission.message = message
        submission.newsletter = message.newsletter
        submission.save()
        try:
            submission.subscriptions.set(message.newsletter.get_subscriptions())
        except AttributeError:  # Django < 1.10
            submission.subscriptions = message.newsletter.get_subscriptions()
        return submission

    def save(self, **kwargs):
        """Set the newsletter from associated message upon saving."""
        assert self.message.newsletter

        self.newsletter = self.message.newsletter

        return super().save()

    def get_absolute_url(self):
        assert self.newsletter.slug
        assert self.message.slug

        return reverse(
            "newsletter_archive_detail",
            kwargs={
                "newsletter_slug": self.newsletter.slug,
                "year": self.publish_date.year,
                "month": self.publish_date.month,
                "day": self.publish_date.day,
                "slug": self.message.slug,
            },
        )

    newsletter = models.ForeignKey(
        "Newsletter",
        verbose_name=_("newsletter"),
        editable=False,
        on_delete=models.CASCADE,
    )
    message = models.ForeignKey(
        "Message",
        verbose_name=_("message"),
        editable=True,
        null=False,
        on_delete=models.CASCADE,
    )

    subscriptions = models.ManyToManyField(
        "Subscription",
        help_text=_(
            "If you select none, the system will automatically find "
            "the subscribers for you."
        ),
        blank=True,
        db_index=True,
        verbose_name=_("recipients"),
        limit_choices_to={"subscribed": True},
    )

    publish_date = models.DateTimeField(
        verbose_name=_("publication date"),
        blank=True,
        null=True,
        default=now,
        db_index=True,
    )
    publish = models.BooleanField(
        default=True,
        verbose_name=_("publish"),
        help_text=_("Publish in archive."),
        db_index=True,
    )

    prepared = models.BooleanField(
        default=False, verbose_name=_("prepared"), db_index=True, editable=False
    )
    sent = models.BooleanField(
        default=False, verbose_name=_("sent"), db_index=True, editable=False
    )
    sending = models.BooleanField(
        default=False, verbose_name=_("sending"), db_index=True, editable=False
    )
