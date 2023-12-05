from django.contrib.auth import get_user_model
from django.db.models import Model, Subquery
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.http import Http404

from users.models import UserSubs
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
    return UserSubs.objects.get_or_create(user_id=user, sub_id=sub)


def unsubscribe(user_id: int, sub_id: int) -> QuerySet:
    user = get_object_or_404(User, id=user_id)
    sub = get_object_or_404(User, id=sub_id)
    try:
        get_object_or_404(UserSubs, user_id=user, sub_id=sub).delete()
    except Http404:
        raise NotSubscribedError


def get_subs_ids(user_id: int) -> list[tuple[int]]:
    return UserSubs.objects.filter(user_id=user_id).values_list('sub_id')


def get_subscriptions(user_id: int) -> QuerySet:
    subs = UserSubs.objects.filter(user_id=user_id).values('sub_id')
    return User.objects.filter(id__in=Subquery(subs))
