from django.urls import path
from .views import (
    TestModelListView,
    TestModelCreateView,
    TestModelUpdateView,
    TestModelDetailView,
    TestModelDeleteView,
    TestModelSendMarketingEmailView,
    TestModelCreateMarketingEmailView,
    TestModelUpdateMarketingEmailView,
    TestModelDeleteMarketingEmailView,
    # TestModelUnsubscribeView,
    unsubscribe_view,
    unsubscribe_success,
)

urlpatterns = [
    path("test-models/", TestModelListView.as_view(), name="test_model_list"),
    path(
        "test-models/create/", TestModelCreateView.as_view(), name="test_model_create"
    ),
    path(
        "test-models/<int:pk>/update/",
        TestModelUpdateView.as_view(),
        name="test_model_update",
    ),
    path(
        "test-models/<int:pk>/", TestModelDetailView.as_view(), name="test_model_detail"
    ),
    path(
        "test-models/<int:pk>/delete/",
        TestModelDeleteView.as_view(),
        name="test_model_delete",
    ),
    path(
        "send-marketing-email/",
        TestModelSendMarketingEmailView.as_view(),
        name="send_marketing_email",
    ),
    path(
        "create-marketing-email-message/",
        TestModelCreateMarketingEmailView.as_view(),
        name="create_marketing_email_message",
    ),
    path(
        "update-marketing-email-message/<int:pk>/",
        TestModelUpdateMarketingEmailView.as_view(),
        name="update_marketing_email_message",
    ),
    path(
        "delete-marketing-email-message/<int:pk>/",
        TestModelDeleteMarketingEmailView.as_view(),
        name="delete_marketing_email_message",
    ),
    path(
        "unsubscribe/<str:email>/<uuid:token>/",
        unsubscribe_view,
        name="unsubscribe",
    ),
    path(
        "unsubscribe_success/",
        unsubscribe_success,
        name="unsubscribe_success",
    ),
]
