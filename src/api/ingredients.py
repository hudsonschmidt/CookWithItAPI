from fastapi import APIRouter, Depends, status, Path
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

class IngredientAmount(BaseModel):
    ingredient_id: int
    name: str
    measure_unit: str
    amount: int


class UserIngredient(BaseModel):
    ingredient_id: int
    amount: int


class SearchResponse(BaseModel):
    results: List[Ingredient]


class IngredientAmounts(BaseModel):
    results: List[IngredientAmount]


@router.get("/search/", response_model=SearchResponse)
def search_ingredients(search_term: str):
    with db.engine.begin() as connection:
        # Get all food items that a relevant to the search term
        foods = connection.execute(
            sqlalchemy.text(
                """
                SELECT DISTINCT ON (i.description) i.fdc_id, i.description, mu.name AS measure_unit
                FROM ingredients AS i

                JOIN food_portion AS fp 
                ON fp.fdc_id = i.fdc_id

                JOIN measure_unit AS mu 
                ON mu.id = fp.measure_unit_id

                WHERE i.description ILIKE '%' || :search_term || '%'
                ORDER BY i.description, i.publication_date DESC
                LIMIT 10;
                """
            ),
            {"search_term": f"%{search_term}%"},
        ).fetchall()

        # Create page of all returned ingredients
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


@router.post("/{user_id}/add-ingredients/", status_code=status.HTTP_204_NO_CONTENT)
def add_ingredient_by_id(ingredient: UserIngredient, user_id: int = Path(...)):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_ingredients (user_id, fdc_id, amount)
                VALUES(:user_id, :fdc_id, :amount)
                """
            ),
            {"user_id": user_id, "fdc_id": ingredient.ingredient_id, "amount": ingredient.amount},
        )


@router.get("/{user_id}/get-ingredients/")
def get_user_ingredients(user_id: int = Path(...)):
    with db.engine.begin() as connection:
        # Gets all the ingredients in the users pantry
        user_ingredients = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                    SUM(ui.amount) AS amount, 
                    i.fdc_id, 
                    i.description AS name, 
                    mu.name AS measure_unit
                FROM user_ingredients ui
                JOIN ingredients i ON ui.fdc_id = i.fdc_id
                JOIN food_portion fp ON fp.fdc_id = i.fdc_id
                JOIN measure_unit mu ON fp.measure_unit_id = mu.id
                WHERE ui.user_id = :user_id
                GROUP BY i.fdc_id, i.description, mu.name
                """
            ), {"user_id": user_id}
        ).fetchall()

        # Create listing of all ingredients
        ingredient_list: List[IngredientAmount] = []
        for ingredient in user_ingredients:
            ingredient_list.append(
                IngredientAmount(
                    ingredient_id=ingredient.fdc_id,
                    name=ingredient.name,
                    measure_unit=ingredient.measure_unit,
                    amount=ingredient.amount,
                )
            )

        return IngredientAmounts(results=ingredient_list)

@router.delete("/{user_id}/remove-ingredients/", status_code=status.HTTP_204_NO_CONTENT)
def remove_ingredient(ingredient: UserIngredient, user_id: int = Path(...)):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_ingredients (user_id, fdc_id, amount)
                VALUES(:user_id, :fdc_id, :amount)
                """
            ),
            {"user_id": user_id, "fdc_id": ingredient.ingredient_id, "amount": -1 * ingredient.amount},
        )
