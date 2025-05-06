from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"],
    dependencies=[Depends(auth.get_api_key)],
)


class Ingredient(BaseModel):
    ingredient_id: int
    name: str
    measure_unit: str


class UserIngredient(BaseModel):
    ingredient_id: int
    name: str


class SearchResponse(BaseModel):
    results: List[Ingredient]


@router.get("/search/", response_model=SearchResponse)
def search_ingredients(search_term: str):
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


@router.post("/user-ingredients/", status_code=status.HTTP_204_NO_CONTENT)
def add_ingredient_by_id(ingredient: UserIngredient):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_ingredients (fdc_id, amount, description, measure_unit_name)
                SELECT 
                    ingredients.fdc_id,
                    :amount AS amount,
                    ingredients.description,
                    mu.name AS measure_unit_name
                FROM ingredients
                JOIN food_portion AS fp ON ingredients.fdc_id = fp.fdc_id
                JOIN measure_unit AS mu ON fp.measure_unit_id = mu.id
                WHERE ingredients.fdc_id = :ingredient_id
                ORDER BY fp.amount DESC
                LIMIT 1;
                """
            ),
            {"ingredient_id": ingredient.ingredient_id, "amount": ingredient.amount},
        )
