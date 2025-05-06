from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/food",
    tags=["food"],
    dependencies=[Depends(auth.get_api_key)],
)


class FoodIngredient(BaseModel):
    ingredient_id: int
    amount: int


class Food(BaseModel):
    meal_type: str
    ingredients: List[FoodIngredient]


@router.get("/search/")
def create_food(foods: List[Food]):
    with db.engine.begin() as connection:
        foods = connection.execute(
            sqlalchemy.text(
                """
                SELECT DISTINCT ON (ingredients.description)
                ingredients.fdc_id,
                ingredients.description,
                mu.name AS measure_unit
                FROM ingredients
                JOIN food_portion AS fp ON ingredients.fdc_id = fp.fdc_id
                JOIN measure_unit AS mu ON fp.measure_unit_id = mu.id
                WHERE ingredients.description ILIKE :search_term
                ORDER BY ingredients.description, ingredients.publication_date DESC
                LIMIT 10;
                """
            ),
            {"search_term": f"%{search_term}%"},
        ).fetchall()

        print(foods)

        food_list: List[Ingredient] = []
        for food in foods:
            food_list.append(
                Ingredient(
                    ingredient_id=food.fdc_id,
                    name=food.description,
                    measure_unit=food.measure_unit,
                )
            )

        return SearchResponse(results=food_list)
