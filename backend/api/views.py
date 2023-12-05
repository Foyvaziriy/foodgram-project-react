from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet as DjoserUserViewSet

from api.services import (
    subscribe,
    unsubscribe,
    get_subscriptions
)
from api.exceptions import (
    AlreadySubscribedError,
    NotSubscribedError,
    SelfSubscriptionError
)
from users.serializers import SubscribeSerializer


User = get_user_model()


class UserViewSet(DjoserUserViewSet):

    @action(
        methods=["get", "put", "patch", "delete"],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, args, kwargs)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request: Request, id: int = None) -> Response:
        if request.method == 'POST':
            try:
                user = get_object_or_404(User, id=id)
                subscribe(request.user, user)
            except AlreadySubscribedError:
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except SelfSubscriptionError:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            try:
                unsubscribe(request.user.id, id)
            except NotSubscribedError:
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request: Request, pk: int = None):
        queryset = get_subscriptions(request.user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
