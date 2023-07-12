# адрес сервера (IP или доменное имя)
51.250.27.116
https://foodgramliu.ddns.net/

# логин и пароль администратора
admin
admin

# Foodgram, «Продуктовый помощник»

## О проекте

Это онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Заполнение базы данных данными (ингредиенты) из csv-файла
python backend/foodgram/manage.py import_csv

## Примеры
https://foodgramliu.ddns.net/api/docs/redoc.html


# GET
https://foodgramliu.ddns.net/api/users/

{
"count": 123,
"next": "http://foodgram.example.org/api/users/?page=4",
"previous": "http://foodgram.example.org/api/users/?page=2",
"results": [
{
"email": "user@example.com",
"id": 0,
"username": "string",
"first_name": "Вася",
"last_name": "Пупкин",
"is_subscribed": false
}
]
}



# POST
https://foodgramliu.ddns.net/api/users/

{
"email": "vpupkin@yandex.ru",
"username": "vasya.pupkin",
"first_name": "Вася",
"last_name": "Пупкин",
"password": "Qwerty123"
}
