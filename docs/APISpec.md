# API Specification for Meal and Recipe Tracker

## 1. User Ingredients

### 1.1. Add Ingredient - `/user-ingredients` (POST)

Adds an ingredient to the user's personal ingredient list. Post ingredient_id must match an ingredient in food ingredients table.

**Request**:
```json
{
  "ingredient_id": "ingredient_id",
  "amount": 0
}
```

**Response**: `204 No Content`

### 1.2. Get Ingredients - `/user-ingredients` (GET)

Retrieves all user-added ingredients.

**Response**:
```json
{
  "ingredients": [
    {"uiid": "123", "name": "Eggs", "quantity": 10, "Measurement": "Item"},
    ...
  ]
}
```

### 1.3. Delete Ingredient - `/user-ingredients/{uiid}` (DELETE)

Removes an ingredient from the user's list.

**Request**:
```json
{
  "ingredient_id": "ingredient_id"
}
```

**Response**: `204 No Content`

## 2. Recipes

### 2.1. Create Recipe - `/recipes` (POST)

Creates a new recipe. Amount is multiple of default serving size from ingredients.

**Request**:
```json
{
  "name": "Pancakes",
  "ingredients": [
    {"ingredient_id": "10", "amount": "2"},
    {"ingredient_id": "12", "amount": "5"}
  ],
  "instructions": "1. Beat the eggs 2. Combine butter and eggs"
}
```

**Response**:
```json
{
  "recipe_id": "12",
  "message": "Recipe created successfully."
}
```

### 2.2. Get Recipe - `/recipes/{recipe_id}` (GET)

Retrieves details of a specific recipe including name, ingredients, and instructions.

**Request**: Path Parameter: `recipe_id`

**Response**:
```json
{
  "recipe_id": "456",
  "name": "Pancakes",
  "ingredients": [ ... ],
  "instructions": "..."
}
```

### 2.3 Get Posible Recipes - `/recipes/possible_recipe_search/{user_id}` (GET)

Retrieves at most 10 recipes that the user can make based on current inventory of ingredients 

**Request**: Path Parameter: `user_id`

**Response**:
```json
{
  "recipes": [
    {
      "recipe_id": "456",
      "name": "Pancakes",
      "ingredients": [ ... ],
      "steps ": "..."
    }
    {
      "recipe_id": "789",
      "name": "Waffles",
      "ingredients": [ ... ],
      "steps": "..."
    }
  ]
}
```

### 2.4 Get Recipes that meet Macro Goals - `/recipes/macro-goal-recipes`

Return every recipe that satisfies the requested macro goals with a 1x, 2x or 3x batch size

**Request**: Path Parameter: `user_id`
```json
{
  "protein": 100,
  "energy": 200,
  "carbs": 300,
  "fats": 400
}
```

**Response**:
[
  "pancakes": 3,
  "waffles": 2, 
  "eggs": 1 
]

## 3. Meals (Macro Tracker)

### 3.1. Log Meal - `/meals` (POST)

Logs a meal with specific foods and a mealtime.

**Request**:
Amount is the multiplier of standard portion.
```json
{
  "foods": [
    {"food_id": "152", "amount": "10"}
  ],
  "mealtime": "breakfast"
}
```

**Response**:
```json
{
  "meal_id": "424",
  "message": "Meal logged successfully."
}
```

### 3.2. Get Meal Macros - `/meals/{meal_id}/macros` (GET)

Retrieves macro details for a specific meal.

**Request**:
```json
{
  "meal_id": "424"
}
```

**Response**:
```json
{
  "meal_id": "424",
  "macros": {
    "protein": "20g",
    "carbs": "30g",
    "fats": "10g"
  }
}
```

### 3.3. Get Meal History - `/meals/history/` (GET)

Retrieves meal history for a given date range.

**Query Parameters**:
- `start_date`: (YYYY-MM-DD)
- `end_date`: (YYYY-MM-DD)

**Response**:
```json
{
  "history": [
    {"meal_id": "789", "date": "2024-04-20", "mealtime": "breakfast"},
    ...
  ]
}
```

## 4. Ingredients

### 4.1. Get Ingredient Macros - `/ingredients/{ingredient_id}/macros` (GET)

Retrieves macronutrient information for an ingredient.

**Request**:
```json
{
  "ingredient_id": "123"
}
```
**Response**:
```json
{
  "ingredient_id": "123",
  "name": "Eggs",
  "macros": {
    "protein": "6g",
    "carbs": "1g",
    "fats": "5g"
  }
}
```

### 4.2. Search Ingredients - `/ingredients/search` (GET)

Searches ingredients based on query.

**Query Parameters**:
- `ingredients_term`: Search query term

**Response**:
```json
{
  "results": [
    {"ingredient_id": "123", "name": "Eggs"},
    ...
  ]
}
```


## 5. Food

### 5.1 Create a New Food Item - `/food` (POST)

Creates a new food item composed of specified ingredients and their respective amounts.

**Request**:
```json
{
  "ingredients": {
    "4141": 5,   // Ingredient ID: Amount
    "1231": 1    // Ingredient ID: Amount
  }
}
```

**Response**:
```json
{
  "food_id": "123",
  "name": "Bacon and Eggs",
  "macros": {
    "protein": "12g",
    "carbs": "0g",
    "fats": "15g"
  }
}
```


# Example Flows


### Student Breakfast Macro Tracking Flow

**User Story**: As a college student juggling classes and the gym, I want to quickly log my breakfast and see its macros so I can stay within my daily goals.

**Steps**:

#### 1.1. Search for Ingredients - `/ingredients/search?ingredients_term=egg` (GET)

**Response**:
```json
{
  "results": [
    { "ingredient_id": "123", "name": "Eggs" }
  ]
}
```

#### 1.2. Add Eggs to Personal Pantry - `/user-ingredients` (POST)

**Request**:
```json
{
  "ingredient_id": "123",
  "amount": 10
}
```

**Response**:
`204 NO CONTENT`

#### 1.3. Create a Recipe (Eggs) - `/recipes` (POST)
```json
{
  "name": "Scrambled Eggs",
  "steps": "Crack open eggs, scramble",
  "ingredients": [
    {
      "ingredient_id": 123,
      "amount": 6
    }
  ]
}
```

**Response**:
```json
{
  recipe_id: 100
}
```

#### 1.5. Create a meal and associate with a recipe - `/meals/recipes/` (POST)

**Request**:
```json
{
  "mealtime": "breakfast",
  "recipes": [
    { "recipe_id": "123", "amount": "1" },
    { "recipe_id": "456", "amount": "1" }
  ]
}
```

**Response**:
```json
{
  meal_id: 525
}
```

#### 1.6. View Macros for the Meal - `/meals/macros` (GET)

**Request**:
```json
{
  "meal_id": 525
}

```


**Response**:
```json
{
  "macro_list": [
    {
      "macro_name": "Energy",
      "total_amount": 668
    },
    {
      "macro_name": "Protein",
      "total_amount": 32.4
    },
    {
      "macro_name": "Total lipid (fat)",
      "total_amount": 57.6
    }
  ]
}
```


### 2. Food Blogger Publishing Smoky Vegan Chili

**User Story**: As a food blogger, I want to publish a new chili recipe with complete nutrition facts so my readers can import it into their own trackers.

**Steps**:

#### 2.1. Search for Ingredient Information - `/ingredients/search?ingredients_term=black%20beans` (GET)

**Response**:
```json
{
  "results": [{ "ingredient_id": "811", "name": "Black Beans (canned)" }]
}
```

#### 2.2. Create the Chili Recipe - `/recipes` (POST)

**Request**:
```json
{
  "name": "Smoky Vegan Chili",
  "ingredients": [
    { "ingredient_id": "811", "amount": "1" },
    { "ingredient_id": "812", "amount": "1" },
    { "ingredient_id": "990", "amount": "1" }
  ],
  "instructions": "1. Sauté onions… 2. Add spices… 3. Simmer 30 min."
}
```

**Response**:
```json
{
  "recipe_id": "9907",
  "message": "Recipe created successfully."
}
```

#### 2.3. Retrieve Recipe for Sharing - `/recipes/9907` (GET)

**Response**:
```json
{
  "recipe_id": "9907",
  "name": "Smoky Vegan Chili",
  "ingredients": [
    { "ingredient_id": "811", "amount": "1" },
    { "ingredient_id": "812", "amount": "1" },
    { "ingredient_id": "990", "amount": "1" }
  ],
  "instructions": "1. Sauté onions… 2. Add spices… 3. Simmer 30 min."
}
```


### 3. Personal Trainer Weekly Client Review

**User Story**: As a personal trainer, I want to review my client’s last week of meals and macro totals so I can adjust their nutrition plan.

**Steps**:

#### 3.1. Client Logs Post-Workout Lunch - `/meals` (POST)

**Request**:
```json
{
  "foods": [
    { "food_id": "123", "amount": "2" },
    { "food_id": "456", "amount": "1" }
  ],
  "mealtime": "lunch"
}
```

**Response**:
```json
{
  "meal_id": "912",
  "message": "Meal logged successfully."
}
```

#### 3.2. Trainer Pulls Seven-Day Meal History - `/meals/history?start_date=2025-04-14&end_date=2025-04-21` (GET)

**Response**:
```json
{
  "history": [
    { "meal_id": "801", "date": "2025-04-14", "mealtime": "breakfast" },
    { "meal_id": "912", "date": "2025-04-18", "mealtime": "lunch" }
  ]
}
```

#### 3.3. Inspect Macros for Each Meal - `/meals/912/macros` (GET)

**Response**:
```json
{
  "meal_id": "912",
  "macros": { "protein": "28g", "carbs": "45g", "fats": "18g" }
}
```
