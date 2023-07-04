from django.contrib import admin

from recipes.models import Favorite, Ingredient, Recipe, Tag, UserShoppingCart


class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели рецептов."""

    list_display = ('name', 'author', 'show_average')
    list_filter = ('name', 'author', 'tags')

    def show_average(self, obj):
        """Общее число добавлений этого рецепта в избранное."""
        return obj.favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели ингредиентов."""

    list_display = ('name', 'measurement_unit',)


class TagAdmin(admin.ModelAdmin):
    """Админка для модели тегов."""

    list_display = ('name', 'slug', 'color')


class FavoriteAdmin(admin.ModelAdmin):
    """Админка для модели добавления в избранное рецептов."""

    list_display = ('user', 'recipe')


class UserShoppingCartAdmin(admin.ModelAdmin):
    """Админка для модели добавления в избранное рецептов."""

    list_display = ('user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(UserShoppingCart, UserShoppingCartAdmin)
