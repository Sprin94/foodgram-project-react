from rest_framework.serializers import (
    ModelSerializer, PrimaryKeyRelatedField, ValidationError,
    SerializerMethodField, Serializer, CharField
)
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import authenticate

from recipes.api import serializers as recipe_serializers
from users.models import User, Follow


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

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


class FollowCreateSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    following = PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = '__all__'
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
            msg = 'Must include "email" and "password".'
            raise ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class FollowSerializer(UserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return recipe_serializers.RecipeInlineSerializer(
            recipes, many=True).data
