
from django.contrib import admin
from django.urls import path,include
from search_app import views
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('search_app.urls')),
]
