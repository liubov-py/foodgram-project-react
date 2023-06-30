import base64
import re
import webcolors
from rest_framework import serializers
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer

from recipes.models import Ingredient, Favorite, Tag, Recipe, RecipeIngredient
from users.models import User, Following


def name_is_valid(value):
    return re.compile(r'^[\w.@+-]+\z').match(value) is not None


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

    class Meta:
        model = User
        fields = ('email', 'username',
                  'first_name', 'last_name', 'password',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.following.filter(following=obj).exists()

    def validate_username(self, value):
        if not name_is_valid(value):
            raise serializers.ValidationError('Содержит недопустимые символы.')
        return value
    
    def create(self, validated_data):
        user = User.objects.create(email= validated_data['email'], username=validated_data['username'],
                  first_name=validated_data['first_name'], last_name=validated_data['last_name'],)
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
        fields = ('id', 'name', 'measurement')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer для рецептов."""

    author = UserSerializer()
    tag = TagSerializer(many=True, read_only=True)
    ingredient = IngredientSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'cooking_time', 'name', 'text', 'image',
                  'tag', 'ingredient', 'is_favorite', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.get_user()
        return user.is_authenticated and user.favorites.filter(
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        return user.is_authenticated and user.shopping_cart.filter(
            recipe=obj).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer для промежуточной таблицы Рецепт-Ингердиент."""

    model = RecipeIngredient
    fields = ('name', 'count', 'measurement')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания рецептов."""
    author = UserSerializer()
    tag = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all()))  # Список на выбор
    ingredient = RecipeIngredientSerializer(many=True)  # Список на выбор
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('author', 'cooking_time', 'name', 'text', 'image',
                  'tag', 'ingredient',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное."""

    user = UserSerializer()

    class Meta:
        model = Favorite
        fields = ('user', 'favorite')

        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'favorite'),
                message='Вы уже добавляли этот рецепт в избранное.'
            )
        ]


class FollowingSrializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""

    user = UserSerializer()
    following = UserSerializer()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Following
        fields = ('user', 'following', 'recipes_count')
        validators = [
            UniqueTogetherValidator(
                queryset=Following.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого автора',
            )
        ]

    def validate_following(self, data):
        if data == self.context.get('request').user:
            raise serializers.ValidationError('Подписаться на себя невозможно')
        return data

    def get_recipes_count(self, obj):
        """Количетво объектов внутри поля recipes"""
        return obj.recipes.count()
