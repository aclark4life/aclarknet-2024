import logging


from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.urls import reverse


from ..utils import make_activation_code, ACTIONS

from ..admin.admin_forms import get_address

logger = logging.getLogger(__name__)

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Subscription(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        blank=True,
        null=True,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
    )

    name_field = models.CharField(
        db_column="name",
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("name"),
        help_text=_("optional"),
    )

    def get_name(self):
        if self.user:
            return self.user.get_full_name()
        return self.name_field

    def set_name(self, name):
        if not self.user:
            self.name_field = name

    name = property(get_name, set_name)

    email_field = models.EmailField(
        db_column="email",
        verbose_name=_("e-mail"),
        db_index=True,
        blank=True,
        null=True,
    )

    def get_email(self):
        if self.user:
            return self.user.email
        return self.email_field

    def set_email(self, email):
        if not self.user:
            self.email_field = email

    email = property(get_email, set_email)

    def update(self, action):
        """
        Update subscription according to requested action:
        subscribe/unsubscribe/update/, then save the changes.
        """

        assert action in ("subscribe", "update", "unsubscribe")

        # If a new subscription or update, make sure it is subscribed
        # Else, unsubscribe
        if action == "subscribe" or action == "update":
            self.subscribed = True
        else:
            self.unsubscribed = True

        logger.debug(
            _("Updated subscription %(subscription)s to %(action)s."),
            {"subscription": self, "action": action},
        )

        # This triggers the subscribe() and/or unsubscribe() methods, taking
        # care of stuff like maintaining the (un)subscribe date.
        self.save()

    def _subscribe(self):
        """
        Internal helper method for managing subscription state
        during subscription.
        """
        logger.debug("Subscribing subscription %s.", self)

        self.subscribe_date = now()
        self.subscribed = True
        self.unsubscribed = False

    def _unsubscribe(self):
        """
        Internal helper method for managing subscription state
        during unsubscription.
        """
        logger.debug("Unsubscribing subscription %s.", self)

        self.subscribed = False
        self.unsubscribed = True
        self.unsubscribe_date = now()

    def save(self, *args, **kwargs):
        """
        Perform some basic validation and state maintenance of Subscription.
        TODO: Move this code to a more suitable place (i.e. `clean()`) and
        cleanup the code. Refer to comment below and
        https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.clean
        """
        assert self.user or self.email_field, _(
            "Neither an email nor a username is set. This asks for " "inconsistency!"
        )
        assert (self.user and not self.email_field) or (
            self.email_field and not self.user
        ), _("If user is set, email must be null and vice versa.")

        # This is a lame way to find out if we have changed but using Django
        # API internals is bad practice. This is necessary to discriminate
        # from a state where we have never been subscribed but is mostly for
        # backward compatibility. It might be very useful to make this just
        # one attribute 'subscribe' later. In this case unsubscribed can be
        # replaced by a method property.

        if self.pk:
            assert Subscription.objects.filter(pk=self.pk).count() == 1

            subscription = Subscription.objects.get(pk=self.pk)
            old_subscribed = subscription.subscribed
            old_unsubscribed = subscription.unsubscribed

            # If we are subscribed now and we used not to be so, subscribe.
            # If we user to be unsubscribed but are not so anymore, subscribe.
            if (self.subscribed and not old_subscribed) or (
                old_unsubscribed and not self.unsubscribed
            ):
                self._subscribe()

                assert not self.unsubscribed
                assert self.subscribed

            # If we are unsubcribed now and we used not to be so, unsubscribe.
            # If we used to be subscribed but are not subscribed anymore,
            # unsubscribe.
            elif (self.unsubscribed and not old_unsubscribed) or (
                old_subscribed and not self.subscribed
            ):
                self._unsubscribe()

                assert not self.subscribed
                assert self.unsubscribed
        else:
            if self.subscribed:
                self._subscribe()
            elif self.unsubscribed:
                self._unsubscribe()

        super().save(*args, **kwargs)

    ip = models.GenericIPAddressField(_("IP address"), blank=True, null=True)

    newsletter = models.ForeignKey(
        "Newsletter", verbose_name=_("newsletter"), on_delete=models.CASCADE
    )

    create_date = models.DateTimeField(editable=False, default=now)

    activation_code = models.CharField(
        verbose_name=_("activation code"), max_length=40, default=make_activation_code
    )

    subscribed = models.BooleanField(
        default=False, verbose_name=_("subscribed"), db_index=True
    )
    subscribe_date = models.DateTimeField(
        verbose_name=_("subscribe date"), null=True, blank=True
    )

    # This should be a pseudo-field, I reckon.
    unsubscribed = models.BooleanField(
        default=False, verbose_name=_("unsubscribed"), db_index=True
    )
    unsubscribe_date = models.DateTimeField(
        verbose_name=_("unsubscribe date"), null=True, blank=True
    )

    def __str__(self):
        if self.name:
            return _("%(name)s <%(email)s> to %(newsletter)s") % {
                "name": self.name,
                "email": self.email,
                "newsletter": self.newsletter,
            }

        else:
            return _("%(email)s to %(newsletter)s") % {
                "email": self.email,
                "newsletter": self.newsletter,
            }

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        unique_together = ("user", "email_field", "newsletter")

    def get_recipient(self):
        return get_address(self.name, self.email)

    def send_activation_email(self, action):
        assert action in ACTIONS, "Unknown action: %s" % action

        (subject_template, text_template, html_template) = (
            self.newsletter.get_templates(action)
        )

        variable_dict = {
            "subscription": self,
            "site": Site.objects.get_current(),
            "newsletter": self.newsletter,
            "date": self.subscribe_date,
            "STATIC_URL": settings.STATIC_URL,
            "MEDIA_URL": settings.MEDIA_URL,
        }

        subject = subject_template.render(variable_dict).strip()
        text = text_template.render(variable_dict)

        message = EmailMultiAlternatives(
            subject, text, from_email=self.newsletter.get_sender(), to=[self.email]
        )

        if html_template:
            message.attach_alternative(html_template.render(variable_dict), "text/html")

        message.send()

        logger.debug(
            'Activation email sent for action "%(action)s" to %(subscriber)s '
            'with activation code "%(action_code)s".',
            {"action_code": self.activation_code, "action": action, "subscriber": self},
        )

    def subscribe_activate_url(self):
        return reverse(
            "newsletter_update_activate",
            kwargs={
                "newsletter_slug": self.newsletter.slug,
                "email": self.email,
                "action": "subscribe",
                "activation_code": self.activation_code,
            },
        )

    def unsubscribe_activate_url(self):
        return reverse(
            "newsletter_update_activate",
            kwargs={
                "newsletter_slug": self.newsletter.slug,
                "email": self.email,
                "action": "unsubscribe",
                "activation_code": self.activation_code,
            },
        )

    def update_activate_url(self):
        return reverse(
            "newsletter_update_activate",
            kwargs={
                "newsletter_slug": self.newsletter.slug,
                "email": self.email,
                "action": "update",
                "activation_code": self.activation_code,
            },
        )
