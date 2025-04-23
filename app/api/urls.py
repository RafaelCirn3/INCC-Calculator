# app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import INCCIndexViewSet

router = DefaultRouter()
router.register(r'incc', INCCIndexViewSet, basename='inccindex')

urlpatterns = [
    path('', include(router.urls)),
]
