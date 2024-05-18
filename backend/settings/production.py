from .aclarknet import *
import os

DEBUG = False

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

INSTALLED_APPS.append("allauth.socialaccount.providers.github")
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": os.environ.get("GITHUB_CLIENT_ID"),
            "secret": os.environ.get("GITHUB_SECRET"),
            "key": os.environ.get("GITHUB_KEY"),
        }
    },
}
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

SECRET_KEY = os.environ.get("SECRET_KEY", "not-a-secret")

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = "static.aclark.net"
AWS_S3_REGION_NAME = "us-east-1"

STORAGES.update(
    {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        }
    }
)
CSRF_TRUSTED_ORIGINS = ["https://aclark.net"]
