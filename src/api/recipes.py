from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    dependencies=[Depends(auth.get_api_key)],
)


class IngredientInput(BaseModel):
    ingredient_id: int
    amount: int


class Recipe(BaseModel):
    name: str
    steps: str
    ingredients: List[IngredientInput]


class RecipeResponse(BaseModel):
    recipe_id: int


@router.post("/", response_model=RecipeResponse)
def create_recipe(recipe: Recipe):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                INSERT INTO recipe (name, steps)
                VALUES (:name, :steps)
                RETURNING id;
            """),
            {"name": recipe.name, "steps": recipe.steps},
        )
        recipe_id = result.scalar_one()

        print("RECID", recipe_id)

        value_list = ", ".join(
            f"({recipe_id}, {ingredient.amount}, {ingredient.ingredient_id})"
            for ingredient in recipe.ingredients
        )

        # Format string should be safe since we built it above
        connection.execute(
            sqlalchemy.text(
                f"""
                INSERT INTO recipe_amounts
                (recipe_id, amount, ingredient_id)
                VALUES {value_list};
                """
            ),
        )

    return RecipeResponse(recipe_id=recipe_id)
