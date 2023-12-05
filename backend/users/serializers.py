from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer
)

from api.services import get_subs_ids


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
        user = self.context.get('request').user
        return (obj.id,) in get_subs_ids(user.id)


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


class SubscribeSerializer(serializers.ModelSerializer):
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
        user = self.context.get('request').user
        return (obj.id,) in get_subs_ids(user.id)
