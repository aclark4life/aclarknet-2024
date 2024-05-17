from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("django/doc/", include("django.contrib.admindocs.urls")),
    path("django/", admin.site.urls),
    path("wagtail/", include(wagtailadmin_urls)),
    path("user/", include("siteuser.urls")),
    path("search/", include("search.urls")),
    path("modelformtest/", include("modelformtest.urls")),
    path("resume/", include("resume.urls")),
    path("dashboard/", include("db.urls")),
    path("explorer/", include("explorer.urls")),
    path("newsletter/", include("newsletter.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

urlpatterns += [
    path("hijack/", include("hijack.urls")),
]

urlpatterns += [
    path("", include("blog.urls")),
]

urlpatterns += [
    path("", include(wagtail_urls)),
]
