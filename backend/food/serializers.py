from rest_framework import serializers

from food.models import Tag, Ingredient, Recipe
from api.services import get_ingredient_amount, get_recipe_ingredients


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = (
            'id',
        )


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class InlineIngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def get_amount(self, obj):
        print(self.instance)
        return get_ingredient_amount(
            self.context.get('recipe_id'),
            ingredient_id=obj.id
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField('favorite')
    is_in_shopping_cart = serializers.SerializerMethodField('shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def favorite(self, obj):
        return True

    def shopping_cart(self, obj):
        return True

    def get_ingredients(self, obj):
        return InlineIngredientSerializer(
            get_recipe_ingredients(obj.id),
            many=True,
            context={'recipe_id': int(obj.id)}
            ).data
