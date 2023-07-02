from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAdminUser, IsAuthenticated, AllowAny,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions

from djoser.views import UserViewSet

from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from recipes.models import (Recipe, Tag, Ingredient,
                            User, Favorite, UserShoppingCart)
from users.models import Following
from .serializers import (IngredientSerializer, FavoriteSerializer,
                          FollowingSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          TagSerializer, CustomUserSerializer)
from .filters import IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    serializer_class = RecipeCreateSerializer
    # Написать отдельный
    pagination_class = LimitOffsetPagination
    # Фильтрация по тегам
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('tag',)

    def get_serializer_class(self):
        # if self.request.method in ('POST', 'PATCH'):
        #     return RecipeCreateSerializer
        # return RecipeSerializer
        # if self.action in ('list', 'retrieve'):
        #     return RecipeSerializer
        # return RecipeCreateSerializer
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        serializer.save(author=self.request.user, recipe=recipe)

    def method_post(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors':
                             'Рецепт уже добавлен в список избранного!'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def method_delete(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=[IsAuthenticated | IsAdminUser])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.method_post(Favorite, request.user, pk)
        else:
            return self.method_delete(Favorite, request.user, pk)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=[IsAuthenticated | IsAdminUser])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(UserShoppingCart, request.user, pk)
        else:
            return self.delete_from(UserShoppingCart, request.user, pk)


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


class CustomUserViewSet(UserViewSet):
    """ViewSet для /users."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['POST', 'DELETE'],
            detail=True, )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Following.objects.filter(
            user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы уже подписаны на этого автора'},
                                # Такие же проверки есть на уровне
                                # сериалайзера. Надо ли тут?
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error':
                                 'Невозможно подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowingSerializer(author, context={'request':
                                                              request})
            Following.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription.delete()

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        list_of_following = User.objects.filter(following__user=user)
        page = self.paginate_queryset(list_of_following)
        serializer = FollowingSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
