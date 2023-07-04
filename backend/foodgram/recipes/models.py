from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингедиентов."""

    name = models.CharField(max_length=250,
                            verbose_name='Ингердиент')
    measurement_unit = models.CharField(max_length=250,
                                        verbose_name='Единицы измерения')

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=250,
                            verbose_name='Тег')
    slug = models.SlugField(max_length=50)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(max_length=250,
                            verbose_name='Рецепт')
    text = models.TextField(blank=True,
                            verbose_name='Описание рецепта')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         related_name='recipes',
                                         verbose_name='Ингредиент',
                                         through='RecipeIngredient')
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        default=1,
        validators=[
            MinValueValidator(1)
        ]
                                       )
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  verbose_name='Теги')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецепт - ингредиент."""

    recipe = models.ForeignKey(Recipe, related_name='ingredients_in_recipe',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='recipes_for_ingredient',
                                   on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)])


class Favorite(models.Model):
    """Любимые рецепты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]


class UserShoppingCart(models.Model):
    """Корзина покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        default=1

    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]
