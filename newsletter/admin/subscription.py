import logging

from django.urls import path

from django.conf import settings

from django.contrib import admin, messages

from django.core.exceptions import PermissionDenied

from django.http import HttpResponseRedirect

from django.shortcuts import render

from django.utils.html import format_html
from django.utils.translation import gettext as _, ngettext
from django.utils.formats import date_format


try:
    from django.views.i18n import JavaScriptCatalog

    HAS_CBV_JSCAT = True
except ImportError:  # Django < 1.10
    from django.views.i18n import javascript_catalog

    HAS_CBV_JSCAT = False

# Conditional imports as only one Thumbnail app is required
try:
    from sorl.thumbnail.admin import AdminImageMixin  # noqa
except ImportError:
    pass

try:
    from easy_thumbnails.widgets import ImageClearableFileInput  # noqa
except (ImportError, RuntimeError):
    pass

# from .models import Newsletter, Subscription, Attachment, Article, Message, Submission
from ..models.newsletter import Newsletter

from django.urls import reverse

from .admin_forms import (
    SubscriptionAdminForm,
    ImportForm,
    ConfirmForm,
)
from .admin_utils import ExtendibleModelAdminMixin, make_subscription

from .newsletter import NewsletterAdminLinkMixin


logger = logging.getLogger(__name__)


# Construct URL's for icons
ICON_URLS = {
    "yes": "%snewsletter/admin/img/icon-yes.gif" % settings.STATIC_URL,
    "wait": "%snewsletter/admin/img/waiting.gif" % settings.STATIC_URL,
    "submit": "%snewsletter/admin/img/submitting.gif" % settings.STATIC_URL,
    "no": "%snewsletter/admin/img/icon-no.gif" % settings.STATIC_URL,
}


class SubscriptionAdmin(
    NewsletterAdminLinkMixin, ExtendibleModelAdminMixin, admin.ModelAdmin
):
    form = SubscriptionAdminForm
    list_display = (
        "name",
        "email",
        "admin_newsletter",
        "admin_subscribe_date",
        "admin_unsubscribe_date",
        "admin_status_text",
        "admin_status",
    )
    list_display_links = ("name", "email")
    list_filter = ("newsletter", "subscribed", "unsubscribed", "subscribe_date")
    search_fields = (
        "name_field",
        "email_field",
        "user__first_name",
        "user__last_name",
        "user__email",
    )
    readonly_fields = ("ip", "subscribe_date", "unsubscribe_date", "activation_code")
    date_hierarchy = "subscribe_date"
    actions = ["make_subscribed", "make_unsubscribed"]
    exclude = ["unsubscribed"]

    """ List extensions """

    def admin_status(self, obj):
        img_tag = '<img src="{}" width="10" height="10" alt="{}"/>'
        alt_txt = self.admin_status_text(obj)
        if obj.unsubscribed:
            return format_html(img_tag, ICON_URLS["no"], alt_txt)

        if obj.subscribed:
            return format_html(img_tag, ICON_URLS["yes"], alt_txt)
        else:
            return format_html(img_tag, ICON_URLS["wait"], alt_txt)

    admin_status.short_description = ""

    def admin_status_text(self, obj):
        if obj.subscribed:
            return _("Subscribed")
        elif obj.unsubscribed:
            return _("Unsubscribed")
        else:
            return _("Unactivated")

    admin_status_text.short_description = _("Status")

    def admin_subscribe_date(self, obj):
        if obj.subscribe_date:
            return date_format(obj.subscribe_date)
        else:
            return ""

    admin_subscribe_date.short_description = _("subscribe date")

    def admin_unsubscribe_date(self, obj):
        if obj.unsubscribe_date:
            return date_format(obj.unsubscribe_date)
        else:
            return ""

    admin_unsubscribe_date.short_description = _("unsubscribe date")

    """ Actions """

    def make_subscribed(self, request, queryset):
        rows_updated = queryset.update(subscribed=True)
        self.message_user(
            request,
            ngettext(
                "%d user has been successfully subscribed.",
                "%d users have been successfully subscribed.",
                rows_updated,
            )
            % rows_updated,
        )

    make_subscribed.short_description = _("Subscribe selected users")

    def make_unsubscribed(self, request, queryset):
        rows_updated = queryset.update(subscribed=False)
        self.message_user(
            request,
            ngettext(
                "%d user has been successfully unsubscribed.",
                "%d users have been successfully unsubscribed.",
                rows_updated,
            )
            % rows_updated,
        )

    make_unsubscribed.short_description = _("Unsubscribe selected users")

    """ Views """

    def subscribers_import(self, request):
        if not request.user.has_perm("newsletter.add_subscription"):
            raise PermissionDenied()
        if request.POST:
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                request.session["addresses"] = form.get_addresses()
                request.session["newsletter_pk"] = form.cleaned_data["newsletter"].pk

                confirm_url = reverse("admin:newsletter_subscription_import_confirm")
                return HttpResponseRedirect(confirm_url)
        else:
            form = ImportForm()

        return render(
            request,
            "admin/newsletter/subscription/importform.html",
            {"form": form},
        )

    def subscribers_import_confirm(self, request):
        # If no addresses are in the session, start all over.

        if "addresses" not in request.session:
            import_url = reverse("admin:newsletter_subscription_import")
            return HttpResponseRedirect(import_url)

        addresses = request.session["addresses"]
        newsletter = Newsletter.objects.get(pk=request.session["newsletter_pk"])

        logger.debug("Confirming addresses: %s", addresses)

        if request.POST:
            form = ConfirmForm(request.POST)
            if form.is_valid():
                try:
                    for email, name in addresses.items():
                        address_inst = make_subscription(newsletter, email, name)
                        address_inst.save()
                finally:
                    del request.session["addresses"]
                    del request.session["newsletter_pk"]

                messages.success(
                    request,
                    ngettext(
                        "%d subscription has been successfully added.",
                        "%d subscriptions have been successfully added.",
                        len(addresses),
                    )
                    % len(addresses),
                )

                changelist_url = reverse("admin:newsletter_subscription_changelist")
                return HttpResponseRedirect(changelist_url)
        else:
            form = ConfirmForm()

        return render(
            request,
            "admin/newsletter/subscription/confirmimportform.html",
            {"form": form, "subscribers": addresses},
        )

    """ URLs """

    def get_urls(self):
        urls = super().get_urls()

        my_urls = [
            path(
                "import/",
                self._wrap(self.subscribers_import),
                name=self._view_name("import"),
            ),
            path(
                "import/confirm/",
                self._wrap(self.subscribers_import_confirm),
                name=self._view_name("import_confirm"),
            ),
        ]
        # Translated JS strings - these should be app-wide but are
        # only used in this part of the admin. For now, leave them here.
        if HAS_CBV_JSCAT:
            my_urls.append(
                path(
                    "jsi18n/",
                    JavaScriptCatalog.as_view(packages=("newsletter",)),
                    name="newsletter_js18n",
                )
            )
        else:
            my_urls.append(
                path(
                    "jsi18n/",
                    javascript_catalog,
                    {"packages": ("newsletter",)},
                    name="newsletter_js18n",
                )
            )

        return my_urls + urls
