# CoolAgent Alembic Notes

Alembic is the official schema history for CoolAgent database changes. It is
being added now to make future staging/production work safer, not because those
environments are being deployed today.

## New database

For an empty database:

```bash
cd backend
alembic upgrade head
```

## Existing local development database

If your local database already has tables created by `Base.metadata.create_all()`,
do not run `alembic upgrade head` blindly. First verify that the schema matches
the baseline migration. If it does, mark it as current:

```bash
cd backend
alembic stamp head
```

If the schema does not match, either reset the local database if the data is
discardable, or write a corrective migration before stamping.

## Tests

Integration tests use a separate database, usually `coolagent_test`, so RAG
development data is not mixed with test data:

```bash
cd backend
TEST_DATABASE_URL=postgresql+asyncpg://coolagent:coolagent_dev@localhost:5432/coolagent_test pytest
```
