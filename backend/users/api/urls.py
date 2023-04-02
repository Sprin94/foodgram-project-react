from django.urls import path, include
from rest_framework.routers import SimpleRouter

# from users.api.viewsets import UserViewSet

router_v1 = SimpleRouter()

# router_v1.register('', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls))
]
