from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model


User = get_user_model()

MIN_COOKING_TIME_AND_AMOUNT: int = 1
MAX_COOKING_TIME_AND_AMOUNT: int = 32000


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=128, unique=True,)
    color = models.CharField('Цвет тега', max_length=15, unique=True)
    slug = models.SlugField('Слаг тега', max_length=128, unique=True,)

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class MeasurementUnit(models.Model):
    name = models.CharField('Единица измерения', max_length=16, unique=True,)

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=128, unique=True,)
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',)
    name = models.CharField(
        'Название блюда',
        max_length=200,
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/',)
    text = models.TextField('Текст рецепта',)
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки в минутах',
        validators=[
            MinValueValidator(limit_value=MIN_COOKING_TIME_AND_AMOUNT),
            MaxValueValidator(limit_value=MAX_COOKING_TIME_AND_AMOUNT)
        ]
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag',
        verbose_name='Тег'
    )

    class Meta:
        ordering = ('recipe',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(limit_value=MIN_COOKING_TIME_AND_AMOUNT),
            MaxValueValidator(limit_value=MAX_COOKING_TIME_AND_AMOUNT)
        ]
    )

    class Meta:
        ordering = ('recipe',)


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user',)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user',)
