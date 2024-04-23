from .base import *

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
INSTALLED_APPS.append("db")
INSTALLED_APPS.append("import_export")
INSTALLED_APPS.append("enmerkar")
INSTALLED_APPS.append("django.contrib.humanize")
USE_FAKE = False
DEFAULT_FROM_EMAIL = "aclark@aclark.net"
INSTALLED_APPS.append("django_social_share")
INSTALLED_APPS.append("wagtail.contrib.routable_page")
INSTALLED_APPS.append("django.contrib.postgres")
INSTALLED_APPS.append("wagtailcaptcha")
INSTALLED_APPS.append("hijack")
INSTALLED_APPS.append("resume")
INSTALLED_APPS.append("blog")
INSTALLED_APPS.append("colorful")
INSTALLED_APPS.append("puput")
INSTALLED_APPS.append("nowpage")
MIDDLEWARE.append("hijack.middleware.HijackUserMiddleware")
