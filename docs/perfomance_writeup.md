### Write up of how many rows of data we have and also why we think the service would scale in this way.

---

# API Endpoint Performance Tuning Report

## Endpoint Performance Results

| Endpoint         | Execution Time (ms) |
| ---------------- | ------------------- |
| **Search**       | 138                 |
| Macro Per Recipe | 589                 |
| User Ingredients | 19                  |

**Slowest Endpoint:**
**Macro Per Recipe** (`/macro-per-recipe`), at **589 ms**.

---

## 1. Search Endpoint

### Initial Query with Execution Time

```sql
EXPLAIN ANALYZE
SELECT DISTINCT ON (i.description) i.id, i.description, mu.name AS measure_unit
FROM ingredients AS i
JOIN food_portion AS fp ON fp.id = i.id
JOIN measure_unit AS mu ON mu.id = fp.measure_unit_id
WHERE i.description ILIKE '%egg%'
ORDER BY i.description, i.publication_date DESC
LIMIT 10;
```

**EXPLAIN Output:**

```
Limit  (cost=17100.36..17100.41 rows=10 width=56) (actual time=137.169..138.169 rows=1 loops=1)
  ->  Unique  (cost=17100.36..17100.43 rows=15 width=56) (actual time=137.166..138.165 rows=1 loops=1)
        ->  Sort  (cost=17100.36..17100.40 rows=15 width=56) (actual time=137.165..138.164 rows=1 loops=1)
              Sort Key: i.description, i.publication_date DESC
              Sort Method: quicksort  Memory: 25kB
              ->  Gather  (cost=1000.58..17100.06 rows=15 width=56) (actual time=1.119..138.087 rows=1 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    ->  Nested Loop  (cost=0.58..16098.56 rows=6 width=56) (actual time=87.111..132.412 rows=0 loops=3)
                          ->  Nested Loop  (cost=0.43..16091.25 rows=43 width=28) (actual time=87.105..132.406 rows=0 loops=3)
                                ->  Parallel Seq Scan on ingredients i  (cost=0.00..15721.35 rows=44 width=24) (actual time=87.090..132.390 rows=0 loops=3)
"                                      Filter: (description ~~* '%egg%'::text)"
                                      Rows Removed by Filter: 350704
                                ->  Index Scan using food_portion_pkey on food_portion fp  (cost=0.43..8.41 rows=1 width=8) (actual time=0.039..0.039 rows=1 loops=1)
                                      Index Cond: (id = i.id)
                          ->  Index Scan using measure_unit_pkey on measure_unit mu  (cost=0.15..0.17 rows=1 width=36) (actual time=0.014..0.014 rows=1 loops=1)
                                Index Cond: (id = fp.measure_unit_id)
Planning Time: 1.233 ms
Execution Time: 138.237 ms
```

### Hypothesis about what index will make it faster

Adding an index over `data_type` in `ingredients` will allow the query to more efficiently filter data when a `data_type` filter is applied, which should speed up the search.

### Index Creation

```sql
CREATE INDEX idx_ingredients_data_type ON ingredients(data_type);
```

### Query After Index Creation

```sql
EXPLAIN ANALYZE
SELECT DISTINCT ON (i.description) i.id, i.description, mu.name AS measure_unit
FROM ingredients AS i
JOIN food_portion AS fp ON fp.id = i.id
JOIN measure_unit AS mu ON mu.id = fp.measure_unit_id
WHERE i.description ILIKE '%egg%' AND data_type = 'whole_food'
ORDER BY i.description, i.publication_date DESC
LIMIT 10;
```

**EXPLAIN Output:**

```
Limit  (cost=17610.21..17610.22 rows=3 width=56) (actual time=47.079..49.314 rows=0 loops=1)
  ->  Unique  (cost=17610.21..17610.22 rows=3 width=56) (actual time=47.076..49.311 rows=0 loops=1)
        ->  Sort  (cost=17610.21..17610.21 rows=3 width=56) (actual time=47.076..49.310 rows=0 loops=1)
              Sort Key: i.description, i.publication_date DESC
              Sort Method: quicksort  Memory: 25kB
              ->  Gather  (cost=3152.39..17610.18 rows=3 width=56) (actual time=47.064..49.298 rows=0 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    ->  Nested Loop  (cost=2152.39..16609.88 rows=1 width=56) (actual time=35.482..35.483 rows=0 loops=3)
                          ->  Nested Loop  (cost=2152.24..16608.52 rows=8 width=28) (actual time=35.481..35.482 rows=0 loops=3)
                                ->  Parallel Bitmap Heap Scan on ingredients i  (cost=2151.81..16540.96 rows=8 width=24) (actual time=35.481..35.481 rows=0 loops=3)
"                                      Recheck Cond: (data_type = 'whole_food'::text)"
"                                      Filter: (description ~~* '%egg%'::text)"
                                      Rows Removed by Filter: 65830
                                      Heap Blocks: exact=1598
                                      ->  Bitmap Index Scan on idx_ingredients_data_type  (cost=0.00..2151.81 rows=196184 width=0) (actual time=5.805..5.805 rows=197489 loops=1)
"                                            Index Cond: (data_type = 'whole_food'::text)"
                                ->  Index Scan using food_portion_pkey on food_portion fp  (cost=0.43..8.45 rows=1 width=8) (never executed)
                                      Index Cond: (id = i.id)
                          ->  Index Scan using measure_unit_pkey on measure_unit mu  (cost=0.15..0.17 rows=1 width=36) (never executed)
                                Index Cond: (id = fp.measure_unit_id)
Planning Time: 1.232 ms
Execution Time: 49.370 ms
```

### Conclusion about whether the query was sped up or not

The query execution time improved significantly from **138 ms** to **49 ms** after creating the `data_type` index and filtering by it. The index creation was successful in speeding up the query.

---

## 2. Macro Per Recipe Endpoint

### Initial Query with Execution Time

```sql
EXPLAIN ANALYZE
WITH macro_per_recipe AS (
    SELECT
        r.id AS recipe_id,
        r.name AS recipe_name,
        r.steps AS steps,
        SUM(CASE WHEN n.name = 'Protein' THEN ra.amount * inut.amount / 100 ELSE 0 END) AS protein_g,
        SUM(CASE WHEN n.name = 'Energy' THEN ra.amount * inut.amount / 100 ELSE 0 END) AS energy_kcal,
        SUM(CASE WHEN n.name = 'Carbohydrate, by difference' THEN ra.amount * inut.amount / 100 ELSE 0 END) AS carbs_g,
        SUM(CASE WHEN n.name = 'Total lipid (fat)' THEN ra.amount * inut.amount / 100 ELSE 0 END) AS fats_g
    FROM recipe AS r
    LEFT JOIN recipe_amounts AS ra ON ra.recipe_id = r.id
    LEFT JOIN ingredient_nutrient AS inut ON inut.ingredient_id = ra.ingredient_id
    LEFT JOIN nutrient AS n ON n.id = inut.nutrient_id
    GROUP BY r.id, r.name, r.steps
)
SELECT *
FROM macro_per_recipe
ORDER BY recipe_id;
```

**EXPLAIN Output:**

```
GroupAggregate  (cost=163370.77..163825.44 rows=780 width=100) (actual time=587.059..587.066 rows=2 loops=1)
  Group Key: r.id
  ->  Sort  (cost=163370.77..163391.08 rows=8125 width=108) (actual time=587.041..587.044 rows=11 loops=1)
        Sort Key: r.id
        Sort Method: quicksort  Memory: 25kB
        ->  Hash Left Join  (cost=142103.29..162843.12 rows=8125 width=108) (actual time=578.276..587.034 rows=11 loops=1)
              Hash Cond: (inut.nutrient_id = n.id)
              ->  Hash Right Join  (cost=142075.74..162794.13 rows=8125 width=80) (actual time=578.260..587.015 rows=11 loops=1)
                    Hash Cond: (ra.recipe_id = r.id)
                    ->  Hash Left Join  (cost=142048.20..162745.15 rows=8125 width=16) (actual time=563.631..572.382 rows=10 loops=1)
                          Hash Cond: (ra.ingredient_id = inut.ingredient_id)
                          ->  Seq Scan on recipe_amounts ra  (cost=0.00..30.40 rows=2040 width=12) (actual time=0.015..0.016 rows=1 loops=1)
                          ->  Hash  (cost=68891.42..68891.42 rows=4208542 width=12) (actual time=563.555..563.555 rows=4208432 loops=1)
                                Buckets: 262144  Batches: 64  Memory Usage: 4864kB
                                ->  Seq Scan on ingredient_nutrient inut  (cost=0.00..68891.42 rows=4208542 width=12) (actual time=0.008..220.587 rows=4208432 loops=1)
                    ->  Hash  (cost=17.80..17.80 rows=780 width=68) (actual time=14.620..14.620 rows=2 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 9kB
                          ->  Seq Scan on recipe r  (cost=0.00..17.80 rows=780 width=68) (actual time=14.603..14.607 rows=2 loops=1)
              ->  Hash  (cost=17.80..17.80 rows=780 width=36) (actual time=0.008..0.009 rows=4 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 9kB
                    ->  Seq Scan on nutrient n  (cost=0.00..17.80 rows=780 width=36) (actual time=0.006..0.007 rows=4 loops=1)

JIT:
  Functions: 31
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 1.941 ms (Deform 0.806 ms), Inlining 0.000 ms, Optimization 0.782 ms, Emission 13.849 ms, Total 16.573 ms

Planning Time: 0.669 ms
Execution Time: 589.147 ms
```

### Hypothesis about what index will make it faster

Adding an index over `ingredient_nutrient(nutrient_id)` will help the hash join on `inut.nutrient_id = n.id` by making it faster to find nutrient matches.

### Index Creation

```sql
CREATE INDEX ingredient_nutrient_index ON ingredient_nutrient(nutrient_id);
```

### Query After Index Creation

(Same query as above)

**EXPLAIN Output:**

```
GroupAggregate  (cost=163366.29..163820.97 rows=780 width=100) (actual time=626.133..626.139 rows=2 loops=1)
  Group Key: r.id
  ->  Sort  (cost=163366.29..163386.60 rows=8125 width=108) (actual time=626.117..626.119 rows=11 loops=1)
        Sort Key: r.id
        Sort Method: quicksort  Memory: 25kB
        ->  Hash Left Join  (cost=142099.82..162838.65 rows=8125 width=108) (actual time=618.009..626.109 rows=11 loops=1)
              Hash Cond: (inut.nutrient_id = n.id)
              ->  Hash Right Join  (cost=142072.27..162789.66 rows=8125 width=80) (actual time=617.986..626.085 rows=11 loops=1)
                    Hash Cond: (ra.recipe_id = r.id)
                    ->  Hash Left Join  (cost=142044.72..162740.67 rows=8125 width=16) (actual time=604.246..612.341 rows=10 loops=1)
                          Hash Cond: (ra.ingredient_id = inut.ingredient_id)
                          ->  Seq Scan on recipe_amounts ra  (cost=0.00..30.40 rows=2040 width=12) (actual time=0.014..0.015 rows=1 loops=1)
                          ->  Hash  (cost=68890.32..68890.32 rows=4208432 width=12) (actual time=604.183..604.183 rows=4208432 loops=1)
                                Buckets: 262144  Batches: 64  Memory Usage: 4864kB
                                ->  Seq Scan on ingredient_nutrient inut  (cost=0.00..68890.32 rows=4208432 width=12) (actual time=0.006..261.154 rows=4208432 loops=1)
                    ->  Hash  (cost=17.80..17.80 rows=780 width=68) (actual time=13.731..13.732 rows=2 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 9kB
                          ->  Seq Scan on recipe r  (cost=0.00..17.80 rows=780 width=68) (actual time=13.717..13.720 rows=2 loops=1)
              ->  Hash  (cost=17.80..17.80 rows=780 width=36) (actual time=0.009..0.009 rows=4 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 9kB
                    ->  Seq Scan on nutrient n  (cost=0.00..17.80 rows=780 width=36) (actual time=0.007..0.007 rows=4 loops=1)
Planning Time: 1.084 ms
JIT:
  Functions: 31
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 1.765 ms (Deform 0.640 ms), Inlining 0.000 ms, Optimization 0.761 ms, Emission 12.984 ms, Total 15.510 ms
Execution Time: 628.023 ms
```

### Conclusion about whether the query was sped up or not

Adding the index on `nutrient_id` **did not speed up the query**; execution time increased from 589 ms to 628 ms. The query remains slow and would need a different strategy for significant improvement.

---

## 3. User Ingredients Endpoint

### Initial Query with Execution Time

```sql
EXPLAIN ANALYZE
SELECT DISTINCT r.id AS rid, r.name AS rname, r.steps, i.id AS iid, i.description AS iname, ra.amount, mu.name AS measuring_unit
FROM recipe AS r
JOIN recipe_match AS rm ON rm.id = r.id
JOIN recipe_amounts AS ra ON r.id = ra.recipe_id 
JOIN ingredients AS i ON ra.ingredient_id = i.id
JOIN food_portion AS fp ON fp.id = i.id
JOIN measure_unit AS mu ON mu.id = fp.measure_unit_id
GROUP BY r.id, i.id, ra.amount, mu.name
```

**EXPLAIN Output:**

```
Unique  (cost=6246.42..6265.94 rows=1 width=124) (actual time=18.895..18.942 rows=1 loops=1)
  ->  Incremental Sort  (cost=6246.42..6265.91 rows=2 width=124) (actual time=18.895..18.941 rows=1 loops=1)
        Sort Key: r.id, r.name, r.steps, i.id, i.description, ra.amount, mu.name
        Presorted Key: r.id
        Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 25kB  Peak Memory: 25kB
        ->  Group  (cost=6227.01..6265.82 rows=1 width=124) (actual time=18.883..18.930 rows=1 loops=1)
              Group Key: r.id, i.id, ra.amount, mu.name
              ->  Incremental Sort  (cost=6227.01..6265.80 rows=2 width=124) (actual time=18.882..18.928 rows=1 loops=1)
                    Sort Key: r.id, i.id, ra.amount, mu.name
                    Presorted Key: r.id
                    Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 25kB  Peak Memory: 25kB
                    ->  Nested Loop  (cost=6188.29..6265.71 rows=1 width=124) (actual time=18.879..18.925 rows=1 loops=1)
                          Join Filter: (i.id = ra.ingredient_id)
                          ->  Nested Loop  (cost=6187.86..6265.18 rows=1 width=112) (actual time=18.866..18.912 rows=1 loops=1)
                                ->  Nested Loop  (cost=6187.71..6263.48 rows=10 width=84) (actual time=18.862..18.907 rows=1 loops=1)
                                      ->  Merge Join  (cost=6187. 28..6191.80 rows=10 width=76) (actual time=18.851..18.897 rows=1 loops=1)
Merge Cond: (rm.id = r.id)
->  Sort  (cost=6132.01..6132.12 rows=41 width=16) (actual time=18.847..18.892 rows=1 loops=1)
Sort Key: rm.id
Sort Method: quicksort  Memory: 25kB
->  Hash Join  (cost=6095.05..6130.92 rows=41 width=16) (actual time=18.843..18.888 rows=1 loops=1)
Hash Cond: (ra.recipe\_id = rm.id)
->  Seq Scan on recipe\_amounts ra  (cost=0.00..30.40 rows=2040 width=12) (actual time=0.012..0.013 rows=1 loops=1)
->  Hash  (cost=6095.00..6095.00 rows=4 width=4) (actual time=18.824..18.869 rows=1 loops=1)
Buckets: 1024  Batches: 1  Memory Usage: 9kB
->  Subquery Scan on rm  (cost=6037.53..6095.00 rows=4 width=4) (actual time=18.822..18.867 rows=1 loops=1)
->  Limit  (cost=6037.53..6094.96 rows=4 width=8) (actual time=18.822..18.866 rows=1 loops=1)
->  GroupAggregate  (cost=6037.53..6094.96 rows=4 width=8) (actual time=18.820..18.864 rows=1 loops=1)
Group Key: r\_1.id
Filter: (min((CASE WHEN ((sum(ui.amount)) >= ra\_1.amount) THEN 1 ELSE 0 END)) = 1)
->  Merge Join  (cost=6037.53..6080.06 rows=1030 width=8) (actual time=18.817..18.861 rows=1 loops=1)
Merge Cond: (ra\_1.recipe\_id = r\_1.id)
->  Group  (cost=5982.27..5997.72 rows=1030 width=24) (actual time=18.801..18.844 rows=1 loops=1)
Group Key: ra\_1.recipe\_id, ra\_1.ingredient\_id, (sum(ui.amount)), ra\_1.amount
->  Sort  (cost=5982.27..5984.84 rows=1030 width=20) (actual time=18.799..18.842 rows=1 loops=1)
Sort Key: ra\_1.recipe\_id, ra\_1.ingredient\_id, (sum(ui.amount)), ra\_1.amount
Sort Method: quicksort  Memory: 25kB
->  Hash Join  (cost=5894.86..5930.72 rows=1030 width=20) (actual time=18.794..18.838 rows=1 loops=1)
Hash Cond: (ra\_1.ingredient\_id = ui.ingredient\_id)
->  Seq Scan on recipe\_amounts ra\_1  (cost=0.00..30.40 rows=2040 width=12) (actual time=0.001..0.002 rows=1 loops=1)
->  Hash  (cost=5893.59..5893.59 rows=101 width=12) (actual time=18.785..18.828 rows=102 loops=1)
Buckets: 1024  Batches: 1  Memory Usage: 13kB
->  Finalize GroupAggregate  (cost=5862.52..5893.59 rows=101 width=12) (actual time=17.103..18.811 rows=102 loops=1)
Group Key: ui.ingredient\_id
->  Gather Merge  (cost=5862.52..5891.57 rows=202 width=12) (actual time=17.082..18.783 rows=103 loops=1)
Workers Planned: 2
Workers Launched: 2
->  Partial GroupAggregate  (cost=4862.49..4868.23 rows=101 width=12) (actual time=5.787..6.338 rows=34 loops=3)
Group Key: ui.ingredient\_id
->  Sort  (cost=4862.49..4864.07 rows=631 width=8) (actual time=5.724..5.978 rows=5500 loops=3)
Sort Key: ui.ingredient\_id
Sort Method: quicksort  Memory: 735kB
Worker 0:  Sort Method: quicksort  Memory: 25kB
Worker 1:  Sort Method: quicksort  Memory: 85kB
->  Parallel Seq Scan on user\_ingredients ui  (cost=0.00..4833.15 rows=631 width=8) (actual time=0.009..5.069 rows=5500 loops=3)
Filter: (user\_id = 1)
Rows Removed by Filter: 49146
->  Sort  (cost=55.27..57.22 rows=780 width=4) (actual time=0.014..0.014 rows=2 loops=1)
Sort Key: r\_1.id
Sort Method: quicksort  Memory: 25kB
->  Seq Scan on recipe r\_1  (cost=0.00..17.80 rows=780 width=4) (actual time=0.009..0.009 rows=2 loops=1)
->  Sort  (cost=55.27..57.22 rows=780 width=68) (actual time=0.002..0.003 rows=2 loops=1)
Sort Key: r.id
Sort Method: quicksort  Memory: 25kB
->  Seq Scan on recipe r  (cost=0.00..17.80 rows=780 width=68) (actual time=0.001..0.001 rows=2 loops=1)
->  Index Scan using food\_portion\_pkey on food\_portion fp  (cost=0.43..7.17 rows=1 width=8) (actual time=0.008..0.008 rows=1 loops=1)
Index Cond: (id = ra.ingredient\_id)
->  Index Scan using measure\_unit\_pkey on measure\_unit mu  (cost=0.15..0.17 rows=1 width=36) (actual time=0.003..0.003 rows=1 loops=1)
Index Cond: (id = fp.measure\_unit\_id)
->  Index Scan using ingredients\_pkey on ingredients i  (cost=0.43..0.51 rows=1 width=20) (actual time=0.011..0.011 rows=1 loops=1)
Index Cond: (id = fp.id)
Planning Time: 2.322 ms
Execution Time: 19.071 ms

````

### Hypothesis about what index will make it faster

Adding an index over `user_id` in `user_ingredients` should make it much faster to retrieve only the relevant user's ingredients.

### Index Creation

```sql
CREATE INDEX user_id_index ON user_ingredients(user_id);
````

### Query After Index Creation

(Same query as above)

**EXPLAIN Output:**

```
Unique  (cost=3828.27..3828.39 rows=1 width=124) (actual time=11.154..11.160 rows=1 loops=1)
  ->  Incremental Sort  (cost=3828.27..3828.36 rows=2 width=124) (actual time=11.153..11.158 rows=1 loops=1)
        Sort Key: r.id, r.name, r.steps, i.id, i.description, ra.amount, mu.name
        Presorted Key: r.id
        Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 25kB  Peak Memory: 25kB
        ->  Group  (cost=3828.25..3828.27 rows=1 width=124) (actual time=11.140..11.145 rows=1 loops=1)
              Group Key: r.id, i.id, ra.amount, mu.name
              ->  Sort  (cost=3828.25..3828.26 rows=1 width=124) (actual time=11.138..11.143 rows=1 loops=1)
                    Sort Key: r.id, i.id, ra.amount, mu.name
                    Sort Method: quicksort  Memory: 25kB
                    ->  Nested Loop  (cost=3711.28..3828.24 rows=1 width=124) (actual time=11.131..11.136 rows=1 loops=1)
                          Join Filter: (i.id = ra.ingredient_id)
                          ->  Nested Loop  (cost=3710.85..3827.72 rows=1 width=112) (actual time=11.120..11.125 rows=1 loops=1)
                                ->  Nested Loop  (cost=3710.70..3826.02 rows=10 width=84) (actual time=11.113..11.118 rows=1 loops=1)
                                      ->  Nested Loop  (cost=3710.27..3754.33 rows=10 width=76) (actual time=11.097..11.102 rows=1 loops=1)
                                            Join Filter: (r.id = rm.id)
                                            ->  Hash Join  (cost=3710.12..3745.99 rows=41 width=16) (actual time=11.071..11.075 rows=1 loops=1)
                                                  Hash Cond: (ra.recipe_id = rm.id)
                                                  ->  Seq Scan on recipe_amounts ra  (cost=0.00..30.40 rows=2040 width=12) (actual time=0.012..0.013 rows=1 loops=1)
                                                  ->  Hash  (cost=3710.07..3710.07 rows=4 width=4) (actual time=11.047..11.051 rows=1 loops=1)
                                                        Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                                        ->  Subquery Scan on rm  (cost=3700.28..3710.07 rows=4 width=4) (actual time=11.041..11.048 rows=1 loops=1)
                                                              ->  Limit  (cost=3700.28..3710.03 rows=4 width=8) (actual time=11.040..11.047 rows=1 loops=1)
                                                                    ->  HashAggregate  (cost=3700.28..3710.03 rows=4 width=8) (actual time=11.038..11.044 rows=1 loops=1)
                                                                          Group Key: r_1.id
                                                                          Filter: (min((CASE WHEN ((sum(ui.amount)) >= ra_1.amount) THEN 1 ELSE 0 END)) = 1)
                                                                          Batches: 1  Memory Usage: 49kB
                                                                          ->  HashJoin  (cost=3668.94..3695.08 rows=1040 width=8) (actual time=11.029..11.036 rows=1 loops=1)
                                                                                HashCond: (ra_1.recipe_id = r_1.id)
                                                                                ->  HashAggregate  (cost=3641.39..3654.39 rows=1040 width=24) (actual time=11.015..11.022 rows=1 loops=1)
                                                                                      Group Key: ra_1.recipe_id, ra_1.ingredient_id, (sum(ui.amount)), ra_1.amount
                                                                                      Batches: 1  Memory Usage: 73kB
                                                                                      ->  HashJoin  (cost=3595.12..3630.99 rows=1040 width=20) (actual time=11.006..11.010 rows=1 loops=1)
                                                                                            HashCond: (ra_1.ingredient_id = ui.ingredient_id)
                                                                                            ->  Seq Scan on recipe_amounts ra_1  (cost=0.00..30.40 rows=2040 width=12) (actual time=0.002..0.004 rows=1 loops=1)
                                                                                            ->  Hash  (cost=3593.85..3593.85 rows=102 width=12) (actual time=10.997..10.998 rows=102 loops=1)
                                                                                                  Buckets: 1024  Batches: 1  Memory Usage: 13kB
                                                                                                  ->  HashAggregate  (cost=3592.83..3593.85 rows=102 width=12) (actual time=10.968..10.981 rows=102 loops=1)
                                                                                                        Group Key: ui.ingredient_id
                                                                                                        Batches: 1  Memory Usage: 24kB
                                                                                                        ->  Bitmap Heap Scan on user_ingredients ui  (cost=188.45..3510.15 rows=16536 width=8) (actual time=1.273..7.850 rows=16499 loops=1)
                                                                                                              Recheck Cond: (user_id = 1)
                                                                                                              Heap Blocks: exact=2600
                                                                                                              ->  Bitmap Index Scan on user_id_index  (cost=0.00..184.31 rows=16536 width=0) (actual time=0.906..0.907 rows=16499 loops=1)
                                                                                                                    Index Cond: (user_id = 1)
                                                                                ->  Hash  (cost=17.80..17.80 rows=780 width=4) (actual time=0.010..0.010 rows=2 loops=1)
                                                                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                                                                      ->  Seq Scan on recipe r_1  (cost=0.00..17.80 rows=780 width=4) (actual time=0.005..0.005 rows=2 loops=1)
                                            ->  Index Scan using recipe_pkey on recipe r  (cost=0.15..0.19 rows=1 width=68) (actual time=0.022..0.022 rows=1 loops=1)
                                                  Index Cond: (id = ra.recipe_id)
                                      ->  Index Scan using food_portion_pkey on food_portion fp  (cost=0.43..7.17 rows=1 width=8) (actual time=0.014..0.014 rows=1 loops=1)
                                            Index Cond: (id = ra.ingredient_id)
                                ->  Index Scan using measure_unit_pkey on measure_unit mu  (cost=0.15..0.17 rows=1 width=36) (actual time=0.005..0.006 rows=1 loops=1)
                                      Index Cond: (id = fp.measure_unit_id)
                          ->  Index Scan using ingredients_pkey on ingredients i  (cost=0.43..0.51 rows=1 width=20) (actual time=0.009..0.009 rows=1 loops=1)
                                Index Cond: (id = fp.id)
Planning Time: 2.043 ms
Execution Time: 11.290 ms
```

### Conclusion about whether the query was sped up or not

Adding the index on `user_id` in `user_ingredients` sped up the query significantly, reducing execution time from **19 ms** to **11 ms**.

---