from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Tag, UserShoppingCart)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели рецептов."""

    list_display = ('name', 'author', 'show_favorite_count')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author__username', 'tags__name')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientsInline,)

    def show_favorite_count(self, obj):
        """Общее число добавлений этого рецепта в избранное."""
        return obj.favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели ингредиентов."""

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка для модели ингредиентов в рецепте."""

    list_display = ('recipe', 'ingredient', 'amount')


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
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(UserShoppingCart, UserShoppingCartAdmin)
