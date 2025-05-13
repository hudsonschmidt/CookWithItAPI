# Student Breakfast Macro Tracking Flow
User Story: As a college student juggling classes and the gym, I want to quickly log my breakfast and see its macros so I can stay within my daily goals.

1. Search for Ingredients
``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/ingredients/search/?search_term=eggs' \
  -H 'accept: application/json' \
  ```
Response
``` json
{
  "results": [
    {
      "ingredient_id": 748967,
      "name": "EGGS, GRADE A, LARGE, egg whole",
      "measure_unit": "egg"
    }
  ]
}
```

2. Add Eggs to Personal Pantry
``` json
curl -X 'POST' \
  'https://cook-with-it.onrender.com/ingredients/user-ingredients/' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "ingredient_id": 748967,
  "amount": 10
}'
  ```
Response
``` json
204 NO CONTENT
```

3. Create a Recipe (Eggs)
``` json
curl -X 'POST' \
  'https://cook-with-it.onrender.com/recipes/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Scrambled Eggs",
  "steps": "Crack open eggs, scramble",
  "ingredients": [
    {
      "ingredient_id": 748967,
      "amount": 6
    }
  ]
}'
  ```
Response
``` json
{
  "recipe_id": 6
}
```

4. Create a meal and associate with a recipe
``` json
curl -X 'POST' \
  'https://cook-with-it.onrender.com/meals/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "mealtime": "breakfast",
  "recipes": [
    {
      "recipe_id": 6,
      "amount": 1
    }
  ]
}'
  ```
Response
``` json
{
  "meal_id": 18
}
```

5. View Macros for the Meal
``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/meals/macros?meal_id=18' \
  -H 'accept: application/json' \
  ```
Response
``` json
{
  "macro_list": [
    {
      "macro_name": "Energy",
      "total_amount": 334
    },
    {
      "macro_name": "Protein",
      "total_amount": 16.2
    },
    {
      "macro_name": "Total lipid (fat)",
      "total_amount": 28.8
    }
  ]
}
```

