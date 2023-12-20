from django.contrib.auth import get_user_model
from django.db.models import Model
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.http import Http404

from users.models import UserSubs
from food.models import (
    RecipeIngredient,
    RecipeTag,
    Ingredient,
    Recipe,
    FavoriteRecipe,
    ShoppingCart,
    Tag
)
from api.exceptions import (
    AlreadySubscribedError,
    NotSubscribedError,
    SelfSubscriptionError
)


User = get_user_model()


def get_all_objects(model: Model) -> QuerySet:
    return model.objects.all()


def subscribe(user: User, sub: User) -> QuerySet:
    if user.id == sub.id:
        raise SelfSubscriptionError
    if UserSubs.objects.filter(user_id=user.id, sub_id=sub.id).exists():
        raise AlreadySubscribedError
    return UserSubs.objects.get_or_create(user=user, sub=sub)


def unsubscribe(user_id: int, sub_id: int) -> QuerySet:
    user = get_object_or_404(User, id=user_id)
    sub = get_object_or_404(User, id=sub_id)
    try:
        get_object_or_404(UserSubs, user_id=user, sub_id=sub).delete()
    except Http404:
        raise NotSubscribedError


def get_subs_ids(user_id: int) -> list[int]:
    return UserSubs.objects.filter(
        user_id=user_id).values_list('sub_id', flat=True)


def get_subscriptions(user_id: int) -> QuerySet:
    return User.objects.filter(id__in=get_subs_ids(user_id))


def get_recipe_ingredients_with_amounts(
        recipe_id: int) -> list[QuerySet, dict[int, int]]:
    ingredients: QuerySet = (
        Ingredient.objects.prefetch_related(
            'recipe_ingredient'
        ).filter(
            recipe_ingredient__recipe_id=recipe_id
        )
    )

    ingredients_amounts: list[tuple[int, int]] = (
        RecipeIngredient.objects.filter(
            ingredient_id__in=ingredients.values_list('id', flat=True),
            recipe_id=recipe_id
        ).values_list('ingredient_id', 'amount')
    )

    amounts: dict[int, int] = {}
    for ingredient_id, amount in ingredients_amounts:
        amounts[ingredient_id] = amount

    return ingredients, amounts


def get_available_ids(model: Model) -> list[int]:
    return model.objects.all().values_list('id', flat=True)


def add_ingredients_to_recipe(
        edit: bool,
        recipe: Recipe,
        ingredients_amounts: list[dict[str, int]]) -> None:
    if edit:
        RecipeIngredient.objects.filter(recipe_id=recipe.id).delete()

    RecipeIngredient.objects.bulk_create(
        [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ing['id'],
                amount=ing['amount']) for ing in ingredients_amounts
        ]
    )


def add_tags_to_recipe(edit: bool,
                       recipe: Recipe,
                       tags_ids: list[int]) -> None:
    if edit:
        RecipeTag.objects.filter(recipe_id=recipe.id).delete()

    RecipeTag.objects.bulk_create(
        [RecipeTag(recipe=recipe, tag_id=tag_id) for tag_id in tags_ids]
    )


def create_recipe(author_id: int,
                  ingredients: list[dict[str, int]],
                  tags_ids: list[int],
                  **kwargs) -> Recipe:
    recipe_instance = Recipe.objects.create(
        author_id=author_id,
        **kwargs
    )

    add_ingredients_to_recipe(False, recipe_instance, ingredients)
    add_tags_to_recipe(False, recipe_instance, tags_ids)

    return recipe_instance


def get_user_recipes(user_id: int) -> QuerySet:
    return Recipe.objects.filter(author_id=user_id)


def get_user_fav_or_shopping_recipes_ids(
        user: User, is_shopping_cart: bool = False) -> list[int]:
    if is_shopping_cart:
        return user.shopping_cart.all().values_list('recipe_id', flat=True)
    return user.favorite_recipe.all().values_list('recipe_id', flat=True)


def get_recipes_ids_with_same_tag(tags: list[str]) -> list[int]:
    return RecipeTag.objects.filter(
        tag_id__in=(
            Tag.objects.filter(slug__in=tags).values_list('id', flat=True)
        )
    ).values_list('recipe_id', flat=True)


def get_subs_recipes(user: User) -> dict[int, QuerySet]:
    subs_recipes = {}
    for sub_id in get_subs_ids(user.id):
        subs_recipes[sub_id] = get_user_recipes(sub_id)

    return subs_recipes


def get_user_shopping_cart(user: User) -> list[tuple[str, int, str]]:
    return (
        RecipeIngredient.objects.select_related(
            'ingredient'
        ).filter(
            recipe_id__in=get_user_fav_or_shopping_recipes_ids(user, True)
        ).select_related(
            'ingredient__measurement_unit'
        ).values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit__name'
        )
    )


def get_tag_names() -> list[tuple[str, None]]:
    return [(tag.slug, None) for tag in Tag.objects.all()]


def get_favorited_count(recipe_id: int) -> int:
    return get_object_or_404(
        Recipe, id=recipe_id
    ).favorite_recipe.all().count()
