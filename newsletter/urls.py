# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.newsletter, name='newsletter'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/success/', views.subscribe_success, name='subscribe_success'),
    path('send_newsletter/', views.send_newsletter, name='send_newsletter'),
    path('newsletter_sent/', views.newsletter_sent, name='newsletter_sent'),
]
