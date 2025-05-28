from fastapi import APIRouter, Depends, Path, status, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List
from collections import defaultdict

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    dependencies=[Depends(auth.get_api_key)],
)


class IngredientAmount(BaseModel):
    ingredient_id: int
    amount: int


class IngredientInfo(BaseModel):
    ingredient_id: int
    name: str
    amount: int
    measure_unit: str


class Recipe(BaseModel):
    name: str
    steps: str
    ingredients_list: List[IngredientAmount]


class RecipeTotals(BaseModel):
    recipe_id: int
    name: str
    steps: str
    ingredients_list: List[IngredientInfo]


class RecipeResponse(BaseModel):
    recipe_id: int

class RemoveIngredientRequest(BaseModel):
    recipe_id: int
    ingredient_id: int


@router.get("/search/{recipe_id}", response_model=RecipeTotals)
def search_ingredients(recipe_id: int = Path(...)):
    with db.engine.begin() as connection:
        # Get ingredients from a given recipe
        recipe = connection.execute(
            sqlalchemy.text(
                """
                SELECT DISTINCT r.name AS rname, r.steps, i.id, i.description AS iname, ra.amount, mu.name AS measuring_unit
                FROM recipe AS r
                JOIN recipe_amounts AS ra ON r.id = ra.recipe_id 
                JOIN ingredients AS i ON ra.ingredient_id = i.id
                JOIN food_portion AS fp ON fp.id = i.id
                JOIN measure_unit AS mu ON mu.id = fp.measure_unit_id
                WHERE r.id = :recipe_id
                """
            ),{"recipe_id": recipe_id}
        ).fetchall()

        # Return list of ingredients
        ingredient_list: List[IngredientInfo] = []
        for ingredient in recipe:
            ingredient_list.append(
                IngredientInfo(
                    ingredient_id=ingredient.id,
                    name=ingredient.iname,
                    amount = ingredient.amount,
                    measure_unit=ingredient.measuring_unit,
                )
            )

        return RecipeTotals(recipe_id=recipe_id, name=recipe[0].rname, steps=recipe[0].steps, ingredients_list=ingredient_list)


@router.post("/add-recipe", response_model=RecipeResponse)
def create_recipe(recipe: Recipe):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO recipes (name, steps)
                VALUES (:name, :steps)
                RETURNING id;
                """
            ),{"name": recipe.name, "steps": recipe.steps},
        )
        recipe_id = result.scalar_one()

        # Insert all ingredients into the given recipe
        data = []
        for ingredient in recipe.ingredients_list:
            # Prepare parameters for use in sql statement
            data.append({
                "recipe_id": recipe_id,
                "amount": ingredient.amount,
                "ingredient_id": ingredient.ingredient_id,
            })

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO recipe_amounts (recipe_id, amount, ingredient_id)
                VALUES (:recipe_id, :amount, :ingredient_id);
                """
            ),data
        )

    return RecipeResponse(recipe_id=recipe_id)

@router.delete("/remove-ingredient", status_code=status.HTTP_204_NO_CONTENT,)
def remove_ingredient_from_recipe(request: RemoveIngredientRequest):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM recipe_amounts
                WHERE recipe_id = :recipe_id AND ingredient_id = :ingredient_id
                """
            ),
            {"recipe_id": request.recipe_id, "ingredient_id": request.ingredient_id}
        )
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Ingredient does not exist for recipe.",
            )
        
class MacroAmount(BaseModel):
    macro_name: str
    total_amount: float

class MacroResponse(BaseModel):
    macro_list: List[MacroAmount]

class MacroGoalRequest(BaseModel):
    protein: float
    energy: float
    carbs: float
    fats: float

# super duper complex endpoint am i right
@router.post( 
    "/macro-goal-recipes",
    response_model=dict[str, int],
    status_code=status.HTTP_200_OK,
)
def get_macro_goal_recipes(request: MacroGoalRequest):
    """
    Return every recipe that satisfies the requested macro goals with a
    1x, 2x or 3x batch size
    """
    # avoid division by zero
    if min(request.protein, request.energy, request.carbs, request.fats) <= 0:
        raise HTTPException(
            status_code=400,
            detail="All macro goals must be > 0.",
        )

    with db.engine.begin() as connection:
        # 1. aggregate macros for every recipe
        recipes = connection.execute(
            sqlalchemy.text(
                """
                WITH macro_per_recipe AS (
                    SELECT
                        r.id AS recipe_id,
                        r.name AS recipe_name,
                        r.steps AS steps,
                        -- macros per recipe, scaled by the ingredient weight
                        SUM(CASE WHEN n.name = 'Protein'THEN ra.amount * inut.amount / 100 ELSE 0 END) AS protein_g,
                        SUM(CASE WHEN n.name = 'Energy' THEN ra.amount * inut.amount / 100 ELSE 0 END) AS energy_kcal,
                        SUM(CASE WHEN n.name = 'Carbohydrate, by difference'THEN ra.amount * inut.amount / 100 ELSE 0 END) AS carbs_g,
                        SUM(CASE WHEN n.name = 'Total lipid (fat)'THEN ra.amount * inut.amount / 100 ELSE 0 END) AS fats_g
                    FROM recipe AS r
                    JOIN recipe_amounts AS ra ON ra.recipe_id = r.id
                    JOIN ingredient_nutrient AS inut ON inut.ingredient_id = ra.ingredient_id
                    JOIN nutrient AS n ON n.id = inut.nutrient_id
                    WHERE n.name IN (
                        'Protein',
                        'Energy',
                        'Carbohydrate, by difference',
                        'Total lipid (fat)'
                    )
                    GROUP BY r.id, r.name, r.steps
                )
                SELECT *
                FROM macro_per_recipe
                """
            )
        ).fetchall()

    # 2. determine which multiplier (1, 2, 3) – if any – meets the goals
    good_recipes: dict[str, int] = {}

    for row in recipes:
        # Skip recipes that have a zero for any macro (missing data)
        if 0 in (row.protein_g, row.energy_kcal, row.carbs_g, row.fats_g):
            continue

        # Largest ratio of goal/recipe => how much we need to scale
        try:
            ratio = max(
                request.protein / row.protein_g,
                request.energy  / row.energy_kcal,
                request.carbs   / row.carbs_g,
                request.fats    / row.fats_g,
            )
        except ZeroDivisionError:
            continue

        if ratio <= 1:
            multiplier = 1
        elif ratio <= 2:
            multiplier = 2
        elif ratio <= 3:
            multiplier = 3
        else:
            continue

        good_recipes[str(row.recipe_id)] = multiplier

    return good_recipes