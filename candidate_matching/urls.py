# candidate_matching/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("candidate_matching/", views.upload_resume, name="candidate_matching"),
]
