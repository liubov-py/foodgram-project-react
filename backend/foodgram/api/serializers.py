import base64
import re

import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Tag, UserShoppingCart)
from users.models import Following, User


def name_is_valid(value):
    return re.compile(r'^[\w.@+-]+\Z').match(value) is not None


class Base64ImageField(serializers.ImageField):
    """Для картинок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    """Для цветов в тегах."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class CustomUserSerializer(UserSerializer):
    """Serializer для /users."""

    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and Following.objects.filter(
            user=user, following=obj).exists())

    def validate_username(self, value):
        if not name_is_valid(value):
            raise serializers.ValidationError('Содержит недопустимые символы.')
        return value

    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'],
                                   username=validated_data['username'],
                                   first_name=validated_data['first_name'],
                                   last_name=validated_data['last_name'],)
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    """Serializer для тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredienReadSerializer(serializers.ModelSerializer):
    """Serializer для ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer для рецептов."""

    author = CustomUserSerializer()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredienReadSerializer(many=True, read_only=True,
                                                source='ingredients_in_recipe')
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'cooking_time', 'name', 'text', 'image',
                  'tags', 'ingredients', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        return (user.is_authenticated and Favorite.objects.filter(
            recipe=obj,
            user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        return (user.is_authenticated and UserShoppingCart.objects.filter(
            recipe=obj,
            user=user).exists())


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer для промежуточной таблицы Рецепт-Ингердиент."""

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания рецептов."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'cooking_time', 'name', 'text', 'image',
                  'tags', 'ingredients',)

    def to_representation(self, value):
        return RecipeSerializer(value, context=self.context).data

    def ingredient_create(self, recipe, ingredients):
        recipe_list = []
        for ingredient in ingredients:
            recipe_list.append(
                RecipeIngredient(recipe=recipe,
                                 ingredient_id=ingredient['id'],
                                 amount=ingredient['amount']))
        RecipeIngredient.objects.bulk_create(
            recipe_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredient_create(self, recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().update(recipe, validated_data)
        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        self.ingredient_create(self, recipe, ingredients)
        recipe.save()
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    user = CustomUserSerializer()

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавляли этот рецепт в избранное.'
            )
        ]


class FollowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта в подписках."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowingSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

        validators = [
            UniqueTogetherValidator(
                queryset=Following.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого автора',
            )
        ]

    def validate_following(self, data):
        if data == self.context.get('request').user:
            raise serializers.ValidationError(
                'Подписаться на себя невозможно')
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and Following.objects.filter(
            following=obj, user=user).exists())

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = obj.recipes.all()[:(int(limit_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return FollowRecipeSerializer(recipes, many=True,
                                      context=context).data
