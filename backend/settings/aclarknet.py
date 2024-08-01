from .base import *  # noqa

FOUR_O_3 = "Sorry, you are not allowed to see or do that."

CLIENT_CATEGORIES = {
    "government": "government",
    "non-profit": "nonprofit",
    "private-sector": "commercial",
    "colleges-universities": "education",
}

DOC_TYPES = {
    "invoice": "Invoice",
    "estimate": "Estimate",
    "statement-of-work": "Statement of Work",
    "task-order": "Task Order",
}

MAIL_FROM = "aclark.net@aclark.net"
MAIL_TO = "aclark@aclark.net"
PER_PAGE = 10
DOC_TYPE = "Invoice"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
INSTALLED_APPS.append("db")  # noqa
INSTALLED_APPS.append("import_export")  # noqa
INSTALLED_APPS.append("enmerkar")  # noqa
INSTALLED_APPS.append("django.contrib.humanize")  # noqa
USE_FAKE = False
DEFAULT_FROM_EMAIL = "aclark@aclark.net"
INSTALLED_APPS.append("django_social_share")  # noqa
INSTALLED_APPS.append("wagtail.contrib.routable_page")  # noqa
INSTALLED_APPS.append("django.contrib.postgres")  # noqa
INSTALLED_APPS.append("wagtailcaptcha")  # noqa
INSTALLED_APPS.append("hijack")  # noqa
INSTALLED_APPS.append("resume")  # noqa
INSTALLED_APPS.append("blog")  # noqa
INSTALLED_APPS.append("puput")  # noqa
INSTALLED_APPS.append("colorful")  # noqa
INSTALLED_APPS.append("nowpage")  # noqa
INSTALLED_APPS.append("django.contrib.sites")  # noqa
INSTALLED_APPS.append("newsletter")  # noqa
INSTALLED_APPS.append("explorer")  # noqa
INSTALLED_APPS.append("django.contrib.admindocs")  # noqa
INSTALLED_APPS.append("sorl.thumbnail")  # noqa
MIDDLEWARE.append("hijack.middleware.HijackUserMiddleware")  # noqa
EXPLORER_CONNECTIONS = {"Default": "default"}
EXPLORER_DEFAULT_CONNECTION = "default"
SITE_ID = 1  # newsletter
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django.contrib.admin"]  # noqa
INSTALLED_APPS.append("backend.apps.CustomAdminConfig")  # noqa
