from django.db import models

from users.models import MyUser


class Tag(models.Model):
    """Модель теги для рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
        blank=False,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        default='#49B64E',
        unique=True,
        max_length=7,
        blank=False,
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Слаг',
        blank=False,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        blank=False,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200,
        blank=False,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепты."""

    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
        blank=False,
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        blank=False,
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
        help_text='Вставьте сюда картинку блюда',
        blank=False,
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        help_text='Текстовое описание рецепта',
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        blank=False,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
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
        verbose_name='Ингридиент',
    )
    amount = models.PositiveIntegerField(
        null=False,
        verbose_name='Количество/объем',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='ingredient_list',
    )

    class Meta:
        verbose_name = 'Ингредиент Рецепт'
        verbose_name_plural = 'Ингредиенты Рецепт'
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_IngredientRecipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favourite(models.Model):
    """Модель избранные."""

    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} отметил {self.recipe}'


class ShoppingCart(models.Model):
    """Модель корзина покупок."""

    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Рецепт в корзине покупок'
        verbose_name_plural = 'Рецепты в корзине покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'
