# named_entity_recognition/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('success/', views.upload_success, name='success'),
]