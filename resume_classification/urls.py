# resume_classification/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('resume_classification/', views.resume_classification, name='resume_classification'),
]

