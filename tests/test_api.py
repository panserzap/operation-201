import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def create_part(client, part_number="M10-BOLT-40", batch_id="BATCH-001"):
    response = client.post(
        "/parts",
        json={"part_number": part_number, "batch_id": batch_id},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


def create_inspection(client, part_uid, **overrides):
    payload = {
        "station_id": "sentry-camera-03",
        "result": "no_defect",
        "confidence": 0.98,
    }
    payload.update(overrides)

    return client.post(f"/parts/{part_uid}/inspections", json=payload)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_part_can_be_created_and_retrieved(client):
    created = create_part(client)

    assert created["part_uid"].startswith("PART-")
    assert created["part_number"] == "M10-BOLT-40"
    assert created["batch_id"] == "BATCH-001"
    assert created["created_at"] is not None

    response = client.get(f"/parts/{created['part_uid']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created


def test_invalid_part_returns_422(client):
    response = client.post("/parts", json={"batch_id": "BATCH-001"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_unknown_part_returns_404(client):
    response = client.get("/parts/PART-DOES-NOT-EXIST")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Part not found"


def test_clean_inspection_can_be_created_and_retrieved(client):
    part = create_part(client)

    create_response = create_inspection(client, part["part_uid"])
    inspection = create_response.json()

    assert create_response.status_code == status.HTTP_201_CREATED
    assert inspection["inspection_id"].startswith("INS-")
    assert inspection["part_uid"] == part["part_uid"]
    assert inspection["result"] == "no_defect"
    assert inspection["severity"] is None
    assert inspection["captured_at"] is not None

    get_response = client.get(f"/parts/{part['part_uid']}/inspections")

    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json() == [inspection]


def test_defect_inspection_can_be_created(client):
    part = create_part(client)

    response = create_inspection(
        client, part["part_uid"],
        result="defect_detected", confidence=0.94,
        severity="high", defect_type="surface_crack",
    )
    inspection = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert inspection["result"] == "defect_detected"
    assert inspection["severity"] == "high"
    assert inspection["defect_type"] == "surface_crack"


def test_invalid_inspection_returns_422(client):
    part = create_part(client)

    response = create_inspection(
        client, part["part_uid"],
        result="defect_detected", confidence=0.94,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_inspection_for_unknown_part_returns_404(client):
    response = create_inspection(client, "PART-DOES-NOT-EXIST")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_inspections_are_filtered_by_part(client):
    part_one = create_part(client, part_number="M10-BOLT-40")
    part_two = create_part(client, part_number="M12-BOLT-50")

    create_inspection(
        client, part_one["part_uid"],
        result="defect_detected", confidence=0.95, severity="high",
    )
    create_inspection(client, part_two["part_uid"])

    response = client.get(f"/parts/{part_one['part_uid']}/inspections")
    inspections = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(inspections) == 1
    assert inspections[0]["part_uid"] == part_one["part_uid"]
    assert inspections[0]["result"] == "defect_detected"


def test_empty_quality_summary(client):
    response = client.get("/quality/summary")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "parts_registered": 0,
        "parts_inspected": 0,
        "total_inspections": 0,
        "defects_detected": 0,
        "defect_rate": 0.0,
        "severity_breakdown": {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
            "unclassified": 0,
        },
    }


def test_quality_summary(client):
    clean_part = create_part(client)
    defective_part = create_part(client)

    create_inspection(client, clean_part["part_uid"])
    create_inspection(
        client, defective_part["part_uid"],
        result="defect_detected", confidence=0.95,
        severity="high", defect_type="surface_crack",
    )

    response = client.get("/quality/summary")
    summary = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert summary["parts_registered"] == 2
    assert summary["parts_inspected"] == 2
    assert summary["total_inspections"] == 2
    assert summary["defects_detected"] == 1
    assert summary["defect_rate"] == pytest.approx(0.5)
    assert summary["severity_breakdown"]["high"] == 1

def test_root_points_to_docs(client):
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["hint"] == "Backend engineers usually check /docs."


def test_candidate(client):
    response = client.get("/candidate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["applying_for"] == "Backend Engineer"


def test_candidate_evidence(client):
    response = client.get("/candidate/evidence")

    assert response.status_code == status.HTTP_200_OK
    assert "production_automation" in response.json()


def test_tea(client):
    response = client.get("/tea")

    assert response.status_code == status.HTTP_418_IM_A_TEAPOT