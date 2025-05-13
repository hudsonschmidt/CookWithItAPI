from fastapi import FastAPI
from src.api import (
    ingredients,
    recipes,
    meals
)
from starlette.middleware.cors import CORSMiddleware

description = """
Central Coast Cauldrons is the premier ecommerce site for all your alchemical desires.
"""
tags_metadata = [
    {
        "name": "ingredients",
        "description": "See ingredients to make recipes out of.",
    },
    {
        "name": "recipes",
        "description": "Recipe with steps and ingredeients.",
    },
    {
        "name": "meals",
        "description": "A meal houses foods per a given day and meal type.",
    },
]

app = FastAPI(
    title="Cook With It",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Lucas Pierce",
        "email": "lupierce@calpoly.edu",
    },
    openapi_tags=tags_metadata,
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(meals.router)


@app.get("/")
async def root():
    return {"message": "Shop is open for business!"}
