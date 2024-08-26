"""
URL configuration for resume_analyzer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('set-api-key/', views.set_openai_api_key, name='set_openai_api_key'),
    path("admin/", admin.site.urls),
    path('', views.index, name='index'),
    path('', include('named_entity_recognition.urls')),
    path('', include('candidate_matching.urls')),
    path('', include('resume_classification.urls')),
    path('', include('chatbot.urls')),
    path('', include('resume_generation.urls')),
    path('', include('resume_analytics.urls')),
]

# Serving static files from multiple directories
urlpatterns += static(settings.NER_MEDIA_URL, document_root=settings.NER_MEDIA_ROOT)
urlpatterns += static(settings.RA_MEDIA_URL, document_root=settings.RA_MEDIA_ROOT)
