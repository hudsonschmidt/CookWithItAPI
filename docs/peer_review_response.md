Peer review response md


Code reviews.

1. Please Please Please comment your code
	Comments added in ambiguous parts, mainly on long sql queries to describe what they're doing.
2. Use alembic versions
3. Update the current alembic version to not have gold and global inventory
4. What is the difference between ingredient and ingredient amount. I feel like these can be merged into one class
5. What is UserIngredient for? It has the same fields as Ingredient and ingredient amount
6. in inventory.py there are a lot of references to user\_id but I can't find anything describing what that is or who it's attached to
7. in remove ingredient you can just do "amount":  -ingredient.amount instead of "amount": -1 \* ingredient.amount
8. Meal and MealCreateResponse both having an id where meal's id is just called id but MealCreateResponse is called meal\_id is going to get confusing. Fix this with better names or combine them
9. Change description on Get Macros call
10. Consider changing "Total lipid (fat)" to just "fat"
11. move class SearchResponse(BaseModel): results: List\[Meal] to the top of the file
12. add a description to history
13. What is the difference between IngredientAmount and IngredientInfo
14. in search recipe id consider defining a path type for type security
15. change the name and email in server.py


1. The endpoint for DELETE ingredients/{user\_id}/remove-ingredients/ is titled "add\_ingredient\_by\_id" is poorly named and should be something like "remove\_ingredient\_by\_id".
2. Deleting ingredients currently adds their total, just with a negative sign. This breaks idempotency and can cause confusion.
3. GET user ingredients and DELETE user ingredients have no response model.
4. Doing recipe\[0] in GET/search/{recipe\_id} assumes recipe isn't an empty list and will cause a 500 error if it is. Instead, a 404 could be manually raised with detailed information.
5. The BaseModel "IngredientAmount" is defined both in ingredients.py and in recipes.py, each with different data, making it confusing. They should either include the same data or be separately named.
6. The date for the MEAL model should be a timestamp, not a string.
7. Remove print("RECID", recipe\_id).
8. The SearchResponse class is defined multiple times but refer to different types of lists.
9. Include input validation, especially to avoid adding negative integers to tables.
10. get\_marcos should be get\_macros.
11. The packages Field, Enum, and HTTPException are imported but never used in several files.
12. The Recipe class is defined differently between routers. They should either include the same data or be separately named.
13. Remove empty files init.py and user-ingredients.py










Schema/API comments.


1. Use alembic versions for your schema
2. What is food category id and why is it needed. I don't think you need it
3. What is the purpose of having the publication date?
4. consider renaming food portion's id to something more readable
5. in food portion table why are all these columns needed? I think it's overcomplicating everything.
6. Write an API that can remove an ingredient from a recipe
7. create an API that can edit an ingredient's fields
8. Create an API that can edit the instructions in a recipe.
9. for Log Meal - /meals (POST) it might get confusing what a "portion" is for something like eggs like is 1 egg a portion or for sugar or salt for example.
10. 3.2 get meal macros change the API spec to reflect the correct meal id. it requests 424 but returns meal 412.
11. For ingredient macros consider including fiber
12. for ingredient search search by name instead of ingredients\_term



1. Every table should have a clearly defined primary key
2. NOT NULL should be enforced on appropriate fields, like nutrient\_id or recipe\_id
3. recipe\_amounts should refer to recipe\_id as foreign key
4. Use INTEGER instead of float4 for values like data\_points and nutrient\_number
5. Store dates as DATE or TIMESTAMP, not text
6. Rename min and max to something like min\_value to avoid postgress confusion
7. Add checks to make sure inputed data makes sense eg. amount >= 0
8. Add UNIQUE constraints where fitting, like measure\_unit.name and nutrient.name
9. Some tables are singular while others are plural (meal vs ingredients). Choosing one would be cleaner
10. Some primary keys are just "id" while others, like ingredients, are "fdc\_id." It's cleaner to just have it as "id" for all
11. Table headers don't need to be in quotations ("name" in several tables)
12. footnote is defined as a float in the food\_portions table but as text in the ingredient\_nutrient table
13. The user\_ingredients table never references a user, making it unable to refer to individual accounts
14. None of the tables include created\_at, complicating debugging and data history because records can't be tracked

