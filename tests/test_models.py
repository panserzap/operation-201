from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models import (
    DefectSeverity,
    InspectionCreate,
    InspectionResult,
    Part,
    PartCreate,
)


def inspection(**overrides):
    data = {
        "station_id": "sentry-camera-03",
        "result": "no_defect",
        "confidence": 0.98,
    }
    data.update(overrides)
    return InspectionCreate(**data)


def test_part_create():
    part = PartCreate(part_number="M10-BOLT-40")

    assert part.part_number == "M10-BOLT-40"
    assert part.batch_id is None


def test_part_generates_server_fields():
    part = Part(part_number="M10-BOLT-40", batch_id="BATCH-001")

    assert part.part_uid.startswith("PART-")
    assert isinstance(part.created_at, datetime)


def test_part_create_rejects_extra_fields():
    with pytest.raises(ValidationError):
        PartCreate(part_number="M10-BOLT-40", part_uid="NOT-MY-FIELD")


def test_clean_inspection():
    result = inspection()

    assert result.result == InspectionResult.NO_DEFECT
    assert result.confidence == 0.98
    assert result.severity is None
    assert result.defect_type is None


def test_defect_inspection():
    result = inspection(
        result="defect_detected",
        confidence=0.94,
        severity="high",
        defect_type="surface_crack",
    )

    assert result.result == InspectionResult.DEFECT_DETECTED
    assert result.severity == DefectSeverity.HIGH
    assert result.defect_type == "surface_crack"


@pytest.mark.parametrize(
    "overrides",
    [
        {"result": "defect_detected"},
        {"result": "no_defect", "severity": "high"},
        {"result": "no_defect", "defect_type": "surface_crack"},
    ],
)
def test_invalid_defect_combinations_are_rejected(overrides):
    with pytest.raises(ValidationError):
        inspection(**overrides)


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_invalid_confidence_is_rejected(confidence):
    with pytest.raises(ValidationError):
        inspection(confidence=confidence)


@pytest.mark.parametrize("confidence", [0, 1])
def test_confidence_boundaries_are_valid(confidence):
    result = inspection(confidence=confidence)

    assert result.confidence == confidence


def test_invalid_result_is_rejected():
    with pytest.raises(ValidationError):
        inspection(result="the_camera_has_vibes")


def test_invalid_severity_is_rejected():
    with pytest.raises(ValidationError):
        inspection(
            result="defect_detected",
            severity="c3po_cannot_translate_this",
        )


def test_inspection_create_rejects_extra_fields():
    with pytest.raises(ValidationError):
        inspection(inspection_id="YOU-SHALL-NOT-PICK-YOUR-OWN-ID")