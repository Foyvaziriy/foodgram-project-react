from rest_framework.routers import DefaultRouter
from django.urls import path, include

from api import views


router = DefaultRouter()
router.register('users', views.UserViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
