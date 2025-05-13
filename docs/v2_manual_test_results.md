# Food Blogger Publishing Smoky Vegan Chili
User Story: As a food blogger, I want to publish a new chili recipe with complete nutrition facts so my readers can import it into their own trackers.

1. Search for Ingredients
``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/ingredients/search/?search_term=beans' \
  -H 'accept: application/json' \
  ```
Response
``` json
{
  "results": [
    {
      "ingredient_id": 739546,
      "name": "BLACK BEANS, CANNED",
      "measure_unit": "can"
    }
  ]
}
```

``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/ingredients/search/?search_term=onion' \
  -H 'accept: application/json' \
  ```
Response
``` json
{
  "results": [
    {
      "ingredient_id": 739562,
      "name": "ONION, WHOLE",
      "measure_unit": "piece"
    }
  ]
}
```

``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/ingredients/search/?search_term=beef' \
  -H 'accept: application/json' \
  ```
Response
``` json
{
  "results": [
    {
      "ingredient_id": 385662,
      "name": "GROUND BEEF",
      "measure_unit": "package"
    }
  ]
}
```

2. Create the Chili Recipe
``` json
curl -X 'POST' \
  'https://cook-with-it.onrender.com/recipes/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Smoky Vegan Chili",
  "steps": "1. Sauté onions… 2. Add spices… 3. Simmer 30 min",
  "ingredients": [
    { "ingredient_id": "739546", "amount": "1" },
    { "ingredient_id": "739562", "amount": "2" },
    { "ingredient_id": "385662", "amount": "1" }
  ]
}'
  ```
Response
``` json
{
  "recipe_id": 8
}
```

3.  Retrieve Recipe for Sharing
``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/recipes/search/17' \
  -H 'accept: application/json' \
  ```
Response
``` json
{
  "name": "Smoky Vegan Chili",
  "steps": "1. Sauté onions… 2. Add spices… 3. Simmer 30 min",
  "ingredients": [
    { "ingredient_id": "739546", "amount": "1" },
    { "ingredient_id": "739562", "amount": "2" },
    { "ingredient_id": "385662", "amount": "1" }
  ]
}
```

# Personal Trainer Weekly Client Review
User Story: As a personal trainer, I want to review my client’s last week of meals and macro totals so I can adjust their nutrition plan.

1. Client Logs Post-Workout Lunch
``` json
curl -X 'POST' \
  'https://cook-with-it.onrender.com/meals/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "mealtime": "lunch",
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
  "meal_id": 19
}
```

2. Trainer Pulls Meal History
``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/meals/history/?start=2025-05-12&end=2025-05-13' \
  -H 'accept: application/json' \
  ```
Response
``` json
{
  "results": [
    {
      "id": 19,
      "meal_type": "lunch",
      "date": "2025-05-12"
    }
  ]
}
```

3. Inspect Macros for Meal
``` json
curl -X 'GET' \
  'https://cook-with-it.onrender.com/meals/macros?meal_id=17' \
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
