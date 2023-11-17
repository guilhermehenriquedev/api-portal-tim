from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from modules.views import (
    homeviews,
    ldap,
    ldap_search,
    change_properties,
)

router = DefaultRouter()

router.register(r'authenticate', ldap.LdapViewSet, basename='authenticate')
router.register(r'search', ldap_search.SearchViewSet, basename='search')
router.register(r'change', change_properties.ChangeViewSet, basename='change')

urlpatterns = [
    path('', homeviews.index, name="index"),
    path('api/', include(router.urls)),
]
