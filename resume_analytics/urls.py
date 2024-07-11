# resume_analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('resume_analytics/', views.upload_document, name='resume_analytics'),
]