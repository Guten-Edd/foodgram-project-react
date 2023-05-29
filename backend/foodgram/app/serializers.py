from rest_framework.serializers import ModelSerializer

from .models import Recipe


class RecipeShortSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
