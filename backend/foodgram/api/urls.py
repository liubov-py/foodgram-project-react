from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = routers.DefaultRouter()

router.register('recipes',
                RecipeViewSet,
                basename='')
router.register('ingredients',
                IngredientViewSet,
                basename='')
router.register('tags',
                TagViewSet,
                basename='')
router.register('users',
                CustomUserViewSet,
                basename='user')
urlpatterns = [
    path('', include(router.urls)),
]
