import django_filters

from food.models import Recipe, Ingredient
from api.services import (
    get_user_fav_or_shopping_recipes_ids,
    get_recipes_ids_with_same_tag,
    get_tag_names,
)


class IngredientFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(method='favorite')
    is_in_shopping_cart = django_filters.NumberFilter(method='shopping_cart')
    tags = django_filters.MultipleChoiceFilter(
        method='by_tags',
        choices=get_tag_names()
    )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def by_tags(self, queryset, name, value):
        return queryset.filter(id__in=get_recipes_ids_with_same_tag(value))

    def favorite(self, queryset, name, value):
        if not self.request.user:
            return queryset
        favs = get_user_fav_or_shopping_recipes_ids(self.request.user)
        if value:
            return queryset.filter(id__in=favs)
        return queryset.exclude(id__in=favs)

    def shopping_cart(self, queryset, name, value):
        if not self.request.user:
            return queryset
        shopping_cart = get_user_fav_or_shopping_recipes_ids(
            self.request.user, is_shopping_cart=True)
        if value:
            return queryset.filter(id__in=shopping_cart)
        return queryset.exclude(id__in=shopping_cart)
