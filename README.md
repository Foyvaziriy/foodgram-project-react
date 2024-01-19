# Foodgram
### Описание
 **Foodgram** - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
 ![image](https://github.com/itsme-emichka/foodgram-project-react/assets/108690873/fab1a492-943d-49bf-8fbd-254bb8c67ecc)
### Стек технологий
- React
- Django
- REST API
- Nginx
- Gunicorn
- PostgreSQL
- Docker
### Автор
**Имя:** Эмилар Локтев  
**Почта:** emilar-l@yandex.ru  
**Telegram** @itsme_emichka  
### Как запустить проект
1. Скачать файл `docker-compose-production.yml`
2. В той же директории создать файл `.env` со следующими переменными:
	- SECRET_KEY
	- DEBUG
	- POSTGRES_DB
	- POSTGRES_USER
	- POSTGRES_PASSWORD
	- DB_HOST
	- DB_PORT
	- ALLOWED_HOSTS
    - CSRF_TRUSTED_ORIGINS
3. Находясь в этой директории прописать команду:

   `docker compose -f docker-compose.production.yml up -d`

### Примеры запросов к API

>Полная спецификация API доступна по адресу `http://your_domain/api`  
>Для тестирования API можете использовать postman-collection  

**GET** `api/recipes/`  
**Response:**  
```
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "tags": [
                {
                    "id": 1,
                    "name": "Завтрак",
                    "color": "#f00000",
                    "slug": "breakfast"
                }
            ],
            "author": {
                "email": "test@yandex.ru",
                "id": 2,
                "username": "test",
                "first_name": "Test",
                "last_name": "Test",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 14,
                    "name": "айвовое пюре",
                    "measurement_unit": "г",
                    "amount": 13
                },
                {
                    "id": 1220,
                    "name": "патока крахмальная",
                    "measurement_unit": "г",
                    "amount": 12
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "name": "Test",
            "image": "http://127.0.0.1:8000/media/recipes/images/temp_8CiUUPl.png",
            "text": "testtest",
            "cooking_time": 40
        },
        {
            "id": 4,
            "tags": [
                {
                    "id": 2,
                    "name": "Обед",
                    "color": "#f135002",
                    "slug": "lunch"
                }
            ],
            "author": {
                "email": "emichka@yandex.ru",
                "id": 1,
                "username": "emichka",
                "first_name": "Emichka",
                "last_name": "Emichka",
                "is_subscribed": false
            },
            "ingredients": [
                {
                    "id": 120,
                    "name": "бекон",
                    "measurement_unit": "по вкусу",
                    "amount": 12
                },
                {
                    "id": 154,
                    "name": "букет гарни",
                    "measurement_unit": "пучок",
                    "amount": 13
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "name": "test_test",
            "image": "http://127.0.0.1:8000/media/recipes/images/temp_xYJViZ5.png",
            "text": "testtesttest",
            "cooking_time": 21
        }
    ]
}
```
---
**GET** `api/users/`  
**Response:**
```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "email": "biba@yandex.ru",
            "id": 1,
            "username": "biba",
            "first_name": "Biba",
            "last_name": "Bibov",
            "is_subscribed": false
        },
        {
            "email": "boba@yandex.ru",
            "id": 2,
            "username": "boba",
            "first_name": "Boba",
            "last_name": "Bobov",
            "is_subscribed": true
        },
    ]
}
```
