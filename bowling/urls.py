from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^games$', views.index)
]