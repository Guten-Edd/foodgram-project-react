from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (SerializerMethodField,
                                        ModelSerializer,
                                        ValidationError)
from .models import Follow
from app.models import Recipe
from app.serializers import RecipeShortSerializer


User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    """ Сериализатор пользователя. """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError("Имя недопустимо")
        return value

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()


class FollowShowSerializer(ModelSerializer):
    """ Сериализатор просмотра Подписок. """

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if recipes_limit:
            return RecipeShortSerializer(
                Recipe.objects.filter(author=author)[:int(recipes_limit)],
                many=True, context={'request': queryset}
            ).data
        return RecipeShortSerializer(
            Recipe.objects.filter(author=author),
            many=True,
            context={'request': queryset}
        ).data

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()


class FollowSerializer(ModelSerializer):
    """Сериализатор Подписки."""

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise ValidationError({
                'errors': 'Подписка на себя запрещена.'
            })
        if Follow.objects.filter(
                user=self.context['request'].user,
                author=data['author']
        ):
            raise ValidationError({
                'errors': 'Подписка уже оформлена.'
            })
        return data

    def to_representation(self, instance):
        return FollowShowSerializer(
            instance['author'],
            context={'request': self.context.get('request')}
        ).data

