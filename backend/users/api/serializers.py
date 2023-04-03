from rest_framework.serializers import (
    ModelSerializer, SlugRelatedField, CurrentUserDefault, ValidationError,
    SerializerMethodField, Serializer, CharField,
)
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import authenticate

from users.models import User, Follow


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return Follow.objects.filter(user=user, following=obj).exists()
        return False


class SetPasswordSerializer(Serializer):
    new_password = CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    current_password = CharField(
        write_only=True,
        required=True,
    )


class FollowSerializer(ModelSerializer):
    user = SlugRelatedField(
        slug_field='username',
        queryset=Follow.objects.all(),
        default=CurrentUserDefault()
    )
    following = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = '__all__'
        read_only_fields = ('user',)
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following'],
                message='Вы уже подписаны.'
            )
        ]

    def validate(self, attrs):
        if self.context.get('request').user == attrs.get('following'):
            raise ValidationError(
                'Нельзя подписаться на самого себя')
        return super().validate(attrs)


class CustomAuthTokenSerializer(Serializer):
    email = CharField(
        write_only=True
    )
    password = CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = CharField(
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
