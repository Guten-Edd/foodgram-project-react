from app.models import (Favourite, Ingredient, IngredientRecipe, Recipe,
                        ShoppingCart, Tag)
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError, ImageField)
from users.models import Follow
import base64


User = get_user_model()


class Base64ImageField(ImageField):
    """Сериализатор поля image для рецептов."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

                        

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
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()

class RecipeShortSerializer(ModelSerializer):
    """ Сериализатор просмотра Рецептов. """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )



class TagSerializer(ModelSerializer):
    """ Сериализатор просмотра Тегов. """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(ModelSerializer):
    """ Сериализатор просмотра Ингредиентов. """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientsSerializer(ModelSerializer):
    """ Сериализатор просмотра ингредиента в рецепте. """

    id = PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(ModelSerializer):
    """ Сериализатор просмотра Рецепта. """

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        read_only=True,
        source='ingridients_recipe',
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favourite.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()


class CreateIngredientRecipeSerializer(ModelSerializer):
    """ Сериализатор добавления ингредиента в рецепт. """

    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount',
        )

    def validate_amount(self, data):
        if int(data) < 1:
            raise ValidationError({
                'ingredients': (
                    'Количество должно быть больше 1'
                ),
                'msg': data
            })
        return data

    def create(self, validated_data):
        return IngredientRecipe.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class RecipeCreateSerializer(ModelSerializer):
    """ Сериализатор создания/обновления рецепта. """

    image = Base64ImageField(use_url=True, max_length=None)
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise ValidationError(
                    'Есть задублированные ингредиенты!'
                )
            ingredients_list.append(ingredient_id)
        if data['cooking_time'] <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0!'
            )
        return data

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data






class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя"""
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError({
                'errors': f"Имя '{value}' недопустимо",
                })
        return value


class FollowShowSerializer(ModelSerializer):
    """ Сериализатор просмотра Подписок. """

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serialiser = RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': queryset}
        )
        return serialiser.data


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
                'errors': 'Подписка на себя запрещена.',
            })
        if Follow.objects.filter(
                user=self.context['request'].user,
                author=data['author']
        ).exists():
            raise ValidationError({
                'errors': 'Запрещено подписываться дважды.',
            })
        return data

    def to_representation(self, instance):
        return FollowShowSerializer(
            instance['author'],
            context={'request': self.context.get('request')}
        ).data
