# Generated by Django 3.2 on 2023-05-31 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20230524_1431'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_IngredientRecipe'),
        ),
    ]
