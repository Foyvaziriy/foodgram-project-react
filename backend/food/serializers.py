import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from food.models import Tag, Ingredient, Recipe
from users.serializers import UserSerializer
from api.services import (
    get_ingredient_amount,
    get_recipe_ingredients,
    get_available_ids,
    create_recipe,
    add_ingredients_to_recipe,
    add_tags_to_recipe
)


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
        return get_ingredient_amount(
            self.context.get('recipe_id'),
            ingredient_id=obj.id
        )


class RecipeGETSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
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
            context={'recipe_id': obj.id}
            ).data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipePOSTSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()))
    tags = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, attrs):
        if set(attrs.keys()).symmetric_difference(self.Meta.fields):
            raise serializers.ValidationError('All fields are required')
        return super().validate(attrs)

    def validate_ingredients(self, value):
        for ingr in value:
            if ingr['id'] not in get_available_ids(Ingredient):
                raise serializers.ValidationError(
                    'Такого ингредиента не существует')
        return value

    def validate_tags(self, value):
        for tag_id in value:
            if tag_id not in get_available_ids(Tag):
                raise serializers.ValidationError(
                    'Такого тэга не существует')
        return value

    def create(self, validated_data):
        return create_recipe(
            author_id=self.context.get('request').user.id,
            ingredients=validated_data.pop('ingredients'),
            tags_ids=validated_data.pop('tags'),
            **validated_data
        )

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')

        instance.save()

        add_ingredients_to_recipe(
            edit=True,
            recipe=instance,
            ingredients_amounts=ingredients
        )
        add_tags_to_recipe(
            edit=True,
            recipe=instance,
            tags_ids=tags
        )

        return instance
