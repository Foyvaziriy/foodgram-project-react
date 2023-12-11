from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer
)

from api.services import get_user_recipes
from food.models import Recipe


User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        subs = self.context.get('subs_ids')
        return obj.id in subs


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]


class UserRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes'
        ]

    def get_is_subscribed(self, obj):
        subs = self.context.get('subs_ids')
        return obj.id in subs

    def get_recipes(self, obj):
        return UserRecipesSerializer(
            get_user_recipes(obj),
            many=True
        ).data
