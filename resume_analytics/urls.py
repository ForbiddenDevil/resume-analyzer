# resume_analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('resume_analytics/', views.resume_analytics, name='resume_analytics'),
]