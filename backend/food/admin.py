from django.contrib import admin

from food.models import Tag, Ingredient, MeasurementUnit, Recipe


class TagInline(admin.TabularInline):
    model = Recipe.tags.through


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
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    fields = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    filter_horizontal = ('tags', 'ingredients',)
    inlines = (
        IngredientsInline,
        TagInline
    )
    exclude = ('ingredients', 'tags',)
    list_display = (
        'name',
        'author',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
