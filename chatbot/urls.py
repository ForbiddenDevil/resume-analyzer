# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("chatbot/", views.chatbot, name="chatbot"),
    path("api/chatbot/", views.chatbot_api, name="chatbot_api"),
]
