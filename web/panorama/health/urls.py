# Packages
from django.conf.urls import url
# Project
from . import views

urlpatterns = [
    url(r'^health$', views.health),
]
