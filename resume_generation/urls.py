# resume_generation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("resume_generation/", views.upload_data, name="resume_generation"),
]
