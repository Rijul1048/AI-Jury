from django.contrib import admin
from django.urls import path
from search_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    # Main pages
    path('', views.index, name='index'),
    path('services', views.services, name='services'),
    path('about', views.about, name='about'),
    path('chat', views.chat, name='chat'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)