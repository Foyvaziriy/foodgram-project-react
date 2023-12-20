from django.contrib import admin
from django.utils.safestring import mark_safe

from food.models import Tag, Ingredient, MeasurementUnit, Recipe
from api.services import get_favorited_count


INGREDIENTS_MIN_NUM: int = 1


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
    min_num = INGREDIENTS_MIN_NUM


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
    readonly_fields = ('is_favorited_count',)
    fields = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'is_favorited_count',
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

    @admin.display(description='Количество добавлений рецепта в избранное')
    def is_favorited_count(self, instance):
        return mark_safe(f'<dev>{get_favorited_count(instance.id)}</dev>')
