from django.contrib import admin
from django.db.models import Avg

from recipes.models import Ingredient, Favorite, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели рецептов."""

    list_display = ('name', 'author', 'show_average')
    list_filter = ('name', 'author', 'tags')

    def show_average(self, obj):
        """Общее число добавлений этого рецепта в избранное."""
        return Favorite.objects.filter(favorite=obj).count


class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели ингредиентов."""

    list_display = ('name', 'measurement_unit',)


class TagAdmin(admin.ModelAdmin):
    """Админка для модели тегов."""

    list_display = ('name', 'slug', 'color')


class FavoriteAdmin(admin.ModelAdmin):
    """Админка для модели добавления в избранное рецептов."""

    list_display = ('user', 'favorite')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
