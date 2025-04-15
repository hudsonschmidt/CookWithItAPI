## User Stories
1. As a student focused on nutrition, I want an endpoint that lets me filter recipes by specific protein and calorie thresholds so that I can quickly find meals that match my dietary goals.
2. As a busy home cook, I want to query recipes based on the ingredients I have on hand so that I can avoid unnecessary grocery trips and prepare a meal faster.
3. As a developer of a meal-planning application, I want to retrieve recipe data (name, directions, ingredients, servings, nutrition) via an API so that I can display relevant recipes on my front end.
4. As a user with dietary restrictions, I want to query recipes that exclude certain allergens (e.g., peanuts, shellfish) so that I can be assured of recipe safety and avoid potential health risks.
5. As a family meal planner, I want to filter recipes by how many people they serve so that I can easily find and choose meals that fit my family size.
6. As a user on a budget, I want to find recipes that meet lower-cost ingredient requirements (potentially from cost metadata or simpler ingredients) so that I can keep my grocery spending in check.
7. As a food blogger, I want to create (POST) new recipes in the database with images and step-by-step directions so that I can share my creations via an API that others can query.
8. As an API consumer, I want to search by keywords in the recipe name or directions so that I can discover relevant meals for a specific cuisine or cooking method.
9. As a health-conscious user, I want to filter recipes by total calories and macros (carbs, fats, proteins) so that I can tailor my meals to my fitness goals.
10 As a person who loves variety, I want to paginate recipe results when querying the API so that I don’t get overwhelmed by thousands of results at once.
11. As a culinary enthusiast, I want to retrieve advanced data (e.g., cooking techniques, difficulty levels) from the recipe API so that I can experiment with new and challenging dishes.
12. As a user who wants to share feedback, I want an endpoint for rating or commenting on recipes so that I can help others discover the most popular or best-reviewed meals.

## Exceptions
1. Invalid Query Parameters
- Scenario: A user calls /recipes?protein_lt=xyz (nonnumerical input) or /recipes?serves=-1 (nonsensical value).
- Handling: Return a 400 Bad Request with an error message indicating which parameter is invalid.
2. Recipe Not Found
- Scenario: A client requests GET /recipes/9999 for a non-existent recipe ID.
- Handling: Return a 404 Not Found with a message like “Recipe ID 9999 does not exist.”
3. No Matching Results
- Scenario: A user queries for /recipes?calories_lt=100&protein_gt=200, and no recipes match both constraints.
- Handling: Return a 200 OK with an empty list (or 404 Not Found based on your design) and a clear message (e.g., “No recipes found for these filters”).
4. Database Connection Issue
- Scenario: The database is unavailable or times out.
- Handling: Return a 503 Service Unavailable or 500 Internal Server Error with a message “Service temporarily unavailable. Please try again later.”
5. Duplicate Recipe Entry
- Scenario: A user tries to POST a recipe with an exact name and details that already exist in the database.
- Handling: Return a 409 Conflict with an error indicating the recipe already exists. Conflicts unlikely; however, we do not want exact duplicate data.
6. Missing Required Fields on Create
- Scenario: A client POSTs a recipe with no name or missing ingredients.
- Handling: Return a 400 Bad Request explaining which fields are missing.
7. Unauthorized Access
- Scenario: A client tries to POST, PUT, or DELETE a recipe without proper authentication (if your API requires it).
- Handling: Return a 401 Unauthorized.
8. Invalid Nutritional Values
- Scenario: A user tries to POST a recipe claiming 10,000 grams of protein per serving, which is outside normal bounds.
- Handling: Return a 400 Bad Request with a message indicating the nutritional values are not realistic or exceed the allowed range.
9. File Upload Error (If supporting recipe images/videos)
- Scenario: A user attempts to upload a huge image or an unsupported file format while creating or editing a recipe.
- Handling: Returns a 400 Bad Request or 415 Unsupported Media Type, indicating that the file is too large or the format is invalid.
10. Allergen Tagging Inconsistency
- Scenario: A client sets allergen data incorrectly (e.g., says “peanut-free” but includes peanuts in the ingredients).
- Handling: Return a 400 Bad Request with an error describing the inconsistency or automatically override with correct allergen labeling (depending on your design).
11. API Rate Limit Exceeded
- Scenario: A single client makes too many requests too quickly, much more than a human who wants recipes would do.
- Handling: Return a 429 Too Many Requests with instructions on when they can try again.
12. Unintended SQL Injection
- Scenario: A user attempts to insert SQL into our database.
- Handling: Sanitize inputs and return a 400 Bad Request if malicious content is detected.