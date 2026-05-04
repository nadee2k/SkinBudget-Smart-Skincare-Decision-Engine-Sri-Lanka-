# SkinBudget

SkinBudget is a FastAPI + PostgreSQL skincare recommendation app for the Sri Lankan market. It builds a routine recommendation from seeded product and ingredient data while keeping the total routine cost within the user's budget.

## What it does

- lets a user choose a skin type, concerns, and total budget
- scores products using concern fit, skin-type fit, ratings, popularity, and ingredient conflict penalties
- picks the best routine combination that stays within the full budget
- serves a simple static frontend from the same FastAPI app

## Project structure

- [`backend/`](/home/Dhananjana/GitHub/SkinBudget-Smart-Skincare-Decision-Engine-Sri-Lanka-/backend) FastAPI app, config, database access, recommendation engine, seed runner
- [`db/seeds/reference_data.sql`](/home/Dhananjana/GitHub/SkinBudget-Smart-Skincare-Decision-Engine-Sri-Lanka-/db/seeds/reference_data.sql) reference brands, products, ingredients, and scores
- [`migrations/`](/home/Dhananjana/GitHub/SkinBudget-Smart-Skincare-Decision-Engine-Sri-Lanka-/migrations) Alembic schema migration
- [`static/`](/home/Dhananjana/GitHub/SkinBudget-Smart-Skincare-Decision-Engine-Sri-Lanka-/static) frontend HTML, CSS, and JavaScript
- [`tests/`](/home/Dhananjana/GitHub/SkinBudget-Smart-Skincare-Decision-Engine-Sri-Lanka-/tests) regression tests for routine optimization and API validation

## Run with Docker

1. Copy `.env.example` to `.env` if needed.
2. Start the stack:

```bash
./run.sh
```

3. Open `http://localhost:8000`.

The Docker flow starts:

- PostgreSQL
- Alembic migrations
- reference data seeding
- the FastAPI app

## Run locally

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start PostgreSQL and create a database that matches `DB_DSN`.
3. Run the schema migration:

```bash
alembic upgrade head
```

4. Seed reference data:

```bash
python -m backend.seed
```

5. Start the app:

```bash
python -m backend.main
```

## Tests

Run the current regression suite with:

```bash
python -m unittest tests.test_recommendation tests.test_api

The repository also includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs the same compile and test checks on every push and pull request.
```

## Current quality improvements already included

- total budget optimization across the full routine
- request validation for empty and invalid inputs
- database-backed validation for unknown skin types and concerns
- safer API error messages
- inline frontend form errors instead of blocking alerts
- safer DOM rendering for recommendation cards
