# named_entity_recognition/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('named_entity_recognition/', views.named_entity_recognition, name='named_entity_recognition'),
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('success/', views.upload_success, name='success'),
]