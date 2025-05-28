# concurrency.md

## Non-Repeatable Read in Recipe Service

### Description

A **Non-Repeatable Read** occurs when a transaction reads the same data twice and gets different results because another concurrent transaction modified and committed that data in between the two reads.

### Scenario

In our service, the `/search/{recipe_id}` endpoint reads a recipe and its ingredients. If one client reads a recipe’s ingredients twice during a transaction, but another client updates the recipe’s ingredients between those reads, the first client will see inconsistent data.

### Sequence Diagram

```

Client 1                 Database               Client 2
|                        |                      |
|-- Begin T1 ----------->|                      |
|-- SELECT recipe ------>|                      |
|<- Returns ingredients -|                      |
|                        |                      |
|                        |<--- Begin T2 --------|
|                        |--- UPDATE ingredients|
|                        |--- Commit T2 --------|
|-- SELECT recipe ------>|                      | (data changed)
|<- Returns updated data-|                      |
|--- Commit T1 --------->|

```

We get a different set of ingredients between both reads in T1.

### Solution

To avoid this issue, use the **Repeatable Read** isolation level for transactions that read recipe data multiple times. This ensures that once data is read within a transaction, subsequent reads see the same data, preventing non-repeatable reads.

---


## Lost Update in /ingredients/{user_id}/add-ingredients

### Description
A **Lost Update** occurs when two concurrent transactions overwrite each other’s changes because each one reads the same row, derives a new value, and then writes it back without noticing the other write.

### Scenario
Assume we switch from the current append-only pattern to a simple “update the running total” on user_ingredients:
1. Both clients read the amount for (user_id = 42, ingredient_id = 748967) (10 eggs).
2. Client A decides to add 4 → intends to write 14.
3. Client B decides to remove 2 → intends to write 8.
Whoever commits last wins; the other update is silently lost.

### Sequence Diagram

```

Client A (T1)                 Database                 Client B (T2)
|                             |                        |
|-- BEGIN ------------------->|                        |
|-- SELECT amount (10) ------>|                        |
|                                                      |-- BEGIN
|                                                      |-- SELECT amount (10)
|-- UPDATE amount=14 -------->|                        |
|                                                      |-- UPDATE amount=8
|-- COMMIT ------------------>| (amount now 8)         |-- COMMIT

```

The increment from Client A disappeared.

### Solution

To avoid this issue, we need to use SELECT … FOR UPDATE (pessimistic locking) on the target row before computing the new amount. Or, we can keep the append-only design because sums are commutative and sidestep the lost-update hazard altogether.


---


## Dirty Read in /meals/macros Endpoint

### Description
A **Dirty Read** happens when a transaction reads data that another concurrent transaction has modified but not yet committed.
If the writer subsequently rolls back, the reader has consumed data that never officially existed.

### Scenario
Transaction T2 is still assembling a new meal and adds rows to meal_recipes. Transaction T1 simultaneously calls GET /meals/macros?meal_id={meal} to compute nutrition. If the database allowed dirty reads, T1 could see the uncommitted meal_recipes rows and include them in its SUM—even though T2 might still roll back.

### Sequence Diagram

```

Client 1 (T1)            Database                 Client 2 (T2)
|                        |                        |
|-- BEGIN -------------->|                        |
|-- SELECT macros ------>|                        |
|                        |<-- BEGIN --------------|
|                        |<-- INSERT meal_recipes |
|                        |                        |
|<-- returns *dirty* sum-|                        |
|                        |<-- ROLLBACK -----------|  (user aborts)
|-- COMMIT --------------|                        |

```

T1 used rows that vanished when T2 rolled back.

### Solution

To avoid this issue, we need to use **read committed** or stricter. Read Committed guarantees that a query never sees uncommitted rows, eliminating dirty reads without adding heavy locks.

