from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from enum import Enum
from typing import List, Optional
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class MealCreateResponse(BaseModel):
    meal_id: int

class Food(BaseModel):
    food_id: int
    amount: int

class Meal(BaseModel):
    meal_type: str
    date: str

@router.post("/", response_model=MealCreateResponse)
def create_meal(foods: List[Food], mealtime: str):
    """
    Creates a new meal with given foods and mealtime.
    """
    with db.engine.begin() as connection:
        meal_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO meal (mealtime, date)
                VALUES (:mealtime, now())
                RETURNING id
                """
            ),
            {"mealtime": mealtime},
        ).scalar()

        for food in foods:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO meal_foods (meal_id, food_id)
                    VALUES (:meal_id, :food_id)
                    """
                ),
                {"meal_id": meal_id, "food_id": food.food_id},
            )

    return MealCreateResponse(meal_id=meal_id)