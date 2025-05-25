from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from typing import List
from src import database as db

router = APIRouter(
    prefix="/meals",
    tags=["meals"],
    dependencies=[Depends(auth.get_api_key)],
)


class MealCreateResponse(BaseModel):
    meal_id: int


class Recipe(BaseModel):
    recipe_id: int
    amount: int


class MealCreateRequest(BaseModel):
    mealtime: str
    recipes: List[Recipe]


class Meal(BaseModel):
    meal_id: int
    meal_type: str
    date: str


class MacroAmount(BaseModel):
    macro_name: str
    total_amount: float


class MacroResponse(BaseModel):
    macro_list: List[MacroAmount]


class MealSearchResponse(BaseModel):
    results: List[Meal]


@router.post("/", response_model=MealCreateResponse)
def create_meal(meal: MealCreateRequest):
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
            {"mealtime": meal.mealtime},
        ).scalar()

        # Add all recipes that were created with the meal
        for recipe in meal.recipes:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO meal_recipes (meal_id, recipe_id)
                    VALUES (:meal_id, :recipe_id)
                    """
                ),
                {"meal_id": meal_id, "recipe_id": recipe.recipe_id},
            )

    return MealCreateResponse(meal_id=meal_id)


@router.get("/macros", response_model=MacroResponse)
def get_macros(meal_id: int):
    """
    Returns all the macronutrients for a given meal.
    """
    with db.engine.begin() as connection:
        # Returns the combined total macronutrients for a given meal
        rows = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                nutrient.name AS nutrient_name,
                SUM(ingredient_nutrient.amount) AS total_amount
                FROM 
                    meal
                JOIN 
                    meal_recipes ON meal_recipes.meal_id = meal.id
                JOIN 
                    recipe ON recipe.id = meal_recipes.recipe_id
                JOIN 
                    recipe_amounts ON recipe_amounts.recipe_id = recipe.id
                JOIN 
                    ingredient_nutrient ON ingredient_nutrient.fdc_id = recipe_amounts.ingredient_id
                JOIN 
                    nutrient ON nutrient.id = ingredient_nutrient.nutrient_id
                WHERE 
                    meal.id = :meal_id
                    AND nutrient.name IN ('Protein', 'Energy', 'Carbohydrates', 'Total lipid (fat)')
                    AND nutrient.unit_name IN ('G', 'KCAL')
                GROUP BY 
                    nutrient.name
                ORDER BY 
                    nutrient.name;
                """
            ),
            {"meal_id": meal_id},
        )

        # Returns list of macros
        nutrients = [
            MacroAmount(
                macro_name=row.nutrient_name,
                total_amount=float(row.total_amount),
            )
            for row in rows
        ]

    return MacroResponse(macro_list=nutrients)

@router.get("/history/", response_model=MealSearchResponse)
def meal_history(start: str, end: str):
    """
    Queries all meals logged from date range given start to end.
    """
    with db.engine.begin() as connection:
        # Query meal by date
        meals = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, mealtime, date
                FROM meal

                WHERE date BETWEEN :start AND :end
                ORDER BY date DESC
                """
            ),
            {"start": f"%{start}%", "end": f"%{end}%"},
        ).fetchall()

        # Return meals within date range
        meal_list: List[Meal] = []
        for meal in meals:
            meal_list.append(
                Meal(
                    id=meal.id,
                    meal_type=meal.mealtime,
                    date=meal.date,
                )
            )

        return MealSearchResponse(results=meal_list)
