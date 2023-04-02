from rest_framework.serializers import (
    ModelSerializer, SlugRelatedField, CurrentUserDefault, ValidationError,
    SerializerMethodField
)
from rest_framework.validators import UniqueTogetherValidator

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
        user = self.context.get('request').user
        if user.is_authenticated():
            return Follow.objects.filter(user=user, following=obj).exists()
        return False


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
