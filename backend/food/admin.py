from django.contrib import admin

from food.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    fields = (
        'name',
        'color',
        'slug',
    )
