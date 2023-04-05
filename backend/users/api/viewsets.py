from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from users.models import Follow, User

from .serializers import (CustomAuthTokenSerializer, FollowCreateSerializer,
                          FollowSerializer, SetPasswordSerializer,
                          UserSerializer)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'subscribe':
            return FollowCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'subscriptions':
            return FollowSerializer
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

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        users = (User.objects
                 .filter(id__in=(Follow.objects
                                 .filter(user=request.user)
                                 .values_list('following', flat=True))))
        users = self.filter_queryset(users)
        serializer = self.get_serializer_class()(
            users,
            many=True,
            context={'recipes_limit': request.GET.get('recipes_limit')}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        data = {'user': request.user.id,
                'following': pk}
        if request.method == 'POST':
            serializer = self.get_serializer_class()(
                data=data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(pk=pk)
                return Response(FollowSerializer(user).data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(**data)
        if follow:
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы не подписаны'})


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    permission_classes = (AllowAny,)


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
