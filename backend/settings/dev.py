from .aclarknet import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-9*0&yg#z5t6g&u3qq9wlrx8lui6g%&1adegoaq7@z@&kf4db@w"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *  # noqa
except ImportError:
    pass
INSTALLED_APPS.append("debug_toolbar")  # noqa
MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa
MIDDLEWARE.append("hijack.middleware.HijackUserMiddleware")  # noqa
INTERNAL_IPS = [
    "127.0.0.1",
]
USE_FAKE = True
