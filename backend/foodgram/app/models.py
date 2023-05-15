from django.db import models


class Tag(models.Model):
    """
    Модель тег для рецептов.
    """

    name = models.CharField(verbose_name='Название',
                            max_length=200,
                            unique=True,
                            blank=False)
    color = models.CharField(verbose_name='Цветовой HEX-код',
                             default='#49B64E',
                             unique=True,
                             max_length=7)
    slug = models.SlugField(unique=True,
                            max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиента.
    """

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
        return self.name
