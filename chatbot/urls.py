# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("chatbot/", views.chatbot_page, name="chatbot_page"),
    path("api/chatbot/", views.chatbot_api, name="chatbot_api"),
]
