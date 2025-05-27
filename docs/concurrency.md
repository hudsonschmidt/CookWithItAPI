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

