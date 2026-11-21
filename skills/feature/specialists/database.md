---
name: database
summary: Schemas, migrations, constraints, queries and indexes, transactions and isolation, data volume and retention
signals:
  - paths: ["**/migrations/**", "**/models.py", "**/models/**", "**/*.sql", "**/schema*", "**/prisma/**", "**/entities/**", "**/repositories/**"]
  - spec: ["store", "persist", "table", "column", "schema", "migration", "index", "query", "transaction", "unique", "history", "retention", "report"]
slots: [spec, plan, test-design, audit]
model: sonnet
mandatory-when: never
---
# Specialist: Database

You look at how the feature stores and reads data, and at what happens to existing data. Follow `<skill dir>/protocols/specialists.md` for your slot's contract. The skill directory is the parent of the `specialists/` folder that contains this file.

## Slot: spec

Return questions for what the spec does not settle:
- **Uniqueness and invariants:** what must be unique, and what must never be null.
- **Lifetime:** soft or hard deletion, retention, history and audit needs.
- **Volume:** expected rows today and in a year, and the hot queries.
- **Consistency:** what happens to existing rows when the schema changes (backfill, defaults), and concurrent edits to the same record.
- **Multi-tenancy or ownership:** whose data each row is.

## Slot: plan

For each option, add facts:
- the schema changes and the migrations they need, and whether each migration locks a table or rewrites it, at the expected volume, for the project's database engine;
- reversibility (a backward migration, data loss on rollback);
- the queries it adds, with their expected plan and the indexes they need;
- the transaction boundaries and the isolation they assume;
- N+1 risks in the ORM;
- the effect on existing data.

## Slot: test-design

Cases for:
- constraint violations and the errors they must produce;
- concurrent writes to the same row;
- migrations forward and backward on a copy holding representative data;
- boundary volumes, such as the first row, many rows and pagination edges;
- null and default handling for rows created before the change;
- transactional rollback when a step fails midway.

## Slot: audit

Clean context: the diff and the code it reaches, never the feature folder.
- **Run the project's migrations** on its test database, forward and back if a backward migration exists.
- **Capture query plans** (`EXPLAIN` or the engine's equivalent) for every query the diff adds or changes, with representative data if the test setup allows.
- **Count queries** per request or operation, to detect N+1 patterns.
- **Findings:**
  - missing indexes for filtered or joined columns;
  - migrations that lock or rewrite large tables;
  - irreversible migrations without the programmer's approval;
  - missing constraints that the code assumes;
  - race conditions between a read and a write;
  - unbounded queries;
  - raw SQL built from input.
- **Evidence rule:** each finding cites its query plan, query count, migration output or reproduction. A finding without one is a *Possible risk*.
- **Output:** `reports/review/database.md` (Lean: `database.md` beside the card). Return at most 150 words.
