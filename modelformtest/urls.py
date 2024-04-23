from django.urls import path
from .views import (
    TestModelListView,
    TestModelCreateView,
    TestModelUpdateView,
    TestModelDetailView,
)

urlpatterns = [
    path('test-models/', TestModelListView.as_view(), name='test_model_list'),
    path('test-models/create/', TestModelCreateView.as_view(), name='test_model_create'),
    path('test-models/<int:pk>/update/', TestModelUpdateView.as_view(), name='test_model_update'),
    path('test-models/<int:pk>/', TestModelDetailView.as_view(), name='test_model_detail'),
]
