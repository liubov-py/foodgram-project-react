from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator


User = get_user_model()


class Ingredient(models.Model):
    """Модель ингедиентов."""

    name = models.CharField(max_length=250,
                            verbose_name='Ингердиент')
    measurement = models.CharField(max_length=250,
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
    ingredient = models.ManyToManyField(Ingredient,
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
    tag = models.ManyToManyField(Tag,
                                 related_name="recipes",
                                 verbose_name='Теги')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецепт - ингредиент."""

    name = models.ForeignKey(Recipe, related_name='recipeing',
                             on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, related_name='recipeing',
                                   on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='Количество')


class Favorite(models.Model):
    """Любимые рецепты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'favorite'], name='unique_favorite'
            )
        ]


class UserShoppingCart(models.Model):
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoping_cart',
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'favorite'], name='unique_shopping_cart'
            )
        ]
