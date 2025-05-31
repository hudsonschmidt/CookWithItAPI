CREATE TABLE public.food_portion (
        id serial NOT NULL PRIMARY KEY,
        seq_num float4 NULL CHECK (seq_num >= 0),
        amount float4 NULL CHECK (amount >= 0),
        measure_unit_id int4 NULL,
        portion_description text NULL,
        modifier text NULL,
        gram_weight float4 NULL CHECK (gram_weight >= 0),
        data_points float4 NULL CHECK (data_points >= 0),
        footnote float4 NULL,
        min_year_acquired float4 NULL CHECK (min_year_acquired >= 0)
);


CREATE TABLE public.ingredient_nutrient (
        id serial NOT NULL PRIMARY KEY,
        ingredient_id  int4  NOT NULL REFERENCES public.ingredients(id),
        nutrient_id    int4  NOT NULL REFERENCES public.nutrient(id),
        amount         float4 NOT NULL CHECK (amount >= 0),
        data_points    float4 CHECK (data_points >= 0),
        derivation_id  float4 CHECK (derivation_id >= 0),
        min_value      float4 CHECK (min_value >= 0),
        max_value      float4 CHECK (max_value >= 0),
        median         float4 CHECK (median >= 0),
        footnote       float4,
        min_year_acquired float4 CHECK (min_year_acquired >= 0),
        CONSTRAINT uq_ingredient_nutrient UNIQUE (ingredient_id, nutrient_id)
);


CREATE TABLE public.ingredients (
        id serial NOT NULL PRIMARY KEY,
        data_type text NULL,
        description text NULL,
        food_category_id float4 NULL CHECK (food_category_id >= 0),
        publication_date date NULL
);


CREATE TABLE public.meals (
        id serial NOT NULL PRIMARY KEY,
        mealtime text NULL,
        "date" text NULL,
        CONSTRAINT meal_pkey PRIMARY KEY (id),
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE public.recipe (
        id serial4 NOT NULL PRIMARY KEY,
        "name" text NULL,
        steps text NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE public.meal_recipes (
        id serial NOT NULL PRIMARY KEY,
        meal_id int4 NOT NULL,
        recipe_id int4 NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        CONSTRAINT meal_recipes_meal_id_fkey FOREIGN KEY (meal_id) REFERENCES public.meals(id),
        CONSTRAINT meal_recipes_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipe(id)
);

CREATE TABLE public.measure_unit (
        id serial NOT NULL PRIMARY KEY,
        "name" text NULL
);

CREATE TABLE public.nutrient (
        id serial NOT NULL PRIMARY KEY,
        "name" text NULL,
        unit_name text NULL,
        nutrient_nbr float4 NULL,
        "rank" float4 NULL
);

CREATE TABLE public.recipe_amounts (
        recipe_id int4 NOT NULL,
        amount int4 NULL CHECK (amount >= 0),
        ingredient_id int4 NULL,
        CONSTRAINT fk_recipe FOREIGN KEY (recipe_id) REFERENCES public.recipe(id)
);

CREATE TABLE public.user_ingredients (
        id int4 NOT NULL PRIMARY KEY,
        user_id int4 NOT NULL,
        ingredient_id int4 NOT NULL,
        amount int4 NULL CHECK (amount >= 0),
        "description" text NULL,
        measure_unit_name text NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


INSERT INTO ingredients (id, data_type, description, food_category_id, publication_date) VALUES
(748967, 'foundation_food', 'EGGS, GRADE A, LARGE, egg whole', 1, '2019-12-16');

INSERT INTO measure_unit (id, name) VALUES
(1099, 'egg');

INSERT INTO public.food_portion (id, seq_num, amount, measure_unit_id, portion_description, modifier, gram_weight, data_points, footnote, min_year_acquired)
VALUES (748967, 1, 1, 1099, NULL, 'whole without shell', 50.3, 526, NULL, 2019);


INSERT INTO nutrient (id, name, unit_name, nutrient_nbr, rank) VALUES
(1008, 'Energy', 'KCAL', NULL, NULL),
(1003, 'Protein', 'G', NULL, NULL),
(1005, 'Carbohydrates', 'G', NULL, NULL),
(1004, 'Total lipid (fat)', 'G', NULL, NULL);

INSERT INTO ingredient_nutrient (
    id, ingredient_id, nutrient_id,
    amount, data_points, derivation_id,
    min_value, max_value, median,
    footnote, min_year_acquired
) VALUES
(748962, 748967, 1008, 148,  NULL, NULL, NULL, NULL, NULL, NULL, NULL),  -- Energy
(748961, 748967, 1003, 12.4, NULL, NULL, NULL, NULL, NULL, NULL, NULL),  -- Protein
(748964, 748967, 1005, 2,    NULL, NULL, NULL, NULL, NULL, NULL, NULL),  -- Carbs
(748963, 748967, 1004, 9.96, NULL, NULL, NULL, NULL, NULL, NULL, NULL);  -- Fat



-- Insert black beans
INSERT INTO ingredients (id, data_type, description, food_category_id, publication_date) VALUES
(739546, 'foundation_food', 'BLACK BEANS, CANNED', 1, '2019-12-16');

INSERT INTO measure_unit (id, name) VALUES
(1100, 'can');

INSERT INTO food_portion (id, seq_num, amount, measure_unit_id, portion_description, modifier, gram_weight, data_points, footnote, min_year_acquired)
VALUES (739546, 1, 1, 1100, NULL, NULL, 256, NULL, NULL, 2019);


-- Insert onions
INSERT INTO ingredients (id, data_type, description, food_category_id, publication_date) VALUES
(739562, 'foundation_food', 'ONION, WHOLE', 1, '2019-12-16');

INSERT INTO measure_unit (id, name) VALUES
(1101, 'piece');

INSERT INTO food_portion (id, seq_num, amount, measure_unit_id, portion_description, modifier, gram_weight, data_points, footnote, min_year_acquired)
VALUES (739562, 1, 1, 1101, NULL, NULL, 110, NULL, NULL, 2019);

-- Insert ground beef
INSERT INTO ingredients (id, data_type, description, food_category_id, publication_date) VALUES
(385662, 'foundation_food', 'GROUND BEEF', 1, '2019-12-16');

INSERT INTO measure_unit (id, name) VALUES
(1102, 'package');

INSERT INTO food_portion (id, seq_num, amount, measure_unit_id, portion_description, modifier, gram_weight, data_points, footnote, min_year_acquired)
VALUES (385662, 1, 1, 1102, NULL, NULL, 454, NULL, NULL, 2019);