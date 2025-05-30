from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Text, Date, MetaData
from sqlalchemy.dialects.postgresql import insert
from faker import Faker
import random
from datetime import datetime
import config
from sqlalchemy import create_engine, text

connection_url = config.get_settings().POSTGRES_URI
engine = create_engine(connection_url, pool_pre_ping=True)


NUTRIENTS = [
    {'id': 1008, 'name': 'Energy', 'unit': 'KCAL', 'min': 40, 'max': 600},
    {'id': 1003, 'name': 'Protein', 'unit': 'G', 'min': 0, 'max': 40},
    {'id': 1005, 'name': 'Carbohydrates', 'unit': 'G', 'min': 0, 'max': 100},
    {'id': 1004, 'name': 'Total lipid (fat)', 'unit': 'G', 'min': 0, 'max': 40},
]

MEASURE_UNITS = [
    'package', 'can', 'egg', 'piece', 'bunch', 'bag', 'slice', 'cup', 'tbsp', 'tsp'
]

FOOD_CATEGORY_ID = 1
DATA_TYPE = 'foundation_food'
BATCH_SIZE = 5000

def random_id(existing):
    while True:
        new_id = random.randint(10**5, 2*10**9)
        if new_id not in existing:
            existing.add(new_id)
            return new_id

def main():
    fake = Faker()
    metadata = MetaData()

    with engine.connect() as conn:
        db, user = conn.execute(text("SELECT current_database(), current_user")).fetchone()
        print("Connected to:", db, "as", user)

    # Define tables with minimal columns needed for insert
    measure_unit = Table('measure_unit', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String))

    ingredients = Table('ingredients', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('data_type', String),
                        Column('description', Text),
                        Column('food_category_id', Integer),
                        Column('publication_date', Date))

    food_portion = Table('food_portion', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('seq_num', Float),
                         Column('amount', Float),
                         Column('measure_unit_id', Integer),
                         Column('portion_description', Text),
                         Column('modifier', Text),
                         Column('gram_weight', Float),
                         Column('data_points', Float),
                         Column('footnote', Float),
                         Column('min_year_acquired', Float))

    ingredient_nutrient = Table('ingredient_nutrient', metadata,
                                Column('ingredient_id', Integer),
                                Column('nutrient_id', Integer),
                                Column('amount', Float))

    N = int(input("How many ingredients do you want to create? "))
    now_date = datetime.now().date()

    used_ids = set()
    used_measure_unit_ids = {}

    # Prepare measure units insert data
    measure_unit_rows = []
    for name in MEASURE_UNITS:
        mu_id = random_id(used_ids)
        used_measure_unit_ids[name] = mu_id
        measure_unit_rows.append({'id': mu_id, 'name': name})

    with engine.connect() as conn:
        # Insert measure units with ON CONFLICT DO NOTHING
        stmt = insert(measure_unit).values(measure_unit_rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
        conn.execute(stmt)
        print(f"Inserted {len(measure_unit_rows)} measure units (skipping conflicts).")

        ingredient_rows = []
        food_portion_rows = []
        ingredient_nutrient_rows = []

        for i in range(N):
            ingredient_id = random_id(used_ids)
            desc = fake.unique.sentence(nb_words=3).upper().replace('.', '').replace(',', '')
            mu_name = random.choice(MEASURE_UNITS)
            mu_id = used_measure_unit_ids[mu_name]
            gram_weight = round(random.uniform(30, 500), 1)
            portion_desc = None
            modifier = None
            portion_amount = 1
            min_year_acquired = random.choice(range(2015, 2025))
            pub_date = now_date

            ingredient_rows.append({
                'id': ingredient_id,
                'data_type': DATA_TYPE,
                'description': desc,
                'food_category_id': FOOD_CATEGORY_ID,
                'publication_date': pub_date
            })

            food_portion_rows.append({
                'id': ingredient_id,
                'seq_num': 1,
                'amount': portion_amount,
                'measure_unit_id': mu_id,
                'portion_description': portion_desc,
                'modifier': modifier,
                'gram_weight': gram_weight,
                'data_points': None,
                'footnote': None,
                'min_year_acquired': min_year_acquired
            })

            for nut in NUTRIENTS:
                amount = round(random.uniform(nut['min'], nut['max']), 2)
                ingredient_nutrient_rows.append({
                    'ingredient_id': ingredient_id,
                    'nutrient_id': nut['id'],
                    'amount': amount
                })

            if (i+1) % 10000 == 0:
                print(f"{i+1} ingredients prepared...")

        print("Inserting ingredients...")
        for i in range(0, len(ingredient_rows), BATCH_SIZE):
            batch = ingredient_rows[i:i+BATCH_SIZE]
            stmt = insert(ingredients).values(batch)
            conn.execute(stmt)

        print("Inserting food portions...")
        for i in range(0, len(food_portion_rows), BATCH_SIZE):
            batch = food_portion_rows[i:i+BATCH_SIZE]
            stmt = insert(food_portion).values(batch)
            conn.execute(stmt)

        print("Inserting ingredient nutrients...")
        for i in range(0, len(ingredient_nutrient_rows), BATCH_SIZE):
            batch = ingredient_nutrient_rows[i:i+BATCH_SIZE]
            stmt = insert(ingredient_nutrient).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=['ingredient_id', 'nutrient_id'])
            conn.execute(stmt)

        conn.commit()
    print(f"Inserted {N} ingredients, {N} portions, {4*N} nutrients.")

if __name__ == '__main__':
    main()
