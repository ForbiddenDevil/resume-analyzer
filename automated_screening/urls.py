# automated_screening/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('automated_screening/', views.automated_screening, name='automated_screening'),
]