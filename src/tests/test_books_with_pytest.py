import pytest
from fastapi import status
from sqlalchemy import select, delete

from src.models import books, seller

# Тест на ручку создания продавца
@pytest.mark.asyncio(scope="function")
async def test_create_seller(async_client):
    data = {"first_name": "Vasya", "last_name": "Pupkin", "email": "vp@ya.ru", "password": "123"}
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "first_name": "Vasya",
        "last_name": "Pupkin",
        "email": "vp@ya.ru",
        "id": 1
    }

# Тест на ручку получения списка продавцов
@pytest.mark.asyncio(scope="function")
async def test_get_sellers(db_session, async_client):
    # Очистка таблицы
    await db_session.execute(delete(seller.Seller))
    await db_session.flush()
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))
    seller_2 = seller.Seller(first_name="I_Still_Hate", last_name="Testing", email="isht@ya.ru", password=str(hash("0qww294e")))

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "I_Hate", "last_name": "Testing", "email": "iht@ya.ru", "id": seller_1.id},
            {"first_name": "I_Still_Hate", "last_name": "Testing", "email": "isht@ya.ru", "id": seller_2.id},
        ]
    }

    
# Тест на ручку получения продавца без книг
@pytest.mark.asyncio(scope="function")
async def test_get_single_seller_no_book(db_session, async_client):
    # Очистка таблицы
    await db_session.execute(delete(seller.Seller))
    await db_session.flush()
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))
    seller_2 = seller.Seller(first_name="I_Still_Hate", last_name="Testing", email="isht@ya.ru", password=str(hash("0qww294e")))

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller_1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "I_Hate",
        "last_name": "Testing",
        "email": "iht@ya.ru",
        "id": seller_1.id,
        "books": []
    }

# Тест на ручку обновления продавца 
@pytest.mark.asyncio(scope="function")
async def test_update_seller(db_session, async_client):
    # Очистка таблицы
    await db_session.execute(delete(seller.Seller))
    await db_session.flush()
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))

    db_session.add(seller_1)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller_1.id}",
        json={"first_name": "Kill", "last_name": "Me", "email": "js_forever@ya.ru", "id": seller_1.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(seller.Seller, seller_1.id)

    assert res.first_name == "Kill"
    assert res.last_name == "Me"
    assert res.email == "js_forever@ya.ru"
    assert res.id == seller_1.id

# Тест на ручку создающую книгу
@pytest.mark.asyncio(scope="function")
async def test_create_book(db_session, async_client):
    # Очистка таблицы
    await db_session.execute(delete(seller.Seller))
    await db_session.flush()
    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))

    db_session.add(seller_1)
    await db_session.flush()
    data = {"title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007, "seller_id": seller_1.id}
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "title": "Wrong Code",
        "author": "Robert Martin",
        "year": 2007,
        "id": 1,
        "count_pages": 104,
        "seller_id": seller_1.id
    }

# Тест на ручку получения списка книг
@pytest.mark.asyncio(scope="function")
async def test_get_books(db_session, async_client):
    # Очистка таблиц
    await db_session.execute(delete(books.Book))
    await db_session.execute(delete(seller.Seller))
    await db_session.flush()
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))

    db_session.add(seller_1)
    await db_session.flush()
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_1.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_1.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {"title": "Eugeny Onegin", "author": "Pushkin", "year": 2001, "id": book.id, "count_pages": 104, "seller_id": seller_1.id},
            {"title": "Mziri", "author": "Lermontov", "year": 1997, "id": book_2.id, "count_pages": 104, "seller_id": seller_1.id},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio(scope="function")
async def test_get_single_book(db_session, async_client):
    # Очистка таблиц
    await db_session.execute(delete(books.Book))
    await db_session.execute(delete(seller.Seller))
    await db_session.flush()

    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))

    db_session.add(seller_1)
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_1.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_1.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "count_pages": 104,
        "id": book.id,
        "seller_id": seller_1.id
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio(scope="function")
async def test_delete_book(db_session, async_client):
    # Очистка таблиц
    await db_session.execute(delete(books.Book))
    await db_session.execute(delete(seller.Seller))
    await db_session.flush()
    
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))

    db_session.add(seller_1)
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_1.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()

    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio(scope="function")
async def test_update_book(db_session, async_client):
     # Очистка таблиц
    await db_session.execute(delete(seller.Seller))
    await db_session.execute(delete(books.Book))
    await db_session.flush()

    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))

    db_session.add(seller_1)
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_1.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={"title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007, "id": book.id, "seller_id": seller_1.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books.Book, book.id)

    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.id == book.id
    assert res.seller_id == seller_1.id

#тест на ручку удаления продавца
@pytest.mark.asyncio(scope="function")
async def test_delete_seller(db_session, async_client):
    # Очистка таблиц
    await db_session.execute(delete(seller.Seller))
    await db_session.execute(delete(books.Book))
    await db_session.flush()

    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))

    db_session.add(seller_1)
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_1.id)

    db_session.add(book)
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 1

    response = await async_client.delete(f"/api/v1/seller/{seller_1.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(seller.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0
    all_books_after = await db_session.execute(select(books.Book))
    res = all_books_after.scalars().all()
    assert len(res) == 0

#тест на ручку получения одного продавца с созданными книгами
@pytest.mark.asyncio(scope="function")
async def test_get_single_seller_with_book(db_session, async_client):
    # Очистка таблиц
    await db_session.execute(delete(seller.Seller))
    await db_session.execute(delete(books.Book))
    await db_session.flush()

    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    seller_1 = seller.Seller(first_name="I_Hate", last_name="Testing", email="iht@ya.ru", password=str(hash("password")))
    seller_2 = seller.Seller(first_name="I_Still_Hate", last_name="Testing", email="isht@ya.ru", password=str(hash("0qww294e")))

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_1.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_1.id)

    db_session.add_all([book, book_2])
    await db_session.flush()
    
    response = await async_client.get(f"/api/v1/seller/{seller_1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "I_Hate",
        "last_name": "Testing",
        "email": "iht@ya.ru",
        "id": seller_1.id,
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "id": book.id,
                "count_pages": 104
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "id": book_2.id,
                "count_pages": 104
            }
        ]
    }

    
