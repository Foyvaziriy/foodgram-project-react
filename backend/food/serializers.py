import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

from food.models import (
    Tag, Ingredient, Recipe,
    MIN_COOKING_TIME_AND_AMOUNT, MAX_COOKING_TIME_AND_AMOUNT
)
from users.serializers import UserSerializer
from api.services import (
    get_recipe_ingredients_with_amounts,
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


class IngredientPOSTSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_COOKING_TIME_AND_AMOUNT,
        max_value=MAX_COOKING_TIME_AND_AMOUNT
    )

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount'
        )

    def validate(self, attrs):
        dif = set(self.Meta.fields).symmetric_difference(set(attrs))
        if dif:
            raise serializers.ValidationError(
                f'Поля {dif} не предоставлены'
            )
        return super().validate(attrs)

    def validate_id(self, value):
        if value not in get_available_ids(Ingredient):
            raise serializers.ValidationError(
                f'Ингредиента {value} не существует')
        return value


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
        return self.context.get('amounts')[obj.id]


class RecipeGETSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField('is_favorite')
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

    def get_author(self, obj):
        return UserSerializer(
            obj.author,
            context={'request': self.context.get('request'),
                     'subs_ids': self.context.get('subs_ids')}
        ).data

    def is_favorite(self, obj):
        return obj.id in self.context.get('favorite_recipes_ids')

    def shopping_cart(self, obj):
        return obj.id in self.context.get('shopping_cart')

    def get_ingredients(self, obj):
        ingredients, amounts = get_recipe_ingredients_with_amounts(obj.id)
        return InlineIngredientSerializer(
            ingredients,
            many=True,
            context={'recipe_id': obj.id,
                     'amounts': amounts}
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
    ingredients = IngredientPOSTSerializer(many=True)
    tags = serializers.ListField(child=serializers.IntegerField())
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME_AND_AMOUNT,
        max_value=MAX_COOKING_TIME_AND_AMOUNT
    )

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

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Получен пустой список')
        for tag_id in value:
            if tag_id not in get_available_ids(Tag):
                raise serializers.ValidationError(
                    'Такого тега не существует')
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
        image = validated_data.get('image')

        if image:
            instance.image = image
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
