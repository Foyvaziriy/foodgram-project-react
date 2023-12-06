from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=128, unique=True,)
    color = models.CharField('Цвет тега', max_length=15, unique=True)
    slug = models.SlugField('Слаг тега', max_length=128, unique=True,)

    def __str__(self) -> str:
        return self.name


class MeasurementUnit(models.Model):
    name = models.CharField('Единица измерения', max_length=16, unique=True,)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=128, unique=True,)
    measurement_unit = models.ForeignKey(
        MeasurementUnit, on_delete=models.CASCADE,)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',)
    name = models.CharField(
        'Название блюда',
        max_length=128,
    )
    image = models.ImageField('Картинка',)
    text = models.TextField('Текст рецепта',)
    cooking_time = models.IntegerField('Время готовки в часах',)

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient')
    ingredient_id = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient')
    amount = models.DecimalField('Количество', max_digits=5, decimal_places=2)
