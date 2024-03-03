from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedNewSeller
from src.models.books import Book
from src.models.seller import Seller
from sqlalchemy.orm import selectinload




seller_router = APIRouter(tags=["seller"], prefix="/seller")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце в БД. Возвращает созданного продавца.
@seller_router.post("/", response_model=ReturnedNewSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
):  # прописываем модель валидирующую входные данные и сессию как зависимость.
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=str(hash(seller.password)),
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая всех продавцов
@seller_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


# Ручка для получения продавца по его ИД
@seller_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    # res_seller = await session.get(Seller, seller_id)
    res_seller = await session.execute(select(Seller).where(Seller.id == seller_id).order_by(Seller.id)
                                            .options(selectinload(Seller.books)))
    seller = res_seller.scalars().first()
    if seller is None :
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return seller

# Ручка для удаления продавца
@seller_router.delete("/{seller_id}")
async def delete_book(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_seller:
        await session.execute(Book.__table__.delete().where(Book.seller_id == seller_id))
        await session.delete(deleted_seller)
        

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


# Ручка для обновления данных о продавце
@seller_router.put("/{seller_id}")
async def update_seller(seller_id: int, new_data: ReturnedNewSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name=new_data.first_name
        updated_seller.last_name=new_data.last_name
        updated_seller.email=new_data.email
 
        await session.flush()
        result = ReturnedNewSeller(first_name=updated_seller.first_name, last_name=updated_seller.last_name, email=updated_seller.email, id=updated_seller.id)
        return result

    return Response(status_code=status.HTTP_404_NOT_FOUND)
