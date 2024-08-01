import logging

from django.urls import path

from django.conf import settings

from django.contrib import admin
from django.contrib.sites.models import Site

from django.core import serializers

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render

from django.utils.html import format_html
from django.utils.translation import gettext as _

from django.views.decorators.clickjacking import xframe_options_sameorigin

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
from ..models.attachment import Attachment
from ..models.submission import Submission

from django.utils.timezone import now
from django.urls import reverse

from .admin_forms import (
    ArticleInline,
    AttachmentInline,
)
from .admin_utils import ExtendibleModelAdminMixin
from .newsletter import NewsletterAdminLinkMixin


logger = logging.getLogger(__name__)


class MessageAdmin(
    NewsletterAdminLinkMixin, ExtendibleModelAdminMixin, admin.ModelAdmin
):
    save_as = True
    list_display = (
        "admin_title",
        "admin_newsletter",
        "admin_preview",
        "date_create",
        "date_modify",
    )
    list_filter = ("newsletter",)
    date_hierarchy = "date_create"
    prepopulated_fields = {"slug": ("title",)}

    inlines = [
        ArticleInline,
        AttachmentInline,
    ]

    """ List extensions """

    def admin_title(self, obj):
        return format_html('<a href="{}/">{}</a>', obj.id, obj.title)

    admin_title.short_description = _("message")

    def admin_preview(self, obj):
        url = reverse(
            "admin:" + self._view_name("preview"),
            args=(obj.id,),
            current_app=self.admin_site.name,
        )
        return format_html('<a href="{}">{}</a>', url, _("Preview"))

    admin_preview.short_description = ""

    """ Views """

    def preview(self, request, object_id):
        return render(
            request,
            "admin/newsletter/message/preview.html",
            {
                "message": self._getobj(request, object_id),
                "attachments": Attachment.objects.filter(message_id=object_id),
            },
        )

    @xframe_options_sameorigin
    def preview_html(self, request, object_id):
        message = self._getobj(request, object_id)

        if not message.html_template:
            raise Http404(
                _(
                    "No HTML template associated with the newsletter this "
                    "message belongs to."
                )
            )

        c = {
            "message": message,
            "site": Site.objects.get_current(),
            "newsletter": message.newsletter,
            "date": now(),
            "STATIC_URL": settings.STATIC_URL,
            "MEDIA_URL": settings.MEDIA_URL,
        }

        return HttpResponse(message.html_template.render(c))

    @xframe_options_sameorigin
    def preview_text(self, request, object_id):
        message = self._getobj(request, object_id)

        c = {
            "message": message,
            "site": Site.objects.get_current(),
            "newsletter": message.newsletter,
            "date": now(),
            "STATIC_URL": settings.STATIC_URL,
            "MEDIA_URL": settings.MEDIA_URL,
        }

        return HttpResponse(message.text_template.render(c), content_type="text/plain")

    def submit(self, request, object_id):
        submission = Submission.from_message(self._getobj(request, object_id))

        change_url = reverse("admin:newsletter_submission_change", args=[submission.id])

        return HttpResponseRedirect(change_url)

    def subscribers_json(self, request, object_id):
        message = self._getobj(request, object_id)

        json = serializers.serialize(
            "json", message.newsletter.get_subscriptions(), fields=()
        )
        return HttpResponse(json, content_type="application/json")

    """ URLs """

    def get_urls(self):
        urls = super().get_urls()

        my_urls = [
            path(
                "<object_id>/preview/",
                self._wrap(self.preview),
                name=self._view_name("preview"),
            ),
            path(
                "<object_id>/preview/html/",
                self._wrap(self.preview_html),
                name=self._view_name("preview_html"),
            ),
            path(
                "<object_id>/preview/text/",
                self._wrap(self.preview_text),
                name=self._view_name("preview_text"),
            ),
            path(
                "<object_id>/submit/",
                self._wrap(self.submit),
                name=self._view_name("submit"),
            ),
            path(
                "<object_id>/subscribers/json/",
                self._wrap(self.subscribers_json),
                name=self._view_name("subscribers_json"),
            ),
        ]

        return my_urls + urls
