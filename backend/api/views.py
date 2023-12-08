from http import HTTPMethod

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from djoser.views import UserViewSet as DjoserUserViewSet

from api.services import (
    get_all_objects,
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
from food.models import Tag, Ingredient, Recipe
from food.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeGETSerializer,
    RecipePOSTSerializer
)


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    ordering = ('username',)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, args, kwargs)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        serializer_class=SubscribeSerializer,
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
            serializer = self.serializer_class(
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
        permission_classes=[IsAuthenticated],
        serializer_class=SubscribeSerializer,
    )
    def subscriptions(self, request: Request, pk: int = None):
        queryset = get_subscriptions(request.user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet
):
    queryset = get_all_objects(Tag)
    serializer_class = TagSerializer
    ordering = ('name',)


class IngredientViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet
):
    queryset = get_all_objects(Ingredient)
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = get_all_objects(Recipe)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == HTTPMethod.GET:
            serializer_class = RecipeGETSerializer
        else:
            serializer_class = RecipePOSTSerializer

        return serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = RecipeGETSerializer(
            instance, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return Response(
                {'detail': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.method == HTTPMethod.PUT:
            raise MethodNotAllowed(request.method)
        if request.user != self.get_object().author:
            return Response(
                {'detail': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeGETSerializer(
            instance, context={'request': request})

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
