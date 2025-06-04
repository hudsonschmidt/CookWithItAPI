from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from typing import List
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)


class UserId(BaseModel):
    user_id: int


@router.post("/create-user", response_model=UserId)
def create_user(first_name: str, last_name: str, email):
    with db.engine.begin() as connection:
        user_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (first_name, last_name, email, created_at)
                VALUES (:first_name, :last_name, :email, now())
                RETURNING id
                """
            ),
            {"first_name": first_name, "last_name": last_name, "email": email},
        ).scalar()

        return UserId(user_id = user_id)
