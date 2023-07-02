from rest_framework import filters
from django_filters.rest_framework import FilterSet, ModelMultipleChoiceFilter

from recipes.models import Tag


class RecipeFilter(FilterSet):
    """Фильтрация по тегам списка рецептовб в т.ч
    на странице пользователя и в списке избранного."""

    tags = ModelMultipleChoiceFilter(
        name='tags__slug',
        to_field_name='slug',
        lookup_type='in',
        queryset=Tag.objects.all()
)


#     is_favorited = filters.BooleanFilter(method='filter_is_favorited')
#     is_in_shopping_cart = filters.BooleanFilter(
#         method='filter_is_in_shopping_cart')

#     class Meta:
#         model = Recipe
#         fields = ('tags', 'author',)

#     def filter_is_favorited(self, queryset, name, value):
#         user = self.request.user
#         if value and not user.is_anonymous:
#             return queryset.filter(favorites__user=user)
#         return queryset

#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         user = self.request.user
#         if value and not user.is_anonymous:
#             return queryset.filter(shopping_cart__user=user)
#         return queryset


# class RecipeFilter(filters.FilterSet):
#     """Кастомный фильтр для представления рецептов."""

#     is_favorited = filters.NumberFilter(
#         field_name='lover__user', method='filter_users_lists'
#     )
#     is_in_shopping_cart = filters.NumberFilter(
#         field_name='buyer__user', method='filter_users_lists'
#     )
#     tags = filters.ModelMultipleChoiceFilter(
#         field_name='tags__slug',
#         queryset=Tag.objects.all(),
#         to_field_name='slug'
#     )

#     class Meta:
#         model = Recipe
#         fields = (
#             'author',
#         )


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'
