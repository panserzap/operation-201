Operation 201

A FastAPI backend for part traceability and visual defect inspection.

It supports registering manufactured parts, attaching quality inspections to their history, and calculating basic quality statistics.

Run
pip install -e ".[dev]"
uvicorn app.main:app --reload

Then visit:

http://localhost:8000/docs

Or with Docker:

docker build -t operation-201 .
docker run --rm -p 8000:8000 operation-201
Quality
python -m ruff check .
python -m ruff format --check .
python -m pytest

Persistence is intentionally in-memory. The goal was to keep the project small and focus on API design, validation, testing, and the manufacturing domain rather than build an entire factory platform.

And yes, /tea returns 418.