from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Tag, UserShoppingCart)
from users.models import Following, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, FollowingSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    serializer_class = RecipeCreateSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def method_post(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors':
                             'Уже добавлен в список'},
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
        return self.method_delete(Favorite, request.user, pk)

    @action(methods=('POST', 'DELETE'), detail=True,
            permission_classes=[IsAuthenticated | IsAdminUser])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.method_post(UserShoppingCart, request.user, pk)
        return self.method_delete(UserShoppingCart, request.user, pk)

    @action(methods=('GET',), detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        recipeingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
            ).values('ingredient__name').annotate(amount=Sum('amount'))
        with open('Shopping.txt', 'w') as file:
            for ing in recipeingredients:
                file.write(ing['ingredient__name'] + ' ' + str(ing['amount']))
        return FileResponse(open('Shopping.txt', 'rb'), as_attachment=True)


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
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['POST', 'DELETE'],
            detail=True, )
    def subscribe(self, request, id):
        user = request.user
        following = get_object_or_404(User, id=id)
        subscription = Following.objects.filter(
            user=user, following=following)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': 'Вы уже подписаны на этого автора'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == following:
                return Response({'error':
                                 'Невозможно подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowingSerializer(following, context={
                'request': request})
            Following.objects.create(user=user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        list_of_following = User.objects.filter(following__user=user)
        page = self.paginate_queryset(list_of_following)
        serializer = FollowingSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)
