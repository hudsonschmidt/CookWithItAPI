from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)


class Ingredient(BaseModel):
    ingredient_id: str
    name: str

class SearchResponse(BaseModel):
    results: List[Ingredient]

@router.get("/search/", response_model=SearchResponse)
def search_ingredients():
    with db.engine.begin() as connection:
        foods = connection.execute(
            sqlalchemy.text(
                """
                SELECT DISTINCT ON (ingredients.description) 
                ingredients.description, 
                (SELECT fdc_id 
                    FROM ingredients 
                    WHERE ingredients.description = ingredients.description 
                    ORDER BY publication_date DESC 
                    LIMIT 1) AS fdc_id,
                fp.amount,
                mu.name AS measure_unit_name
                FROM ingredients AS ingredients
                JOIN food_portion AS fp ON ingredients.fdc_id = fp.fdc_id
                JOIN measure_unit AS mu ON fp.measure_unit_id = mu.id
                WHERE ingredients.description LIKE '%Steak%'
                ORDER BY ingredients.description, ingredients.publication_date DESC
                LIMIT 10;
                """
            )
        ).fetchall()

        print(foods)

        food_list: List[Ingredient] = []

        for food in foods:
            food_list.append(Ingredient(ingredient_id=1, name="food"))

        return food_list


    
print(search_ingredients())
    