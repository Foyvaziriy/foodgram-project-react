import csv
from http import HTTPMethod

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse
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
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from api.services import (
    get_all_objects,
    subscribe,
    unsubscribe,
    get_subscriptions,
    get_user_fav_or_shopping_recipes_ids,
    get_subs_ids,
    get_subs_recipes,
    get_user_shopping_cart,
)
from api.exceptions import (
    AlreadySubscribedError,
    NotSubscribedError,
    SelfSubscriptionError
)
from api.filters import RecipeFilterSet, IngredientFilterSet
from users.serializers import SubscribeSerializer, UserRecipesSerializer
from food.models import Tag, Ingredient, Recipe, FavoriteRecipe, ShoppingCart
from food.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeGETSerializer,
    RecipePOSTSerializer
)


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    ordering = ('username',)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request,
            'subs_ids': get_subs_ids(self.request.user),
            'subs_recipes': get_subs_recipes(self.request.user)
        })
        recipes_limit: str = self.request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            context['recipes_limit'] = int(recipes_limit)
        return context

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
        if request.method == HTTPMethod.POST:
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
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == HTTPMethod.DELETE:
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
        queryset = get_subscriptions(request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(
                page,
                many=True,
                context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(
            queryset,
            many=True,
            context=self.get_serializer_context()
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
    pagination_class = None


class IngredientViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet
):
    queryset = get_all_objects(Ingredient)
    serializer_class = IngredientSerializer
    ordering = ('name',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilterSet
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = get_all_objects(Recipe)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    ordering = ('created_at',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method == HTTPMethod.GET:
            serializer_class = RecipeGETSerializer
        else:
            serializer_class = RecipePOSTSerializer

        return serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request,
            'subs_ids': get_subs_ids(self.request.user),
            'favorite_recipes_ids': get_user_fav_or_shopping_recipes_ids(
                self.request.user),
            'shopping_cart': get_user_fav_or_shopping_recipes_ids(
                self.request.user, True),
        })
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = RecipeGETSerializer(
            instance,
            context=self.get_serializer_context()
        )
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

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeGETSerializer(
            instance,
            context=self.get_serializer_context()
        )

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserRecipesSerializer
    )
    def favorite(self, request, pk=None):
        if request.method == HTTPMethod.POST:
            recipe = get_object_or_404(Recipe, id=pk)
            _, is_created = FavoriteRecipe.objects.get_or_create(
                user=request.user,
                recipe=recipe)
            serializer = self.serializer_class(
                recipe,
                context=self.get_serializer_context()
            )

            if not is_created:
                return Response(
                    {'details': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == HTTPMethod.DELETE:
            get_object_or_404(
                FavoriteRecipe,
                user_id=request.user.id,
                recipe_id=pk).delete()
            return Response('', status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserRecipesSerializer
    )
    def shopping_cart(self, request, pk=None):
        if request.method == HTTPMethod.POST:
            recipe = get_object_or_404(Recipe, id=pk)
            _, is_created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe)
            serializer = self.serializer_class(
                recipe,
                context=self.get_serializer_context()
            )

            if not is_created:
                return Response(
                    {'details': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == HTTPMethod.DELETE:
            get_object_or_404(
                ShoppingCart,
                user_id=request.user.id,
                recipe_id=pk).delete()
            return Response('', status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, pk=None):
        response = HttpResponse(
            content_type='text/plain',
            headers={
                'Content-Disposition': (
                    'attachment; filename="shopping_cart.txt"')
            },
        )

        writer = csv.writer(response)
        writer.writerow(('Список покупок',))
        writer.writerow('')

        amounts = {}
        measurement_units = {}
        shopping_cart = get_user_shopping_cart(self.request.user)

        for ingredient, amount, measurement_unit in shopping_cart:
            measurement_units[ingredient] = measurement_unit

            if amounts.get(ingredient):
                amounts[ingredient] += amount
            else:
                amounts[ingredient] = amount

        for ing in amounts.keys():
            writer.writerow(
                [f'- {ing}: {amounts[ing]} {measurement_units[ing]}']
            )

        return response
