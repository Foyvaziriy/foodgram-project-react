from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer
)
from api.services import get_subscriptions


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
        subs = self.context.get('subs')
        request = self.context.get('request')
        if not subs:
            subs = get_subscriptions(request.user.id)
        return obj in subs


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
        subs = self.context.get('subs')
        request = self.context.get('request')
        if not subs:
            subs = get_subscriptions(request.user.id)
        return obj in subs
