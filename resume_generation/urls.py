# resume_generation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('resume_generation/', views.resume_generation, name='resume_generation'),
]