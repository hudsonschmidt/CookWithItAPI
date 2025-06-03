import random
from faker import Faker

fake = Faker()
measure_units = ['tsp', 'tbsp', 'cup', 'oz', 'gram', 'kg', 'ml', 'l', 'can', 'slice']
ingredients = []

for i in range(1, 1000):
    row = (
        random.randint(100, 200),           # user_id
        random.randint(500, 600),           # ingredient_id
        random.randint(1, 10),              # amount
        fake.sentence(nb_words=3),          # description
        random.choice(measure_units)        # measure_unit_name
    )
    ingredients.append(row)

# Generate SQL
values_sql = ",\n".join([
    f"({user_id}, {ingredient_id}, {amount}, '{description.replace('\'', '\'\'')}', '{measure_unit_name}')"
    for user_id, ingredient_id, amount, description, measure_unit_name in ingredients
])

full_sql = f"""
INSERT INTO public.user_ingredients (user_id, ingredient_id, amount, description, measure_unit_name)
VALUES
{values_sql};
"""

print(full_sql)