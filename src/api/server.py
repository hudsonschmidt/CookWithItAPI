from fastapi import FastAPI
from src.api import (
    ingredients,
    recipes,
    meals,
    user
)
from starlette.middleware.cors import CORSMiddleware

description = """
Cook With It is an API that allows users to track food and recepies. 
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

    {
        "name": "user",
        "description": "Creates a User",
    },
]

app = FastAPI(
    title="Cook With It",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
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
app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "Shop is open for business!"}
