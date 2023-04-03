from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.hashers import check_password

from users.models import User
from .serializers import (UserSerializer, CustomAuthTokenSerializer,
                          SetPasswordSerializer)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer

    @action(detail=False, methods=['GET'], url_path='me',
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='set_password',
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        user = request.user
        serializer = self.get_serializer_class()(data=request.POST)
        if serializer.is_valid():
            if check_password(
                request.POST['current_password'],
                user.password
            ):
                user.set_password(request.POST['new_password'])
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'неверный пароль'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Remove all auth tokens owned by request.user.
        """
        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
