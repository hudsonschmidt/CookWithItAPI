# Peer Review Response

Thanks for the feedback guys! It was great to have another set of eyes on this code, we missed quite a few things.

Below are the feedback and our response to it.

## Code reviews

1. Please Please Please comment your code  
   Comments added in ambiguous parts, mainly on long sql queries to describe what they're doing.

2. Use alembic versions  
   We agree with the above suggestion for this project going forward, however, as it stands we are working from the schema.

3. Update the current alembic version to not have gold and global inventory  
   Assuming we were using alembic we would do this.

4. What is the difference between ingredient and ingredient amount. I feel like these can be merged into one class  
   Ingredient is a listing of all ingredients, while ingredient amount is the specific amount of an ingredient in a recipe.

5. What is UserIngredient for? It has the same fields as Ingredient and ingredient amount  
   UserIngredient would be used for a not yet implemented feature of suggestion meals based off the ingredients a user has.

6. in inventory.py there are a lot of references to user\_id but I can't find anything describing what that is or who it's attached to  
   There is no file named inventory.py.

7. in remove ingredient you can just do "amount":  -ingredient.amount instead of "amount": -1 \* ingredient.amount  
   That's a great suggestion not sure what the -1 * was doing there.

8. Meal and MealCreateResponse both having an id where meal's id is just called id but MealCreateResponse is called meal\_id is going to get confusing. Fix this with better names or combine them  
   Changed all to meal_id.

9. Change description on Get Macros call  
   Good catch docstring updated.

10. Consider changing "Total lipid (fat)" to just "fat"  
    Keeping as Total lipid (fat) as is as it is the total of many different types of fats.

11. move class SearchResponse(BaseModel): results: List\[Meal] to the top of the file  
    Moved class upward.

12. add a description to history  
    Added docstring.

13. What is the difference between IngredientAmount and IngredientInfo  
    Amount is simply the amount, and info contains more information we do not necessarily need for recipes.

14. in search recipe id consider defining a path type for type security  
    We'll let the user handle that one. A invalid input won't cause an issue except on their end.

15. change the name and email in server.py  
    Removed contact as it's a group project.

---

1. The endpoint for DELETE ingredients/{user\_id}/remove-ingredients/ is titled "add\_ingredient\_by\_id" is poorly named and should be something like "remove\_ingredient\_by\_id".  
   Fix naming of function to remove_ingredient.

2. Deleting ingredients currently adds their total, just with a negative sign. This breaks idempotency and can cause confusion.  
   Assumedly this could be fixed with a ledger, although idempotency is not needed in this scenario as the user will not be performing concurrent actions on their ingredients.

3. GET user ingredients and DELETE user ingredients have no response model.  
   No need for a response model, DELETE typically returns no content.

4. Doing recipe\[0] in GET/search/{recipe\_id} assumes recipe isn't an empty list and will cause a 500 error if it is. Instead, a 404 could be manually raised with detailed information.  
   A recipe must have ingredients at time of creation, so this is an error we should not run into.

5. The BaseModel "IngredientAmount" is defined both in ingredients.py and in recipes.py, each with different data, making it confusing. They should either include the same data or be separately named.  
   Not to nitpick but one is named IngredientAmount and the other IngredientAmounts, although I can see how this could be confusing.

6. The date for the MEAL model should be a timestamp, not a string.  
   Strings make it easier for users to input.

7. Remove print("RECID", recipe\_id).  
   Good catch, was used for debugging.

8. The SearchResponse class is defined multiple times but refer to different types of lists.  
   Different SearchResponses for different files, although I renamed them for clarity.

9. Include input validation, especially to avoid adding negative integers to tables.  
   Added non-negative constraints for values that should not be such as quantities.

10. get\_marcos should be get\_macros.  
    Get marcos that's funny, renamed.

11. The packages Field, Enum, and HTTPException are imported but never used in several files.  
    Removed unused imports.

12. The Recipe class is defined differently between routers. They should either include the same data or be separately named.  
    Keeping the class as is, as they mean different things depending on context.

13. Remove empty files init.py and user-ingredients.py  
    Init can stay, user-ingredients will also stay pending further implementation.

---

## Schema/API comments.

1. Use alembic versions for your schema  
   Yes that would have been the appropriate thing to do.

2. What is food category id and why is it needed. I don't think you need it  
   Information leftover from downloaded database, keeping it as assuming you had the whole database downloaded it would be useful.

3. What is the purpose of having the publication date?  
   To know when an ingredient is published/updated.

4. consider renaming food portion's id to something more readable  
   Renamed simply to id.

5. in food portion table why are all these columns needed? I think it's overcomplicating everything.  
   Artifacts of downloaded database which used in the context of the downloaded db are useful.

6. Write an API that can remove an ingredient from a recipe  
   That's a great suggestion, api added

7. create an API that can edit an ingredient's fields  
   Ingredients are meant to be immutable.

8. Create an API that can edit the instructions in a recipe.  
   If the user is changing instructions they should probably make a new recipe.

9. for Log Meal - /meals (POST) it might get confusing what a "portion" is for something like eggs like is 1 egg a portion or for sugar or salt for example.  
   I agree, however, those are the official USDA portions, and are standardized.

10. 3.2 get meal macros change the API spec to reflect the correct meal id. it requests 424 but returns meal 412.  
    Good catch, updated docs.

11. For ingredient macros consider including fiber  
    That is a good addition, however, for now we are focusing on the big three for this projects implementation.

12. for ingredient search search by name instead of ingredients\_term  
    Either search_term or name work in this scenario.

---

1. Every table should have a clearly defined primary key  
   Added primary keys to tables where it made sense to.

2. NOT NULL should be enforced on appropriate fields, like nutrient\_id or recipe\_id  
   Implemented above change.

3. recipe\_amounts should refer to recipe\_id as foreign key  
   Correct, added to schema.

4. Use INTEGER instead of float4 for values like data\_points and nutrient\_number  
   Not sure why its a float4 but keeping it as that is how the database we downloaded is set up.

5. Store dates as DATE or TIMESTAMP, not text  
   Changed text to date obj.

6. Rename min and max to something like min\_value to avoid postgress confusion  
   Changed to ensure we don't use keywords.

7. Add checks to make sure inputed data makes sense eg. amount >= 0  
   Added >= constraints where fitting.

8. Add UNIQUE constraints where fitting, like measure\_unit.name and nutrient.name  
   ID should handle uniqueness where necessary.

9. Some tables are singular while others are plural (meal vs ingredients). Choosing one would be cleaner  
   Adjusted them to plural as there are many of them.

10. Some primary keys are just "id" while others, like ingredients, are "fdc\_id." It's cleaner to just have it as "id" for all  
    I agree, fdc_id are artifacts of the downloaded database, changed to uniform id. 

11. Table headers don't need to be in quotations ("name" in several tables)  
    In quotes to prevent them from being keywords.

12. footnote is defined as a float in the food\_portions table but as text in the ingredient\_nutrient table  
    Fixed data type.

13. The user\_ingredients table never references a user, making it unable to refer to individual accounts.  
    That is correct, there is no user implemented yet so leaving as is.

14. None of the tables include created\_at, complicating debugging and data history because records can't be tracked  
    That is a good suggestion, some sort of event stream would be cool, although for now added created_at as a column on fitting rows.
