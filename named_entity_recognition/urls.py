# named_entity_recognition/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path(
        "named_entity_recognition/",
        views.named_entity_recognition,
        name="named_entity_recognition",
    ),
    path("success/", views.upload_success, name="success"),
    path("view_ner/", views.view_ner, name="view_ner"),
]
