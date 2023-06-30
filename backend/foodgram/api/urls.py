from api import views
from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet, FavoriteViewSet,
                    FollowingViewSet)


router = routers.DefaultRouter()

router.register('recipes',
                RecipeViewSet,
                basename='')
# router.register(r'recipes/(?P<recipes_id>\d+)/shopping_cart',
#                 views.Shopping_cartViewSet,
#                 basename='') #обычную функцию
# router.register(r'recipes/(?P<recipes_id>\d+)/favorite',
#                 views.FavoriteViewSet,
#                 basename='')

router.register('ingredients', IngredientViewSet,
                basename='')

router.register('tags',
                views.TagViewSet,
                basename='')

# router.register(r'users/(?P<id>\d+)/subscribe',
#                 views.FollowingViewSet,
#                 basename='')

# router.register('users/subscriptions',
#                 views.FollowingViewSet,
#                 basename='')

router.register('users',
                views.CustomUserViewSet,
                basename='user')

urlpatterns = [
    path('users/me/',
         views.UserMeDetailUpdateAPIView.as_view(), name='userme'),
    path('', include(router.urls)),
    path('pdf', views.getpdf),
]