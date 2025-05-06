from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/meals",
    tags=["meals"],
    dependencies=[Depends(auth.get_api_key)],
)


class Meal(BaseModel):
    meal_type: str
    date: str

class MealResponse(BaseModel):
    meal_id: int


@router.post("/", response_model=MealResponse)
def create_meal(meal: Meal):
    with db.engine.begin() as connection:
        meal_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO meal (meal_type, date)
                VALUES (:meal_type, :date);
                """
            ),
            {"meal_type": meal.meal_type, "date": meal.date},
        ).scalar_one()

        return MealResponse(meal_id=meal_id)
