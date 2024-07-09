# resume_ranking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('resume_ranking/', views.resume_ranking, name='resume_ranking'),
]