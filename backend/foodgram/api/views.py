from django.shortcuts import get_object_or_404
from django.shortcuts import render
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from djoser.views import UserViewSet

from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from recipes.models import Recipe, Tag, Ingredient, User, RecipeIngredient
from .serializers import (IngredientSerializer, FavoriteSerializer,
                          FollowingSrializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          TagSerializer, CustomUserSerializer)
from .filters import IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    #Фильтрация по тегам
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('tag',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        serializer.save(author=self.request.user, recipe=recipe)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(methods=('POST', 'DELETE'), detail=True)
    def favorite(self, request):
        pass


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """ViewSet для тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """ViewSet для ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    permission_classes = (IsAdminOrReadOnly,)


class Shopping_CartViewSet():
    """ViewSet для списка покупок."""

    # permission_classes = (,) - разрешение автор или админ

# 1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в покупки».

# def shopping_cart(request, pk):
#     favorite = get_object_or_404(Recipe, pk=pk)
#     user = request.user
#     return Response(user=user, favorite=favorite,
#                     status=status.HTTP_201_CREATED)
# # 2. Пользователь переходит на страницу Список покупок, там доступны все добавленные в список
# # рецепты. 
#    shopping_cart_list = Recipe.objects.filter(shopping_cart__user=request.user)
# # Пользователь нажимает кнопку Скачать список и получает файл с суммированным
# # перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке
# покупок».
# 3. При необходимости пользователь может удалить рецепт из списка покупок.
def download_shopping_cart(self, request):
    pass
# Список покупок скачивается в формате .txt (или, по желанию, можно сделать выгрузку PDF).
# При скачивании списка покупок ингредиенты в результирующем списке не должны дублироваться;
# если в двух рецептах есть сахар (в одном рецепте 5 г, в другом — 10 г), то в списке должен быть один
# пункт: Сахар — 15 г.
# В результате список покупок может выглядеть так:
# Фарш (баранина и говядина) (г) — 600


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ViewSet для избранного."""

    serializer_class = FavoriteSerializer
    # permission_classes = (,)   - разрешение автор или админ

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return user.favorites.all() #Оба поля там фейворит. Переделать?

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowingViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """ViewSet для подписки на автора."""

    serializer_class = FollowingSrializer
    # permission_classes = (,)  - разрешение автор или админ

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomUserViewSet(UserViewSet):
    """ViewSet для /users."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
