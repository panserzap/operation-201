# Operation 201

A FastAPI backend for part traceability and visual defect inspection.

Built as a small, slightly rebellious application for Matta's Backend Engineer role.

**Live API:** https://operation-201.onrender.com/docs

## What it does

* Registers manufactured parts with unique IDs
* Attaches defect inspections to part history
* Validates inspection data with Pydantic
* Provides basic quality statistics

## Run locally

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Then visit:

```text
http://localhost:8000/docs
```

Or with Docker:

```bash
docker build -t operation-201 .
docker run --rm -p 8000:8000 operation-201
```

## Quality

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

Persistence is intentionally in-memory. The goal was to keep the project small and focus on API design, validation, testing, and the manufacturing domain rather than build an entire factory platform.

And yes, `/tea` returns `418`.
