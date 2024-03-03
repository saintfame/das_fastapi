from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from .books import ReturnedBookSeller
import re

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedNewSeller"]


# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str

    @field_validator("email")  # Валидатор, проверяет что Email условно-корректный
    @staticmethod
    def validate_email(val: str):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", val):
            raise PydanticCustomError("Validation error", "incorrect email!")
        return val

# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str

# Класс, валидирующий исходящие данные нового продавца. Он уже содержит id
class ReturnedNewSeller(BaseSeller):
    id: int

# Класс, валидирующий исходящие данные ранее созданного продавца. Он уже содержит id и список книг
class ReturnedSeller(BaseSeller):
    id: int
    books: list[ReturnedBookSeller]

# Класс для возврата массива объектов "продавец". Не содержит списка книг каждого продавца, т.к. такого условия не было в контракте 
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedNewSeller]
