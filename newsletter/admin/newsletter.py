import logging


from django.conf import settings

from django.contrib import admin


from django.utils.html import format_html
from django.utils.translation import gettext as _


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

from ..models import Newsletter, Subscription, Message, Submission

# from ..models.newsletter import Newsletter
# from .models.subscription import Subscription
# from .models.attachment import Attachment
# from .models.article import Article
# from .models.submission import Submission
# from .models.message import Message

from django.urls import reverse


logger = logging.getLogger(__name__)


# Construct URL's for icons
ICON_URLS = {
    "yes": "%snewsletter/admin/img/icon-yes.gif" % settings.STATIC_URL,
    "wait": "%snewsletter/admin/img/waiting.gif" % settings.STATIC_URL,
    "submit": "%snewsletter/admin/img/submitting.gif" % settings.STATIC_URL,
    "no": "%snewsletter/admin/img/icon-no.gif" % settings.STATIC_URL,
}


class NewsletterAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "admin_subscriptions",
        "admin_messages",
        "admin_submissions",
    )
    prepopulated_fields = {"slug": ("title",)}

    """ List extensions """

    def _admin_url(self, obj, model, text):
        url = reverse(
            "admin:%s_%s_changelist" % (model._meta.app_label, model._meta.model_name),
            current_app=self.admin_site.name,
        )

        return format_html('<a href="{}?newsletter__id={}">{}</a>', url, obj.id, text)

    def admin_messages(self, obj):
        return self._admin_url(obj, Message, _("Messages"))

    admin_messages.short_description = ""

    def admin_subscriptions(self, obj):
        return self._admin_url(obj, Subscription, _("Subscriptions"))

    admin_subscriptions.short_description = ""

    def admin_submissions(self, obj):
        return self._admin_url(obj, Submission, _("Submissions"))

    admin_submissions.short_description = ""


class NewsletterAdminLinkMixin:
    def admin_newsletter(self, obj):
        opts = Newsletter._meta
        newsletter = obj.newsletter
        url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_change",
            args=(newsletter.id,),
            current_app=self.admin_site.name,
        )

        return format_html('<a href="{}">{}</a>', url, newsletter)

    admin_newsletter.short_description = _("newsletter")
