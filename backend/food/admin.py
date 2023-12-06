from django.contrib import admin
from django.contrib.auth import get_user_model

from food.models import Tag, Ingredient, MeasurementUnit, Recipe


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    fields = (
        'name',
        'color',
        'slug',
    )


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    model = MeasurementUnit
    fields = ('name',)


class IngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    fields = (
        'name',
        'measurement_unit',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    fields = (
        'author',
        'name',
        'image',
        'text',
        'tags',
        'cooking_time',
    )
    filter_horizontal = ('tags', 'ingredients',)
    inlines = (
        IngredientsInline,
    )
    exclude = ('ingredients',)
