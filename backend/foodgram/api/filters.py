from django_filters.rest_framework import (FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)
from rest_framework import filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтрация по тегам списка рецептов."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
        )

    is_favorited = NumberFilter(
       method='get_is_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'is_in_shopping_cart', 'is_favorited', 'tags', 'author',
        )

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart__user=user)
        return queryset


class IngredientFilter(filters.SearchFilter):
    """Фильтрация ингредиентов по имени."""

    search_param = 'name'
