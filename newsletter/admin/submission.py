import logging

from django.urls import path

from django.contrib import admin, messages


from django.http import HttpResponseRedirect


from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.utils.formats import date_format


try:
    from django.views.i18n import JavaScriptCatalog  # noqa

    HAS_CBV_JSCAT = True
except ImportError:  # Django < 1.10
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

from django.utils.timezone import now
from django.urls import reverse

from .admin_forms import (
    SubmissionAdminForm,
)
from .admin_utils import ExtendibleModelAdminMixin
from .newsletter import NewsletterAdminLinkMixin, ICON_URLS


logger = logging.getLogger(__name__)


class SubmissionAdmin(
    NewsletterAdminLinkMixin, ExtendibleModelAdminMixin, admin.ModelAdmin
):
    form = SubmissionAdminForm
    list_display = (
        "admin_message",
        "admin_newsletter",
        "admin_publish_date",
        "publish",
        "admin_status_text",
        "admin_status",
    )
    date_hierarchy = "publish_date"
    list_filter = ("newsletter", "publish", "sent")
    save_as = True
    filter_horizontal = ("subscriptions",)

    """ List extensions """

    def admin_message(self, obj):
        return format_html('<a href="{}/">{}</a>', obj.id, obj.message.title)

    admin_message.short_description = _("submission")

    def admin_publish_date(self, obj):
        if obj.publish_date:
            return date_format(obj.publish_date, "DATETIME_FORMAT")
        else:
            return ""

    admin_publish_date.short_description = _("publish date")

    def admin_status(self, obj):
        if obj.prepared:
            if obj.sent:
                return format_html(
                    '<img src="{}" width="10" height="10" alt="{}"/>',
                    ICON_URLS["yes"],
                    self.admin_status_text(obj),
                )
            else:
                if obj.publish_date > now():
                    return format_html(
                        '<img src="{}" width="10" height="10" alt="{}"/>',
                        ICON_URLS["wait"],
                        self.admin_status_text(obj),
                    )
                else:
                    return format_html(
                        '<img src="{}" width="12" height="12" alt="{}"/>',
                        ICON_URLS["wait"],
                        self.admin_status_text(obj),
                    )
        else:
            return format_html(
                '<img src="{}" width="10" height="10" alt="{}"/>',
                ICON_URLS["no"],
                self.admin_status_text(obj),
            )

    admin_status.short_description = ""

    def admin_status_text(self, obj):
        if obj.prepared:
            if obj.sent:
                return _("Sent.")
            else:
                if obj.publish_date > now():
                    return _("Delayed submission.")
                else:
                    return _("Submitting.")
        else:
            return _("Not sent.")

    admin_status_text.short_description = _("Status")

    """ Views """

    def submit(self, request, object_id):
        submission = self._getobj(request, object_id)

        if submission.sent or submission.prepared:
            messages.info(request, _("Submission already sent."))
            change_url = reverse("admin:newsletter_submission_change", args=[object_id])
            return HttpResponseRedirect(change_url)

        submission.prepared = True
        submission.save()

        messages.info(request, _("Your submission is being sent."))

        changelist_url = reverse("admin:newsletter_submission_changelist")
        return HttpResponseRedirect(changelist_url)

    """ URLs """

    def get_urls(self):
        urls = super().get_urls()

        my_urls = [
            path(
                "<object_id>/submit/",
                self._wrap(self.submit),
                name=self._view_name("submit"),
            )
        ]

        return my_urls + urls
