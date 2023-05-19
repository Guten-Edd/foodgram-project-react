from django.db import models
from users.models import Myuser


class Tag(models.Model):
    """Модель теги для рецептов."""

    name = models.CharField(verbose_name='Название',
                            max_length=200,
                            unique=True,
                            blank=False)
    color = models.CharField(verbose_name='Цветовой HEX-код',
                             default='#49B64E',
                             unique=True,
                             max_length=7)
    slug = models.SlugField(unique=True,
                            max_length=200,
                            verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(verbose_name='Название',
                            max_length=200,
                            blank=False)
    measurement_unit = models.CharField(verbose_name='Единицы измерения',
                                        max_length=200,
                                        blank=False)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепты."""

    author = models.ForeignKey(Myuser,
                               on_delete=models.CASCADE,
                               verbose_name='Автор рецепта')
    name = models.CharField(max_length=200,
                            verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
        help_text='Вставьте сюда картинку блюда',
        null=False,
        blank=False
        )
    text = models.TextField(verbose_name='Текстовое описание',
                            help_text='Текстовое описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe_id', 'ingredient_id'),
        verbose_name='Ингредиенты',
        blank=False
        )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        default_related_name = 'recipe'
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Связывающая таблица рецептов и ингредиентов."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
        )
    amount = models.PositiveIntegerField(null=False,
                                         verbose_name='Количество')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Формирование ингредиентов'
        verbose_name_plural = 'Формирования ингредиентов'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'
