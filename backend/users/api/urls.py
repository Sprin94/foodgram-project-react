from django.urls import path, include
from rest_framework.routers import SimpleRouter

from users.api.viewsets import (
    UserViewSet, CustomAuthToken, Logout
)

router_v1 = SimpleRouter()

router_v1.register('users', UserViewSet, basename='users')

auth_patterns = [
    path(
        'login',
        CustomAuthToken.as_view(),
        name='login'
    ),
    path(
        'logout',
        Logout.as_view(),
        name='logout'
    ),
]

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/', include(auth_patterns)),
]
